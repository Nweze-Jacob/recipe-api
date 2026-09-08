from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.database import get_session

from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.recipe_step import RecipeStep
from app.models.user import User

from app.schemas.recipe_ingredient import (
RecipeIngredientCreate,
RecipeIngredientResponse,
RecipeIngredientUpdate,
)

from app.schemas.recipe import (
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# =================================================
# RECIPE CRUD
# =================================================


@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    data: RecipeCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new recipe for the authenticated user.

    Recipe steps can be created together with the recipe.
    """

    # -------------------------------------------------
    # Check category if supplied
    # -------------------------------------------------

    if data.category_id is not None:

        category_result = await session.execute(
            select(Category).where(
                Category.id == data.category_id
            )
        )

        category = category_result.scalar_one_or_none()

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    # -------------------------------------------------
    # Validate recipe step numbers
    # -------------------------------------------------

    step_numbers = [
        step.step_number
        for step in data.steps
    ]

    if len(step_numbers) != len(set(step_numbers)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate step numbers are not allowed",
        )

    # -------------------------------------------------
    # Create recipe
    # -------------------------------------------------

    recipe = Recipe(
        name=data.name,
        description=data.description,
        category_id=data.category_id,
        owner_id=current_user.id,
        is_public=data.is_public,
        prep_minutes=data.prep_minutes,
        cook_minutes=data.cook_minutes,
    )

    session.add(recipe)

    # Flush first so recipe.id is available
    # before creating RecipeStep records.
    await session.flush()

    # -------------------------------------------------
    # Create recipe steps
    # -------------------------------------------------

    for step_data in data.steps:

        step = RecipeStep(
            recipe_id=recipe.id,
            step_number=step_data.step_number,
            instruction=step_data.instruction,
        )

        session.add(step)

    # -------------------------------------------------
    # Commit transaction
    # -------------------------------------------------

    await session.commit()

    # -------------------------------------------------
    # Reload recipe with steps
    # -------------------------------------------------

    result = await session.execute(
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.id == recipe.id
        )
    )

    recipe = result.scalar_one()

    return recipe


@router.get(
    "",
    response_model=list[RecipeResponse],
)
async def list_recipes(
    search: str | None = Query(
        default=None,
        description="Search recipes by name or description",
    ),
    ingredient: str | None = Query(
        default=None,
        description="Filter recipes by ingredient name",
    ),
    category: str | None = Query(
        default=None,
        description="Filter recipes by category name",
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
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Return recipes belonging to the authenticated user.

    Supports:
    - name/description search
    - ingredient filtering
    - category filtering
    - pagination
    - sorting
    - recipe steps
    """

    query = (
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.owner_id == current_user.id
        )
    )

    # -------------------------------------------------
    # Search by name or description
    # -------------------------------------------------

    if search:

        search_term = f"%{search.strip()}%"

        query = query.where(
            (
                Recipe.name.ilike(search_term)
            )
            |
            (
                Recipe.description.ilike(search_term)
            )
        )

    # -------------------------------------------------
    # Filter by ingredient
    # -------------------------------------------------

    if ingredient:

        query = (
            query
            .join(
                RecipeIngredient,
                RecipeIngredient.recipe_id == Recipe.id,
            )
            .join(
                Ingredient,
                Ingredient.id == RecipeIngredient.ingredient_id,
            )
            .where(
                Ingredient.name.ilike(
                    f"%{ingredient.strip()}%"
                )
            )
            .distinct()
        )

    # -------------------------------------------------
    # Filter by category
    # -------------------------------------------------

    if category:

        query = (
            query
            .join(
                Category,
                Category.id == Recipe.category_id,
            )
            .where(
                Category.name.ilike(
                    f"%{category.strip()}%"
                )
            )
        )

    # -------------------------------------------------
    # Sorting
    # -------------------------------------------------

    sort_column = getattr(
        Recipe,
        sort_by,
    )

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # -------------------------------------------------
    # Pagination
    # -------------------------------------------------

    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit)

    result = await session.execute(query)

    return result.scalars().unique().all()


# =================================================
# PUBLIC RECIPES
# =================================================


@router.get(
    "/public",
    response_model=list[RecipeResponse],
)
async def get_public_recipes(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Return all public recipes.

    Recipe steps are included in the response.
    """

    result = await session.execute(
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.is_public.is_(True)
        )
        .order_by(
            Recipe.created_at.desc()
        )
    )

    return result.scalars().unique().all()


# =================================================
# CURRENT USER'S RECIPES
# =================================================


@router.get(
    "/mine",
    response_model=list[RecipeResponse],
)
async def get_my_recipes(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Return recipes owned by the authenticated user.

    Recipe steps are included in the response.
    """

    result = await session.execute(
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.owner_id == current_user.id
        )
        .order_by(
            Recipe.created_at.desc()
        )
    )

    return result.scalars().unique().all()


