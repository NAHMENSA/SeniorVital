"""Database layer — SQLAlchemy async engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Database:
    """Factory de sesiones async para SQLAlchemy.

    Uso::

        db = Database("postgresql+asyncpg://user:pass@localhost/db")
        async with db.session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_id(1)
    """

    def __init__(self, url: str) -> None:
        self._engine = create_async_engine(url, pool_size=5, max_overflow=5)
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    def session(self) -> AsyncSession:
        """Return a new async session (must be used as context manager)."""
        return self._session_factory()

    async def dispose(self) -> None:
        """Close the engine and all pooled connections."""
        await self._engine.dispose()
