"""Main API functions for fauxdantic."""

from typing import Any, Dict, List, Set, Type, TypeVar

from pydantic import BaseModel

from .exceptions import InvalidKwargsError
from .utils.unique import process_unique_value
from .value_generation import faux_value


def _validate_kwargs(model: Type[BaseModel], kwargs: Dict[str, Any]) -> None:
    """Validate that all kwargs correspond to actual model fields."""
    if not kwargs:
        return

    model_fields = set(model.model_fields.keys())
    provided_fields = set(kwargs.keys())
    invalid_fields = provided_fields - model_fields

    if invalid_fields:
        valid_fields = list(model_fields)
        raise InvalidKwargsError(invalid_fields, model.__name__, valid_fields)


def faux_dict(model: Type[BaseModel], **kwargs: Any) -> Dict[str, Any]:
    """Generate a dictionary of fake values for a Pydantic model."""
    # Validate kwargs against model fields
    _validate_kwargs(model, kwargs)

    model_values: Dict[str, Any] = {}

    for name, field_info in model.model_fields.items():
        if name in kwargs:
            # Process unique values in kwargs
            model_values[name] = process_unique_value(kwargs[name], field_info)
            continue

        # Pass both type and field info for constraint-aware generation
        model_values[name] = faux_value(field_info.annotation, name, field_info)

    return model_values


Model = TypeVar("Model", bound=BaseModel)


def faux(pydantic_model: Type[Model], **kwargs: Any) -> Model:
    """Generate a fake instance of a Pydantic model."""
    return pydantic_model(**faux_dict(pydantic_model, **kwargs))
