import socket
import time
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# Cached database reachability check to prevent blocking async loops
_DB_AVAILABLE: bool | None = None
_LAST_DB_CHECK: float = 0.0
_DB_CHECK_INTERVAL = 10.0  # re-probe every 10 seconds

def is_db_reachable() -> bool:
    """Fast socket-level probe to check if PostgreSQL host:port is listening."""
    global _DB_AVAILABLE, _LAST_DB_CHECK
    now = time.time()
    if _DB_AVAILABLE is not None and (now - _LAST_DB_CHECK) < _DB_CHECK_INTERVAL:
        return _DB_AVAILABLE

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        res = sock.connect_ex((settings.postgres_host, settings.postgres_port))
        sock.close()
        _DB_AVAILABLE = (res == 0)
    except Exception:
        _DB_AVAILABLE = False

    _LAST_DB_CHECK = now
    return _DB_AVAILABLE

# Create asynchronous engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=False,
)

# Async session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession | None, None]:
    """Dependency injection helper for database session.
    
    Yields None immediately if PostgreSQL is not listening, allowing
    routes to fall through to the canonical dataset instantly without
    blocking on socket connect timeouts.
    """
    if not is_db_reachable():
        yield None
        return

    try:
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    except Exception:
        yield None
