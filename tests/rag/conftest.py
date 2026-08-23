"""Conftest for RAG/chunking tests without database dependencies."""

import os
import sys

# Ensure src is on the import path.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src"))

import pytest


@pytest.fixture(scope="session", autouse=True)
def init_database():
    """No-op override of the root DB session fixture."""
    yield


@pytest.fixture(autouse=True)
def auto_init_pool():
    """No-op override of the root DB pool fixture."""
    yield


@pytest.fixture(autouse=True)
def cleanup():
    """No-op override of the root DB cleanup fixture."""
    yield
