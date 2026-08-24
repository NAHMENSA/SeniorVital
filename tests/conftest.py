"""Configuración compartida de pytest para SeniorVital.

Inicializa el pool de base de datos, proporciona la función
load_service_app para cargar dinámicamente cada microservicio
y limpia los datos entre ejecuciones de tests.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import importlib.util
import pytest
from dotenv import load_dotenv

load_dotenv()

os.environ["DATABASE_URL"] = "postgresql://postgres:9739185@127.0.0.1:5432/seniorvital"

SCHEMA_SQL = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "scripts",
    "fix_db.sql",
)


def load_service_app(service_name: str):
    """Carga dinámicamente la aplicación FastAPI de un microservicio.

    :param service_name: Nombre del directorio del servicio (ej. 'auth-profile-service').
    :return: Instancia de la aplicación FastAPI.
    """
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), service_name, "main.py")
    spec = importlib.util.spec_from_file_location(service_name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), service_name))
    spec.loader.exec_module(mod)
    return mod.app


@pytest.fixture(scope="session", autouse=True)
async def init_database():
    """Fixture de sesión que crea todas las tablas antes de cualquier test."""
    from seniorvital_shared import init_pool, close_pool, get_pool

    await init_pool(min_size=1, max_size=5, owner="session")
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DROP SCHEMA IF EXISTS seniorvital CASCADE")
        await conn.execute("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public")
        with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        await conn.execute(schema_sql)
    await close_pool(owner="session")


@pytest.fixture(autouse=True)
async def auto_init_pool():
    """Fixture que inicializa el pool de BD antes de cada test y lo cierra al finalizar."""
    from seniorvital_shared import init_pool, close_pool

    await init_pool(min_size=1, max_size=5, owner="test")
    yield
    await close_pool(owner="test")


@pytest.fixture(autouse=True)
async def cleanup():
    """Fixture que limpia todas las tablas después de cada test."""
    from seniorvital_shared import get_pool

    yield
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE admin_logs, agent_insights, agent_queue, conversation_history, push_subscriptions, workout_sets, workout_exercises, workout_sessions, caregiver_links, event_queue, tracking, routines, projections, habits, exercises, users RESTART IDENTITY CASCADE")
