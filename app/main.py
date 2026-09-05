from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models

from app.database import (
    engine,
    init_models,
)

from app.routers.recipes import (
    router as recipes_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_models()

    yield

    await engine.dispose()


app = FastAPI(
    title="Recipe API",
    description="A fully async Recipe API built with FastAPI and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(
    recipes_router
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Recipe API"
    }