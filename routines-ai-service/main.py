"""Microservicio de generación de rutinas de ejercicio con IA.

Utiliza Ollama (phi3:mini) para generar rutinas personalizadas
basadas en el perfil de salud del usuario y los ejercicios
disponibles en el catálogo, respetando restricciones médicas.

Estrategia Strangler Fig: código refactorizado se activa con
USE_REFACTORED_AGENT=true. Rollback cambiando la env var a false.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import re
from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import httpx

from seniorvital_shared import get_pool, init_pool, close_pool, publish_event, init_db

# -- Feature flag: toggle between old and new implementation --
USE_REFACTORED_AGENT = os.getenv("USE_REFACTORED_AGENT", "false").lower() == "true"
USE_ORCHESTRATOR_AGENT = os.getenv("USE_ORCHESTRATOR_AGENT", "false").lower() == "true"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "600"))
OLLAMA_HEALTH_CHECK_TIMEOUT = float(os.getenv("OLLAMA_HEALTH_TIMEOUT", "15"))

DEFAULT_ROUTINE = {
    "exercises": [
        {"name": "Caminata ligera", "sets": 1, "reps": 10, "rest_duration_sec": 30, "description": "Camina a paso suave", "exercise_id": 0, "duration_min": 5},
        {"name": "Estiramiento de brazos", "sets": 2, "reps": 8, "rest_duration_sec": 45, "description": "Estira los brazos hacia arriba", "exercise_id": 0, "duration_min": 3},
        {"name": "Respiración profunda", "sets": 1, "reps": 5, "rest_duration_sec": 20, "description": "Inhala y exhala profundamente", "exercise_id": 0, "duration_min": 2},
    ],
    "warmup": [{"name": "Rotación de cuello", "sets": 1, "reps": 5, "duration_min": 1}],
}


# ── Refactored components (lazy init) ──
_refactored_agent = None
_coach_agent = None
_orchestrator_agent = None


async def _get_refactored_agent():
    """Lazy-init del agente refactorizado (solo cuando se necesita)."""
    global _refactored_agent
    if _refactored_agent is None:
        from src.agents.wellness import WellnessAgent, WellnessConfig
        from src.services.llm import LLMService
        from src.services.user_data import UserDataService
        from src.database.repositories import UserRepository, ExerciseRepository, RoutineRepository
        from src.database import Database

        db_url = os.getenv("DATABASE_URL")
        # Convert asyncpg URL to async SQLAlchemy URL
        db_url_async = db_url.replace("postgresql://", "postgresql+asyncpg://")

        db = Database(db_url_async)
        session = db.session()

        config = WellnessConfig(
            llm_url=OLLAMA_URL,
            llm_model=OLLAMA_MODEL,
            llm_timeout=OLLAMA_TIMEOUT,
        )
        llm = LLMService(base_url=config.llm_url, model=config.llm_model, timeout=config.llm_timeout)
        user_data = UserDataService(UserRepository(session), ExerciseRepository(session))
        routine_repo = RoutineRepository(session)

        _refactored_agent = WellnessAgent(
            llm=llm,
            user_data=user_data,
            routine_repo=routine_repo,
            config=config,
        )
    return _refactored_agent


async def _get_coach_agent():
    """Lazy-init del Wellness Coach Agent 2.0 con memoria conversacional."""
    global _coach_agent
    if _coach_agent is None:
        from src.agents.wellness.coach import WellnessCoachAgent
        from src.agents.wellness.config import WellnessConfig
        from src.services.llm import LLMService
        from src.services.user_data import UserDataService
        from src.database.repositories import UserRepository, ExerciseRepository
        from src.database import Database
        from src.memory.postgres_store import PostgresMemoryStore
        from src.tools.wellness import (
            ExerciseCatalogTool, GenerateRoutineTool, GetHabitsTool,
            LogHabitTool, GetProgressTool, GetRoutineTool,
            RAGSearchTool, SafetyCheckTool,
        )

        db_url = os.getenv("DATABASE_URL")
        db_url_async = db_url.replace("postgresql://", "postgresql+asyncpg://")

        db = Database(db_url_async)
        session = db.session()

        pool = await get_pool()
        memory = PostgresMemoryStore(pool)

        config = WellnessConfig(
            llm_url=OLLAMA_URL,
            llm_model=OLLAMA_MODEL,
            llm_timeout=OLLAMA_TIMEOUT,
        )
        llm = LLMService(base_url=config.llm_url, model=config.llm_model, timeout=config.llm_timeout)
        user_data = UserDataService(UserRepository(session), ExerciseRepository(session))

        tools = [
            ExerciseCatalogTool(session),
            GenerateRoutineTool(llm=llm, user_data=user_data),
            GetHabitsTool(session),
            LogHabitTool(session),
            GetProgressTool(session),
            GetRoutineTool(session),
            RAGSearchTool(),
            SafetyCheckTool(session),
        ]

        _coach_agent = WellnessCoachAgent(
            llm=llm,
            user_data=user_data,
            tools=tools,
            memory_store=memory,
            config=config,
        )
    return _coach_agent


async def _get_orchestrator_agent():
    """Lazy-init del Orchestrator Agent (multi-agente supervisor)."""
    global _orchestrator_agent
    if _orchestrator_agent is None:
        from src.orchestration.router import OrchestratorAgent
        from src.agents.wellness.coach_adapter import WellnessCoachAgentAdapter
        from src.services.llm import LLMService

        config = WellnessConfig(
            llm_url=OLLAMA_URL,
            llm_model=OLLAMA_MODEL,
            llm_timeout=OLLAMA_TIMEOUT,
        )
        llm = LLMService(
            base_url=config.llm_url,
            model=config.llm_model,
            timeout=config.llm_timeout,
        )

        _orchestrator_agent = OrchestratorAgent(llm)

        # Register WellnessCoachAgent as fallback (general domain)
        coach = await _get_coach_agent()
        adapter = WellnessCoachAgentAdapter(coach)
        _orchestrator_agent.register_agent("general", adapter)
        _orchestrator_agent.set_fallback(adapter)

        # Register NutritionAgent (specialized nutrition domain)
        from src.agents.nutrition.agent import NutritionAgent
        from src.agents.nutrition.adapter import NutritionAgentAdapter
        from src.tools.wellness import RAGSearchTool, SafetyCheckTool
        from src.services.user_data import UserDataService
        from src.database.repositories import UserRepository, ExerciseRepository
        from src.database import Database
        from src.memory.postgres_store import PostgresMemoryStore

        db_url = os.getenv("DATABASE_URL")
        db_url_async = db_url.replace("postgresql://", "postgresql+asyncpg://")
        db_nutrition = Database(db_url_async)
        session_nutrition = db_nutrition.session()
        pool_nutrition = await get_pool()
        memory_nutrition = PostgresMemoryStore(pool_nutrition)

        user_data_nutrition = UserDataService(UserRepository(session_nutrition), ExerciseRepository(session_nutrition))
        nutrition_tools = [RAGSearchTool(), SafetyCheckTool(session_nutrition)]

        nutrition_agent = NutritionAgent(
            llm=llm,
            user_data=user_data_nutrition,
            tools=nutrition_tools,
            memory_store=memory_nutrition,
        )
        nutrition_adapter = NutritionAgentAdapter(nutrition_agent)
        _orchestrator_agent.register_agent("nutrition", nutrition_adapter)

        print(f"[Orchestrator] Initialized with fallback: {adapter.name}, nutrition: {nutrition_adapter.name}", flush=True)
    return _orchestrator_agent


# ── Legacy helpers (used by old code path and SSE streaming) ──

def map_exercises(exercises: list) -> list:
    """Convierte ejercicios del formato BD al formato esperado por el frontend."""
    result = []
    for i, ex in enumerate(exercises):
        if isinstance(ex, str):
            try:
                ex = json.loads(ex)
            except json.JSONDecodeError:
                ex = {}
        result.append({
            "exercise_id": ex.get("exercise_id", 0),
            "name": ex.get("name", ""),
            "description": ex.get("description", ""),
            "video_url": ex.get("video_url", ""),
            "sets": ex.get("sets", 1),
            "reps_per_set": ex.get("reps_per_set") or ex.get("reps") or 10,
            "rest_duration_sec": ex.get("rest_duration_sec") or (ex.get("duration_min") or 1) * 60,
            "progression_level_used": ex.get("progression_level_used", 1),
            "order_number": ex.get("order_number", i + 1),
        })
    return result


class GenerateRequest(BaseModel):
    """Solicitud para generar una rutina de ejercicios."""
    user_id: str
    force: bool = False


def build_prompt(profile: dict, health_profile: dict, preferences: dict,
                 safe_exercises: list) -> str:
    """Construye el prompt para Ollama (legacy — delega a RoutinePromptBuilder)."""
    from src.agents.wellness.prompts import RoutinePromptBuilder
    return RoutinePromptBuilder().build(profile, health_profile, preferences, safe_exercises)


def _clean_ollama_response(response_text: str) -> str:
    """Limpia la respuesta de Ollama para extraer JSON válido."""
    match = re.search(r"```(?:json)?\s*(.+?)\s*```", response_text, re.DOTALL)
    if match:
        response_text = match.group(1)
    response_text = response_text.strip()
    response_text = re.sub(r"//.*?$", "", response_text, flags=re.MULTILINE)
    response_text = re.sub(r",\s*([}\]])", r"\1", response_text)
    return response_text


async def _ollama_urls():
    """Genera la lista de URLs a intentar."""
    urls = [OLLAMA_URL]
    if "localhost" in OLLAMA_URL:
        urls.append(OLLAMA_URL.replace("localhost", "127.0.0.1"))
    return urls


async def call_ollama_stream(prompt: str):
    """Envía un prompt a Ollama con streaming (legacy)."""
    urls = await _ollama_urls()
    last_error = None
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
        "format": "json",
        "options": {"num_predict": 600, "temperature": 0.2, "top_p": 0.9, "num_ctx": 4096},
    }
    for ollama_url in urls:
        try:
            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                async with client.stream("POST", f"{ollama_url}/api/generate", json=payload) as resp:
                    resp.raise_status()
                    async for chunk in resp.aiter_lines():
                        if chunk:
                            yield chunk
                    return
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_error = e
            continue
        except Exception:
            raise
    raise last_error


def _accumulate_ollama_stream(chunk: str, accumulated: str) -> str:
    """Acumula chunks SSE de Ollama."""
    try:
        data = json.loads(chunk)
        if data.get("done"):
            return accumulated
        if data.get("response"):
            return accumulated + data["response"]
    except (json.JSONDecodeError, KeyError):
        pass
    return accumulated


async def call_ollama(prompt: str) -> dict:
    """Envía un prompt a Ollama y parsea la respuesta JSON (legacy)."""
    full_response = ""
    async for chunk in call_ollama_stream(prompt):
        full_response = _accumulate_ollama_stream(chunk, full_response)
    response_text = full_response.strip()
    response_text = _clean_ollama_response(response_text)
    return json.loads(response_text)


async def _get_user_data(user_id: int, pool):
    """Obtiene usuario, perfil, y ejercicios seguros (legacy)."""
    today = date.today()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        existing = await conn.fetchrow(
            "SELECT * FROM routines WHERE user_id = $1 AND date = $2 AND active = true",
            user_id, today,
        )
        profile = json.loads(user["profile"]) if isinstance(user["profile"], str) else (user["profile"] or {})
        health_profile = json.loads(user["health_profile"]) if isinstance(user["health_profile"], str) else (user["health_profile"] or {})
        preferences = json.loads(user["preferences"]) if isinstance(user["preferences"], str) else (user["preferences"] or {})
        exercises = await conn.fetch("SELECT * FROM exercises")
        safe_exercises = []
        restrictions = set(health_profile.get("medical_restrictions", profile.get("medical_restrictions", [])))
        for ex in exercises:
            raw = ex.get("contraindications")
            ex_contra = set(x.strip() for x in raw.split(",") if x.strip()) if raw else set()
            if not ex_contra.intersection(restrictions):
                safe_exercises.append(dict(ex))
        return user, profile, health_profile, preferences, safe_exercises, existing


def _send_sse_event(event_type: str, data: dict) -> str:
    """Formatea un evento SSE."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ── FastAPI App ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida del servicio: inicializa y cierra el pool de conexiones."""
    await init_pool(owner="routines")
    await init_db()
    yield
    await close_pool(owner="routines")


