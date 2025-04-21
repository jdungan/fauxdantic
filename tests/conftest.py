from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

import pytest
from pydantic import BaseModel


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Address(BaseModel):
    street: str
    city: str
    zip_code: str


class User(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool
    role: UserRole
    address: Address
    tags: List[str]
    preferences: Dict[str, str]
    created_at: datetime
    user_id: UUID
    optional_field: Optional[str] = None


@pytest.fixture
def user_model():
    return User


@pytest.fixture
def address_model():
    return Address


@pytest.fixture
def user_role_enum():
    return UserRole
