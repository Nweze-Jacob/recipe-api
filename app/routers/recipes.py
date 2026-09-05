from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
    Query,
)

from sqlalchemy import (
    func,
    select,
)

from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.database import get_session

from app.models.ingredient import Ingredient
from app.models.category import Category
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.recipe_step import RecipeStep

from app.schemas.ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientResponse,
    RecipeIngredientUpdate,
)

from app.schemas.recipe import (
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)

from app.schemas.recipe_step import (
    RecipeStepCreate,
    RecipeStepResponse,
    RecipeStepUpdate,
)



router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# ============================================================
# CREATE RECIPE
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



 #GET ONE RECIPE
@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    result = await session.execute(statement)

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


# ============================================================
# LESSON 23 — UPDATE RECIPE
# ============================================================

@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    result = await session.execute(statement)

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    recipe.name = recipe_data.name

    recipe.description = (
        recipe_data.description
    )

    recipe.category_id = (
        recipe_data.category_id
    )

    await session.commit()

    await session.refresh(recipe)

    return recipe


# ============================================================
# LESSON 24 — DELETE RECIPE
# ============================================================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    result = await session.execute(statement)

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    await session.delete(recipe)

    await session.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )



@router.post(
    "/{recipe_id}/ingredients",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_ingredient_to_recipe(
    recipe_id: int,
    ingredient_data: RecipeIngredientCreate,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # STEP 1 — Find the recipe
    # --------------------------------------------------------

    recipe_statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # STEP 2 — Find existing ingredient
    # --------------------------------------------------------

    ingredient_statement = select(Ingredient).where(
        Ingredient.name == ingredient_data.name
    )

    ingredient_result = await session.execute(
        ingredient_statement
    )

    ingredient = (
        ingredient_result.scalar_one_or_none()
    )

    # --------------------------------------------------------
    # STEP 3 — Create ingredient if it doesn't exist
    # --------------------------------------------------------

    if ingredient is None:
        ingredient = Ingredient(
            name=ingredient_data.name
        )

        session.add(ingredient)

        await session.flush()

    # --------------------------------------------------------
    # STEP 4 — Check if relationship already exists
    # --------------------------------------------------------

    relationship_statement = select(
        RecipeIngredient
    ).where(
        RecipeIngredient.recipe_id == recipe_id,
        RecipeIngredient.ingredient_id
        == ingredient.id,
    )

    relationship_result = await session.execute(
        relationship_statement
    )

    existing_relationship = (
        relationship_result.scalar_one_or_none()
    )

    if existing_relationship is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ingredient already exists "
                "in this recipe"
            ),
        )

    # --------------------------------------------------------
    # STEP 5 — Create RecipeIngredient relationship
    # --------------------------------------------------------

    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient.id,
        amount=ingredient_data.amount,
        unit=ingredient_data.unit,
        preparation=ingredient_data.preparation,
    )

    session.add(recipe_ingredient)

    # --------------------------------------------------------
    # STEP 6 — Commit transaction
    # --------------------------------------------------------

    await session.commit()

    # --------------------------------------------------------
    # STEP 7 — Refresh relationship record
    # --------------------------------------------------------

    await session.refresh(
        recipe_ingredient
    )

    # --------------------------------------------------------
    # STEP 8 — Return complete relationship
    # --------------------------------------------------------

    return recipe_ingredient



@router.get(
    "/{recipe_id}/ingredients",
    response_model=list[RecipeIngredientResponse],
    status_code=status.HTTP_200_OK,
)
async def get_recipe_ingredients(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # STEP 1 — Verify that the recipe exists
    # --------------------------------------------------------

    recipe_statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # STEP 2 — Select RecipeIngredient records
    # --------------------------------------------------------

    statement = (
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.recipe_id
            == recipe_id
        )
    )

    # --------------------------------------------------------
    # STEP 3 — Execute asynchronously
    # --------------------------------------------------------

    result = await session.execute(statement)

    # --------------------------------------------------------
    # STEP 4 — Extract RecipeIngredient objects
    # --------------------------------------------------------

    recipe_ingredients = (
        result.scalars().all()
    )

    # --------------------------------------------------------
    # STEP 5 — Return nested data
    # --------------------------------------------------------

    return recipe_ingredients


