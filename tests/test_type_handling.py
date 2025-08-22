"""Tests for type_handling module functionality."""

import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Literal, Union
from pydantic import UUID4

from fauxdantic.type_handling import (
    handle_literal_type,
    get_prioritized_union_type,
    get_union_types,
    is_union_type
)


class Color(str, Enum):
    RED = "red"
    GREEN = "green" 
    BLUE = "blue"


def test_handle_literal_type():
    """Test handling of Literal types."""
    # Test valid literal type
    result = handle_literal_type(Literal["red", "green", "blue"])
    assert result in ["red", "green", "blue"]
    
    # Test single literal value
    result = handle_literal_type(Literal["only"])
    assert result == "only"
    
    # Test non-literal type
    result = handle_literal_type(str)
    assert result is None
    
    # Test mixed literal types
    result = handle_literal_type(Literal[1, "two", 3.0])
    assert result in [1, "two", 3.0]


def test_get_prioritized_union_type_literal():
    """Test union prioritization with Literal types (highest priority)."""
    types = [str, int, Literal["test"]]
    result = get_prioritized_union_type(types)
    assert result == Literal["test"]


def test_get_prioritized_union_type_enum():
    """Test union prioritization with Enum types."""
    types = [str, int, Color, bool]
    result = get_prioritized_union_type(types)
    assert result == Color


def test_get_prioritized_union_type_datetime():
    """Test union prioritization with datetime types."""
    types = [str, int, datetime, bool]
    result = get_prioritized_union_type(types)
    assert result == datetime
    
    # Test date vs datetime (datetime should win as it's first)
    types = [str, datetime, date, bool]
    result = get_prioritized_union_type(types)
    assert result == datetime


def test_get_prioritized_union_type_bool():
    """Test union prioritization with bool types."""
    types = [str, int, bool]
    result = get_prioritized_union_type(types)
    assert result == bool


def test_get_prioritized_union_type_numeric():
    """Test union prioritization with numeric types."""
    types = [str, int, float]
    result = get_prioritized_union_type(types)
    assert result == int
    
    # Test float wins over str
    types = [str, float]
    result = get_prioritized_union_type(types)
    assert result == float


def test_get_prioritized_union_type_uuid():
    """Test union prioritization with UUID types."""
    types = [str, uuid.UUID, UUID4]
    result = get_prioritized_union_type(types)
    assert result in [uuid.UUID, UUID4]  # Either is acceptable


def test_get_prioritized_union_type_str_fallback():
    """Test union prioritization falls back to first type."""
    types = [str, bytes]
    result = get_prioritized_union_type(types)
    assert result == str
    
    # Test with unknown types
    types = [bytes, complex]
    result = get_prioritized_union_type(types)
    assert result == bytes


def test_get_prioritized_union_type_complex_hierarchy():
    """Test union prioritization with complex type hierarchies."""
    # Literal should beat everything
    types = [str, int, bool, datetime, Color, Literal["test"]]
    result = get_prioritized_union_type(types)
    assert result == Literal["test"]
    
    # Enum should beat datetime, bool, numeric, uuid, str
    types = [str, int, bool, datetime, Color, uuid.UUID]
    result = get_prioritized_union_type(types)
    assert result == Color
    
    # Datetime should beat bool, numeric, uuid, str
    types = [str, int, bool, datetime, uuid.UUID]
    result = get_prioritized_union_type(types)
    assert result == datetime


def test_get_union_types():
    """Test getting all supported union types."""
    union_types = get_union_types()
    
    # Should at least contain Union
    assert Union in union_types
    assert isinstance(union_types, tuple)
    
    # Test it handles import errors gracefully
    assert len(union_types) >= 1


def test_is_union_type():
    """Test union type detection."""
    # Test with Union origin
    from typing import get_origin
    
    union_type = Union[str, int]
    origin = get_origin(union_type)
    assert is_union_type(origin) is True
    
    # Test with non-union origin
    list_type = List[str]
    origin = get_origin(list_type)
    assert is_union_type(origin) is False
    
    # Test with None
    assert is_union_type(None) is False


def test_prioritization_edge_cases():
    """Test edge cases in type prioritization."""
    # Empty list should not crash
    with pytest.raises((IndexError, AttributeError)):
        get_prioritized_union_type([])
    
    # Single type should return that type
    result = get_prioritized_union_type([str])
    assert result == str
    
    # Multiple of same priority should return first
    result = get_prioritized_union_type([int, float])
    assert result == int


def test_literal_type_edge_cases():
    """Test edge cases for literal type handling."""
    # Test with boolean literals
    result = handle_literal_type(Literal[True, False])
    assert result in [True, False]
    
    # Test with numeric literals
    result = handle_literal_type(Literal[1, 2, 3])
    assert result in [1, 2, 3]
    
    # Test with single literal
    result = handle_literal_type(Literal["singleton"])
    assert result == "singleton"


# Import pytest for edge case tests
import pytest