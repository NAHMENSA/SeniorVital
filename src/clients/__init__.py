"""Clients — abstraction layer for data sources (Firestore, BigQuery).

Provides dual-mode clients that work with local backends (PostgreSQL, DuckDB)
in development and GCP services (Firestore, BigQuery) in production.
"""

from src.clients.base import BigQueryClientProtocol, FirestoreClientProtocol
from src.clients.config import GCPConfig
from src.clients.firestore_client import FirestoreClient
from src.clients.bigquery_client import BigQueryClient

__all__ = [
    "FirestoreClientProtocol",
    "BigQueryClientProtocol",
    "GCPConfig",
    "FirestoreClient",
    "BigQueryClient",
]
