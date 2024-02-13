"""Pydantic schemas for user model."""

from pydantic import BaseModel, Field, SecretStr, validator
from fastapi import Query, File, UploadFile
from typing import Optional, List, Literal, Union
from app.models.user_models import UserRole
from fastapi.exceptions import RequestValidationError
from app.errors import E


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


def validate_user_pass(secret_value):
    value = secret_value.get_secret_value()
    if any(x.isupper() for x in value) and any(x.islower() for x in value) and any(x.isdigit() for x in value):
        return secret_value
    
    raise RequestValidationError({"loc": ["query", "user_pass"], "input": value,
                                    "type": "too_easy", "msg": E.USER_PASS_EASY})


class UserRegisterSchema(BaseModel):
    """Pydantic schema for user registration request."""

    user_login: str = Query(..., min_length=2, max_length=40)
    user_pass: SecretStr = Query(..., min_length=6)
    first_name: str = Query(..., min_length=2, max_length=40)
    last_name: str = Query(..., min_length=2, max_length=40)

    @validator("user_pass")
    def user_pass_validator(cls, secret_value):
        return validate_user_pass(secret_value)


class UserLoginSchema(BaseModel):
    """Pydantic schema for user login request."""

    user_login: str
    user_pass: SecretStr


class TokenSelectSchema(BaseModel):
    """Pydantic schema for token selection request."""

    user_login: str
    user_totp: str = Query(..., min_length=6, max_length=6)
    exp: Optional[int] = None


class UsersListSchema(BaseModel):
    """Pydantic schema for users list request."""

    user_role__eq: Optional[UserRole] = None
    user_login__eq: Optional[str] = None
    full_name__ilike: Optional[str] = None
    offset: int = 0
    limit: int = Query(..., ge=1, le=200)
    order_by: Literal["id", "created_date", "updated_date", "user_login", "first_name", "last_name"] = "id"
    order: Literal["asc", "desc"] = "desc"

class UserUpdateSchema(BaseModel):
    """Pydantic schema for user updation request."""

    first_name: str = Query(..., min_length=2, max_length=40)
    last_name: str = Query(..., min_length=2, max_length=40)
    user_summary: Optional[str] = Query(default=None, max_length=512)


class PassUpdateSchema(BaseModel):

    user_pass: SecretStr = Query(..., min_length=6)
    user_pass_new: SecretStr = Query(..., min_length=6)

    @validator("user_pass_new")
    def user_pass_new_validator(cls, secret_value):
        return validate_user_pass(secret_value)


class RoleUpdateSchema(BaseModel):
    """Pydantic schema for role updation request."""

    user_role: UserRole
