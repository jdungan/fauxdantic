"""Core value generation logic."""

import random
import uuid
from datetime import date, datetime
from enum import Enum
from typing import (
    Annotated,
    Any,
    Optional,
    get_args,
    get_origin,
)

from pydantic import UUID4, BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .config import get_faker, get_random_collection_size
from .exceptions import GenerationError, UnsupportedTypeError
from .generators.numbers import generate_constrained_number
from .generators.strings import generate_constrained_string
from .type_handling import (
    get_prioritized_union_type,
    handle_literal_type,
    is_union_type,
)
from .types.constraints import extract_field_constraints


def faux_value(
    field_type: Any, field_name: str = "", field_info: Optional[FieldInfo] = None
) -> Any:
    """Generate a fake value for a given type and field configuration."""
    try:
        return _faux_value_internal(field_type, field_name, field_info)
    except Exception as e:
        # Wrap generation errors with better context
        if isinstance(e, (UnsupportedTypeError, GenerationError)):
            raise  # Re-raise our custom errors as-is
        else:
            # Wrap unexpected errors
            raise GenerationError(field_name, field_type, e) from e


def _faux_value_internal(
    field_type: Any, field_name: str = "", field_info: Optional[FieldInfo] = None
) -> Any:
    """Internal value generation with error handling."""
    # Handle None or PydanticUndefined field types
    if field_type is None or field_type is PydanticUndefined:
        return get_faker().word()

    # Extract constraints if field_info provided
    constraints = {}
    if field_info:
        constraints = extract_field_constraints(field_info)

    # Handle Literal types first
    literal_value = handle_literal_type(field_type)
    if literal_value is not None:
        return literal_value

    # Handle Annotated types
    if get_origin(field_type) is Annotated:
        field_type = get_args(field_type)[0]

    # Get the origin type (e.g., List from List[str])
    origin = get_origin(field_type)
    args = get_args(field_type)

    # Handle Union types (including Optional) and new union operator (|)
    if is_union_type(origin):
        # Filter out None for Optional types
        types = [t for t in args if t is not type(None)]
        if types:
            # Use prioritized type selection for better fake data generation
            prioritized_type = get_prioritized_union_type(types)
            return _faux_value_internal(prioritized_type, field_name, field_info)
        return None

    # Handle List types
    if origin is list:
        item_type = args[0] if args else Any
        return [_faux_value_internal(item_type, field_name) for _ in range(get_random_collection_size())]

    # Handle Dict types
    if origin is dict:
        key_type = args[0] if args else str
        value_type = args[1] if len(args) > 1 else Any
        return {
            _faux_value_internal(key_type, f"{field_name}_key"): _faux_value_internal(
                value_type, f"{field_name}_value"
            )
            for _ in range(get_random_collection_size())
        }

    # Handle basic types
    if isinstance(field_type, type):
        if issubclass(field_type, BaseModel):
            # Import here to avoid circular import
            from .core import faux_dict
            return faux_dict(field_type)
        elif issubclass(field_type, Enum):
            return random.choice(list(field_type))
        elif field_type is str:
            return generate_constrained_string(field_name, constraints)
        elif field_type is int:
            return generate_constrained_number(field_type, field_name, constraints)
        elif field_type is float:
            return generate_constrained_number(field_type, field_name, constraints)
        elif field_type is bool:
            return get_faker().boolean()
        elif field_type is datetime:
            return get_faker().date_time()
        elif field_type is date:
            return date.fromisoformat(get_faker().date())
        elif field_type is uuid.UUID or field_type is UUID4:
            return uuid.UUID(get_faker().uuid4())
        elif field_type is dict:
            # Handle plain dict type (without type parameters)
            return {
                _faux_value_internal(str, f"{field_name}_key"): _faux_value_internal(
                    Any, f"{field_name}_value"
                )
                for _ in range(get_random_collection_size())
            }
        elif field_type is list:
            # Handle plain list type (without type parameters)
            return [
                _faux_value_internal(Any, f"{field_name}_item")
                for _ in range(get_random_collection_size())
            ]
        elif field_type is tuple:
            # Handle plain tuple type (without type parameters)
            return tuple(
                _faux_value_internal(Any, f"{field_name}_item")
                for _ in range(get_random_collection_size())
            )
        elif field_type is set:
            # Handle plain set type (without type parameters)
            return {
                _faux_value_internal(Any, f"{field_name}_item")
                for _ in range(get_random_collection_size())
            }
        elif field_type is frozenset:
            # Handle plain frozenset type (without type parameters)
            return frozenset(
                _faux_value_internal(Any, f"{field_name}_item")
                for _ in range(get_random_collection_size())
            )
        elif field_type is bytes:
            # Handle bytes type
            return get_faker().binary(length=random.randint(10, 50))
        elif field_type is complex:
            # Handle complex type
            return complex(get_faker().random_number(), get_faker().random_number())

    # Handle FieldInfo objects
    if isinstance(field_type, FieldInfo):
        return _faux_value_internal(field_type.annotation, field_name, field_type)

    # Check for common unsupported types and provide helpful suggestions
    suggestions = []
    type_name = getattr(field_type, '__name__', str(field_type))
    
    # Provide suggestions for common mistakes
    if hasattr(field_type, '__module__'):
        module_name = field_type.__module__
        if 'numpy' in module_name:
            suggestions.append("Use Python built-in types (int, float) instead of numpy types")
        elif 'pandas' in module_name:
            suggestions.append("Use Python built-in types or Pydantic types instead")
        elif 'typing' in module_name:
            suggestions.append("Check if you're using a supported typing construct")
    
    if 'function' in type_name.lower() or 'callable' in type_name.lower():
        suggestions.append("Functions/callables are not supported for fake data generation")
    
    # For unknown types, try a graceful fallback first
    if hasattr(field_type, '__name__') and field_type.__name__ in ['object', 'Any']:
        return get_faker().word()  # Graceful fallback for generic types
    
    # If we can't handle it, raise an informative error
    raise UnsupportedTypeError(field_type, field_name, suggestions)