from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Literal, Union
from uuid import UUID

import pytest
from pydantic import UUID4, BaseModel, Field

from fauxdantic import faux, faux_dict


class SimpleUser(BaseModel):
    name: str
    age: int


def test_faux_simple() -> None:
    user = faux(SimpleUser)
    assert isinstance(user, SimpleUser)
    assert isinstance(user.name, str)
    assert isinstance(user.age, int)


def test_faux_simple_with_custom_values() -> None:
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


def test_faux_basic() -> None:
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


def test_faux_with_custom_values() -> None:
    custom_name = "John Doe"
    custom_age = 30
    user = faux(User, name=custom_name, age=custom_age)
    assert user.name == custom_name
    assert user.age == custom_age
    assert isinstance(user.email, str)  # Other fields should still be fake


def test_faux_dict() -> None:
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


def test_faux_dict_with_custom_values() -> None:
    custom_values = {"name": "John Doe", "age": 30}
    model_dict = faux_dict(User, **custom_values)
    assert model_dict["name"] == "John Doe"
    assert model_dict["age"] == 30
    assert isinstance(model_dict["email"], str)  # Other fields should still be fake


# New constraint-aware tests


class ConstrainedStringModel(BaseModel):
    short_string: str = Field(..., min_length=5, max_length=10)
    long_string: str = Field(..., min_length=20, max_length=100)
    email_field: str = Field(..., max_length=50)
    description_field: str = Field(..., max_length=200)


def test_string_length_constraints() -> None:
    """Test that string fields respect min_length and max_length constraints"""
    for _ in range(10):  # Test multiple times to ensure consistency
        model = faux(ConstrainedStringModel)

        assert 5 <= len(model.short_string) <= 10
        assert 20 <= len(model.long_string) <= 100
        assert len(model.email_field) <= 50
        assert len(model.description_field) <= 200

        # Email field should contain '@' when name contains 'email'
        assert "@" in model.email_field


class ConstrainedNumericModel(BaseModel):
    age: int = Field(..., ge=18, le=65)
    percentage: float = Field(..., ge=0.0, le=100.0)
    score: int = Field(..., gt=0, lt=1000)
    crop_year: int = Field(..., ge=1900, le=2100)


def test_numeric_constraints() -> None:
    """Test that numeric fields respect range constraints"""
    for _ in range(10):  # Test multiple times to ensure consistency
        model = faux(ConstrainedNumericModel)

        assert 18 <= model.age <= 65
        assert 0.0 <= model.percentage <= 100.0
        assert 1 <= model.score <= 999
        assert 1900 <= model.crop_year <= 2100


class LiteralModel(BaseModel):
    rep: Literal[1, 2, 3, 4]
    status: Literal["active", "inactive", "pending"]
    priority: Literal["low", "medium", "high"]


def test_literal_constraints() -> None:
    """Test that Literal fields only generate valid values"""
    for _ in range(20):  # Test multiple times to ensure all values can be generated
        model = faux(LiteralModel)

        assert model.rep in [1, 2, 3, 4]
        assert model.status in ["active", "inactive", "pending"]
        assert model.priority in ["low", "medium", "high"]


class ComplexEnum(Enum):
    VALUE_A = "value_a"
    VALUE_B = "value_b"
    VALUE_C = "value_c"
    VALUE_D = "value_d"
    VALUE_E = "value_e"


class EnumModel(BaseModel):
    simple_enum: UserRole
    complex_enum: ComplexEnum


def test_enum_handling() -> None:
    """Test that enum fields generate valid enum values"""
    for _ in range(10):
        model = faux(EnumModel)

        assert isinstance(model.simple_enum, UserRole)
        assert model.simple_enum in [UserRole.ADMIN, UserRole.USER, UserRole.GUEST]

        assert isinstance(model.complex_enum, ComplexEnum)
        assert model.complex_enum in list(ComplexEnum)


class YearFieldModel(BaseModel):
    crop_year: int
    birth_year: int = Field(..., ge=1900, le=2010)
    regular_number: int


def test_year_field_heuristics() -> None:
    """Test that year fields generate reasonable values"""
    current_year = datetime.now().year

    for _ in range(10):
        model = faux(YearFieldModel)

        # crop_year should be reasonable (using heuristics)
        assert 1900 <= model.crop_year <= current_year + 10

        # birth_year should respect explicit constraints
        assert 1900 <= model.birth_year <= 2010

        # regular_number should use default range
        assert 0 <= model.regular_number <= 100


# Complex model test based on the user's example
from enum import Enum