# =================================================
# MULTIPLE INGREDIENT SEARCH
# =================================================


@router.get(
    "/search/multiple-ingredients",
    response_model=list[RecipeResponse],
)
async def search_multiple_ingredients(
    ingredients: str = Query(
        ...,
        description=(
            "Comma-separated ingredient names"
        ),
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Search public recipes containing all
    requested ingredients.

    Recipe steps are included in the response.

    Example:

    /recipes/search/multiple-ingredients?ingredients=chicken,rice
    """

    ingredient_names = [
        name.strip().lower()
        for name in ingredients.split(",")
        if name.strip()
    ]

    if not ingredient_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one ingredient is required",
        )

    unique_names = set(ingredient_names)

    query = (
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .join(
            RecipeIngredient,
            RecipeIngredient.recipe_id == Recipe.id,
        )
        .join(
            Ingredient,
            Ingredient.id == RecipeIngredient.ingredient_id,
        )
        .where(
            Recipe.is_public.is_(True),
            func.lower(Ingredient.name).in_(
                unique_names
            ),
        )
        .group_by(Recipe.id)
        .having(
            func.count(
                func.distinct(
                    func.lower(Ingredient.name)
                )
            )
            == len(unique_names)
        )
        .order_by(
            Recipe.created_at.desc()
        )
    )

    result = await session.execute(query)

    return result.scalars().unique().all()


# =================================================
# SEARCH BY TOTAL TIME
# =================================================


@router.get(
    "/search/by-time",
    response_model=list[RecipeResponse],
)
async def search_recipes_by_time(
    min_time: int | None = Query(
        default=None,
        ge=0,
        description="Minimum total recipe time in minutes",
    ),
    max_time: int | None = Query(
        default=None,
        ge=0,
        description="Maximum total recipe time in minutes",
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Search public recipes by total preparation
    plus cooking time.

    Recipe steps are included in the response.

    Total time:

        prep_minutes + cook_minutes
    """

    if (
        min_time is not None
        and max_time is not None
        and min_time > max_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "min_time cannot be greater "
                "than max_time"
            ),
        )

    total_time = (
        Recipe.prep_minutes
        + Recipe.cook_minutes
    )

    query = (
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.is_public.is_(True)
        )
    )

    if min_time is not None:
        query = query.where(
            total_time >= min_time
        )

    if max_time is not None:
        query = query.where(
            total_time <= max_time
        )

    query = query.order_by(
        total_time.asc()
    )

    result = await session.execute(query)

    return result.scalars().unique().all()


# =================================================
# GET SINGLE RECIPE
# =================================================


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve one recipe.

    Public recipes can be viewed.

    Private recipes can only be viewed
    by their owner.

    Recipe steps are included in the response.
    """

    result = await session.execute(
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # -------------------------------------------------
    # Private recipe authorization
    # -------------------------------------------------

    if (
        not recipe.is_public
        and recipe.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this recipe",
        )

    return recipe


# =================================================
# UPDATE RECIPE
# =================================================


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Update a recipe.

    Only the owner can update the recipe.

    If steps are supplied, the existing recipe steps
    are replaced with the supplied ordered steps.
    """

    result = await session.execute(
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # -------------------------------------------------
    # Authorization
    # -------------------------------------------------

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own recipes",
        )

    # -------------------------------------------------
    # Validate category if supplied
    # -------------------------------------------------

    if data.category_id is not None:

        category_result = await session.execute(
            select(Category).where(
                Category.id == data.category_id
            )
        )

        category = category_result.scalar_one_or_none()

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    # -------------------------------------------------
    # Validate recipe steps if supplied
    # -------------------------------------------------

    if data.steps is not None:

        step_numbers = [
            step.step_number
            for step in data.steps
        ]

        if len(step_numbers) != len(set(step_numbers)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate step numbers are not allowed",
            )

    # -------------------------------------------------
    # Apply recipe fields only
    # -------------------------------------------------

    update_data = data.model_dump(
        exclude_unset=True,
        exclude={"steps"},
    )

    for field, value in update_data.items():
        setattr(
            recipe,
            field,
            value,
        )

    # -------------------------------------------------
    # Replace recipe steps if supplied
    # -------------------------------------------------

    if data.steps is not None:

        # Remove existing steps first.
        for step in list(recipe.recipe_steps):
            await session.delete(step)

        # Flush the deletes before inserting new steps.
        # This prevents conflicts with the unique
        # (recipe_id, step_number) constraint.
        await session.flush()

        # Create the new steps.
        for step_data in data.steps:

            step = RecipeStep(
                recipe_id=recipe.id,
                step_number=step_data.step_number,
                instruction=step_data.instruction,
            )

            session.add(step)

    # -------------------------------------------------
    # Commit transaction
    # -------------------------------------------------

    await session.commit()

    # -------------------------------------------------
    # Reload recipe with steps
    # -------------------------------------------------

    result = await session.execute(
        select(Recipe)
        .options(
            selectinload(
                Recipe.recipe_steps
            )
        )
        .where(
            Recipe.id == recipe.id
        )
    )

    recipe = result.scalar_one()

    return recipe


