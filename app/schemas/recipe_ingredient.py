from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# =================================================
# CREATE RECIPE INGREDIENT
# =================================================

class RecipeIngredientCreate(BaseModel):

    ingredient_id: int = Field(
        gt=0,
    )

    amount: float | None = Field(
        default=None,
        ge=0,
    )

    unit: str | None = Field(
        default=None,
        max_length=50,
    )

    preparation: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("unit")
    @classmethod
    def validate_unit(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

    @field_validator("preparation")
    @classmethod
    def validate_preparation(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value


# =================================================
# UPDATE RECIPE INGREDIENT
# =================================================

class RecipeIngredientUpdate(BaseModel):

    amount: float | None = Field(
        default=None,
        ge=0,
    )

    unit: str | None = Field(
        default=None,
        max_length=50,
    )

    preparation: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("unit")
    @classmethod
    def validate_unit(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

    @field_validator("preparation")
    @classmethod
    def validate_preparation(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value


# =================================================
# RECIPE INGREDIENT RESPONSE
# =================================================

class RecipeIngredientResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    recipe_id: int

    ingredient_id: int

    amount: float | None

    unit: str | None

    preparation: str | None