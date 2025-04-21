import enum
import random
import uuid
from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_args, get_origin, Annotated

from faker import Faker
from pydantic import UUID4, BaseModel, StrictFloat
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined


faker = Faker()


def _faux_value(field_type: Any, field_name: str = "") -> Any:
    # Handle None or PydanticUndefined field types
    if field_type is None or field_type is PydanticUndefined:
        return faker.word()

    # Handle Annotated types
    if get_origin(field_type) is Annotated:
        field_type = get_args(field_type)[0]

    # Get the origin type (e.g., List from List[str])
    origin = get_origin(field_type)
    args = get_args(field_type)

    # Handle Union types (including Optional)
    if origin is Union:
        # Filter out None for Optional types
        types = [t for t in args if t is not type(None)]
        if types:
            return _faux_value(types[0], field_name)
        return None

    # Handle List types
    if origin is list:
        item_type = args[0] if args else Any
        return [_faux_value(item_type, field_name) for _ in range(2)]

    # Handle Dict types
    if origin is dict:
        key_type = args[0] if args else str
        value_type = args[1] if len(args) > 1 else Any
        return {
            _faux_value(key_type, f"{field_name}_key"): _faux_value(value_type, f"{field_name}_value")
            for _ in range(2)
        }

    # Handle basic types
    if isinstance(field_type, type):
        if issubclass(field_type, BaseModel):
            return faux_dict(field_type)
        elif issubclass(field_type, Enum):
            return random.choice(list(field_type.__members__.values()))
        elif field_type is str:
            if "email" in field_name.lower():
                return faker.email()
            elif "name" in field_name.lower():
                return faker.name()
            return faker.word()
        elif field_type is int:
            return faker.random_int(min=0, max=100)
        elif field_type is float:
            return round(faker.random_float(min=0, max=100), 2)
        elif field_type is bool:
            return faker.boolean()
        elif field_type is datetime:
            return faker.date_time()
        elif field_type is date:
            return faker.date()
        elif field_type is uuid.UUID:
            return faker.uuid4()

    # Handle FieldInfo objects
    if isinstance(field_type, FieldInfo):
        return _faux_value(field_type.annotation, field_name)

    # Default fallback
    return faker.word()


def faux_dict(model: Type[BaseModel], **kwargs) -> Dict:
    model_values = {}

    for name, field in model.model_fields.items():
        if name in kwargs:
            model_values[name] = kwargs[name]
            continue

        # For simple types, use the field type directly
        field_type = field.annotation
        if isinstance(field_type, type):
            model_values[name] = _faux_value(field_type, name)
            continue

        # For more complex types (Union, List, etc.), use the field info
        model_values[name] = _faux_value(field, name)

    return model_values


Model = TypeVar("Model", bound=BaseModel)


def faux(pydantic_model: Type[Model], **kwargs) -> Model:
    return pydantic_model(**faux_dict(pydantic_model, **kwargs)) 