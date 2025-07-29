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
    Literal,
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


def _extract_field_constraints(field_info: FieldInfo) -> Dict[str, Any]:
    """Extract constraints from Pydantic FieldInfo"""
    constraints = {}

    # Handle Pydantic 2.x metadata-based constraints
    if hasattr(field_info, "metadata") and field_info.metadata:
        for constraint in field_info.metadata:
            constraint_type = type(constraint).__name__
            if constraint_type == "MaxLen":
                constraints["max_length"] = constraint.max_length
            elif constraint_type == "MinLen":
                constraints["min_length"] = constraint.min_length
            elif constraint_type == "Ge":
                constraints["min_value"] = constraint.ge
            elif constraint_type == "Le":
                constraints["max_value"] = constraint.le
            elif constraint_type == "Gt":
                constraints["min_value"] = constraint.gt + 1
            elif constraint_type == "Lt":
                constraints["max_value"] = constraint.lt - 1

    # Fallback to direct attributes (Pydantic 1.x style)
    if hasattr(field_info, "max_length") and field_info.max_length is not None:
        constraints["max_length"] = field_info.max_length
    if hasattr(field_info, "min_length") and field_info.min_length is not None:
        constraints["min_length"] = field_info.min_length
    if hasattr(field_info, "ge") and field_info.ge is not None:
        constraints["min_value"] = field_info.ge
    if hasattr(field_info, "le") and field_info.le is not None:
        constraints["max_value"] = field_info.le
    if hasattr(field_info, "gt") and field_info.gt is not None:
        constraints["min_value"] = field_info.gt + 1
    if hasattr(field_info, "lt") and field_info.lt is not None:
        constraints["max_value"] = field_info.lt - 1

    return constraints


def _handle_literal_type(field_type: Any) -> Any:
    """Handle Literal types by choosing from allowed values"""
    if get_origin(field_type) is Literal:
        literal_values = get_args(field_type)
        return random.choice(literal_values)
    return None


def _generate_constrained_string(field_name: str, constraints: Dict[str, Any]) -> str:
    """Generate string respecting length constraints"""
    min_length = constraints.get("min_length", 1)
    max_length = constraints.get("max_length", 50)

    # Use field name heuristics when possible, but ensure constraints are respected
    field_name_lower = field_name.lower()

    # Try field-specific generation first
    if "email" in field_name_lower and max_length >= 7:  # minimum for "a@b.com"
        base_value = faker.email()
        if len(base_value) > max_length:
            # Generate a shorter email that fits
            username = faker.user_name()[
                : max(1, max_length - 6)
            ]  # Leave room for "@x.com"
            base_value = f"{username}@{faker.random_letter()}.com"
            if len(base_value) > max_length:
                base_value = f"a@{faker.random_letter()}.co"[:max_length]
    elif "name" in field_name_lower:
        base_value = faker.name()
        if len(base_value) > max_length:
            base_value = faker.first_name()
            if len(base_value) > max_length:
                base_value = faker.first_name()[:max_length]
    elif "url" in field_name_lower and max_length >= 10:
        base_value = faker.url()
        if len(base_value) > max_length:
            base_value = f"http://{faker.word()}.com"[:max_length]
    elif "phone" in field_name_lower and max_length >= 10:
        base_value = faker.phone_number()
        if len(base_value) > max_length:
            base_value = faker.phone_number()[:max_length]
    elif "description" in field_name_lower:
        # For description fields, generate longer text but respect explicit constraints
        if not constraints or "max_length" not in constraints:
            # No explicit constraints, generate longer description text
            max_length = 120  # Override default for descriptions
            base_value = faker.text(max_nb_chars=120)
        else:
            # Has explicit max_length constraint
            base_value = faker.text(max_nb_chars=max_length)
        base_value = base_value.rstrip(".\n ")
    elif "street" in field_name_lower or "address" in field_name_lower:
        base_value = faker.street_address()
        if len(base_value) > max_length:
            base_value = faker.street_address()[:max_length]
    elif "city" in field_name_lower:
        base_value = faker.city()
        if len(base_value) > max_length:
            base_value = faker.city()[:max_length]
    elif "zip" in field_name_lower or "postal" in field_name_lower:
        base_value = faker.postcode()
        if len(base_value) > max_length:
            base_value = faker.postcode()[:max_length]
    else:
        # General string generation with length awareness
        if max_length <= 5:
            base_value = faker.lexify("?????")[:max_length]
        elif max_length <= 10:
            base_value = faker.word()
            if len(base_value) > max_length:
                base_value = faker.lexify("?" * max_length)
        elif max_length <= 20:
            words = faker.words(nb=2)
            base_value = " ".join(words)
            if len(base_value) > max_length:
                base_value = faker.words(nb=1)[0]
                if len(base_value) > max_length:
                    base_value = faker.lexify("?" * max_length)
        else:
            base_value = faker.text(max_nb_chars=max_length)
            base_value = base_value.rstrip(".\n ")

    # Ensure we don't exceed max_length
    if len(base_value) > max_length:
        base_value = base_value[:max_length]

    # Pad to meet min_length if needed
    if len(base_value) < min_length:
        padding_needed = min_length - len(base_value)
        padding = "".join(faker.random_letter() for _ in range(padding_needed))
        base_value = base_value + padding

    return base_value


