from pydantic import BaseModel, ConfigDict, Field


class IngredientCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    amount: float | None = Field(
        default=None,
        ge=0,
    )

    unit: str = Field(
        min_length=1,
        max_length=50,
    )

    preparation: str | None = Field(
        default=None,
        max_length=255,
    )


class IngredientResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str


class RecipeIngredientCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    amount: float | None = Field(
        default=None,
        ge=0,
    )

    unit: str = Field(
        min_length=1,
        max_length=50,
    )

    preparation: str | None = Field(
        default=None,
        max_length=255,
    )


class RecipeIngredientUpdate(BaseModel):
    amount: float | None = Field(
        default=None,
        ge=0,
    )

    unit: str = Field(
        min_length=1,
        max_length=50,
    )

    preparation: str | None = Field(
        default=None,
        max_length=255,
    )


class RecipeIngredientResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    recipe_id: int
    ingredient_id: int
    amount: float | None
    unit: str
    preparation: str | None
    ingredient: IngredientResponse