# =================================================
# DELETE RECIPE
# =================================================


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a recipe.

    Only the owner can delete the recipe.

    Associated recipe steps are deleted through
    the Recipe -> RecipeStep cascade relationship.
    """

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

    # -------------------------------------------------
    # Authorization
    # -------------------------------------------------

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own recipes",
        )

    await session.delete(recipe)

    await session.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# =================================================
# RECIPE INGREDIENTS
# =================================================


@router.post(
    "/{recipe_id}/ingredients",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_ingredient_to_recipe(
    recipe_id: int,
    data: RecipeIngredientCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # =================================================
    # GET RECIPE
    # =================================================

    result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.owner_id == current_user.id,
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # =================================================
    # GET INGREDIENT
    # =================================================

    result = await session.execute(
        select(Ingredient).where(
            Ingredient.id == data.ingredient_id
        )
    )

    ingredient = result.scalar_one_or_none()

    if ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found",
        )

    # =================================================
    # CHECK FOR DUPLICATE INGREDIENT
    # =================================================

    result = await session.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.ingredient_id == data.ingredient_id,
        )
    )

    existing = result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingredient already exists in this recipe",
        )

    # =================================================
    # CREATE RECIPE INGREDIENT
    # =================================================

    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=data.ingredient_id,
        amount=data.amount,
        unit=data.unit,
        preparation=data.preparation,
    )

    session.add(recipe_ingredient)

    await session.commit()

    # =================================================
    # RELOAD WITH INGREDIENT RELATIONSHIP
    # =================================================

    result = await session.execute(
        select(RecipeIngredient)
        .options(
            selectinload(RecipeIngredient.ingredient)
        )
        .where(
            RecipeIngredient.id == recipe_ingredient.id
        )
    )

    recipe_ingredient = result.scalar_one()

    return recipe_ingredient

@router.get(
    "/{recipe_id}/ingredients",
    response_model=list[RecipeIngredientResponse],
)
async def get_recipe_ingredients(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get ingredients belonging to a recipe.

    Public recipes can be viewed.

    Private recipes can only be viewed
    by their owner.
    """

    recipe_result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # -------------------------------------------------
    # Authorization for private recipe
    # -------------------------------------------------

    if (
        not recipe.is_public
        and recipe.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this recipe",
        )

    # -------------------------------------------------
    # Load ingredients
    # -------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.recipe_id == recipe_id
        )
        .order_by(
            RecipeIngredient.id.asc()
        )
    )

    return result.scalars().all()


@router.put(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
)
async def update_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    data: RecipeIngredientUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Update an ingredient relationship.

    Only the recipe owner can update it.
    """

    # -------------------------------------------------
    # Find recipe
    # -------------------------------------------------

    recipe_result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # -------------------------------------------------
    # Authorization
    # -------------------------------------------------

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own recipes",
        )

    # -------------------------------------------------
    # Find recipe ingredient
    # -------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.id
            == recipe_ingredient_id,
            RecipeIngredient.recipe_id
            == recipe_id,
        )
    )

    recipe_ingredient = result.scalar_one_or_none()

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    # -------------------------------------------------
    # Update supplied fields
    # -------------------------------------------------

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            recipe_ingredient,
            field,
            value,
        )

    await session.commit()

    await session.refresh(
        recipe_ingredient
    )

    return recipe_ingredient


@router.delete(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an ingredient from a recipe.

    Only the recipe owner can delete it.
    """

    # -------------------------------------------------
    # Find recipe
    # -------------------------------------------------

    recipe_result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # -------------------------------------------------
    # Authorization
    # -------------------------------------------------

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own recipes",
        )

    # -------------------------------------------------
    # Find relationship
    # -------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.id
            == recipe_ingredient_id,
            RecipeIngredient.recipe_id
            == recipe_id,
        )
    )

    recipe_ingredient = result.scalar_one_or_none()

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    await session.delete(
        recipe_ingredient
    )

    await session.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

