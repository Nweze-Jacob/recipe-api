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

from app.models.category import Category
from app.models.user import User

from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)


# ==================================================
# ROUTER CONFIGURATION
# ==================================================

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


# ==================================================
# CREATE CATEGORY
# ==================================================

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------
    # CHECK IF CATEGORY ALREADY EXISTS
    # --------------------------------------------------

    result = await db.execute(
        select(Category).where(
            Category.name == category_data.name
        )
    )

    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )

    # --------------------------------------------------
    # CREATE CATEGORY
    # --------------------------------------------------

    category = Category(
        name=category_data.name,
    )

    db.add(category)

    # --------------------------------------------------
    # SAVE CATEGORY
    # --------------------------------------------------

    await db.commit()

    await db.refresh(category)

    return category


# ==================================================
# GET ALL CATEGORIES
# ==================================================

@router.get(
    "",
    response_model=list[CategoryResponse],
)
async def list_categories(
    db: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------
    # GET ALL CATEGORIES
    # --------------------------------------------------

    result = await db.execute(
        select(Category)
        .order_by(Category.name.asc())
    )

    categories = result.scalars().all()

    return categories

