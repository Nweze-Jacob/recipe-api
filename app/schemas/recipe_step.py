from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class RecipeStepCreate(BaseModel):
    step_number: int = Field(
        gt=0
    )

    instruction: str = Field(
        min_length=1
    )


class RecipeStepUpdate(BaseModel):
    step_number: int = Field(
        gt=0
    )

    instruction: str = Field(
        min_length=1
    )


class RecipeStepResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    recipe_id: int
    step_number: int
    instruction: str