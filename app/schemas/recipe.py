from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    category_id: int | None = None

    is_public: bool = True


class RecipeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    category_id: int | None = None

    is_public: bool | None = None


class RecipeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    description: str | None
    category_id: int | None
    owner_id: int
    is_public: bool
    created_at: datetime