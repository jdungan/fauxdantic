from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

import pytest
from pydantic import UUID4, BaseModel

from fauxdantic import faux, faux_dict


class SimpleUser(BaseModel):
    name: str
    age: int


def test_faux_simple():
    user = faux(SimpleUser)
    assert isinstance(user, SimpleUser)
    assert isinstance(user.name, str)
    assert isinstance(user.age, int)


def test_faux_simple_with_custom_values():
    custom_name = "John Doe"
    custom_age = 30
    user = faux(SimpleUser, name=custom_name, age=custom_age)
    assert user.name == custom_name
    assert user.age == custom_age


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


def test_faux_basic():
    user = faux(User)
    assert isinstance(user, User)
    assert isinstance(user.name, str)
    assert isinstance(user.age, int)
    assert isinstance(user.email, str)
    assert isinstance(user.is_active, bool)
    assert isinstance(user.role, UserRole)
    assert isinstance(user.address, Address)
    assert isinstance(user.tags, list)
    assert all(isinstance(tag, str) for tag in user.tags)
    assert isinstance(user.preferences, dict)
    assert all(
        isinstance(k, str) and isinstance(v, str) for k, v in user.preferences.items()
    )
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.user_id, UUID)
    assert user.optional_field is None or isinstance(user.optional_field, str)


def test_faux_with_custom_values():
    custom_name = "John Doe"
    custom_age = 30
    user = faux(User, name=custom_name, age=custom_age)
    assert user.name == custom_name
    assert user.age == custom_age
    assert isinstance(user.email, str)  # Other fields should still be fake


def test_faux_dict():
    model_dict = faux_dict(User)
    assert isinstance(model_dict, dict)
    assert "name" in model_dict
    assert "age" in model_dict
    assert "email" in model_dict
    assert "is_active" in model_dict
    assert "role" in model_dict
    assert "address" in model_dict
    assert "tags" in model_dict
    assert "preferences" in model_dict
    assert "created_at" in model_dict
    assert "user_id" in model_dict
    assert "optional_field" in model_dict


def test_faux_dict_with_custom_values():
    custom_values = {"name": "John Doe", "age": 30}
    model_dict = faux_dict(User, **custom_values)
    assert model_dict["name"] == "John Doe"
    assert model_dict["age"] == 30
    assert isinstance(model_dict["email"], str)  # Other fields should still be fake
