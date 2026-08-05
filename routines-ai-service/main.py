"""Microservicio de generación de rutinas de ejercicio con IA.

Utiliza Ollama (phi3:mini) para generar rutinas personalizadas
basadas en el perfil de salud del usuario y los ejercicios
disponibles en el catálogo, respetando restricciones médicas.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import re
import asyncio
from datetime import date
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import httpx

from seniorvital_shared import get_pool, init_pool, close_pool, publish_event, init_db

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
    """Construye el prompt para Ollama con el perfil completo del usuario.

    :param profile: Perfil adicional del usuario (jsonb).
    :param health_profile: Perfil de salud (edad, peso, restricciones, etc.).
    :param preferences: Preferencias del usuario (ejercicios favoritos, etc.).
    :param safe_exercises: Lista de ejercicios sin contraindicaciones.
    :return: Prompt formateado para el modelo.
    """
    age = health_profile.get('age', profile.get('age', 'desconocida'))
    fitness_level = health_profile.get('fitness_level', profile.get('fitness_level', 'bajo'))
    goals = health_profile.get('goals', profile.get('goals', []))
    medical_restrictions = health_profile.get('medical_restrictions', profile.get('medical_restrictions', []))
    equipment = health_profile.get('equipment', profile.get('equipment', []))
    conditions = health_profile.get('conditions', [])
    medications = health_profile.get('medications', [])
    wake_time = health_profile.get('wake_time', '08:00')
    sleep_time = health_profile.get('sleep_time', '22:00')
    duration_pref = health_profile.get('duration_pref', 30)

    favorite_exercises = preferences.get('favorite_exercises', [])
    avoid_exercises = preferences.get('avoid_exercises', [])

    exercise_list = []
    for ex in safe_exercises:
        exercise_list.append({
            "id": ex.get("id", 0),
            "name": ex.get("name", ""),
            "description": ex.get("description", ""),
            "level": ex.get("level", 1),
            "duration_min": ex.get("duration_min", 5),
            "contraindications": (ex.get("contraindications") or "").split(",") if ex.get("contraindications") else [],
        })

    return f"""
Genera una rutina de ejercicios para un adulto mayor con el siguiente perfil DETALLADO:

PERFIL DEL USUARIO:
- Edad: {age}
- Nivel de condición física: {fitness_level}
- Objetivos: {', '.join(goals) if goals else 'mantener actividad'}
- Equipo disponible: {', '.join(equipment) if equipment else 'ninguno'}
- Condiciones médicas: {', '.join(conditions) if conditions else 'ninguna'}
- Medicamentos: {', '.join(medications) if medications else 'ninguno'}
- Restricciones médicas/contraindicaciones: {', '.join(medical_restrictions) if medical_restrictions else 'ninguna'}
- Horario: se levanta a las {wake_time}, duerme a las {sleep_time}
- Duración preferida: {duration_pref} minutos

PREFERENCIAS:
- Ejercicios favoritos: {', '.join(favorite_exercises) if favorite_exercises else 'ninguno'}
- Ejercicios a evitar: {', '.join(avoid_exercises) if avoid_exercises else 'ninguno'}

EJERCICIOS DISPONIBLES SEGUROS (usa los IDs para referenciar):
{json.dumps(exercise_list, ensure_ascii=False)}

INSTRUCCIONES:
1. Prioriza ejercicios favoritos si son seguros.
2. Evita ejercicios en "evitar" y cualquier ejercicio con contraindicaciones que coincidan con restricciones.
3. Incluye un ejercicio de calentamiento suave (2-3 min).
4. Cada ejercicio debe tener: exercise_id (número del catálogo), name, sets, reps, duration_min, rest_duration_sec.
5. Total de ejercicios: 3-4. Duración total: ~{duration_pref} minutos.