app = FastAPI(
    title="Routines AI Service",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


# ── Endpoints ──

@app.post("/routines/generate")
async def generate_routine(req: GenerateRequest):
    """Genera una rutina de ejercicios para el día de hoy."""
    if USE_REFACTORED_AGENT:
        return await _generate_routine_refactored(req)
    return await _generate_routine_legacy(req)


async def _generate_routine_refactored(req: GenerateRequest):
    """NUEVO: delega a WellnessAgent."""
    from src.database.repositories.user_repository import UserNotFoundError

    try:
        agent = await _get_refactored_agent()
        result = await agent.generate_routine(int(req.user_id), req.force)
        return result.to_dict()
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


async def _generate_routine_legacy(req: GenerateRequest):
    """VIEJO: código inline (se mantiene para rollback)."""
    today = date.today()
    pool = await get_pool()
    user_id = int(req.user_id)

    user, profile, health_profile, preferences, safe_exercises, existing = await _get_user_data(user_id, pool)

    if existing and not req.force:
        exercises = json.loads(existing["exercises"]) if isinstance(existing["exercises"], str) else (existing["exercises"] or [])
        return {
            "id": str(existing["id"]),
            "user_id": str(existing["user_id"]),
            "scheduled_date": existing["date"].isoformat(),
            "exercises": map_exercises(exercises),
            "generated_at": existing["created_at"].isoformat() if existing.get("created_at") else existing["date"].isoformat(),
            "generated_by": existing.get("generated_by") or "ollama",
        }

    llm_available = True
    llm_error = None
    routine_data = None

    try:
        prompt = build_prompt(profile, health_profile, preferences, safe_exercises)
        routine_data = await call_ollama(prompt)
    except httpx.TimeoutException:
        print(f"OLLAMA_TIMEOUT after {OLLAMA_TIMEOUT}s with model {OLLAMA_MODEL}", flush=True)
        llm_available = False
        llm_error = f"timeout after {OLLAMA_TIMEOUT}s"
        routine_data = DEFAULT_ROUTINE
    except httpx.ConnectError as e:
        print(f"OLLAMA_CONNECT_ERROR: {e} at {OLLAMA_URL}", flush=True)
        llm_available = False
        llm_error = f"connection error: {str(e)}"
        routine_data = DEFAULT_ROUTINE
    except Exception as e:
        print(f"OLLAMA_ERROR: {type(e).__name__}: {e}", flush=True)
        llm_available = False
        llm_error = f"{type(e).__name__}: {str(e)}"
        routine_data = DEFAULT_ROUTINE

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO routines (user_id, date, exercises, warmup, generated_by) VALUES ($1, $2, $3, $4, $5) RETURNING id, created_at",
            user_id, today,
            json.dumps(routine_data.get("exercises", [])),
            json.dumps(routine_data.get("warmup", [])),
            "ollama" if llm_available else "fallback",
        )
        await publish_event("rutina-generada", {"user_id": req.user_id, "routine_id": str(row["id"])})

    return {
        "id": str(row["id"]),
        "user_id": str(user_id),
        "scheduled_date": today.isoformat(),
        "exercises": map_exercises(routine_data.get("exercises", [])),
        "generated_at": row["created_at"].isoformat() if row.get("created_at") else today.isoformat(),
        "generated_by": "ollama" if llm_available else "fallback",
        "llm_available": llm_available,
        "llm_model": OLLAMA_MODEL if llm_available else None,
        "llm_error": llm_error,
    }


