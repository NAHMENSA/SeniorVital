"""Microservicio de tracking de ejercicios y hábitos diarios.

Registra sesiones de ejercicio, hábitos diarios (agua/sueño),
publica eventos de completado y detecta fatiga alta.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional, Union
from contextlib import asynccontextmanager

from seniorvital_shared import get_pool, init_pool, close_pool, publish_event, init_db


class TrackEntry(BaseModel):
    """Datos de una entrada individual de tracking de ejercicio."""
    user_id: str
    exercise_id: Optional[Union[str, int]] = None
    sets: int
    reps: int
    rpe: Optional[int] = None
    felt_difficulty: Optional[str] = None
    completed_at: Optional[datetime] = None

    @field_validator("exercise_id", mode="before")
    @staticmethod
    def normalize_exercise_id(v):
        if v is None or v == 0 or v == "0":
            return None
        return str(v)


class BatchTrackRequest(BaseModel):
    """Solicitud para registrar múltiples entradas de tracking."""
    entries: List[TrackEntry]


class HabitsSaveRequest(BaseModel):
    """Datos para guardar hábitos diarios."""
    user_id: str
    date: str
    water_intake_glasses: int = 0
    sleep_hours: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida del servicio: inicializa y cierra el pool de conexiones."""
    await init_pool(owner="tracking")
    await init_db()
    yield
    await close_pool(owner="tracking")


