from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, constr

id_max_40 = constr(min_length=1, max_length=40, strip_whitespace=True)
non_empty_string = constr(min_length=1, strip_whitespace=True)


class CreateCategoryDTO(BaseModel):
    title: non_empty_string = Field(...)
    description: Optional[str] = Field(None)


class UpdateCategoryDTO(BaseModel):
    category_id: id_max_40 = Field(...)
    title: Optional[non_empty_string] = Field(None)
    description: Optional[str] = Field(None)


class CategoryResponseDTO(BaseModel):
    category_id: str = Field(...)
    title: str = Field(...)
    description: Optional[str] = Field(None)
    created_by: str = Field(...)
    created_at: datetime = Field(...)
    updated_by: Optional[str] = Field(None)
    updated_at: Optional[datetime] = Field(None)
    version: int = Field(...)

    # pyrefly: ignore [bad-assignment]
    model_config = ConfigDict(from_attributes=True)
