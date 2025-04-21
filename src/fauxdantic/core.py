import enum
import random
import uuid
from datetime import date, datetime
from enum import Enum
from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

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
        return [_faux_value(item_type, field_name) for _ in range(random.randint(1, 3))]

    # Handle Dict types
    if origin is dict:
        key_type = args[0] if args else str
        value_type = args[1] if len(args) > 1 else Any
        return {
            _faux_value(key_type, f"{field_name}_key"): _faux_value(
                value_type, f"{field_name}_value"
            )
            for _ in range(random.randint(1, 3))
        }

    # Handle basic types
    if isinstance(field_type, type):
        if issubclass(field_type, BaseModel):
            return faux_dict(field_type)
        elif issubclass(field_type, Enum):
            return random.choice(list(field_type.__members__.values()))
        elif field_type is str:
            field_name_lower = field_name.lower()
            if "email" in field_name_lower:
                return faker.email()
            elif "name" in field_name_lower:
                return faker.name()
            elif "street" in field_name_lower:
                return faker.street_address()
            elif "city" in field_name_lower:
                return faker.city()
            elif "state" in field_name_lower:
                return faker.state()
            elif "zip" in field_name_lower or "postal" in field_name_lower:
                return faker.postcode()
            elif "phone" in field_name_lower:
                return faker.phone_number()
            elif "url" in field_name_lower:
                return faker.url()
            elif "description" in field_name_lower:
                return faker.text(max_nb_chars=200)
            return faker.sentence(nb_words=3)
        elif field_type is int:
            return faker.random_int(min=0, max=100)
        elif field_type is float:
            return round(faker.random_float(min=0, max=100), 2)
        elif field_type is bool:
            return faker.boolean()
        elif field_type is datetime:
            return faker.date_time()
        elif field_type is date:
            return date.fromisoformat(faker.date())
        elif field_type is uuid.UUID or field_type is UUID4:
            return uuid.UUID(faker.uuid4())

    # Handle FieldInfo objects
    if isinstance(field_type, FieldInfo):
        return _faux_value(field_type.annotation, field_name)

    # Default fallback
    return faker.word()


def faux_dict(model: Type[BaseModel], **kwargs: Any) -> Dict[str, Any]:
    model_values: Dict[str, Any] = {}

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


def faux(pydantic_model: Type[Model], **kwargs: Any) -> Model:
    return pydantic_model(**faux_dict(pydantic_model, **kwargs))