def _generate_constrained_number(
    field_type: Type, field_name: str, constraints: Dict[str, Any]
) -> Union[int, float]:
    """Generate numbers respecting range constraints"""
    # Special handling for year fields
    if "year" in field_name.lower() and field_type is int:
        current_year = datetime.now().year
        min_val = constraints.get("min_value", 1900)
        max_val = constraints.get("max_value", current_year + 10)
        return faker.random_int(min=int(min_val), max=int(max_val))

    # General numeric constraints
    if field_type is int:
        min_val = constraints.get("min_value", 0)
        max_val = constraints.get("max_value", 100)
        return faker.random_int(min=int(min_val), max=int(max_val))
    else:
        min_val = constraints.get("min_value", 0.0)
        max_val = constraints.get("max_value", 100.0)
        return round(
            faker.pyfloat(min_value=float(min_val), max_value=float(max_val)), 2
        )


def _faux_value(
    field_type: Any, field_name: str = "", field_info: FieldInfo = None
) -> Any:
    # Handle None or PydanticUndefined field types
    if field_type is None or field_type is PydanticUndefined:
        return faker.word()

    # Extract constraints if field_info provided
    constraints = {}
    if field_info:
        constraints = _extract_field_constraints(field_info)

    # Handle Literal types first
    literal_value = _handle_literal_type(field_type)
    if literal_value is not None:
        return literal_value

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
            return _faux_value(types[0], field_name, field_info)
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
            return random.choice(list(field_type))
        elif field_type is str:
            return _generate_constrained_string(field_name, constraints)
        elif field_type is int:
            return _generate_constrained_number(field_type, field_name, constraints)
        elif field_type is float:
            return _generate_constrained_number(field_type, field_name, constraints)
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
        return _faux_value(field_type.annotation, field_name, field_type)

    # Default fallback
    return faker.word()


def faux_dict(model: Type[BaseModel], **kwargs: Any) -> Dict[str, Any]:
    model_values: Dict[str, Any] = {}

    for name, field_info in model.model_fields.items():
        if name in kwargs:
            model_values[name] = kwargs[name]
            continue

        # Pass both type and field info for constraint-aware generation
        model_values[name] = _faux_value(field_info.annotation, name, field_info)

    return model_values


Model = TypeVar("Model", bound=BaseModel)


def faux(pydantic_model: Type[Model], **kwargs: Any) -> Model:
    return pydantic_model(**faux_dict(pydantic_model, **kwargs))
