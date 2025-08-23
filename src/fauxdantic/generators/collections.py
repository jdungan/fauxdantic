"""List and Dict generation utilities."""

from typing import Any, Callable, Dict, List

from ..config import get_random_collection_size


def generate_list(
    item_type: Any, field_name: str, faux_value_func: Callable[[Any, str], Any]
) -> List[Any]:
    """Generate a list with random items of the specified type"""
    return [
        faux_value_func(item_type, field_name)
        for _ in range(get_random_collection_size())
    ]


def generate_dict(
    key_type: Any,
    value_type: Any,
    field_name: str,
    faux_value_func: Callable[[Any, str], Any],
) -> Dict[Any, Any]:
    """Generate a dictionary with random key-value pairs"""
    return {
        faux_value_func(key_type, f"{field_name}_key"): faux_value_func(
            value_type, f"{field_name}_value"
        )
        for _ in range(get_random_collection_size())
    }
