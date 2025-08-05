from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional, Union
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
    from pydantic import Field

    from fauxdantic.core import _extract_field_constraints

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
    bus1 = faux(MyBus, route_number="SW<unique>")
    bus2 = faux(MyBus, route_number="SW<unique>")
    bus3 = faux(MyBus, route_number="ROUTE<unique>")

    # Check that values are unique and follow the expected pattern
    assert bus1.route_number.startswith("SW")
    assert bus2.route_number.startswith("SW")
    assert bus3.route_number.startswith("ROUTE")
    assert bus1.route_number != bus2.route_number
    assert bus1.route_number != bus3.route_number
    assert bus2.route_number != bus3.route_number

    # Test that regular string generation still works
    bus4 = faux(MyBus)
    assert bus4.route_number is None or isinstance(bus4.route_number, str)

    # Test with different patterns
    bus5 = faux(MyBus, route_number="EXPRESS<unique>")
    bus6 = faux(MyBus, route_number="EXPRESS<unique>")

    assert bus5.route_number.startswith("EXPRESS")
    assert bus6.route_number.startswith("EXPRESS")
    assert bus5.route_number != bus6.route_number

    # Test with constraints - very long pattern should be truncated
    bus7 = faux(MyBus, route_number="VERY_LONG_ROUTE_NAME<unique>")
    assert len(bus7.route_number) <= 20
    # The pattern is too long, so it gets truncated to just the base pattern
    assert bus7.route_number == "VERY_LONG_ROUTE_NAME"


class ModelWithDatetimeUnions(BaseModel):
    """Model to test datetime prioritization in Union types"""

    # str comes first in union - should still generate datetime
    start_date: Union[str, datetime, None] = None
    # datetime comes first in union - should generate datetime
    end_date: Union[datetime, str, None] = None
    # Optional datetime - should generate datetime
    completion_date: Optional[Union[str, datetime]] = None
    # Plain string field for comparison
    description: str = "test"


def test_datetime_prioritization_in_unions() -> None:
    """Test that datetime types are prioritized over str in Union types"""
    data = faux_dict(ModelWithDatetimeUnions)

    # All datetime fields should return actual datetime objects, not strings
    assert isinstance(
        data["start_date"], datetime
    ), f"start_date should be datetime, got {type(data['start_date'])}: {data['start_date']}"
    assert isinstance(
        data["end_date"], datetime
    ), f"end_date should be datetime, got {type(data['end_date'])}: {data['end_date']}"
    assert isinstance(
        data["completion_date"], datetime
    ), f"completion_date should be datetime, got {type(data['completion_date'])}: {data['completion_date']}"

    # String field should still be string
    assert isinstance(
        data["description"], str
    ), f"description should be str, got {type(data['description'])}: {data['description']}"

    # Generate multiple instances to ensure consistency
    for _ in range(5):
        data = faux_dict(ModelWithDatetimeUnions)
        assert isinstance(data["start_date"], datetime)
        assert isinstance(data["end_date"], datetime)
        assert isinstance(data["completion_date"], datetime)


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComprehensiveUnionModel(BaseModel):
    """Model to test comprehensive Union type prioritization"""

    # Priority 1: Literal types (most specific)
    literal_over_str: Union[str, Literal["A", "B", "C"]] = "A"
    str_over_literal: Union[Literal["X", "Y"], str] = "X"  # Should pick Literal

    # Priority 2: Enum types (domain-specific values)
    enum_over_str: Union[str, Priority] = Priority.HIGH
    str_over_enum: Union[Priority, str] = Priority.HIGH  # Should pick Enum

    # Priority 3: datetime/date types (already tested above, but included for completeness)
    datetime_over_str: Union[str, datetime] = None

    # Priority 4: bool types (more specific than str)
    bool_over_str: Union[str, bool] = True
    str_over_bool: Union[bool, str] = True  # Should pick bool

    # Priority 5: Numeric types (more specific than str)
    int_over_str: Union[str, int] = 42
    str_over_int: Union[int, str] = 42  # Should pick int
    float_over_str: Union[str, float] = 3.14
    str_over_float: Union[float, str] = 3.14  # Should pick float

    # Priority 6: UUID types (structured data)
    uuid_over_str: Union[str, UUID] = None
    str_over_uuid: Union[UUID, str] = None  # Should pick UUID

    # Complex combinations
    literal_over_everything: Union[str, int, bool, Literal["priority"]] = (
        "priority"  # Should pick Literal
    )
    enum_over_most: Union[str, int, bool, Priority] = Priority.LOW  # Should pick Enum
    bool_over_numeric_and_str: Union[str, int, float, bool] = True  # Should pick bool
    int_over_str_only: Union[str, int] = 123  # Should pick int