@router.put(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
)
async def update_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    ingredient_data: RecipeIngredientUpdate,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. Check that the recipe exists
    # --------------------------------------------------------

    recipe_statement = (
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # 2. Find the recipe-ingredient relationship
    # --------------------------------------------------------

    statement = (
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.id == recipe_ingredient_id,
            RecipeIngredient.recipe_id == recipe_id,
        )
    )

    result = await session.execute(statement)

    recipe_ingredient = result.scalar_one_or_none()

    # --------------------------------------------------------
    # 3. Check relationship exists
    # --------------------------------------------------------

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    # --------------------------------------------------------
    # 4. Update fields
    # --------------------------------------------------------

    recipe_ingredient.amount = ingredient_data.amount
    recipe_ingredient.unit = ingredient_data.unit
    recipe_ingredient.preparation = (
        ingredient_data.preparation
    )

    # --------------------------------------------------------
    # 5. Save changes
    # --------------------------------------------------------

    await session.commit()

    # --------------------------------------------------------
    # 6. Refresh object
    # --------------------------------------------------------

    await session.refresh(recipe_ingredient)

    # --------------------------------------------------------
    # 7. Return updated relationship
    # --------------------------------------------------------

    return recipe_ingredient


@router.delete(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. Check that the recipe exists
    # --------------------------------------------------------

    recipe_statement = (
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # 2. Find the recipe-ingredient relationship
    # --------------------------------------------------------

    statement = (
        select(RecipeIngredient)
        .where(
            RecipeIngredient.id == recipe_ingredient_id,
            RecipeIngredient.recipe_id == recipe_id,
        )
    )

    result = await session.execute(
        statement
    )

    recipe_ingredient = result.scalar_one_or_none()

    # --------------------------------------------------------
    # 3. Check that relationship exists
    # --------------------------------------------------------

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    # --------------------------------------------------------
    # 4. Delete relationship
    # --------------------------------------------------------

    await session.delete(
        recipe_ingredient
    )

    # --------------------------------------------------------
    # 5. Commit transaction
    # --------------------------------------------------------

    await session.commit()

    # --------------------------------------------------------
    # 6. Return 204 No Content
    # --------------------------------------------------------

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/{recipe_id}/steps",
    response_model=RecipeStepResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe_step(
    recipe_id: int,
    step_data: RecipeStepCreate,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. Check that recipe exists
    # --------------------------------------------------------

    recipe_statement = (
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # 2. Create recipe step
    # --------------------------------------------------------

    recipe_step = RecipeStep(
        recipe_id=recipe_id,
        step_number=step_data.step_number,
        instruction=step_data.instruction,
    )

    session.add(recipe_step)

    # --------------------------------------------------------
    # 3. Save to database
    # --------------------------------------------------------

    await session.commit()

    # --------------------------------------------------------
    # 4. Refresh object
    # --------------------------------------------------------

    await session.refresh(
        recipe_step
    )

    return recipe_step


# ============================================================

# GET RECIPE STEPS
# ============================================================

@router.get(
    "/{recipe_id}/steps",
    response_model=list[RecipeStepResponse],
)
async def get_recipe_steps(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. Check that recipe exists
    # --------------------------------------------------------

    recipe_statement = (
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # 2. Get recipe steps
    # --------------------------------------------------------

    statement = (
        select(RecipeStep)
        .where(
            RecipeStep.recipe_id == recipe_id
        )
        .order_by(
            RecipeStep.step_number
        )
    )

    result = await session.execute(
        statement
    )

    steps = result.scalars().all()

    return steps


# UPDATE RECIPE STE
@router.put(
    "/{recipe_id}/steps/{step_id}",
    response_model=RecipeStepResponse,
)
async def update_recipe_step(
    recipe_id: int,
    step_id: int,
    step_data: RecipeStepUpdate,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. Check recipe
    # --------------------------------------------------------

    recipe_statement = (
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # 2. Find step belonging to this recipe
    # --------------------------------------------------------

    statement = (
        select(RecipeStep)
        .where(
            RecipeStep.id == step_id,
            RecipeStep.recipe_id == recipe_id,
        )
    )

    result = await session.execute(
        statement
    )

    recipe_step = result.scalar_one_or_none()

    if recipe_step is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe step not found",
        )

    # --------------------------------------------------------
    # 3. Update step
    # --------------------------------------------------------

    recipe_step.step_number = (
        step_data.step_number
    )

    recipe_step.instruction = (
        step_data.instruction
    )

    # --------------------------------------------------------
    # 4. Save
    # --------------------------------------------------------

    await session.commit()

    await session.refresh(
        recipe_step
    )

    return recipe_step


# ============================================================
# DELETE RECIPE STEP
# ============================================================

@router.delete(
    "/{recipe_id}/steps/{step_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe_step(
    recipe_id: int,
    step_id: int,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. Check recipe
    # --------------------------------------------------------

    recipe_statement = (
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe_result = await session.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # 2. Find step
    # --------------------------------------------------------

    statement = (
        select(RecipeStep)
        .where(
            RecipeStep.id == step_id,
            RecipeStep.recipe_id == recipe_id,
        )
    )

    result = await session.execute(
        statement
    )

    recipe_step = result.scalar_one_or_none()

    if recipe_step is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe step not found",
        )

    # --------------------------------------------------------
    # 3. Delete
    # --------------------------------------------------------

    await session.delete(
        recipe_step
    )

    await session.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# SEARCH RECIPES BY NAME
@router.get(
    "/",
    response_model=list[RecipeResponse],
)
async def search_recipes(
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Recipe)

    # --------------------------------------------------------
    # Apply search filter when search is provided
    # --------------------------------------------------------

    if search:
        statement = statement.where(
            func.lower(Recipe.name).contains(
                search.lower()
            )
        )

    # --------------------------------------------------------
    # Execute query
    # --------------------------------------------------------

    result = await session.execute(
        statement
    )

    recipes = result.scalars().all()

    return recipes


@router.get(
    "",
    response_model=list[RecipeResponse],
)
async def search_recipes_by_ingredient(
    ingredient: str,
    db: AsyncSession = Depends(get_session),
):
    query = (
        select(Recipe)
        .join(
            RecipeIngredient,
            Recipe.id == RecipeIngredient.recipe_id,
        )
        .join(
            Ingredient,
            RecipeIngredient.ingredient_id == Ingredient.id,
        )
        .where(
            Ingredient.name.ilike(f"%{ingredient}%")
        )
        .distinct()
    )

    result = await db.execute(query)

    recipes = result.scalars().all()

    return recipes


@router.get(
    "",
    response_model=list[RecipeResponse],
)
async def search_recipes_by_category(
    category: str,
    db: AsyncSession = Depends(get_session),
):
    query = (
        select(Recipe)
        .join(
            Category,
            Recipe.category_id == Category.id,
        )
        .where(
            Category.name.ilike(f"%{category}%")
        )
        .distinct()
    )

    result = await db.execute(query)

    recipes = result.scalars().all()

    return recipes




@router.get(
    "",
    response_model=list[RecipeResponse],
)
async def search_and_paginate_recipes(
    search: str | None = Query(
        default=None,
        min_length=1,
    ),

    ingredient: str | None = Query(
        default=None,
        min_length=1,
    ),

    category: str | None = Query(
        default=None,
        min_length=1,
    ),

    page: int = Query(
        default=1,
        ge=1,
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),

    sort_by: Literal[
        "name",
        "created_at",
        "id",
    ] = "created_at",

    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",

    db: AsyncSession = Depends(get_session),
):
    query = select(Recipe)

    # --------------------------------------------------
    # SEARCH BY RECIPE NAME
    # --------------------------------------------------

    if search:
        query = query.where(
            Recipe.name.ilike(
                f"%{search}%"
            )
        )

    # --------------------------------------------------
    # SEARCH BY CATEGORY
    # --------------------------------------------------

    if category:
        query = query.join(
            Category,
            Recipe.category_id == Category.id,
        )

        query = query.where(
            Category.name.ilike(
                f"%{category}%"
            )
        )

    # --------------------------------------------------
    # SEARCH BY INGREDIENT
    # --------------------------------------------------

    if ingredient:
        query = query.join(
            RecipeIngredient,
            Recipe.id
            == RecipeIngredient.recipe_id,
        )

        query = query.join(
            Ingredient,
            RecipeIngredient.ingredient_id
            == Ingredient.id,
        )

        query = query.where(
            Ingredient.name.ilike(
                f"%{ingredient}%"
            )
        )

    # --------------------------------------------------
    # REMOVE DUPLICATE RECIPES
    # --------------------------------------------------

    query = query.distinct()

    # --------------------------------------------------
    # SORTING
    # --------------------------------------------------

    sort_column = {
        "id": Recipe.id,
        "name": Recipe.name,
        "created_at": Recipe.created_at,
    }[sort_by]

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # --------------------------------------------------
    # PAGINATION
    # --------------------------------------------------

    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit)

    # --------------------------------------------------
    # EXECUTE QUERY
    # --------------------------------------------------

    result = await db.execute(query)

    recipes = result.scalars().all()

    return recipes