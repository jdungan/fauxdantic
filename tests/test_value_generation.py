"""Tests for value_generation module functionality."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import pytest
from pydantic import UUID4, BaseModel

from fauxdantic.exceptions import GenerationError, UnsupportedTypeError
from fauxdantic.value_generation import _faux_value_internal, faux_value


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class NestedModel(BaseModel):
    value: str


def test_faux_value_basic_types():
    """Test faux_value with basic Python types."""
    # String
    result = faux_value(str, "test_field")
    assert isinstance(result, str)

    # Integer
    result = faux_value(int, "age")
    assert isinstance(result, int)

    # Float
    result = faux_value(float, "price")
    assert isinstance(result, float)

    # Boolean
    result = faux_value(bool, "is_active")
    assert isinstance(result, bool)


def test_faux_value_datetime_types():
    """Test faux_value with datetime types."""
    # Datetime
    result = faux_value(datetime, "created_at")
    assert isinstance(result, datetime)

    # Date
    result = faux_value(date, "birth_date")
    assert isinstance(result, date)


def test_faux_value_uuid_types():
    """Test faux_value with UUID types."""
    # Standard UUID
    result = faux_value(UUID, "id")
    assert isinstance(result, UUID)

    # Pydantic UUID4
    result = faux_value(UUID4, "user_id")
    assert isinstance(result, UUID)


def test_faux_value_enum_types():
    """Test faux_value with enum types."""
    result = faux_value(Status, "status")
    assert isinstance(result, Status)
    assert result in [Status.ACTIVE, Status.INACTIVE]


def test_faux_value_collection_types():
    """Test faux_value with collection types."""
    # List
    result = faux_value(List[str], "tags")
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)
    assert 1 <= len(result) <= 3  # Default collection size range

    # Dict
    result = faux_value(Dict[str, int], "counts")
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())


def test_faux_value_union_types():
    """Test faux_value with Union types."""
    # Union of basic types
    result = faux_value(Union[str, int], "mixed")
    assert isinstance(result, (str, int))

    # Optional (Union with None)
    result = faux_value(Optional[str], "optional_field")
    assert result is None or isinstance(result, str)


def test_faux_value_nested_model():
    """Test faux_value with nested BaseModel."""
    result = faux_value(NestedModel, "nested")
    assert isinstance(result, dict)  # Should return dict, not model instance
    assert "value" in result
    assert isinstance(result["value"], str)


def test_faux_value_builtin_collections():
    """Test faux_value with builtin collection types without parameters."""
    # Plain list
    result = faux_value(list, "items")
    assert isinstance(result, list)

    # Plain dict
    result = faux_value(dict, "data")
    assert isinstance(result, dict)

    # Tuple
    result = faux_value(tuple, "coords")
    assert isinstance(result, tuple)

    # Set
    result = faux_value(set, "unique_items")
    assert isinstance(result, set)

    # Frozenset
    result = faux_value(frozenset, "immutable_items")
    assert isinstance(result, frozenset)


def test_faux_value_special_types():
    """Test faux_value with special types."""
    # Bytes
    result = faux_value(bytes, "binary_data")
    assert isinstance(result, bytes)

    # Complex
    result = faux_value(complex, "complex_number")
    assert isinstance(result, complex)


def test_faux_value_any_type():
    """Test faux_value with Any type (graceful fallback)."""
    result = faux_value(Any, "anything")
    assert isinstance(result, str)  # Should fallback to string


def test_faux_value_none_type():
    """Test faux_value with None type."""
    result = faux_value(None, "null_field")
    assert isinstance(result, str)  # Should fallback to string


def test_faux_value_error_wrapping():
    """Test that faux_value wraps errors appropriately."""

    # Test with unsupported type
    class UnsupportedType:
        pass

    with pytest.raises(UnsupportedTypeError):
        faux_value(UnsupportedType, "unsupported")


def test_faux_value_field_name_context():
    """Test that field names are properly passed through."""

    # This should include field name in any error messages
    class BadType:
        pass

    with pytest.raises(UnsupportedTypeError) as exc_info:
        faux_value(BadType, "my_field")

    assert "my_field" in str(exc_info.value)


def test_internal_faux_value_direct():
    """Test _faux_value_internal directly for edge cases."""
    # Test that internal function works the same for basic types
    result = _faux_value_internal(str, "test")
    assert isinstance(result, str)

    # Test error conditions
    class BadType:
        pass

    with pytest.raises(UnsupportedTypeError):
        _faux_value_internal(BadType, "bad_field")


def test_error_suggestions():
    """Test that appropriate error suggestions are generated."""
    # Test function type suggestion
    from typing import Callable

    with pytest.raises(UnsupportedTypeError) as exc_info:
        faux_value(Callable, "callback")

    error_msg = str(exc_info.value)
    assert "callable" in error_msg.lower() or "function" in error_msg.lower()

    # Test numpy-like suggestion
    class NumpyArray:
        __name__ = "ndarray"
        __module__ = "numpy.core"

    with pytest.raises(UnsupportedTypeError) as exc_info:
        faux_value(NumpyArray, "array")

    error_msg = str(exc_info.value)
    assert "numpy" in error_msg.lower()


def test_complex_nested_types():
    """Test complex nested type combinations."""
    # List of dicts
    result = faux_value(List[Dict[str, int]], "complex_data")
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)

    # Dict of lists
    result = faux_value(Dict[str, List[str]], "grouped_data")
    assert isinstance(result, dict)
    assert all(isinstance(v, list) for v in result.values())


def test_field_info_integration():
    """Test faux_value with FieldInfo objects."""
    from pydantic import Field

    # Test with constraints
    field_info = Field(min_length=5, max_length=10)
    result = faux_value(str, "constrained_field", field_info)
    assert isinstance(result, str)
    assert 5 <= len(result) <= 10


def test_recursive_model_generation():
    """Test that recursive model generation doesn't cause infinite loops."""
    # For now, skip this test as we need to implement recursion protection
    # This is a known limitation that we'll address separately
    pytest.skip(
        "Recursive model generation needs recursion protection - future enhancement"
    )


def test_performance_basic_types():
    """Test that basic type generation is reasonably fast."""
    import time

    start = time.time()
    for _ in range(1000):
        faux_value(str, "test")
    duration = time.time() - start

    # Should be able to generate 1000 strings in well under a second
    assert duration < 1.0
