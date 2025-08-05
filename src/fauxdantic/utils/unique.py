"""Unique string pattern handling utilities."""

from typing import Any, Dict

from pydantic.fields import FieldInfo


def generate_unique_string(pattern: str, max_length: int) -> str:
    """Generate a unique string based on a pattern containing '<unique>'"""
    import hashlib
    import time
    import uuid

    # Replace "<unique>" with a truly unique identifier
    if "<unique>" in pattern:
        # Calculate the base pattern (without <unique>)
        base_pattern = pattern.replace("<unique>", "")

        # If the base pattern is already longer than max_length, truncate it
        if len(base_pattern) > max_length:
            return base_pattern[:max_length]

        # Calculate available space for unique part
        available_length = max_length - len(base_pattern)

        # Calculate timestamp and hash once for all strategies
        timestamp = int(time.time() * 1000000)
        timestamp_hash = hashlib.md5(str(timestamp).encode()).hexdigest()

        # Choose strategy based on available space
        if available_length >= 20:
            # Use timestamp + UUID for maximum uniqueness
            unique_id = uuid.uuid4().hex[:8]
            unique_part = f"{timestamp}_{unique_id}"
        elif available_length >= 12:
            # Use 12 characters of hashed timestamp
            unique_part = timestamp_hash[:12]
        elif available_length >= 8:
            # Use 8 characters of hashed timestamp
            unique_part = timestamp_hash[:8]
        elif available_length >= 6:
            # Use 6 characters of hashed timestamp
            unique_part = timestamp_hash[:6]
        elif available_length > 0:
            # Use whatever space is available
            unique_part = timestamp_hash[:available_length]
        else:
            # If no space available, return just the base pattern
            return base_pattern

        result = pattern.replace("<unique>", unique_part)
        return result

    return pattern


def process_unique_value(value: Any, field_info: FieldInfo = None) -> Any:
    """Process a value to handle unique string patterns"""
    if isinstance(value, str) and "<unique>" in value:
        from ..types.constraints import extract_field_constraints

        constraints = {}
        if field_info:
            constraints = extract_field_constraints(field_info)
        max_length = constraints.get("max_length", 50)
        return generate_unique_string(value, max_length)
    return value
