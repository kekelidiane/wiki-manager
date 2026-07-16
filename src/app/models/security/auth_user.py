from typing import List

from sqlmodel import JSON, Field, SQLModel


class AuthenticatedUser(SQLModel, table=True):
    __tablename__ = "authenticated_users"  # type: ignore

    user_id: str = Field(max_length=40, primary_key=True, unique=True, nullable=False)
    username: str = Field(max_length=50, unique=True, nullable=False)
    email: str = Field(max_length=100, unique=True, nullable=False)
    scopes: List[str] = Field(sa_type=JSON, default=list)
    roles: List[str] = Field(sa_type=JSON, default=list)
    groups: List[str] = Field(sa_type=JSON, default=list)

    def has_role(self, role: str) -> bool:
        return role.lower() in [r.lower() for r in self.roles]
