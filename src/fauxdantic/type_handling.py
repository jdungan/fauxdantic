"""Type handling utilities for value generation."""

import random
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Type, Union, get_args, get_origin

from pydantic import UUID4


def handle_literal_type(field_type: Any) -> Any:
    """Handle Literal types by choosing from allowed values"""
    if get_origin(field_type) is Literal:
        literal_values = get_args(field_type)
        return random.choice(literal_values)
    return None


def get_prioritized_union_type(types: List[Type]) -> Type:
    """
    Select the most appropriate type from a Union for fake data generation.

    Prioritization order (highest to lowest priority):
    1. Literal types (most specific)
    2. Enum types (domain-specific values)
    3. datetime/date types (structured temporal data)
    4. bool types (more specific than str)
    5. Numeric types (int, float - more specific than str)
    6. UUID types (structured data)
    7. str (fallback, least specific)
    """
    # Priority 1: Literal types (most specific constraints)
    literal_types = [t for t in types if get_origin(t) is Literal]
    if literal_types:
        return literal_types[0]

    # Priority 2: Enum types (domain-specific values)
    enum_types = [t for t in types if isinstance(t, type) and issubclass(t, Enum)]
    if enum_types:
        return enum_types[0]

    # Priority 3: datetime/date types (structured temporal data)
    datetime_types = [t for t in types if t in (datetime, date)]
    if datetime_types:
        return datetime_types[0]

    # Priority 4: bool types (more specific than str)
    bool_types = [t for t in types if t is bool]
    if bool_types:
        return bool_types[0]

    # Priority 5: Numeric types (more specific than str)
    numeric_types = [t for t in types if t in (int, float)]
    if numeric_types:
        return numeric_types[0]

    # Priority 6: UUID types (structured data)
    uuid_types = [t for t in types if t in (uuid.UUID, UUID4)]
    if uuid_types:
        return uuid_types[0]

    # Priority 7: Fallback to first type (includes str and others)
    return types[0]


def get_union_types() -> tuple:
    """Get all supported union types, handling Python version differences."""
    union_types: tuple = (Union,)
    try:
        from types import UnionType

        union_types = (Union, UnionType)
    except ImportError:
        pass

    try:
        from types import TypeAliasType  # type: ignore[attr-defined]

        union_types = union_types + (TypeAliasType,)
    except ImportError:
        pass

    return union_types


def is_union_type(origin: Any) -> bool:
    """Check if the given origin is a union type."""
    return origin in get_union_types()
