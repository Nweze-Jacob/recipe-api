from app.database.base import Base
from app.database.connection import engine


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)