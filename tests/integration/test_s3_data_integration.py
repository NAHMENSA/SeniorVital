"""S3-05 Data Integration tests — agents enriched by Firestore/BigQuery clients.

Evidencia mockeada (sin BD real): los agentes se enriquecen con hábitos,
tracking (Firestore adapter local -> pool mock) y métricas analíticas
(BigQuery adapter local -> DuckDB mock).

No requiere PostgreSQL ni DuckDB reales.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.nutrition.agent import NutritionAgent
from src.agents.wellness.coach import WellnessCoachAgent
from src.clients.bigquery_client import BigQueryClient
from src.clients.firestore_client import FirestoreClient


# ── Fixtures mokeadas ──


@pytest.fixture
def firestore_local():
    """FirestoreClient local mode con pool mock de PostgreSQL."""
    pool = AsyncMock()
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)
    conn.fetch = AsyncMock(
        return_value=[
            {"date": MagicMock(isoformat=MagicMock(return_value="2026-08-20")),
             "water_intake_glasses": 6, "sleep_hours": 7.5},
        ]
    )
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=conn)
    ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=ctx)
    return FirestoreClient(mode="local", pool=pool)


@pytest.fixture
def bigquery_local():
    """BigQueryClient local mode con DuckDB mocked via _connect patch."""
    mock_con = MagicMock()
    mock_con.execute = MagicMock(
        return_value=MagicMock(
            fetchone=MagicMock(return_value=(12, 6.5, 4)),
            fetchall=MagicMock(
                return_value=[("2026-08-25", "Buen progreso esta semana.", 2)],
            ),
        )
    )
    mock_con.close = MagicMock()

    with patch(
        "src.clients.bigquery_client.LocalBigQueryAdapter._connect",
        return_value=mock_con,
    ):
        client = BigQueryClient(mode="local")
        client._adapter._connect = MagicMock(return_value=mock_con)
        return client


@pytest.fixture
def coach_agent_with_clients(firestore_local, bigquery_local):
    """WellnessCoachAgent con clientes de datos + LLM mock."""
    llm = AsyncMock()
    llm.generate = AsyncMock(
        return_value=json.dumps({"thought": "Respuesta de prueba",
                                 "final_answer": "Todo en orden."})
    )
    user_data = AsyncMock()
    data = MagicMock()
    data.profile = {"name": "María", "age": 72}
    data.health_profile = {"age": 72}
    data.preferences = {}
    user_data.get_user_data = AsyncMock(return_value=data)

    agent = WellnessCoachAgent(
        llm=llm,
        user_data=user_data,
        tools=[],
        firestore_client=firestore_local,
        bigquery_client=bigquery_local,
    )
    return agent


@pytest.fixture
def nutrition_agent_with_clients(firestore_local, bigquery_local):
    """NutritionAgent con clientes de datos + LLM mock."""
    llm = AsyncMock()
    llm.generate = AsyncMock(
        return_value=json.dumps({"thought": "Respuesta de prueba",
                                 "final_answer": "Recomendación nutricional."})
    )
    user_data = AsyncMock()
    data = MagicMock()
    data.profile = {"name": "María", "age": 72}
    data.health_profile = {"age": 72}
    data.preferences = {"dietary_restrictions": ["sin sal"]}
    user_data.get_user_data = AsyncMock(return_value=data)

    agent = NutritionAgent(
        llm=llm,
        user_data=user_data,
        tools=[],
        firestore_client=firestore_local,
        bigquery_client=bigquery_local,
    )
    return agent


# ── Tests ──


@pytest.mark.asyncio
async def test_coach_profile_enriched_with_firestore_and_bigquery(coach_agent_with_clients):
    """S3-05: el perfil del coach incluye hábitos (Firestore) y métricas (BigQuery)."""
    profile = await coach_agent_with_clients._get_user_profile(user_id=1)

    assert profile["name"] == "María"
    # Firestore adapter local
    assert "recent_habits" in profile
    assert profile["recent_habits"][0]["water_glasses"] == 6
    # BigQuery adapter local (duckdb mock)
    assert profile["activity_summary"] == {"total_sessions": 12, "avg_rpe": 6.5, "weeks_active": 4}
    assert "weekly_insights" in profile
    assert profile["weekly_insights"][0]["insight"] == "Buen progreso esta semana."


@pytest.mark.asyncio
async def test_nutrition_profile_enriched(coach_agent_with_clients, nutrition_agent_with_clients):
    """S3-05: el perfil de nutrición incluye insights semanales analíticos."""
    profile = await nutrition_agent_with_clients._get_user_profile(user_id=1)

    assert "weekly_insights" in profile
    assert profile["weekly_insights"][0]["level"] == 2


@pytest.mark.asyncio
async def test_chat_works_with_clients_injected(coach_agent_with_clients):
    """S3-05: chat() no falla con los clientes inyectados (smoke E2E)."""
    response = await coach_agent_with_clients.chat(user_id=1, message="¿Cómo sigo?")
    assert response == "Todo en orden."


@pytest.mark.asyncio
async def test_nutrition_chat_works_with_clients_injected(nutrition_agent_with_clients):
    """S3-05: chat() de nutrición no falla con clientes inyectados."""
    response = await nutrition_agent_with_clients.chat(user_id=1, message="¿Qué como?")
    assert response == "Recomendación nutricional."


@pytest.mark.asyncio
async def test_agents_work_without_clients():
    """Regresión: agentes sin clientes siguen funcionando."""
    llm = AsyncMock()
    llm.generate = AsyncMock(
        return_value=json.dumps({"thought": "test", "final_answer": "ok"})
    )
    user_data = AsyncMock()
    data = MagicMock()
    data.profile = {"name": "X"}
    data.health_profile = {}
    data.preferences = {}
    user_data.get_user_data = AsyncMock(return_value=data)

    coach = WellnessCoachAgent(llm=llm, user_data=user_data, tools=[])
    profile = await coach._get_user_profile(user_id=1)
    assert "activity_summary" not in profile
    assert "recent_habits" not in profile


@pytest.mark.asyncio
async def test_error_in_client_does_not_break_agent():
    """S3-05: los fallos de clientes se degradan sin romper el agente."""
    broken_firestore = MagicMock()
    broken_firestore.get_user_habits = AsyncMock(side_effect=Exception("timeout"))
    broken_firestore.get_user_tracking = AsyncMock(side_effect=Exception("timeout"))

    llm = AsyncMock()
    llm.generate = AsyncMock(
        return_value=json.dumps({"thought": "test", "final_answer": "ok"})
    )
    user_data = AsyncMock()
    data = MagicMock()
    data.profile = {"name": "X"}
    data.health_profile = {}
    data.preferences = {}
    user_data.get_user_data = AsyncMock(return_value=data)

    agent = WellnessCoachAgent(
        llm=llm, user_data=user_data, tools=[],
        firestore_client=broken_firestore,
    )
    profile = await agent._get_user_profile(user_id=1)
    assert profile["name"] == "X"  # degradación segura
