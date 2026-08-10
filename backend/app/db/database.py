import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.domain.models import Base

# DB Path configuration
DB_DIR = os.path.join(os.path.dirname(__file__), "../../../data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "qsci_v2.db")

# SQLite async URL
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """Initialize the database tables if they do not exist."""
    async with engine.begin() as conn:
        # Create all tables defined in Base
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency to yield database sessions."""
    async with AsyncSessionLocal() as session:
        yield session
