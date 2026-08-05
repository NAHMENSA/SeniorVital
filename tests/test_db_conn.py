"""Script de verificación de conexión a PostgreSQL.

Conecta a la base de datos, imprime la versión y lista las tablas.
Útil para diagnóstico rápido de conectividad.
"""
import asyncio
import asyncpg


async def main():
    """Conecta a PostgreSQL, imprime versión y lista de tablas."""
    conn = await asyncpg.connect(
        "postgresql://postgres:9739185@localhost:5432/seniorvital"
    )
    print("Connected!")
    ver = await conn.fetchval("SELECT version()")
    print(f"Version: {ver}")
    tables = await conn.fetch(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    )
    print("Tables:", [t["table_name"] for t in tables])
    await conn.close()


asyncio.run(main())