Responde SOLO con JSON válido:
{{
  "exercises": [
    {{"exercise_id": 1, "name": "string", "sets": 2, "reps": 8, "duration_min": 5, "rest_duration_sec": 30, "description": "string"}}
  ],
  "warmup": [
    {{"name": "string", "sets": 1, "reps": 5, "duration_min": 2, "description": "string"}}
  ]
}}
"""


async def _ollama_urls():
    """Genera la lista de URLs a intentar (localhost primero, luego 127.0.0.1)."""
    urls = [OLLAMA_URL]
    if "localhost" in OLLAMA_URL:
        urls.append(OLLAMA_URL.replace("localhost", "127.0.0.1"))
    return urls


def _clean_ollama_response(response_text: str) -> str:
    """Limpia la respuesta de Ollama para extraer JSON válido."""
    match = re.search(r"```(?:json)?\s*(.+?)\s*```", response_text, re.DOTALL)
    if match:
        response_text = match.group(1)
    response_text = response_text.strip()
    response_text = re.sub(r"//.*?$", "", response_text, flags=re.MULTILINE)
    response_text = re.sub(r",\s*([}\]])", r"\1", response_text)
    return response_text


async def call_ollama_stream(prompt: str):
    """Envía un prompt a Ollama con streaming y yieldea chunks de respuesta.

    :param prompt: Texto del prompt para el modelo.
    :yield: Chunks de texto generados por el modelo.
    """
    urls = await _ollama_urls()
    last_error = None

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
        "format": "json",
        "options": {
            "num_predict": 600,
            "temperature": 0.2,
            "top_p": 0.9,
            "num_ctx": 4096,
        },
    }

    for ollama_url in urls:
        try:
            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    f"{ollama_url}/api/generate",
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
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


async def call_ollama(prompt: str) -> dict:
    """Envía un prompt a Ollama de forma no bloqueante y parsea la respuesta JSON.

    :param prompt: Texto del prompt para el modelo.
    :raises httpx.HTTPError: Si la llamada a Ollama falla.
    :raises json.JSONDecodeError: Si la respuesta no es JSON válido.
    :return: Diccionario con la respuesta parseada.
    """
    full_response = ""
    async for chunk in call_ollama_stream(prompt):
        full_response = _accumulate_ollama_stream(chunk, full_response)

    response_text = full_response.strip()
    response_text = _clean_ollama_response(response_text)
    return json.loads(response_text)


def _accumulate_ollama_stream(chunk: str, accumulated: str) -> str:
    """Acumula chunks SSE de Ollama en una sola cadena de respuesta."""
    try:
        data = json.loads(chunk)
        if data.get("done"):
            return accumulated
        if data.get("response"):
            return accumulated + data["response"]
    except (json.JSONDecodeError, KeyError):
        pass
    return accumulated


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida del servicio: inicializa y cierra el pool de conexiones."""
    await init_pool(owner="routines")
    await init_db()
    yield
    await close_pool(owner="routines")


