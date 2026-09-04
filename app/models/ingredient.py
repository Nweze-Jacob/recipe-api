from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.recipe_ingredient import RecipeIngredient


class Ingredient(Base):
    __tablename__ = "ingredients"

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="uq_ingredients_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    recipe_ingredients: Mapped[
        list["RecipeIngredient"]
    ] = relationship(
        back_populates="ingredient",
    )