import enum
import random
import uuid

from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from faker import Faker
from pydantic import UUID4, BaseModel, StrictFloat


fake = Faker()


def fake_value(field_type: Any, name: str) -> Any:
    try:
        if issubclass(field_type, BaseModel):
            return make_dict(field_type)
    except TypeError:
        pass
    outer_type = (
        field_type.__origin__ if hasattr(field_type, "__origin__") else field_type
    )
    inner_type = (
        field_type.__args__[0]
        if hasattr(field_type, "__args__") and field_type.__args__
        else None
    )

    if outer_type in [List, list]:
        return [fake_value(inner_type, name) for _ in range(random.randint(1, 5))]
    elif isinstance(field_type, enum.EnumMeta):
        return random.choice([v.value for v in field_type.__members__.values()])

    if field_type == Any:
        return "Any"
    elif field_type == int:
        return random.randint(2000, 2100)
    elif field_type == str:
        return fake.word()
    elif field_type == bool:
        return random.choice([True, False])
    elif field_type == float or field_type == StrictFloat:
        return random.uniform(0, 100)
    elif field_type == uuid.UUID:
        return str(uuid.uuid4())
    elif field_type == UUID4:
        return uuid.uuid4()
    elif field_type == datetime:
        return str(datetime.now())
    elif field_type == Optional[str]:
        return random.choice([None, fake.word()])
    elif field_type == Optional[int]:
        return random.choice([None, fake.pyint()])
    elif field_type == Optional[datetime]:
        return random.choice([None, str(datetime.now())])
    elif field_type == Dict[int, str]:
        fake_dict = {}
        for _ in range(random.randint(1, 5)):
            key = random.randint(1, 1000)
            value = fake.word()
            fake_dict[key] = value
        return fake_dict
    elif (
        field_type == Dict
        or field_type == Dict[str, Any]
        or field_type == Dict[str, str]
    ):
        return {}
    elif outer_type == Union:
        inner_type = field_type.__args__[0]
        if inner_type.__class__ == type(BaseModel):
            return make_dict(inner_type)
        else:
            return fake_value(inner_type, name)
    else:
        raise ValueError(f"Unsupported type: name: {name}:  {field_type} ")


def make_dict(model: Type[BaseModel], **kwargs) -> Dict:
    model_values = dict()

    for name, field in model.__fields__.items():
        if name in kwargs:
            model_values[name] = kwargs[name]
        else:
            field_type = field.outer_type_
            field_default = field.default
            field_default_factory = field.default_factory

            if field_default is not None:
                model_values[name] = field_default
            elif field_default_factory is not None:
                model_values[name] = field_default_factory()
            else:
                model_values[name] = fake_value(field_type, name)
    return model_values


Model = TypeVar("Model", bound=BaseModel)


def fake_model(pydantic_model: Type[Model], **kwargs) -> Model:
    return pydantic_model(**make_dict(pydantic_model, **kwargs)) 