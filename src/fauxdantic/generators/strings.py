"""Smart string generation with field heuristics."""

from datetime import datetime
from typing import Any, Dict

from faker import Faker

faker = Faker()


def generate_constrained_string(field_name: str, constraints: Dict[str, Any]) -> str:
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
    elif (
        "state" in field_name_lower
        or "province" in field_name_lower
        or "region" in field_name_lower
    ):
        # For state/province fields, use full state name or abbreviation based on max_length
        if max_length <= 3:
            base_value = faker.state_abbr()
        else:
            base_value = faker.state()
            if len(base_value) > max_length:
                base_value = faker.state_abbr()
    elif "country" in field_name_lower:
        base_value = faker.country()
        if len(base_value) > max_length:
            # If country name is too long, try country code
            base_value = faker.country_code()
            if len(base_value) > max_length:
                base_value = faker.country()[:max_length]
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
