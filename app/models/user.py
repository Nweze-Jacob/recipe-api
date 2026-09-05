from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.review import Review


class User(Base):
    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # User information
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Relationships
    recipes: Mapped[list["Recipe"]] = relationship(
        "Recipe",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan"
    )