class Variety(str, Enum):
    ATLANTIC = "Atlantic"
    CLEARWATER = "Clearwater"
    FL_1833 = "FL 1833"
    FL_2312 = "FL 2312"
    HERMES = "Hermes"


class TrialPlotCreate(BaseModel):
    check: Union[bool, str, None] = None
    crop: str = Field(..., max_length=50)
    crop_year: Union[int, str] = Field(...)
    farm_name: Union[str, None] = Field(None, max_length=50)
    harvest: str = Field(..., min_length=1, max_length=20)
    location_uuid: UUID
    plot_id: Union[str, None] = Field(None, max_length=20)
    plot_map_number: str = Field(..., min_length=1, max_length=20)
    plot_range: Union[int, None] = None
    plot_row: Union[int, None] = None
    rd_number: Union[str, None] = Field(None, max_length=20)
    rep: Union[Literal[1, 2, 3, 4], None] = None
    rh_code: Union[str, None] = Field(None, max_length=20)
    status: Union[str, None] = Field(None, max_length=50)
    trial_name: str
    trial_type: Union[str, None] = Field(None, max_length=20)
    variety: str = Field(..., max_length=50)


def test_complex_model_constraints() -> None:
    """Test the complex TrialPlotCreate model with various constraints"""
    for _ in range(5):  # Test multiple generations
        model = faux(TrialPlotCreate)

        # String length constraints
        assert len(model.crop) <= 50
        assert 1 <= len(model.harvest) <= 20
        assert 1 <= len(model.plot_map_number) <= 20
        assert len(model.variety) <= 50

        if model.farm_name is not None:
            assert len(model.farm_name) <= 50
        if model.plot_id is not None:
            assert len(model.plot_id) <= 20
        if model.rd_number is not None:
            assert len(model.rd_number) <= 20
        if model.rh_code is not None:
            assert len(model.rh_code) <= 20
        if model.status is not None:
            assert len(model.status) <= 50
        if model.trial_type is not None:
            assert len(model.trial_type) <= 20

        # Literal constraints
        if model.rep is not None:
            assert model.rep in [1, 2, 3, 4]

        # Type constraints
        assert isinstance(model.location_uuid, UUID)
        assert isinstance(model.trial_name, str)
        assert isinstance(model.crop_year, (int, str))


def test_constraint_extraction() -> None:
    """Test that constraint extraction works correctly"""
    from fauxdantic.core import _extract_field_constraints
    from pydantic import Field

    # Test string constraints
    field_info = Field(min_length=5, max_length=20)
    constraints = _extract_field_constraints(field_info)
    assert constraints["min_length"] == 5
    assert constraints["max_length"] == 20

    # Test numeric constraints
    field_info = Field(ge=10, le=100)
    constraints = _extract_field_constraints(field_info)
    assert constraints["min_value"] == 10
    assert constraints["max_value"] == 100

    # Test gt/lt constraints
    field_info = Field(gt=0, lt=50)
    constraints = _extract_field_constraints(field_info)
    assert constraints["min_value"] == 1
    assert constraints["max_value"] == 49


def test_unique_string_functionality() -> None:
    """Test the new unique string functionality"""

    class MyBus(BaseModel):
        route_number: Optional[str] = Field(None, max_length=20)

    # Test unique string generation
    bus1 = faux(MyBus, route_number="SW_unique")
    bus2 = faux(MyBus, route_number="SW_unique")
    bus3 = faux(MyBus, route_number="ROUTE_unique")

    # Check that values are unique and follow the expected pattern
    assert bus1.route_number.startswith("SW_")
    assert bus2.route_number.startswith("SW_")
    assert bus3.route_number.startswith("ROUTE_")
    assert bus1.route_number != bus2.route_number
    assert bus1.route_number != bus3.route_number
    assert bus2.route_number != bus3.route_number

    # Test that regular string generation still works
    bus4 = faux(MyBus)
    assert bus4.route_number is None or isinstance(bus4.route_number, str)

    # Test with different patterns
    bus5 = faux(MyBus, route_number="EXPRESS_unique")
    bus6 = faux(MyBus, route_number="EXPRESS_unique")

    assert bus5.route_number.startswith("EXPRESS_")
    assert bus6.route_number.startswith("EXPRESS_")
    assert bus5.route_number != bus6.route_number

    # Test with constraints - very long pattern should be truncated
    bus7 = faux(MyBus, route_number="VERY_LONG_ROUTE_NAME_unique")
    assert len(bus7.route_number) <= 20
    # The pattern is too long, so it gets truncated to just the base pattern
    assert bus7.route_number == "VERY_LONG_ROUTE_NAME"
