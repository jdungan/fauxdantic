from datetime import date, datetime
from uuid import UUID

import pytest
from pydantic import BaseModel

from fauxdantic import faux


class BuiltinTypesModel(BaseModel):
    # Basic types
    string_field: str
    int_field: int
    float_field: float
    bool_field: bool

    # Container types
    dict_field: dict
    list_field: list
    tuple_field: tuple
    set_field: set
    frozenset_field: frozenset

    # Special types
    bytes_field: bytes
    complex_field: complex

    # Date/time types
    datetime_field: datetime
    date_field: date

    # UUID type
    uuid_field: UUID


def test_basic_types() -> None:
    """Test basic built-in types"""
    model = faux(BuiltinTypesModel)

    # Basic types
    assert isinstance(model.string_field, str)
    assert isinstance(model.int_field, int)
    assert isinstance(model.float_field, float)
    assert isinstance(model.bool_field, bool)


def test_container_types() -> None:
    """Test container built-in types"""
    model = faux(BuiltinTypesModel)

    # Container types
    assert isinstance(model.dict_field, dict)
    assert isinstance(model.list_field, list)
    assert isinstance(model.tuple_field, tuple)
    assert isinstance(model.set_field, set)
    assert isinstance(model.frozenset_field, frozenset)

    # Check that containers have reasonable sizes
    assert len(model.dict_field) >= 1
    assert len(model.list_field) >= 1
    assert len(model.tuple_field) >= 1
    assert len(model.set_field) >= 1
    assert len(model.frozenset_field) >= 1


def test_special_types() -> None:
    """Test special built-in types"""
    model = faux(BuiltinTypesModel)

    # Special types
    assert isinstance(model.bytes_field, bytes)
    assert isinstance(model.complex_field, complex)

    # Check reasonable values
    assert len(model.bytes_field) >= 10
    assert isinstance(model.complex_field.real, (int, float))
    assert isinstance(model.complex_field.imag, (int, float))


def test_datetime_types() -> None:
    """Test datetime built-in types"""
    model = faux(BuiltinTypesModel)

    # Date/time types
    assert isinstance(model.datetime_field, datetime)
    assert isinstance(model.date_field, date)


def test_uuid_type() -> None:
    """Test UUID built-in type"""
    model = faux(BuiltinTypesModel)

    # UUID type
    assert isinstance(model.uuid_field, UUID)


def test_all_types_integration() -> None:
    """Test that all types work together in one model"""
    model = faux(BuiltinTypesModel)

    # Verify all fields have the correct types
    assert isinstance(model.string_field, str)
    assert isinstance(model.int_field, int)
    assert isinstance(model.float_field, float)
    assert isinstance(model.bool_field, bool)
    assert isinstance(model.dict_field, dict)
    assert isinstance(model.list_field, list)
    assert isinstance(model.tuple_field, tuple)
    assert isinstance(model.set_field, set)
    assert isinstance(model.frozenset_field, frozenset)
    assert isinstance(model.bytes_field, bytes)
    assert isinstance(model.complex_field, complex)
    assert isinstance(model.datetime_field, datetime)
    assert isinstance(model.date_field, date)
    assert isinstance(model.uuid_field, UUID)


def test_custom_values_with_builtin_types() -> None:
    """Test that custom values work with built-in types"""
    custom_data = {
        "string_field": "custom_string",
        "int_field": 42,
        "float_field": 3.14,
        "bool_field": True,
        "dict_field": {"custom": "value"},
        "list_field": [1, 2, 3],
        "tuple_field": (1, 2, 3),
        "set_field": {1, 2, 3},
        "frozenset_field": frozenset([1, 2, 3]),
        "bytes_field": b"custom_bytes",
        "complex_field": complex(1, 2),
        "datetime_field": datetime(2023, 1, 1),
        "date_field": date(2023, 1, 1),
        "uuid_field": UUID("12345678-1234-5678-1234-567812345678"),
    }

    model = faux(BuiltinTypesModel, **custom_data)

    # Verify custom values are used
    assert model.string_field == "custom_string"
    assert model.int_field == 42
    assert model.float_field == 3.14
    assert model.bool_field is True
    assert model.dict_field == {"custom": "value"}
    assert model.list_field == [1, 2, 3]
    assert model.tuple_field == (1, 2, 3)
    assert model.set_field == {1, 2, 3}
    assert model.frozenset_field == frozenset([1, 2, 3])
    assert model.bytes_field == b"custom_bytes"
    assert model.complex_field == complex(1, 2)
    assert model.datetime_field == datetime(2023, 1, 1)
    assert model.date_field == date(2023, 1, 1)
    assert model.uuid_field == UUID("12345678-1234-5678-1234-567812345678")


if __name__ == "__main__":
    # Run basic test to verify all types work
    test_all_types_integration()
    print("✅ All built-in types are supported!")