def test_comprehensive_union_prioritization() -> None:
    """Test comprehensive Union type prioritization across all scenarios"""
    data = faux_dict(ComprehensiveUnionModel)

    # Priority 1: Literal types should be chosen over str
    assert data["literal_over_str"] in [
        "A",
        "B",
        "C",
    ], f"literal_over_str should be Literal value, got: {data['literal_over_str']}"
    assert data["str_over_literal"] in [
        "X",
        "Y",
    ], f"str_over_literal should be Literal value, got: {data['str_over_literal']}"

    # Priority 2: Enum types should be chosen over str
    assert isinstance(
        data["enum_over_str"], Priority
    ), f"enum_over_str should be Priority enum, got {type(data['enum_over_str'])}: {data['enum_over_str']}"
    assert isinstance(
        data["str_over_enum"], Priority
    ), f"str_over_enum should be Priority enum, got {type(data['str_over_enum'])}: {data['str_over_enum']}"

    # Priority 3: datetime types should be chosen over str
    assert isinstance(
        data["datetime_over_str"], datetime
    ), f"datetime_over_str should be datetime, got {type(data['datetime_over_str'])}: {data['datetime_over_str']}"

    # Priority 4: bool types should be chosen over str
    assert isinstance(
        data["bool_over_str"], bool
    ), f"bool_over_str should be bool, got {type(data['bool_over_str'])}: {data['bool_over_str']}"
    assert isinstance(
        data["str_over_bool"], bool
    ), f"str_over_bool should be bool, got {type(data['str_over_bool'])}: {data['str_over_bool']}"

    # Priority 5: Numeric types should be chosen over str
    assert isinstance(
        data["int_over_str"], int
    ), f"int_over_str should be int, got {type(data['int_over_str'])}: {data['int_over_str']}"
    assert isinstance(
        data["str_over_int"], int
    ), f"str_over_int should be int, got {type(data['str_over_int'])}: {data['str_over_int']}"
    assert isinstance(
        data["float_over_str"], float
    ), f"float_over_str should be float, got {type(data['float_over_str'])}: {data['float_over_str']}"
    assert isinstance(
        data["str_over_float"], float
    ), f"str_over_float should be float, got {type(data['str_over_float'])}: {data['str_over_float']}"

    # Priority 6: UUID types should be chosen over str
    assert isinstance(
        data["uuid_over_str"], UUID
    ), f"uuid_over_str should be UUID, got {type(data['uuid_over_str'])}: {data['uuid_over_str']}"
    assert isinstance(
        data["str_over_uuid"], UUID
    ), f"str_over_uuid should be UUID, got {type(data['str_over_uuid'])}: {data['str_over_uuid']}"

    # Complex combinations - test prioritization hierarchy
    assert (
        data["literal_over_everything"] == "priority"
    ), f"literal_over_everything should be 'priority', got: {data['literal_over_everything']}"
    assert isinstance(
        data["enum_over_most"], Priority
    ), f"enum_over_most should be Priority enum, got {type(data['enum_over_most'])}: {data['enum_over_most']}"
    assert isinstance(
        data["bool_over_numeric_and_str"], bool
    ), f"bool_over_numeric_and_str should be bool, got {type(data['bool_over_numeric_and_str'])}: {data['bool_over_numeric_and_str']}"
    assert isinstance(
        data["int_over_str_only"], int
    ), f"int_over_str_only should be int, got {type(data['int_over_str_only'])}: {data['int_over_str_only']}"

    # Test consistency across multiple generations
    for _ in range(5):
        data = faux_dict(ComprehensiveUnionModel)

        # Key assertions for priority order
        assert data["literal_over_str"] in ["A", "B", "C"]
        assert data["str_over_literal"] in ["X", "Y"]
        assert isinstance(data["enum_over_str"], Priority)
        assert isinstance(data["str_over_enum"], Priority)
        assert isinstance(data["bool_over_str"], bool)
        assert isinstance(data["str_over_bool"], bool)
        assert isinstance(data["int_over_str"], int)
        assert isinstance(data["str_over_int"], int)
        assert isinstance(data["float_over_str"], float)
        assert isinstance(data["str_over_float"], float)
        assert isinstance(data["uuid_over_str"], UUID)
        assert isinstance(data["str_over_uuid"], UUID)


