"""BigQuery Client — dual-mode client for analytics data access.

Local mode: queries DuckDB (embedded analytics database).
GCP mode: queries BigQuery via google-cloud-bigquery SDK.

Agents depend on BigQueryClientProtocol, not on this concrete class.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from src.clients.config import GCPConfig

logger = logging.getLogger(__name__)

DUCKDB_PATH = os.getenv(
    "DUCKDB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "seniorvital_analytics.duckdb"),
)


class LocalBigQueryAdapter:
    """Local adapter: queries DuckDB as BigQuery replacement.

    Uses the embedded DuckDB file for analytics queries.
    """

    def __init__(self, duckdb_path: str = DUCKDB_PATH) -> None:
        self._duckdb_path = duckdb_path

    def _connect(self):
        """Create a DuckDB connection."""
        try:
            import duckdb
            return duckdb.connect(self._duckdb_path, read_only=True)
        except Exception as e:
            logger.warning(f"LocalBigQuery: DuckDB connection failed: {e}")
            return None

    async def get_weekly_progress(self, user_id: int, weeks: int = 4) -> list[dict]:
        """Get weekly progress from DuckDB weekly_progress table."""
        con = self._connect()
        if not con:
            return []
        try:
            result = con.execute(
                """SELECT week_start, insight_text, estimated_level
                   FROM weekly_progress
                   WHERE user_id = ? AND week_start >= CURRENT_DATE - INTERVAL '? weeks'
                   ORDER BY week_start DESC""",
                [user_id, weeks],
            ).fetchall()
            return [
                {
                    "week": str(r[0]) if r[0] else None,
                    "insight": r[1],
                    "level": r[2],
                }
                for r in result
            ]
        except Exception as e:
            logger.warning(f"LocalBigQuery: get_weekly_progress failed for {user_id}: {e}")
            return []
        finally:
            con.close()

    async def get_activity_summary(self, user_id: int) -> dict:
        """Get aggregated activity summary from DuckDB."""
        con = self._connect()
        if not con:
            return {}
        try:
            result = con.execute(
                """SELECT COUNT(*) as total_sessions,
                          AVG(rpe) as avg_rpe,
                          COUNT(DISTINCT DATE_TRUNC('week', event_date)) as weeks_active
                   FROM raw_events
                   WHERE user_id = ?""",
                [user_id],
            ).fetchone()
            if result:
                return {
                    "total_sessions": result[0] or 0,
                    "avg_rpe": round(float(result[1]), 1) if result[1] else None,
                    "weeks_active": result[2] or 0,
                }
            return {}
        except Exception as e:
            logger.warning(f"LocalBigQuery: get_activity_summary failed for {user_id}: {e}")
            return {}
        finally:
            con.close()

    async def get_population_trends(self, condition: str | None = None) -> list[dict]:
        """Population trends not available in local mode (DuckDB is single-user)."""
        logger.info("LocalBigQuery: population_trends not available in local mode")
        return []


class GCPBigQueryAdapter:
    """GCP adapter: queries BigQuery via google-cloud-bigquery SDK.

    Requires:
        - google-cloud-bigquery installed
        - GOOGLE_APPLICATION_CREDENTIALS env var set
        - GCP_PROJECT_ID env var set
    """

    def __init__(self, config: GCPConfig) -> None:
        self._config = config
        self._client = None

    def _get_client(self):
        """Lazy-init BigQuery client."""
        if self._client is None:
            try:
                from google.cloud import bigquery
                self._client = bigquery.Client(project=self._config.project_id)
                logger.info(f"GCPBigQuery: initialized for project {self._config.project_id}")
            except ImportError:
                raise ImportError(
                    "google-cloud-bigquery is required for GCP mode. "
                    "Install with: pip install google-cloud-bigquery"
                )
        return self._client

    async def get_weekly_progress(self, user_id: int, weeks: int = 4) -> list[dict]:
        """Get weekly progress from BigQuery."""
        try:
            client = self._get_client()
            query = f"""
                SELECT week_start, insight_text, estimated_level
                FROM `{self._config.bigquery_dataset}.weekly_progress`
                WHERE user_id = @user_id
                  AND week_start >= DATE_SUB(CURRENT_DATE(), INTERVAL @weeks WEEK)
                ORDER BY week_start DESC
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "INT64", user_id),
                    bigquery.ScalarQueryParameter("weeks", "INT64", weeks),
                ]
            )
            results = client.query(query, job_config=job_config).result()
            return [
                {
                    "week": str(r.week_start) if r.week_start else None,
                    "insight": r.insight_text,
                    "level": r.estimated_level,
                }
                for r in results
            ]
        except Exception as e:
            logger.warning(f"GCPBigQuery: get_weekly_progress failed for {user_id}: {e}")
            return []

    async def get_activity_summary(self, user_id: int) -> dict:
        """Get aggregated activity from BigQuery."""
        try:
            client = self._get_client()
            query = f"""
                SELECT COUNT(*) as total_sessions,
                       AVG(rpe) as avg_rpe,
                       COUNT(DISTINCT DATE_TRUNC(event_date, WEEK(MONDAY))) as weeks_active
                FROM `{self._config.bigquery_dataset}.tracking`
                WHERE user_id = @user_id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "INT64", user_id),
                ]
            )
            results = client.query(query, job_config=job_config).result()
            for r in results:
                return {
                    "total_sessions": r.total_sessions or 0,
                    "avg_rpe": round(float(r.avg_rpe), 1) if r.avg_rpe else None,
                    "weeks_active": r.weeks_active or 0,
                }
            return {}
        except Exception as e:
            logger.warning(f"GCPBigQuery: get_activity_summary failed for {user_id}: {e}")
            return {}

    async def get_population_trends(self, condition: str | None = None) -> list[dict]:
        """Get anonymized population trends from BigQuery."""
        try:
            client = self._get_client()
            condition_filter = ""
            params = []
            if condition:
                condition_filter = "WHERE health_condition = @condition"
                params.append(
                    bigquery.ScalarQueryParameter("condition", "STRING", condition)
                )
            query = f"""
                SELECT health_condition,
                       AVG(progress_score) as avg_progress,
                       COUNT(DISTINCT user_id) as user_count
                FROM `{self._config.bigquery_dataset}.population_analytics`
                {condition_filter}
                GROUP BY health_condition
                ORDER BY user_count DESC
                LIMIT 20
            """
            job_config = bigquery.QueryJobConfig(query_parameters=params) if params else None
            results = client.query(query, job_config=job_config).result()
            return [
                {
                    "condition": r.health_condition,
                    "avg_progress": round(float(r.avg_progress), 2) if r.avg_progress else None,
                    "user_count": r.user_count,
                }
                for r in results
            ]
        except Exception as e:
            logger.warning(f"GCPBigQuery: get_population_trends failed: {e}")
            return []


class BigQueryClient:
    """Unified BigQuery client with local/GCP adapter switching.

    Agents use this client without knowing the underlying backend.
    In local mode (development), queries DuckDB.
    In GCP mode (production), queries BigQuery.

    Precondiciones:
        - DuckDB file for local mode.
        - GCPConfig for GCP mode.

    Postcondiciones:
        - All methods return empty dict/list on error (never raise).
        - Logging on every failure for debugging.

    Ejemplo de uso::

        client = BigQueryClient(mode="local")
        summary = await client.get_activity_summary(user_id=1)
    """

    def __init__(self, mode: str = "local", config: GCPConfig | None = None) -> None:
        if mode == "gcp" and config:
            self._adapter = GCPBigQueryAdapter(config)
        else:
            self._adapter = LocalBigQueryAdapter()

    async def get_weekly_progress(self, user_id: int, weeks: int = 4) -> list[dict]:
        return await self._adapter.get_weekly_progress(user_id, weeks)

    async def get_activity_summary(self, user_id: int) -> dict:
        return await self._adapter.get_activity_summary(user_id)

    async def get_population_trends(self, condition: str | None = None) -> list[dict]:
        return await self._adapter.get_population_trends(condition)
