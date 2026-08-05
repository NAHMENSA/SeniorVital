"""Tests de aceptación para el servicio de tracking de ejercicios.

Cubre registro individual, detección de fatiga alta y registro por lote.
"""

import pytest
import json
from httpx import AsyncClient, ASGITransport
from .conftest import load_service_app
from seniorvital_shared import get_pool
import datetime

app = load_service_app("tracking-service")


@pytest.fixture
async def client():
    """Fixture que proporciona un cliente HTTP asíncrono contra la app FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def seed_users():
    """Crea 3 usuarios senior y 4 ejercicios en BD para usar en tests de tracking."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        for i in range(1, 5):
            await conn.execute(
                "INSERT INTO exercises (name, level, contraindications, video_url) VALUES ($1, $2, $3, $4)",
                f"Exercise {i}",
                1,
                "",
                "",
            )
        rows = []
        for i in range(1, 4):
            row = await conn.fetchrow(
                "INSERT INTO users (email, role, profile, password, nombre_senior) VALUES ($1, $2, $3, $4, $5) RETURNING id",
                f"tracking_user_{i}@test.com",
                "senior",
                json.dumps({}),
                "pw",
                f"Tracking User {i}",
            )
            rows.append(str(row["id"]))
    return rows


@pytest.mark.asyncio
async def test_record_exercise(client, seed_users):
    user_id = seed_users[0]
    resp = await client.post("/tracking/record", json={
        "user_id": user_id,
        "exercise_id": "1",
        "sets": 3,
        "reps": 10,
        "rpe": 5,
    })
    assert resp.status_code == 200
    assert "id" in resp.json()


@pytest.mark.asyncio
async def test_record_exercise_no_exercise_id(client, seed_users):
    """Tracking should accept exercise_id of 0 or None (routine-generated exercises without DB mapping)."""
    user_id = seed_users[0]
    # Numeric 0 (as sent by frontend)
    resp = await client.post("/tracking/record", json={
        "user_id": user_id,
        "exercise_id": 0,
        "sets": 1,
        "reps": 10,
        "rpe": 5,
    })
    assert resp.status_code == 200
    # String "0"
    resp = await client.post("/tracking/record", json={
        "user_id": user_id,
        "exercise_id": "0",
        "sets": 1,
        "reps": 8,
        "rpe": 4,
    })
    assert resp.status_code == 200
    # None / omitted
    resp = await client.post("/tracking/record", json={
        "user_id": user_id,
        "sets": 2,
        "reps": 6,
        "rpe": 3,
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_record_high_fatigue(client, seed_users):
    user_id = seed_users[1]
    resp = await client.post("/tracking/record", json={
        "user_id": user_id,
        "exercise_id": "2",
        "sets": 3,
        "reps": 10,
        "rpe": 9,
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_batch_record(client, seed_users):
    user_id = seed_users[2]
    resp = await client.post("/tracking/batch", json={
        "entries": [
            {
                "user_id": user_id,
                "exercise_id": "3",
                "sets": 2,
                "reps": 8,
                "rpe": 4,
            },
            {
                "user_id": user_id,
                "exercise_id": "4",
                "sets": 3,
                "reps": 12,
                "rpe": 6,
            },
        ]
    })
    assert resp.status_code == 200
    assert resp.json()["count"] == 2


@pytest.mark.asyncio
async def test_track_01_get_today_habits_defaults(client, seed_users):
    """AC-TRACK-01: Habits for new user returns defaults 0, not NaN/undefined"""
    user_id = seed_users[0]
    resp = await client.get(f"/habits/today?user_id={user_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["water_intake_glasses"] == 0
    assert data["sleep_hours"] == 0.0


@pytest.mark.asyncio
async def test_track_02_save_and_retrieve_habits(client, seed_users):
    """AC-TRACK-02: Save habits then retrieve returns saved values"""
    user_id = seed_users[1]
    today = datetime.date.today().isoformat()
    resp = await client.post("/habits", json={
        "user_id": user_id,
        "date": today,
        "water_intake_glasses": 5,
        "sleep_hours": 7.5,
    })
    assert resp.status_code == 200
    assert resp.json()["water_intake_glasses"] == 5
    assert resp.json()["sleep_hours"] == 7.5

    resp = await client.get(f"/habits/today?user_id={user_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["water_intake_glasses"] == 5
    assert data["sleep_hours"] == 7.5


@pytest.mark.asyncio
async def test_track_03_get_habits_with_null_db_values(client, seed_users):
    """AC-TRACK-03: Habits with NULL sleep_hours in DB returns 0.0, not 500"""
    user_id = seed_users[2]
    today = datetime.date.today()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO habits (user_id, date, water_intake_glasses, sleep_hours) VALUES ($1, $2, NULL, NULL)",
            int(user_id), today,
        )
    resp = await client.get(f"/habits/today?user_id={user_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["water_intake_glasses"] == 0
    assert data["sleep_hours"] == 0.0

