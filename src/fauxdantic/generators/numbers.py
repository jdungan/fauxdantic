"""Number generation with constraints."""

from datetime import datetime
from typing import Any, Dict, Type, Union

from faker import Faker

faker = Faker()


def generate_constrained_number(
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