app = FastAPI(
    title="Routines AI Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


async def _get_user_data(user_id: int, pool):
    """Obtiene usuario, perfil, y ejercicios seguros de la base de datos.

    :param user_id: ID del usuario.
    :param pool: Pool de conexiones asyncpg.
    :return: Tuple de (user_row, profile_dict, health_profile_dict, preferences_dict, safe_exercises_list).
    :raises HTTPException 404: Si el usuario no existe.
    """
    today = date.today()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing = await conn.fetchrow(
            "SELECT * FROM routines WHERE user_id = $1 AND date = $2 AND active = true",
            user_id,
            today,
        )

        profile = json.loads(user["profile"]) if isinstance(user["profile"], str) else (user["profile"] or {})
        health_profile = json.loads(user["health_profile"]) if isinstance(user["health_profile"], str) else (user["health_profile"] or {})
        preferences = json.loads(user["preferences"]) if isinstance(user["preferences"], str) else (user["preferences"] or {})

        exercises = await conn.fetch("SELECT * FROM exercises")
        safe_exercises = []
        restrictions = set(health_profile.get("medical_restrictions", profile.get("medical_restrictions", [])))
        for ex in exercises:
            raw = ex.get("contraindications")
            if raw:
                ex_contra = set(x.strip() for x in raw.split(",") if x.strip())
            else:
                ex_contra = set()
            if not ex_contra.intersection(restrictions):
                safe_exercises.append(dict(ex))

        return user, profile, health_profile, preferences, safe_exercises, existing


def _send_sse_event(event_type: str, data: dict) -> str:
    """Formatea un evento SSE."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/routines/generate")
async def generate_routine(req: GenerateRequest):
    """Genera una rutina de ejercicios para el día de hoy.

    Si ya existe una rutina activa para hoy y force=false, la retorna.
    Si Ollama falla, usa una rutina por defecto como fallback.

    :param req: Solicitud con user_id y flag force.
    :raises HTTPException 404: Si el usuario no existe.
    :return: Rutina generada con ID, ejercicios y warmup.
    """
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
            user_id,
            today,
            json.dumps(routine_data.get("exercises", [])),
            json.dumps(routine_data.get("warmup", [])),
            "ollama" if llm_available else "fallback",
        )
        await publish_event("rutina-generada", {
            "user_id": req.user_id,
            "routine_id": str(row["id"]),
        })

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
    """Genera una rutina con server-sent events (SSE) para mostrar progreso en tiempo real.

    :param req: Solicitud con user_id y flag force.
    :raises HTTPException 404: Si el usuario no existe.
    :return: Stream SSE con eventos de progreso y resultado final.
    """
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
                "llm_available": True,
                "llm_model": "cached",
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
                routine_data = {
                    "exercises": raw_routine.get("exercises", []),
                    "warmup": raw_routine.get("warmup", []),
                }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"STREAM_PARSE_ERROR: {e}", flush=True)
                llm_available = False
                llm_error = f"JSON parse error: {str(e)}"
                routine_data = DEFAULT_ROUTINE

        yield _send_sse_event("progress", {"step": 5, "message": "Guardando rutina en la base de datos"})

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO routines (user_id, date, exercises, warmup, generated_by) VALUES ($1, $2, $3, $4, $5) RETURNING id, created_at",
                user_id,
                today,
                json.dumps(routine_data.get("exercises", [])),
                json.dumps(routine_data.get("warmup", [])),
                "ollama" if llm_available else "fallback",
            )
            await publish_event("rutina-generada", {
                "user_id": req.user_id,
                "routine_id": str(row["id"]),
            })

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
    """Health check: verifica si Ollama está disponible y el modelo cargado.

    Usa /api/tags (ligero) en lugar de generar texto, que tardaría
    más de 100 segundos en CPU.

    :return: Estado de conectividad con Ollama y nombre del modelo.
    """
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_HEALTH_CHECK_TIMEOUT) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
            models = [m.get("name") for m in resp.json().get("models", [])]
            loaded = OLLAMA_MODEL in models or any(
                m.startswith(OLLAMA_MODEL) for m in models
            )
            return {
                "available": True,
                "model": OLLAMA_MODEL,
                "ollama_url": OLLAMA_URL,
                "installed": loaded,
            }
    except Exception as e:
        return {"available": False, "model": OLLAMA_MODEL, "ollama_url": OLLAMA_URL,
                "error": f"{type(e).__name__}: {str(e)}"}


@app.get("/routines/today")
async def get_today_routine(user_id: str):
    """Obtiene la rutina activa del día de hoy para un usuario.

    :param user_id: ID del usuario.
    :raises HTTPException 404: Si no hay rutina para hoy.
    :return: Rutina del día con ejercicios y warmup.
    """
    today = date.today()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM routines WHERE user_id = $1 AND date = $2 AND active = true",
            int(user_id),
            today,
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
