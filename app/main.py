from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.base import Base
from app.database.connection import engine

from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.recipe_step import RecipeStep

from app.routers.recipes import router as recipes_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    await engine.dispose()


app = FastAPI(
    title="Recipe API",
    description="A backend API for creating and managing recipes.",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(recipes_router)


@app.get("/")
async def root():
    return {
        "message": "Recipe API is running"
    }