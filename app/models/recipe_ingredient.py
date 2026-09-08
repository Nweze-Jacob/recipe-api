from typing import TYPE_CHECKING

from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.ingredient import Ingredient


class RecipeIngredient(Base):

    __tablename__ = "recipe_ingredients"

    # =================================================
    # PRIMARY KEY
    # =================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =================================================
    # RECIPE
    # =================================================

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey(
            "recipes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =================================================
    # INGREDIENT
    # =================================================

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "ingredients.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =================================================
    # AMOUNT
    # =================================================

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # =================================================
    # UNIT
    # =================================================

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # =================================================
    # PREPARATION
    # =================================================

    preparation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =================================================
    # RECIPE RELATIONSHIP
    # =================================================

    recipe: Mapped["Recipe"] = relationship(
        back_populates="recipe_ingredients",
    )

    # =================================================
    # INGREDIENT RELATIONSHIP
    # =================================================

    ingredient: Mapped["Ingredient"] = relationship(
        back_populates="recipe_ingredients",
    )