"""Pydantic schemas for user model."""

from pydantic import BaseModel, Field, SecretStr
from fastapi import Query, File, UploadFile
from typing import Optional, List, Literal
from app.models.user_models import UserRole


class UserSchema(BaseModel):
    """Pydantic schema for user selection response."""

    id: int
    created_date: int
    updated_date: int
    user_role: UserRole
    user_login: str
    first_name: str
    last_name: str
    userpic: Optional[str] = None
    user_summary: Optional[str] = None


class UserRegisterSchema(BaseModel):
    """Pydantic schema for user registration request."""

    user_login: str = Field(Query(..., min_length=2, max_length=40))
    user_pass: SecretStr = Field(Query(..., min_length=6))
    first_name: str = Field(Query(..., min_length=2, max_length=40))
    last_name: str = Field(Query(..., min_length=2, max_length=40))


class UserLoginSchema(BaseModel):
    """Pydantic schema for user login request."""

    user_login: str
    user_pass: SecretStr


class TokenSelectSchema(BaseModel):
    """Pydantic schema for token selection request."""

    user_login: str
    user_totp: str = Field(Query(..., min_length=6, max_length=6))
    exp: Optional[int] = None


class UserSelectSchema(BaseModel):
    """Pydantic schema for user selection request."""

    id: int
