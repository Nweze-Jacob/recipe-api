from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# ============================================================
# CREATE RECIPE
# POST /recipes/
# ============================================================

@router.post(
    "/",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    recipe_data: RecipeCreate,
    session: AsyncSession = Depends(get_session),
):
    recipe = Recipe(
        name=recipe_data.name,
        description=recipe_data.description,
        category_id=recipe_data.category_id,
    )

    session.add(recipe)

    await session.commit()

    await session.refresh(recipe)

    return recipe


# ============================================================
# GET ALL RECIPES
# GET /recipes/
# ============================================================

@router.get(
    "/",
    response_model=list[RecipeResponse],
    status_code=status.HTTP_200_OK,
)
async def get_recipes(
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Recipe).order_by(Recipe.id)
    )

    recipes = result.scalars().all()

    return recipes


# ============================================================
# GET ONE RECIPE
# GET /recipes/{recipe_id}
# ============================================================

@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


# ============================================================
# UPDATE RECIPE
# PUT /recipes/{recipe_id}
# ============================================================

@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
)
async def update_recipe(
    recipe_id: int,
    recipe_data: RecipeCreate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    recipe.name = recipe_data.name
    recipe.description = recipe_data.description
    recipe.category_id = recipe_data.category_id

    await session.commit()

    await session.refresh(recipe)

    return recipe


# ============================================================
# DELETE RECIPE
# DELETE /recipes/{recipe_id}
# ============================================================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    await session.delete(recipe)

    await session.commit()

    return None