"""Microservicio de dashboard y analítica.

Proporciona consultas agregadas de progreso semanal,
proyecciones generadas por IA e insights históricos
para seniors y cuidadores.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from seniorvital_shared import get_pool, init_pool, close_pool, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida del servicio: inicializa y cierra el pool de conexiones."""
    await init_pool(owner="dashboard")
    await init_db()
    yield
    await close_pool(owner="dashboard")


app = FastAPI(
    title="Dashboard Service",
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


@app.get("/dashboard/progress/{user_id}")
async def get_progress(user_id: str):
    """Obtiene el resumen de progreso semanal de un usuario.

    Incluye calendario de actividad, tendencia de RPE,
    racha de días consecutivos y total de sesiones en la semana.

    :param user_id: ID del usuario.
    :raises HTTPException 404: Si el usuario no existe.
    :return: Progreso semanal del usuario.
    """
    uid = int(user_id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM users WHERE id = $1", uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        week_ago = date.today() - timedelta(days=7)
        rows = await conn.fetch(
            """SELECT completed_at::date as day, SUM(reps) as total_reps,
                AVG(rpe) as avg_rpe
                FROM tracking
                WHERE user_id = $1 AND completed_at >= $2
                GROUP BY completed_at::date
                ORDER BY day""",
            uid,
            week_ago,
        )

        calendar = {}
        rpe_trend = []
        for r in rows:
            day_str = r["day"].isoformat()
            avg_rpe = round(float(r["avg_rpe"]), 1) if r["avg_rpe"] else 0
            calendar[day_str] = {"completed": True, "rpe_avg": avg_rpe}
            rpe_trend.append({"date": day_str, "avg_rpe": avg_rpe})

        today = date.today()
        streak_days = 0
        check = today
        while True:
            day_rows = await conn.fetchval(
                "SELECT COUNT(*) FROM tracking WHERE user_id = $1 AND completed_at::date = $2",
                uid,
                check,
            )
            if day_rows and day_rows > 0:
                streak_days += 1
                check -= timedelta(days=1)
            else:
                break

        total_sessions = await conn.fetchval(
            "SELECT COUNT(DISTINCT completed_at::date) FROM tracking WHERE user_id = $1",
            uid,
        )

        sessions_this_week = await conn.fetchval(
            "SELECT COUNT(DISTINCT completed_at::date) FROM tracking WHERE user_id = $1 AND completed_at >= $2",
            uid,
            week_ago,
        )

        return {
            "sessions_this_week": sessions_this_week or 0,
            "current_streak": streak_days,
            "total_sessions": total_sessions or 0,
            "rpe_trend": rpe_trend,
            "calendar": calendar,
        }


@app.get("/dashboard/projection/{user_id}")
async def get_projection(user_id: str):
    """Obtiene la última proyección generada por el agente semanal.

    :param user_id: ID del usuario.
    :return: Proyección más reciente o null si no existe.
    """
    uid = int(user_id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM projections WHERE user_id = $1 ORDER BY week_start DESC LIMIT 1",
            uid,
        )
        if not row:
            return {"projection": None}
        return {
            "projection": {
                "id": str(row["id"]),
                "week_start": row["week_start"].isoformat(),
                "insight_text": row["insight_text"],
                "estimated_level": row["estimated_level"],
            }
        }


@app.get("/dashboard/insights/{user_id}")
async def get_insights(user_id: str):
    """Obtiene el historial de insights generados para un usuario.

    :param user_id: ID del usuario.
    :return: Lista de hasta 10 insights ordenados por semana descendente.
    """
    uid = int(user_id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM projections WHERE user_id = $1 ORDER BY week_start DESC LIMIT 10",
            uid,
        )
        return [
            {
                "id": str(r["id"]),
                "week_start": r["week_start"].isoformat(),
                "insight_text": r["insight_text"],
                "estimated_level": r["estimated_level"],
            }
            for r in rows
        ]
