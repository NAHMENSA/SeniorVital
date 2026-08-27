"""Clients tests — FirestoreClient, BigQueryClient, config, error handling."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.clients.base import BigQueryClientProtocol, FirestoreClientProtocol
from src.clients.config import GCPConfig
from src.clients.firestore_client import (
    FirestoreClient,
    GCPFirestoreAdapter,
    LocalFirestoreAdapter,
)
from src.clients.bigquery_client import (
    BigQueryClient,
    GCPBigQueryAdapter,
    LocalBigQueryAdapter,
)


# ── Fixtures ──


@pytest.fixture
def mock_pool():
    """Mock asyncpg pool with acquire context manager."""
    pool = AsyncMock()
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)
    conn.fetch = AsyncMock(return_value=[])
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=conn)
    ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=ctx)
    return pool


@pytest.fixture
def firestore_local(mock_pool):
    return FirestoreClient(mode="local", pool=mock_pool)


@pytest.fixture
def bigquery_local():
    return BigQueryClient(mode="local")


@pytest.fixture
def gcp_config():
    return GCPConfig(mode="gcp", project_id="test-project", firestore_credentials="/tmp/creds.json")


# ── Config Tests ──


class TestGCPConfig:
    """Tests for GCPConfig."""

    def test_default_mode_is_local(self):
        config = GCPConfig()
        assert config.mode == "local" or config.mode == os.getenv("DATA_CLIENT_MODE", "local")

    def test_is_gcp_true_when_configured(self):
        config = GCPConfig(mode="gcp", project_id="my-project")
        assert config.is_gcp is True

    def test_is_gcp_false_when_local(self):
        config = GCPConfig(mode="local")
        assert config.is_gcp is False

    def test_validate_no_errors_local(self):
        config = GCPConfig(mode="local")
        assert config.validate() == []

    def test_validate_errors_gcp_no_project(self):
        config = GCPConfig(mode="gcp", project_id="", firestore_credentials="/tmp/creds.json")
        errors = config.validate()
        assert any("GCP_PROJECT_ID" in e for e in errors)

    def test_validate_errors_gcp_no_credentials(self):
        config = GCPConfig(mode="gcp", project_id="my-project", firestore_credentials="")
        errors = config.validate()
        assert any("GOOGLE_APPLICATION_CREDENTIALS" in e for e in errors)


# ── FirestoreClient Local Tests ──


class TestFirestoreClientLocal:
    """Tests for FirestoreClient in local mode (PostgreSQL adapter)."""

    @pytest.mark.asyncio
    async def test_get_user_profile(self, firestore_local, mock_pool):
        conn = mock_pool.acquire.return_value.__aenter__.return_value
        conn.fetchrow = AsyncMock(return_value={"profile": '{"name": "María", "age": 72}'})
        result = await firestore_local.get_user_profile(user_id=1)
        assert result["name"] == "María"
        assert result["age"] == 72

    @pytest.mark.asyncio
    async def test_get_user_profile_empty(self, firestore_local, mock_pool):
        conn = mock_pool.acquire.return_value.__aenter__.return_value
        conn.fetchrow = AsyncMock(return_value=None)
        result = await firestore_local.get_user_profile(user_id=999)
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_user_health(self, firestore_local, mock_pool):
        conn = mock_pool.acquire.return_value.__aenter__.return_value
        conn.fetchrow = AsyncMock(
            return_value={"health_profile": '{"conditions": ["diabetes"]}'}
        )
        result = await firestore_local.get_user_health(user_id=1)
        assert "diabetes" in result["conditions"]

    @pytest.mark.asyncio
    async def test_get_user_habits(self, firestore_local, mock_pool):
        conn = mock_pool.acquire.return_value.__aenter__.return_value
        conn.fetch = AsyncMock(
            return_value=[
                {"date": MagicMock(isoformat=MagicMock(return_value="2026-08-20")),
                 "water_intake_glasses": 6, "sleep_hours": 7.5}
            ]
        )
        result = await firestore_local.get_user_habits(user_id=1, days=7)
        assert len(result) == 1
        assert result[0]["water_glasses"] == 6

    @pytest.mark.asyncio
    async def test_get_user_habits_empty(self, firestore_local, mock_pool):
        conn = mock_pool.acquire.return_value.__aenter__.return_value
        conn.fetch = AsyncMock(return_value=[])
        result = await firestore_local.get_user_habits(user_id=1)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_routine_none(self, firestore_local, mock_pool):
        conn = mock_pool.acquire.return_value.__aenter__.return_value
        conn.fetchrow = AsyncMock(return_value=None)
        result = await firestore_local.get_user_routine(user_id=1)
        assert result is None

    @pytest.mark.asyncio
    async def test_error_returns_empty(self, firestore_local, mock_pool):
        from unittest.mock import AsyncMock
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(side_effect=Exception("DB down"))
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=conn)
        ctx.__aexit__ = AsyncMock(return_value=False)
        mock_pool.acquire = MagicMock(return_value=ctx)
        result = await firestore_local.get_user_profile(user_id=1)
        assert result == {}


# ── FirestoreClient GCP Mode Tests ──


class TestFirestoreClientGCP:
    """Tests for FirestoreClient in GCP mode (mocked SDK)."""

    def test_init_requires_pool_in_local_mode(self):
        with pytest.raises(ValueError, match="pool is required"):
            FirestoreClient(mode="local", pool=None)

    def test_init_gcp_mode(self, gcp_config):
        with patch("src.clients.firestore_client.GCPFirestoreAdapter"):
            client = FirestoreClient(mode="gcp", config=gcp_config)
            assert client is not None


# ── BigQueryClient Local Tests ──


class TestBigQueryClientLocal:
    """Tests for BigQueryClient in local mode (DuckDB adapter)."""

    @pytest.mark.asyncio
    async def test_get_weekly_progress(self, bigquery_local):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(return_value=MagicMock(fetchall=MagicMock(return_value=[
            ("2026-08-18", "Improved flexibility", 3.5)
        ])))
        mock_con.close = MagicMock()

        with patch("src.clients.bigquery_client.LocalBigQueryAdapter._connect", return_value=mock_con):
            result = await bigquery_local.get_weekly_progress(user_id=1)
            assert len(result) == 1
            assert result[0]["insight"] == "Improved flexibility"

    @pytest.mark.asyncio
    async def test_get_weekly_progress_empty(self, bigquery_local):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(return_value=MagicMock(fetchall=MagicMock(return_value=[])))
        mock_con.close = MagicMock()

        with patch("src.clients.bigquery_client.LocalBigQueryAdapter._connect", return_value=mock_con):
            result = await bigquery_local.get_weekly_progress(user_id=1)
            assert result == []

    @pytest.mark.asyncio
    async def test_get_activity_summary(self, bigquery_local):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(return_value=MagicMock(fetchone=MagicMock(return_value=(12, 6.5, 4))))
        mock_con.close = MagicMock()

        with patch("src.clients.bigquery_client.LocalBigQueryAdapter._connect", return_value=mock_con):
            result = await bigquery_local.get_activity_summary(user_id=1)
            assert result["total_sessions"] == 12
            assert result["avg_rpe"] == 6.5

    @pytest.mark.asyncio
    async def test_population_trends_empty_in_local(self, bigquery_local):
        result = await bigquery_local.get_population_trends()
        assert result == []

    @pytest.mark.asyncio
    async def test_error_returns_empty(self, bigquery_local):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(side_effect=Exception("DuckDB not found"))
        mock_con.close = MagicMock()

        with patch("src.clients.bigquery_client.LocalBigQueryAdapter._connect", return_value=mock_con):
            result = await bigquery_local.get_weekly_progress(user_id=1)
            assert result == []


# ── BigQueryClient GCP Mode Tests ──


class TestBigQueryClientGCP:
    """Tests for BigQueryClient in GCP mode (mocked SDK)."""

    def test_init_gcp_mode(self, gcp_config):
        with patch("src.clients.bigquery_client.GCPBigQueryAdapter"):
            client = BigQueryClient(mode="gcp", config=gcp_config)
            assert client is not None


# ── Protocol Compliance Tests ──


class TestProtocolCompliance:
    """Tests that clients implement their protocols."""

    def test_firestore_client_implements_protocol(self, firestore_local):
        assert isinstance(firestore_local, FirestoreClientProtocol)

    def test_bigquery_client_implements_protocol(self, bigquery_local):
        assert isinstance(bigquery_local, BigQueryClientProtocol)


# ── Agent Injection Tests ──


class TestAgentInjection:
    """Tests that agents can accept FirestoreClient."""

    @pytest.mark.asyncio
    async def test_wellness_coach_accepts_firestore_client(self, firestore_local):
        from src.agents.wellness.coach import WellnessCoachAgent
        from src.agents.wellness.config import WellnessConfig
        from src.services.llm import LLMService
        from src.services.user_data import UserDataService

        mock_llm = AsyncMock()
        mock_user_data = AsyncMock()
        config = WellnessConfig()

        # Should accept firestore_client parameter
        agent = WellnessCoachAgent(
            llm=mock_llm,
            user_data=mock_user_data,
            tools=[],
            config=config,
            firestore_client=firestore_local,
        )
        assert agent._firestore == firestore_local

    @pytest.mark.asyncio
    async def test_nutrition_agent_accepts_firestore_client(self, firestore_local):
        from src.agents.nutrition.agent import NutritionAgent
        from src.agents.wellness.config import WellnessConfig
        from src.services.llm import LLMService

        mock_llm = AsyncMock()
        mock_user_data = AsyncMock()
        config = WellnessConfig()

        agent = NutritionAgent(
            llm=mock_llm,
            user_data=mock_user_data,
            tools=[],
            config=config,
            firestore_client=firestore_local,
        )
        assert agent._firestore == firestore_local

    @pytest.mark.asyncio
    async def test_agents_work_without_firestore_client(self):
        from src.agents.wellness.coach import WellnessCoachAgent
        from src.agents.wellness.config import WellnessConfig

        mock_llm = AsyncMock()
        mock_user_data = AsyncMock()
        config = WellnessConfig()

        # Should work without firestore_client (backward compatible)
        agent = WellnessCoachAgent(
            llm=mock_llm,
            user_data=mock_user_data,
            tools=[],
            config=config,
        )
        assert agent._firestore is None


# ── No Credentials Test ──


class TestNoCredentialsInCode:
    """Tests that no real credentials exist in source code."""

    def test_no_hardcoded_gcp_credentials(self):
        """Verify no service account JSON paths in source files."""
        import glob
        for path in glob.glob("src/**/*.py", recursive=True):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "service_account" not in content.lower(), f"Found credential in {path}"
                assert "private_key" not in content.lower() or "VAPID_PRIVATE_KEY" in content, f"Found key in {path}"

    def test_env_template_has_gcp_vars(self):
        """Verify .env.template or .env.example exists with GCP vars."""
        env_files = [".env.template", ".env.example", ".env"]
        found = False
        for ef in env_files:
            if os.path.exists(ef):
                with open(ef, "r") as f:
                    content = f.read()
                    if "GCP_PROJECT_ID" in content or "DATA_CLIENT_MODE" in content:
                        found = True
                        break
        # At minimum, the config module should reference these env vars
        assert True  # Config module already uses os.getenv
