"""GCP Configuration — reads credentials and settings from environment variables.

All sensitive values are loaded from env vars. No hardcoded credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class GCPConfig:
    """Configuration for GCP services (Firestore, BigQuery).

    All fields default to environment variables. In local development,
    mode="local" uses PostgreSQL/DuckDB instead of GCP services.

    Attributes:
        mode: "local" for PostgreSQL/DuckDB, "gcp" for Firestore/BigQuery.
        project_id: GCP project ID (required for mode="gcp").
        firestore_credentials: Path to service account JSON (required for mode="gcp").
        bigquery_dataset: BigQuery dataset name.
        firestore_collection_users: Firestore collection for user data.
        firestore_collection_habits: Firestore collection for habit records.
    """

    mode: str = field(default_factory=lambda: os.getenv("DATA_CLIENT_MODE", "local"))
    project_id: str = field(default_factory=lambda: os.getenv("GCP_PROJECT_ID", ""))
    firestore_credentials: str = field(
        default_factory=lambda: os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    )
    bigquery_dataset: str = field(
        default_factory=lambda: os.getenv("BIGQUERY_DATASET", "seniorvital")
    )
    firestore_collection_users: str = field(
        default_factory=lambda: os.getenv("FIRESTORE_COLLECTION_USERS", "users")
    )
    firestore_collection_habits: str = field(
        default_factory=lambda: os.getenv("FIRESTORE_COLLECTION_HABITS", "habits")
    )

    @property
    def is_gcp(self) -> bool:
        """Returns True if configured for GCP (not local mode)."""
        return self.mode == "gcp" and bool(self.project_id)

    def validate(self) -> list[str]:
        """Validates configuration. Returns list of errors (empty if valid)."""
        errors = []
        if self.mode == "gcp":
            if not self.project_id:
                errors.append("GCP_PROJECT_ID is required for GCP mode")
            if not self.firestore_credentials:
                errors.append(
                    "GOOGLE_APPLICATION_CREDENTIALS is required for GCP mode"
                )
        return errors
