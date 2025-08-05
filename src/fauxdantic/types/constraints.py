"""Pydantic constraint extraction utilities."""

from typing import Any, Dict

from pydantic.fields import FieldInfo


def extract_field_constraints(field_info: FieldInfo) -> Dict[str, Any]:
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
