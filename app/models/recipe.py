from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.recipe_ingredient import RecipeIngredient
    from app.models.recipe_step import RecipeStep


class Recipe(Base):

    __tablename__ = "recipes"

    # =================================================
    # PRIMARY KEY
    # =================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # =================================================
    # BASIC RECIPE INFORMATION
    # =================================================

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =================================================
    # CATEGORY
    # =================================================

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )

    # =================================================
    # OWNER
    # =================================================

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # =================================================
    # VISIBILITY
    # =================================================

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
        index=True,
    )

    # =================================================
    # PREPARATION TIME
    # =================================================

    prep_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
    )

    # =================================================
    # COOKING TIME
    # =================================================

    cook_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
    )

    # =================================================
    # CREATED AT
    # =================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =================================================
    # CATEGORY RELATIONSHIP
    # =================================================

    category: Mapped[
        "Category | None"
    ] = relationship(
        back_populates="recipes",
    )

    # =================================================
    # OWNER RELATIONSHIP
    # =================================================

    owner: Mapped["User"] = relationship(
        back_populates="recipes",
    )

    # =================================================
    # INGREDIENT RELATIONSHIP
    # =================================================

    recipe_ingredients: Mapped[
        list["RecipeIngredient"]
    ] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    # =================================================
    # RECIPE STEPS RELATIONSHIP
    # =================================================

    recipe_steps: Mapped[
        list["RecipeStep"]
    ] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeStep.step_number",
    )