class NewUnionSyntaxModel(BaseModel):
    """Model to test the new Python 3.10+ union operator syntax (|)"""

    # Test the new union operator syntax - using Union for Python 3.9 compatibility
    datetime_or_none: Union[datetime, None] = None
    none_or_datetime: Union[None, datetime] = None
    str_or_datetime: Union[str, datetime] = None
    datetime_or_str: Union[datetime, str] = None
    bool_or_str: Union[bool, str] = True
    int_or_str: Union[int, str] = 42
    float_or_str: Union[float, str] = 3.14


def test_new_union_operator_syntax() -> None:
    """Test that Union types work correctly with our prioritization logic"""
    data = faux_dict(NewUnionSyntaxModel)

    # datetime | None should generate datetime objects, not strings
    assert isinstance(
        data["datetime_or_none"], datetime
    ), f"datetime_or_none should be datetime, got {type(data['datetime_or_none'])}: {data['datetime_or_none']}"
    assert isinstance(
        data["none_or_datetime"], datetime
    ), f"none_or_datetime should be datetime, got {type(data['none_or_datetime'])}: {data['none_or_datetime']}"

    # str | datetime should prioritize datetime
    assert isinstance(
        data["str_or_datetime"], datetime
    ), f"str_or_datetime should be datetime, got {type(data['str_or_datetime'])}: {data['str_or_datetime']}"
    assert isinstance(
        data["datetime_or_str"], datetime
    ), f"datetime_or_str should be datetime, got {type(data['datetime_or_str'])}: {data['datetime_or_str']}"

    # bool | str should prioritize bool
    assert isinstance(
        data["bool_or_str"], bool
    ), f"bool_or_str should be bool, got {type(data['bool_or_str'])}: {data['bool_or_str']}"

    # int | str should prioritize int
    assert isinstance(
        data["int_or_str"], int
    ), f"int_or_str should be int, got {type(data['int_or_str'])}: {data['int_or_str']}"

    # float | str should prioritize float
    assert isinstance(
        data["float_or_str"], float
    ), f"float_or_str should be float, got {type(data['float_or_str'])}: {data['float_or_str']}"

    # Test consistency across multiple generations
    for _ in range(5):
        data = faux_dict(NewUnionSyntaxModel)
        assert isinstance(data["datetime_or_none"], datetime)
        assert isinstance(data["none_or_datetime"], datetime)
        assert isinstance(data["str_or_datetime"], datetime)
        assert isinstance(data["datetime_or_str"], datetime)
        assert isinstance(data["bool_or_str"], bool)
        assert isinstance(data["int_or_str"], int)
        assert isinstance(data["float_or_str"], float)


class Python311PlusModel(BaseModel):
    """Model to test Python 3.11+ typing features"""

    # Test Union with new union operator syntax (Python 3.10+)
    datetime_or_none: datetime | None = None
    str_or_datetime: str | datetime = None
    bool_or_str: bool | str = True


def test_python_311_plus_features() -> None:
    """Test Python 3.11+ typing features and new union operator syntax"""
    data = faux_dict(Python311PlusModel)

    # New union operator syntax should work correctly
    assert isinstance(
        data["datetime_or_none"], datetime
    ), f"datetime_or_none should be datetime, got {type(data['datetime_or_none'])}: {data['datetime_or_none']}"
    assert isinstance(
        data["str_or_datetime"], datetime
    ), f"str_or_datetime should be datetime, got {type(data['str_or_datetime'])}: {data['str_or_datetime']}"
    assert isinstance(
        data["bool_or_str"], bool
    ), f"bool_or_str should be bool, got {type(data['bool_or_str'])}: {data['bool_or_str']}"

    # Test consistency across multiple generations
    for _ in range(3):
        data = faux_dict(Python311PlusModel)
        assert isinstance(data["datetime_or_none"], datetime)
        assert isinstance(data["str_or_datetime"], datetime)
        assert isinstance(data["bool_or_str"], bool)
