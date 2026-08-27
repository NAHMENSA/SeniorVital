"""Base protocols — contracts for Firestore and BigQuery clients.

Defines the interface that both local (PostgreSQL/DuckDB) and GCP adapters
must implement. Agents depend only on these protocols, not on concrete implementations.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class FirestoreClientProtocol(Protocol):
    """Contract for user data access (Firestore or PostgreSQL equivalent).

    Provides structured access to user data without exposing the underlying
    storage mechanism. Local adapter queries PostgreSQL; GCP adapter queries Firestore.
    """

    async def get_user_profile(self, user_id: int) -> dict:
        """Get user profile (name, age, city, etc.)."""
        ...

    async def get_user_health(self, user_id: int) -> dict:
        """Get user health profile (conditions, restrictions, fitness level)."""
        ...

    async def get_user_habits(self, user_id: int, days: int = 7) -> list[dict]:
        """Get recent habit records (water intake, sleep hours)."""
        ...

    async def get_user_tracking(self, user_id: int, weeks: int = 4) -> list[dict]:
        """Get recent exercise tracking records."""
        ...

    async def get_user_routine(self, user_id: int) -> dict | None:
        """Get the user's current active routine."""
        ...


@runtime_checkable
class BigQueryClientProtocol(Protocol):
    """Contract for analytics data access (BigQuery or DuckDB equivalent).

    Provides aggregated analytics, trends, and cross-user insights.
    Local adapter queries DuckDB; GCP adapter queries BigQuery.
    """

    async def get_weekly_progress(self, user_id: int, weeks: int = 4) -> list[dict]:
        """Get weekly progress insights and projections."""
        ...

    async def get_activity_summary(self, user_id: int) -> dict:
        """Get aggregated activity summary (total sessions, avg RPE, etc.)."""
        ...

    async def get_population_trends(self, condition: str | None = None) -> list[dict]:
        """Get anonymized population-level trends (BigQuery only, local returns empty)."""
        ...
