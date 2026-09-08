from pydantic import BaseModel, ConfigDict, Field
# ==================================================
# CREATE CATEGORY
# ==================================================

class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )
# ==================================================
# UPDATE CATEGORY
# ==================================================

class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )


# ==================================================
# CATEGORY RESPONSE
# ==================================================

class CategoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
