from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_session
from app.models.ingredient import Ingredient
from app.models.user import User
from app.schemas.ingredient import (
    IngredientCreate,
    IngredientResponse,
)


router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"],
)


# =================================================
# CREATE INGREDIENT
# =================================================

@router.post(
    "",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ingredient(
    data: IngredientCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    result = await session.execute(
        select(Ingredient).where(
            Ingredient.name == data.name
        )
    )

    existing = result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingredient already exists",
        )

    ingredient = Ingredient(
        name=data.name,
    )

    session.add(ingredient)

    await session.commit()
    await session.refresh(ingredient)

    return ingredient