@app.post("/routines/generate-stream")
async def generate_routine_stream(req: GenerateRequest):
    """Genera una rutina con server-sent events (SSE)."""
    if USE_REFACTORED_AGENT:
        return await _generate_stream_refactored(req)
    return await _generate_stream_legacy(req)


async def _generate_stream_refactored(req: GenerateRequest):
    """NUEVO: delega a WellnessAgent con SSE wrapper."""
    from src.database.repositories.user_repository import UserNotFoundError

    async def event_stream():
        try:
            agent = await _get_refactored_agent()
            result = await agent.generate_routine(int(req.user_id), req.force)
            yield _send_sse_event("progress", {"step": 1, "message": "Generando rutina..."})
            yield _send_sse_event("progress", {"step": 5, "message": "Rutina generada"})
            yield _send_sse_event("complete", result.to_dict())
        except UserNotFoundError:
            yield _send_sse_event("error", {"detail": "User not found"})
        except Exception as e:
            yield _send_sse_event("error", {"detail": str(e)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def _generate_stream_legacy(req: GenerateRequest):
    """VIEJO: código SSE inline (se mantiene para rollback)."""
    today = date.today()
    pool = await get_pool()
    user_id = int(req.user_id)

    async def event_stream():
        try:
            user, profile, health_profile, preferences, safe_exercises, existing = await _get_user_data(user_id, pool)
        except HTTPException:
            yield _send_sse_event("error", {"detail": "User not found"})
            return
        except Exception as e:
            print(f"STREAM_GET_USER_ERROR: {type(e).__name__}: {e}", flush=True)
            yield _send_sse_event("error", {"detail": f"Error al obtener datos del usuario: {str(e)}"})
            return

        if existing and not req.force:
            exercises = json.loads(existing["exercises"]) if isinstance(existing["exercises"], str) else (existing["exercises"] or [])
            yield _send_sse_event("complete", {
                "id": str(existing["id"]),
                "user_id": str(existing["user_id"]),
                "scheduled_date": existing["date"].isoformat(),
                "exercises": map_exercises(exercises),
                "generated_at": existing["created_at"].isoformat() if existing.get("created_at") else existing["date"].isoformat(),
                "generated_by": existing.get("generated_by") or "ollama",
                "llm_available": True, "llm_model": "cached",
            })
            return

        yield _send_sse_event("progress", {"step": 1, "message": "Preparando datos del usuario"})
        yield _send_sse_event("progress", {"step": 2, "message": f"Construyendo prompt ({len(safe_exercises)} ejercicios seguros)"})

        prompt = build_prompt(profile, health_profile, preferences, safe_exercises)
        yield _send_sse_event("progress", {"step": 3, "message": "Enviando prompt a Ollama..."})

        llm_available = True
        llm_error = None
        routine_data = None
        accumulated = ""

        try:
            async for chunk in call_ollama_stream(prompt):
                accumulated = _accumulate_ollama_stream(chunk, accumulated)
                if accumulated and len(accumulated) % 50 == 0:
                    yield _send_sse_event("progress", {"step": 4, "message": "Generando rutina...", "preview": accumulated[:100]})
        except httpx.TimeoutException:
            print(f"OLLAMA_TIMEOUT after {OLLAMA_TIMEOUT}s with model {OLLAMA_MODEL}", flush=True)
            llm_available = False
            llm_error = f"timeout after {OLLAMA_TIMEOUT}s"
            routine_data = DEFAULT_ROUTINE
        except httpx.ConnectError as e:
            print(f"OLLAMA_CONNECT_ERROR: {e} at {OLLAMA_URL}", flush=True)
            llm_available = False
            llm_error = f"connection error: {str(e)}"
            routine_data = DEFAULT_ROUTINE
        except Exception as e:
            print(f"OLLAMA_ERROR: {type(e).__name__}: {e}", flush=True)
            llm_available = False
            llm_error = f"{type(e).__name__}: {str(e)}"
            routine_data = DEFAULT_ROUTINE

        if llm_available and accumulated:
            try:
                response_text = _clean_ollama_response(accumulated)
                raw_routine = json.loads(response_text)
                routine_data = {"exercises": raw_routine.get("exercises", []), "warmup": raw_routine.get("warmup", [])}
            except (json.JSONDecodeError, KeyError) as e:
                print(f"STREAM_PARSE_ERROR: {e}", flush=True)
                llm_available = False
                llm_error = f"JSON parse error: {str(e)}"
                routine_data = DEFAULT_ROUTINE

        yield _send_sse_event("progress", {"step": 5, "message": "Guardando rutina en la base de datos"})

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO routines (user_id, date, exercises, warmup, generated_by) VALUES ($1, $2, $3, $4, $5) RETURNING id, created_at",
                user_id, today,
                json.dumps(routine_data.get("exercises", [])),
                json.dumps(routine_data.get("warmup", [])),
                "ollama" if llm_available else "fallback",
            )
            await publish_event("rutina-generada", {"user_id": req.user_id, "routine_id": str(row["id"])})

        yield _send_sse_event("complete", {
            "id": str(row["id"]),
            "user_id": str(user_id),
            "scheduled_date": today.isoformat(),
            "exercises": map_exercises(routine_data.get("exercises", [])),
            "generated_at": row["created_at"].isoformat() if row.get("created_at") else today.isoformat(),
            "generated_by": "ollama" if llm_available else "fallback",
            "llm_available": llm_available,
            "llm_model": OLLAMA_MODEL if llm_available else None,
            "llm_error": llm_error,
        })

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/ollama/status")
async def ollama_status():
    """Health check: verifica si Ollama está disponible y el modelo cargado."""
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_HEALTH_CHECK_TIMEOUT) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            models = [m.get("name") for m in resp.json().get("models", [])]
            loaded = OLLAMA_MODEL in models or any(m.startswith(OLLAMA_MODEL) for m in models)
            return {"available": True, "model": OLLAMA_MODEL, "ollama_url": OLLAMA_URL, "installed": loaded}
    except Exception as e:
        return {"available": False, "model": OLLAMA_MODEL, "ollama_url": OLLAMA_URL,
                "error": f"{type(e).__name__}: {str(e)}"}


