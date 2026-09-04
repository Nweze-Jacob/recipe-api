from pydantic import BaseModel, ConfigDict, Field, field_validator


class IngredientCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Ingredient name cannot be empty.")

        return value


class IngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str