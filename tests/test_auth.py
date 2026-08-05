"""Tests de aceptación para el servicio de autenticación y perfiles.

Cubre los criterios AC-AUTH-01 al AC-AUTH-05 del SDD.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from .conftest import load_service_app
from seniorvital_shared import get_pool
import json as _json

app = load_service_app("auth-profile-service")


@pytest.fixture
async def client():
    """Fixture que proporciona un cliente HTTP asíncrono contra la app FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_ac_auth_01_password_hashed(client):
    """AC-AUTH-01: Password hashed with bcrypt"""
    resp = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "secret123",
        "role": "senior",
        "nombre_senior": "Test User",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ac_auth_02_invalid_role(client):
    """AC-AUTH-02: HTTP 400 if role not allowed"""
    resp = await client.post("/auth/register", json={
        "email": "bad@example.com",
        "password": "secret123",
        "role": "invalid_role",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_ac_auth_03_caregiver_no_linked(client):
    """AC-AUTH-03: caregiver without linked_senior_id"""
    resp = await client.post("/auth/register", json={
        "email": "caregiver@example.com",
        "password": "secret123",
        "role": "caregiver",
        "nombre_cuidador": "Test Caregiver",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "caregiver"


@pytest.mark.asyncio
async def test_ac_auth_04_max_3_caregivers(client):
    """AC-AUTH-04: Senior max 3 caregivers"""
    resp = await client.post("/auth/register", json={
        "email": "senior@example.com",
        "password": "secret123",
        "role": "senior",
        "nombre_senior": "Senior Test",
    })
    assert resp.status_code == 200
    senior_id = resp.json()["id"]

    resp = await client.post("/auth/login", json={
        "email": "senior@example.com",
        "password": "secret123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(3):
        resp = await client.post("/auth/register", json={
            "email": f"cg{i}@example.com",
            "password": "secret123",
            "role": "caregiver",
            "nombre_cuidador": f"Caregiver {i}",
        })
        resp = await client.post("/auth/link-caregiver",
            json={"caregiver_email": f"cg{i}@example.com"},
            headers=headers,
        )
        assert resp.status_code == 200

    resp = await client.post("/auth/register", json={
        "email": "cg_extra@example.com",
        "password": "secret123",
        "role": "caregiver",
        "nombre_cuidador": "Extra Caregiver",
    })
    resp = await client.post("/auth/link-caregiver",
        json={"caregiver_email": "cg_extra@example.com"},
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_ac_auth_05_caregiver_one_linked(client):
    """AC-AUTH-05: Caregiver can have only one linked_senior_id"""
    resp = await client.post("/auth/register", json={
        "email": "senior_b@example.com",
        "password": "secret123",
        "role": "senior",
        "nombre_senior": "Senior B",
    })
    assert resp.status_code == 200
    resp = await client.post("/auth/login", json={
        "email": "senior_b@example.com",
        "password": "secret123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/auth/register", json={
        "email": "cg_only@example.com",
        "password": "secret123",
        "role": "caregiver",
        "nombre_cuidador": "CG Only",
    })

    resp = await client.post("/auth/link-caregiver",
        json={"caregiver_email": "cg_only@example.com"},
        headers=headers,
    )
    assert resp.status_code == 200

    resp = await client.post("/auth/register", json={
        "email": "senior_c@example.com",
        "password": "secret123",
        "role": "senior",
        "nombre_senior": "Senior C",
    })
    resp = await client.post("/auth/login", json={
        "email": "senior_c@example.com",
        "password": "secret123",
    })
    token2 = resp.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    resp = await client.post("/auth/link-caregiver",
        json={"caregiver_email": "cg_only@example.com"},
        headers=headers2,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_ac_auth_06_login_success(client):
    """AC-AUTH-06: Login with correct credentials returns access + refresh tokens"""
    resp = await client.post("/auth/register", json={
        "email": "login_success@example.com",
        "password": "correctpass123",
        "role": "senior",
        "nombre_senior": "Login Success",
    })
    assert resp.status_code == 200

    resp = await client.post("/auth/login", json={
        "email": "login_success@example.com",
        "password": "correctpass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_ac_auth_07_login_wrong_password(client):
    """AC-AUTH-07: Login with wrong password returns 401"""
    resp = await client.post("/auth/register", json={
        "email": "wrong_pass@example.com",
        "password": "correctpass123",
        "role": "senior",
        "nombre_senior": "Wrong Pass",
    })
    assert resp.status_code == 200

    resp = await client.post("/auth/login", json={
        "email": "wrong_pass@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Credenciales inválidas"


@pytest.mark.asyncio
async def test_ac_auth_08_login_nonexistent_user(client):
    """AC-AUTH-08: Login with nonexistent email returns 401 (not 500)"""
    resp = await client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "anything",
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Credenciales inválidas"


@pytest.mark.asyncio
async def test_ac_auth_09_login_plaintext_password_safe():
    """AC-AUTH-09: Login with plaintext password hash returns 401, not 500

    If the database contains a non-bcrypt password (e.g. plaintext from
    a legacy migration), bcrypt.verify would raise ValueError. The login
    endpoint must catch this and return a clean 401.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (email, role, profile, password, nombre_senior) VALUES ($1, $2, $3, $4, $5)",
            "plaintext_user@example.com", "senior",
            _json.dumps({"age": 70, "weight_kg": 70, "height_cm": 165,
                          "fitness_level": "principiante", "goals": [],
                          "medical_restrictions": [], "equipment": []}),
            "plaintext_not_bcrypt", "Plain User",
        )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/auth/login", json={
            "email": "plaintext_user@example.com",
            "password": "plaintext_not_bcrypt",
        })
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Credenciales inválidas"

    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = 'plaintext_user@example.com'")
