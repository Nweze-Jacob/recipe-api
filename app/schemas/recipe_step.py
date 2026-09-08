from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =================================================
# CREATE RECIPE STEP
# =================================================

class RecipeStepCreate(BaseModel):

    step_number: int = Field(
        gt=0,
        description="The position of this instruction in the recipe",
    )

    instruction: str = Field(
        min_length=1,
        description="Instruction for this recipe step",
    )


# =================================================
# UPDATE RECIPE STEP
# =================================================

class RecipeStepUpdate(BaseModel):

    step_number: int | None = Field(
        default=None,
        gt=0,
        description="The new position of this instruction",
    )

    instruction: str | None = Field(
        default=None,
        min_length=1,
        description="The new instruction",
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