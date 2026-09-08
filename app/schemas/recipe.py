from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =================================================
# RECIPE STEP NESTED SCHEMA
# =================================================

class RecipeStepInput(BaseModel):
    step_number: int = Field(
        gt=0,
        description="The position of this instruction in the recipe",
    )

    instruction: str = Field(
        min_length=1,
        description="Instruction for this recipe step",
    )


# =================================================
# CREATE RECIPE
# =================================================

class RecipeCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    category_id: int | None = None

    is_public: bool = True

    prep_minutes: int = Field(
        default=0,
        ge=0,
        description="Preparation time in minutes",
    )

    cook_minutes: int = Field(
        default=0,
        ge=0,
        description="Cooking time in minutes",
    )

    steps: list[RecipeStepInput] = Field(
        default_factory=list,
        description="Ordered cooking instructions",
    )


# =================================================
# UPDATE RECIPE
# =================================================

class RecipeUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    category_id: int | None = None

    is_public: bool | None = None

    prep_minutes: int | None = Field(
        default=None,
        ge=0,
        description="Preparation time in minutes",
    )

    cook_minutes: int | None = Field(
        default=None,
        ge=0,
        description="Cooking time in minutes",
    )

    steps: list[RecipeStepInput] | None = Field(
        default=None,
        description="Replace the recipe's ordered cooking instructions",
    )


# =================================================
# RECIPE STEP RESPONSE
# =================================================

class RecipeStepResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    recipe_id: int

    step_number: int

    instruction: str


# =================================================
# RECIPE RESPONSE
# =================================================

class RecipeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    name: str

    description: str | None

    category_id: int | None

    owner_id: int

    is_public: bool

    prep_minutes: int

    cook_minutes: int

    created_at: datetime

    steps: list[RecipeStepResponse] = Field(
        default_factory=list,
    )