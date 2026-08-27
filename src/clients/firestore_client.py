"""Firestore Client — dual-mode client for user data access.

Local mode: queries PostgreSQL via asyncpg pool.
GCP mode: queries Firestore via google-cloud-firestore SDK.

Agents depend on FirestoreClientProtocol, not on this concrete class.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from src.clients.config import GCPConfig

logger = logging.getLogger(__name__)


class LocalFirestoreAdapter:
    """Local adapter: queries PostgreSQL as Firestore replacement.

    Uses the same asyncpg pool as the rest of the application.
    Maps Firestore-style document queries to SQL.
    """

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def get_user_profile(self, user_id: int) -> dict:
        """Get user profile from PostgreSQL users table."""
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT profile FROM users WHERE id = $1", user_id
                )
                if row and row["profile"]:
                    import json
                    profile = row["profile"]
                    if isinstance(profile, str):
                        profile = json.loads(profile)
                    return profile
                return {}
        except Exception as e:
            logger.warning(f"LocalFirestore: get_user_profile failed for {user_id}: {e}")
            return {}

    async def get_user_health(self, user_id: int) -> dict:
        """Get user health profile from PostgreSQL users table."""
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT health_profile FROM users WHERE id = $1", user_id
                )
                if row and row["health_profile"]:
                    import json
                    health = row["health_profile"]
                    if isinstance(health, str):
                        health = json.loads(health)
                    return health
                return {}
        except Exception as e:
            logger.warning(f"LocalFirestore: get_user_health failed for {user_id}: {e}")
            return {}

    async def get_user_habits(self, user_id: int, days: int = 7) -> list[dict]:
        """Get recent habits from PostgreSQL habits table."""
        try:
            since = date.today() - timedelta(days=days)
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT date, water_intake_glasses, sleep_hours
                       FROM habits
                       WHERE user_id = $1 AND date >= $2
                       ORDER BY date DESC""",
                    user_id, since,
                )
                return [
                    {
                        "date": r["date"].isoformat() if r["date"] else None,
                        "water_glasses": r["water_intake_glasses"] or 0,
                        "sleep_hours": float(r["sleep_hours"]) if r["sleep_hours"] else None,
                    }
                    for r in rows
                ]
        except Exception as e:
            logger.warning(f"LocalFirestore: get_user_habits failed for {user_id}: {e}")
            return []

    async def get_user_tracking(self, user_id: int, weeks: int = 4) -> list[dict]:
        """Get recent tracking records from PostgreSQL tracking table."""
        try:
            since = date.today() - timedelta(weeks=weeks)
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT completed_at, exercise_id, sets, reps, rpe, felt_difficulty
                       FROM tracking
                       WHERE user_id = $1 AND completed_at >= $2
                       ORDER BY completed_at DESC""",
                    user_id, since,
                )
                return [
                    {
                        "date": r["completed_at"].isoformat() if r["completed_at"] else None,
                        "exercise_id": r["exercise_id"],
                        "sets": r["sets"],
                        "reps": r["reps"],
                        "rpe": r["rpe"],
                        "felt_difficulty": r["felt_difficulty"],
                    }
                    for r in rows
                ]
        except Exception as e:
            logger.warning(f"LocalFirestore: get_user_tracking failed for {user_id}: {e}")
            return []

    async def get_user_routine(self, user_id: int) -> dict | None:
        """Get current active routine from PostgreSQL routines table."""
        try:
            import json
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """SELECT id, date, exercises, warmup, generated_by
                       FROM routines
                       WHERE user_id = $1 AND active = true AND date = CURRENT_DATE
                       ORDER BY created_at DESC LIMIT 1""",
                    user_id,
                )
                if not row:
                    return None
                exercises = row["exercises"]
                if isinstance(exercises, str):
                    exercises = json.loads(exercises)
                return {
                    "id": str(row["id"]),
                    "date": row["date"].isoformat() if row["date"] else None,
                    "exercises": exercises,
                    "generated_by": row["generated_by"],
                }
        except Exception as e:
            logger.warning(f"LocalFirestore: get_user_routine failed for {user_id}: {e}")
            return None


class GCPFirestoreAdapter:
    """GCP adapter: queries Firestore via google-cloud-firestore SDK.

    Requires:
        - google-cloud-firestore installed
        - GOOGLE_APPLICATION_CREDENTIALS env var set
        - GCP_PROJECT_ID env var set
    """

    def __init__(self, config: GCPConfig) -> None:
        self._config = config
        self._client = None

    def _get_client(self):
        """Lazy-init Firestore client."""
        if self._client is None:
            try:
                from google.cloud import firestore
                self._client = firestore.Client(project=self._config.project_id)
                logger.info(f"GCPFirestore: initialized for project {self._config.project_id}")
            except ImportError:
                raise ImportError(
                    "google-cloud-firestore is required for GCP mode. "
                    "Install with: pip install google-cloud-firestore"
                )
        return self._client

    async def get_user_profile(self, user_id: int) -> dict:
        """Get user profile from Firestore."""
        try:
            client = self._get_client()
            doc = client.collection(self._config.firestore_collection_users).document(str(user_id)).get()
            if doc.exists:
                return doc.to_dict().get("profile", {})
            return {}
        except Exception as e:
            logger.warning(f"GCPFirestore: get_user_profile failed for {user_id}: {e}")
            return {}

    async def get_user_health(self, user_id: int) -> dict:
        """Get user health profile from Firestore."""
        try:
            client = self._get_client()
            doc = client.collection(self._config.firestore_collection_users).document(str(user_id)).get()
            if doc.exists:
                return doc.to_dict().get("health_profile", {})
            return {}
        except Exception as e:
            logger.warning(f"GCPFirestore: get_user_health failed for {user_id}: {e}")
            return {}

    async def get_user_habits(self, user_id: int, days: int = 7) -> list[dict]:
        """Get recent habits from Firestore subcollection."""
        try:
            client = self._get_client()
            since = (date.today() - timedelta(days=days)).isoformat()
            docs = (
                client.collection(self._config.firestore_collection_users)
                .document(str(user_id))
                .collection(self._config.firestore_collection_habits)
                .where("date", ">=", since)
                .order_by("date", direction="DESC")
                .limit(days)
                .stream()
            )
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.warning(f"GCPFirestore: get_user_habits failed for {user_id}: {e}")
            return []

    async def get_user_tracking(self, user_id: int, weeks: int = 4) -> list[dict]:
        """Get tracking records from Firestore subcollection."""
        try:
            client = self._get_client()
            since = (date.today() - timedelta(weeks=weeks)).isoformat()
            docs = (
                client.collection(self._config.firestore_collection_users)
                .document(str(user_id))
                .collection("tracking")
                .where("completed_at", ">=", since)
                .order_by("completed_at", direction="DESC")
                .limit(100)
                .stream()
            )
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.warning(f"GCPFirestore: get_user_tracking failed for {user_id}: {e}")
            return []

    async def get_user_routine(self, user_id: int) -> dict | None:
        """Get current routine from Firestore."""
        try:
            client = self._get_client()
            docs = (
                client.collection(self._config.firestore_collection_users)
                .document(str(user_id))
                .collection("routines")
                .where("active", "==", True)
                .limit(1)
                .stream()
            )
            for doc in docs:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.warning(f"GCPFirestore: get_user_routine failed for {user_id}: {e}")
            return None


class FirestoreClient:
    """Unified Firestore client with local/GCP adapter switching.

    Agents use this client without knowing the underlying backend.
    In local mode (development), queries PostgreSQL.
    In GCP mode (production), queries Firestore.

    Precondiciones:
        - pool (asyncpg) for local mode.
        - GCPConfig for GCP mode.

    Postcondiciones:
        - All methods return empty dict/list on error (never raise).
        - Logging on every failure for debugging.

    Ejemplo de uso::

        client = FirestoreClient(mode="local", pool=pool)
        profile = await client.get_user_profile(user_id=1)
    """

    def __init__(self, mode: str = "local", pool: Any = None, config: GCPConfig | None = None) -> None:
        if mode == "gcp" and config:
            self._adapter = GCPFirestoreAdapter(config)
        else:
            if pool is None:
                raise ValueError("pool is required for local mode")
            self._adapter = LocalFirestoreAdapter(pool)

    async def get_user_profile(self, user_id: int) -> dict:
        return await self._adapter.get_user_profile(user_id)

    async def get_user_health(self, user_id: int) -> dict:
        return await self._adapter.get_user_health(user_id)

    async def get_user_habits(self, user_id: int, days: int = 7) -> list[dict]:
        return await self._adapter.get_user_habits(user_id, days)

    async def get_user_tracking(self, user_id: int, weeks: int = 4) -> list[dict]:
        return await self._adapter.get_user_tracking(user_id, weeks)

    async def get_user_routine(self, user_id: int) -> dict | None:
        return await self._adapter.get_user_routine(user_id)
