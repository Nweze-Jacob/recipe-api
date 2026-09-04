from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class RecipeStepCreate(BaseModel):
    step_number: int = Field(
        gt=0,
    )

    instruction: str = Field(
        min_length=1,
        max_length=5000,
    )

    @field_validator("instruction")
    @classmethod
    def validate_instruction(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Instruction cannot be empty."
            )

        return value


class RecipeStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int
    step_number: int
    instruction: str