app = FastAPI(
    title="Tracking Service",
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


@app.post("/tracking/record")
async def record_exercise(entry: TrackEntry):
    """Registra un ejercicio completado y publica eventos asociados.

    Si el RPE es >= 8, publica además un evento de fatiga-alta.
    Todo se ejecuta dentro de una misma transacción.

    Si el exercise_id no existe en el catálogo (por ejemplo cuando una
    rutina usa IDs generados por la IA que aún no existen en exercises),
    el registro se guarda igualmente con exercise_id NULL para que el
    progreso del usuario nunca se pierda.

    :param entry: Datos del ejercicio registrado.
    :return: ID del registro y confirmación.
    """
    pool = await get_pool()
    uid = int(entry.user_id)
    eid = int(entry.exercise_id) if entry.exercise_id else None
    completed_at = entry.completed_at or datetime.utcnow()
    async with pool.acquire() as conn:
        async with conn.transaction():
            if eid is not None:
                exists = await conn.fetchval("SELECT 1 FROM exercises WHERE id = $1", eid)
                if not exists:
                    print(f"TRACKING: exercise_id {eid} no existe en exercises; guardando con NULL", flush=True)
                    eid = None
            row = await conn.fetchrow(
                """INSERT INTO tracking (user_id, exercise_id, sets, reps, rpe, felt_difficulty, completed_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id""",
                uid,
                eid,
                entry.sets,
                entry.reps,
                entry.rpe,
                entry.felt_difficulty,
                completed_at,
            )
            event_payload = {
                "user_id": entry.user_id,
                "exercise_id": entry.exercise_id,
                "rpe": entry.rpe,
                "timestamp": completed_at.isoformat(),
                "sets": entry.sets,
                "reps": entry.reps,
            }
            await conn.execute(
                "INSERT INTO event_queue (stream_name, payload) VALUES ($1, $2)",
                "ejercicio-completado",
                json.dumps(event_payload),
            )
            if entry.rpe is not None and entry.rpe >= 8:
                await conn.execute(
                    "INSERT INTO event_queue (stream_name, payload) VALUES ($1, $2)",
                    "fatiga-alta",
                    json.dumps({
                        "user_id": entry.user_id,
                        "rpe_value": entry.rpe,
                        "exercise_id": entry.exercise_id,
                    }),
                )
    return {"id": str(row["id"]), "detail": "Exercise recorded"}


@app.post("/tracking/batch")
async def record_batch(req: BatchTrackRequest):
    """Registra un lote de ejercicios en una sola transacción.

    :param req: Lista de entradas de tracking.
    :return: IDs de los registros creados y conteo total.
    """
    pool = await get_pool()
    ids = []
    async with pool.acquire() as conn:
        async with conn.transaction():
            for entry in req.entries:
                uid = int(entry.user_id)
                eid = int(entry.exercise_id) if entry.exercise_id and entry.exercise_id != "0" else None
                completed_at = entry.completed_at or datetime.utcnow()
                if eid is not None:
                    exists = await conn.fetchval("SELECT 1 FROM exercises WHERE id = $1", eid)
                    if not exists:
                        print(f"TRACKING BATCH: exercise_id {eid} no existe en exercises; guardando con NULL", flush=True)
                        eid = None
                row = await conn.fetchrow(
                    """INSERT INTO tracking (user_id, exercise_id, sets, reps, rpe, felt_difficulty, completed_at)
                       VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id""",
                    uid,
                    eid,
                    entry.sets,
                    entry.reps,
                    entry.rpe,
                    entry.felt_difficulty,
                    completed_at,
                )
                ids.append(str(row["id"]))
                event_payload = {
                    "user_id": entry.user_id,
                    "exercise_id": entry.exercise_id,
                    "rpe": entry.rpe,
                    "timestamp": completed_at.isoformat(),
                    "sets": entry.sets,
                    "reps": entry.reps,
                }
                await conn.execute(
                    "INSERT INTO event_queue (stream_name, payload) VALUES ($1, $2)",
                    "ejercicio-completado",
                    json.dumps(event_payload),
                )
                if entry.rpe is not None and entry.rpe >= 8:
                    await conn.execute(
                        "INSERT INTO event_queue (stream_name, payload) VALUES ($1, $2)",
                        "fatiga-alta",
                        json.dumps({
                            "user_id": entry.user_id,
                            "rpe_value": entry.rpe,
                            "exercise_id": entry.exercise_id,
                        }),
                    )
    return {"ids": ids, "count": len(ids)}


@app.get("/habits/today")
async def get_today_habits(user_id: str = Query(...)):
    """Obtiene los hábitos registrados hoy para un usuario.

    :param user_id: ID del usuario.
    :return: Hábitos del día o valores por defecto.
    """
    today = date.today()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM habits WHERE user_id = $1 AND date = $2",
            int(user_id),
            today,
        )
        if not row:
            return {
                "user_id": user_id,
                "date": today.isoformat(),
                "water_intake_glasses": 0,
                "sleep_hours": 0.0,
            }
        return {
            "id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "date": row["date"].isoformat(),
            "water_intake_glasses": row["water_intake_glasses"] or 0,
            "sleep_hours": float(row["sleep_hours"]) if row["sleep_hours"] is not None else 0.0,
        }


@app.post("/habits")
async def save_habits(req: HabitsSaveRequest):
    """Guarda o actualiza los hábitos diarios de un usuario.

    Usa INSERT ... ON CONFLICT para upsert por (user_id, date).

    :param req: Datos de hábitos.
    :return: Hábitos guardados.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO habits (user_id, date, water_intake_glasses, sleep_hours)
               VALUES ($1, $2, $3, $4)
               ON CONFLICT (user_id, date)
               DO UPDATE SET water_intake_glasses = $3, sleep_hours = $4, updated_at = NOW()
               RETURNING id, user_id, date, water_intake_glasses, sleep_hours""",
            int(req.user_id),
            date.fromisoformat(req.date),
            req.water_intake_glasses,
            req.sleep_hours,
        )
        await publish_event("habits-actualizados", {
            "user_id": req.user_id,
            "water_intake_glasses": req.water_intake_glasses,
            "sleep_hours": req.sleep_hours,
        })
        return {
            "id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "date": row["date"].isoformat(),
            "water_intake_glasses": row["water_intake_glasses"] or 0,
            "sleep_hours": float(row["sleep_hours"]) if row["sleep_hours"] is not None else 0.0,
        }

