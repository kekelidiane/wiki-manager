from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, func


class AuditMixin(SQLModel):
    __abstract__ = True
    created_by: str = Field(max_length=55, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )
    updated_by: Optional[str] = Field(default=None, max_length=55, nullable=True)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"server_default": func.now()},
        nullable=True,
    )
    version: int = Field(default=1, nullable=False)
    id: Optional[int] = Field(default=None, primary_key=True, index=True, exclude=True)