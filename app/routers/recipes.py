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
from app.core.dependencies import (
    get_current_user,
)
from sqlalchemy.orm import selectinload

from app.database import get_session

from app.models.ingredient import Ingredient
from app.models.category import Category
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.recipe_step import RecipeStep
from app.models.user import User

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


# ==================================================
# CREATE RECIPE
# ==================================================

@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_session),
):
    # ----------------------------------------------
    # CHECK CATEGORY
    # ----------------------------------------------

    if recipe_data.category_id is not None:

        result = await db.execute(
            select(Category).where(
                Category.id
                == recipe_data.category_id
            )
        )

        category = (
            result.scalar_one_or_none()
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    # ----------------------------------------------
    # CREATE RECIPE
    # ----------------------------------------------

    recipe = Recipe(
        name=recipe_data.name,
        description=recipe_data.description,
        category_id=recipe_data.category_id,

        # Authenticated user becomes
        # the owner of the recipe.
        owner_id=current_user.id,

        
        # Save whether the recipe is public
        # or private.
        is_public=recipe_data.is_public,
    )

    # ----------------------------------------------
    # SAVE RECIPE
    # ----------------------------------------------

    db.add(recipe)

    await db.commit()

    await db.refresh(recipe)

    return recipe



@router.get(
    "",
    response_model=list[RecipeResponse],
)
async def list_recipes(
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

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_session
    ),
):
    # =================================================
    # START QUERY
    # =================================================
    # Only return recipes owned by the
    # authenticated user.

    query = select(Recipe).where(
        Recipe.owner_id == current_user.id
    )

    # =================================================
    # SEARCH BY RECIPE NAME
    # =================================================

    if search:
        query = query.where(
            Recipe.name.ilike(
                f"%{search}%"
            )
        )

    # =================================================
    # SEARCH BY CATEGORY
    # =================================================

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

    # =================================================
    # SEARCH BY INGREDIENT
    # =================================================

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

    # =================================================
    # REMOVE DUPLICATE RECIPES
    # =================================================

    query = query.distinct()

    # =================================================
    # SORTING
    # =================================================

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

    # =================================================
    # PAGINATION
    # =================================================

    offset = (page - 1) * limit

    query = query.offset(
        offset
    ).limit(
        limit
    )

    # =================================================
    # EXECUTE QUERY
    # =================================================

    result = await db.execute(query)

    recipes = result.scalars().all()

    return recipes



# =========================================================
# GET PUBLIC RECIPES
# =========================================================

@router.get(
    "/public",
    response_model=list[RecipeResponse],
)
async def get_public_recipes(
    db: AsyncSession = Depends(get_session),
):
    # ----------------------------------------------
    # GET ONLY PUBLIC RECIPES
    # ----------------------------------------------

    result = await db.execute(
        select(Recipe)
        .where(
            Recipe.is_public.is_(True)
        )
        .order_by(
            Recipe.created_at.desc()
        )
    )

    recipes = result.scalars().all()

    return recipes


# =========================================================
# GET MY RECIPES
# =========================================================

@router.get(
    "/mine",
    response_model=list[RecipeResponse],
)
async def get_my_recipes(
    db: AsyncSession = Depends(get_session),

    current_user: User = Depends(
        get_current_user
    ),
):
    # ----------------------------------------------
    # GET RECIPES BELONGING TO CURRENT USER
    # ----------------------------------------------

    result = await db.execute(
        select(Recipe)
        .where(
            Recipe.owner_id == current_user.id
        )
        .order_by(
            Recipe.created_at.desc()
        )
    )

    recipes = result.scalars().all()

    return recipes



@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def get_recipe(
    recipe_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_session
    ),
):
    # -----------------------------------------------------
    # FIND RECIPE
    # -----------------------------------------------------

    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    # -----------------------------------------------------
    # RECIPE NOT FOUND
    # -----------------------------------------------------

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # -----------------------------------------------------
    # PUBLIC RECIPE
    # -----------------------------------------------------
    # Anyone who is authenticated can view
    # a public recipe.

    if recipe.is_public:
        return recipe

    # -----------------------------------------------------
    # PRIVATE RECIPE
    # -----------------------------------------------------
    # Only the owner can view a private recipe.

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this recipe",
        )

    # -----------------------------------------------------
    # OWNER CAN VIEW PRIVATE RECIPE
    # -----------------------------------------------------

    return recipe


# ============================================================
#  UPDATE RECIPE
# ============================================================


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def update_recipe(
    recipe_id: int,

    recipe_data: RecipeUpdate,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_session
    ),
):
    # ----------------------------------------------
    # FIND RECIPE
    # ----------------------------------------------

    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    # ----------------------------------------------
    # RECIPE NOT FOUND
    # ----------------------------------------------

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # ----------------------------------------------
    # AUTHORIZATION / OWNERSHIP CHECK
    # ----------------------------------------------
    # Only the owner of the recipe is allowed
    # to modify it.

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to modify this recipe",
        )

    # ----------------------------------------------
    # VALIDATE CATEGORY
    # ----------------------------------------------

    if recipe_data.category_id is not None:

        result = await db.execute(
            select(Category).where(
                Category.id
                == recipe_data.category_id
            )
        )

        category = (
            result.scalar_one_or_none()
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    # ----------------------------------------------
    # UPDATE NAME
    # ----------------------------------------------

    if recipe_data.name is not None:
        recipe.name = recipe_data.name

    # ----------------------------------------------
    # UPDATE DESCRIPTION
    # ----------------------------------------------

    if recipe_data.description is not None:
        recipe.description = (
            recipe_data.description
        )

    # ----------------------------------------------
    # UPDATE CATEGORY
    # ----------------------------------------------

    if recipe_data.category_id is not None:
        recipe.category_id = (
            recipe_data.category_id
        )

    # ----------------------------------------------
    # UPDATE PUBLIC / PRIVATE STATUS
    # ----------------------------------------------
    # Lesson 37:
    # The owner can change the recipe between
    # public and private.

    if recipe_data.is_public is not None:
        recipe.is_public = (
            recipe_data.is_public
        )

    # ----------------------------------------------
    # SAVE CHANGES
    # ----------------------------------------------

    await db.commit()

    await db.refresh(recipe)

    return recipe



# ============================================================
 #DELETE RECIPE
# ============================================================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: AsyncSession = Depends(
        get_session
    ),
):
    # ----------------------------------------------
    # FIND RECIPE
    # ----------------------------------------------

    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    # ----------------------------------------------
    # RECIPE NOT FOUND
    # ----------------------------------------------

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # ----------------------------------------------
    # AUTHORIZATION / OWNERSHIP CHECK
    # ----------------------------------------------
    # Only the owner of the recipe can delete it.

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this recipe",
        )

    # ----------------------------------------------
    # DELETE RECIPE
    # ----------------------------------------------

    await db.delete(recipe)

    await db.commit()

    # ----------------------------------------------
    # NO CONTENT RESPONSE
    # ----------------------------------------------

    return None



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