@app.get("/routines/today")
async def get_today_routine(user_id: str):
    """Obtiene la rutina activa del día de hoy para un usuario."""
    if USE_REFACTORED_AGENT:
        return await _get_today_refactored(user_id)
    return await _get_today_legacy(user_id)


async def _get_today_refactored(user_id: str):
    """NUEVO: delega a WellnessAgent."""
    from src.database.repositories.user_repository import UserNotFoundError

    try:
        agent = await _get_refactored_agent()
        result = await agent.get_today_routine(int(user_id))
        return result.to_dict()
    except ValueError:
        raise HTTPException(status_code=404, detail="No routine for today")


async def _get_today_legacy(user_id: str):
    """VIEJO: código inline (se mantiene para rollback)."""
    today = date.today()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM routines WHERE user_id = $1 AND date = $2 AND active = true",
            int(user_id), today,
        )
        if not row:
            raise HTTPException(status_code=404, detail="No routine for today")
        exercises = json.loads(row["exercises"]) if isinstance(row["exercises"], str) else (row["exercises"] or [])
        return {
            "id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "scheduled_date": row["date"].isoformat(),
            "exercises": map_exercises(exercises),
            "generated_at": row["created_at"].isoformat() if row.get("created_at") else row["date"].isoformat(),
            "generated_by": row.get("generated_by") or "ollama",
        }


# ── Wellness Coach Agent 2.0 (S2-03) ──

class ChatRequest(BaseModel):
    """Solicitud para el Wellness Coach Agent."""
    user_id: str
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    """Endpoint conversacional — soporta coach directo y orchestrator multi-agente.

    Feature flag USE_ORCHESTRATOR_AGENT=true activa el Orchestrator Agent
    que delega a agentes especializados. false (default) usa WellnessCoachAgent.
    """
    try:
        if USE_ORCHESTRATOR_AGENT:
            from src.orchestration import AgentMessage

            orchestrator = await _get_orchestrator_agent()
            message = AgentMessage(
                from_agent="user",
                to_agent="orchestrator",
                content={
                    "message": req.message,
                    "user_id": int(req.user_id),
                    "user_profile": {},
                    "conversation_history": [],
                },
                message_type="query",
            )
            result = await orchestrator.route(message)
            return {
                "user_id": req.user_id,
                "response": result.content.get("response", ""),
                "agent": result.content.get("agent", "unknown"),
                "safety_level": result.content.get("safety_level", "safe"),
            }
        else:
            agent = await _get_coach_agent()
            response = await agent.chat(int(req.user_id), req.message)
            return {"user_id": req.user_id, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el coach: {str(e)}")
