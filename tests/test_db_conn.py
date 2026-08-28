"""Script de verificación de conexión a PostgreSQL.

Conecta a la base de datos, imprime la versión y lista las tablas.
Útil para diagnóstico rápido de conectividad.
"""
import asyncio
import asyncpg
import os


async def main():
    """Conecta a PostgreSQL, imprime versión y lista de tablas."""
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("ERROR: DATABASE_URL no está configurada.")
        return

    conn = await asyncpg.connect(dsn)
    print("Connected!")
    ver = await conn.fetchval("SELECT version()")
    print(f"Version: {ver}")
    tables = await conn.fetch(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    )
    print("Tables:", [t["table_name"] for t in tables])
    await conn.close()


asyncio.run(main())
