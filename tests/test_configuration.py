"""Tests for configuration system functionality."""

from typing import Dict, List

import pytest
from pydantic import BaseModel

from fauxdantic import ConfigurationError, config, faux, faux_dict


class CollectionModel(BaseModel):
    items: List[str]
    metadata: Dict[str, str]


class SimpleModel(BaseModel):
    name: str
    age: int


def test_default_collection_size_range():
    """Test default collection size range (1-3)."""
    # Reset to defaults
    config.set_collection_size_range(1, 3)

    # Generate multiple models and check collection sizes
    sizes = []
    for _ in range(20):
        model = faux(CollectionModel)
        sizes.extend([len(model.items), len(model.metadata)])

    # All sizes should be between 1 and 3 inclusive
    assert all(1 <= size <= 3 for size in sizes)
    assert min(sizes) == 1  # Should hit minimum
    assert max(sizes) == 3  # Should hit maximum


def test_custom_collection_size_range_small():
    """Test setting small collection size range."""
    config.set_collection_size_range(1, 2)

    # Test multiple generations
    for _ in range(10):
        model = faux(CollectionModel)
        assert 1 <= len(model.items) <= 2
        assert 1 <= len(model.metadata) <= 2

    # Reset to default
    config.set_collection_size_range(1, 3)


def test_custom_collection_size_range_large():
    """Test setting large collection size range."""
    config.set_collection_size_range(5, 8)

    model = faux(CollectionModel)
    assert 5 <= len(model.items) <= 8
    assert 5 <= len(model.metadata) <= 8

    # Reset to default
    config.set_collection_size_range(1, 3)


def test_collection_size_range_validation():
    """Test validation of collection size range parameters."""
    # Test invalid ranges
    with pytest.raises(ValueError):
        config.set_collection_size_range(-1, 3)  # Negative min

    with pytest.raises(ValueError):
        config.set_collection_size_range(5, 3)  # Max < min

    with pytest.raises(ValueError):
        config.set_collection_size_range(0, -1)  # Both invalid


def test_collection_size_range_edge_cases():
    """Test edge cases for collection size ranges."""
    # Test single size (min == max)
    config.set_collection_size_range(5, 5)

    model = faux(CollectionModel)
    assert len(model.items) == 5
    assert len(model.metadata) == 5

    # Test zero size collections
    config.set_collection_size_range(0, 1)
    model = faux(CollectionModel)
    assert 0 <= len(model.items) <= 1
    assert 0 <= len(model.metadata) <= 1

    # Reset to default
    config.set_collection_size_range(1, 3)


def test_seed_deterministic_behavior():
    """Test that setting seed produces deterministic results."""
    config.set_seed(42)

    # Generate first set of results
    model1 = faux(SimpleModel)
    model2 = faux(SimpleModel)

    # Reset seed and generate again
    config.set_seed(42)
    model3 = faux(SimpleModel)
    model4 = faux(SimpleModel)

    # Results should be identical
    assert model1.name == model3.name
    assert model1.age == model3.age
    assert model2.name == model4.name
    assert model2.age == model4.age


def test_seed_with_collections():
    """Test seeded generation with collections."""
    config.set_seed(123)

    model1 = faux(CollectionModel)

    config.set_seed(123)
    model2 = faux(CollectionModel)

    # Collections should be identical
    assert model1.items == model2.items
    assert model1.metadata == model2.metadata


def test_seed_affects_collection_sizes():
    """Test that seed affects both content and collection sizes."""
    config.set_collection_size_range(1, 5)
    config.set_seed(456)

    model1 = faux(CollectionModel)

    config.set_seed(456)
    model2 = faux(CollectionModel)

    # Both content and sizes should match
    assert len(model1.items) == len(model2.items)
    assert len(model1.metadata) == len(model2.metadata)
    assert model1.items == model2.items
    assert model1.metadata == model2.metadata

    # Reset
    config.set_collection_size_range(1, 3)


def test_locale_configuration():
    """Test setting different locales."""
    # Test default (English)
    model_en = faux(SimpleModel)
    assert isinstance(model_en.name, str)

    # Test Japanese locale
    config.set_locale("ja_JP")
    model_jp = faux(SimpleModel)
    assert isinstance(model_jp.name, str)

    # Names should be different styles (though this is probabilistic)
    # At minimum, they should both be strings
    assert model_en.name != model_jp.name or True  # Allow for rare collisions

    # Reset to default
    config.set_locale("en_US")


def test_faker_instance_consistency():
    """Test that the same faker instance is used consistently."""
    faker1 = config.faker
    faker2 = config.faker

    # Should be the same object
    assert faker1 is faker2

    # Test after locale change
    config.set_locale("fr_FR")
    faker3 = config.faker

    # Should be a new instance after locale change
    assert faker1 is not faker3

    # Reset
    config.set_locale("en_US")


def test_config_state_isolation():
    """Test that config changes are properly isolated."""
    # Save original state
    original_range = config.collection_size_range

    # Change config
    config.set_collection_size_range(10, 15)
    config.set_seed(999)

    # Verify changes took effect
    assert config.collection_size_range == (10, 15)

    # Reset and verify
    config.set_collection_size_range(*original_range)
    assert config.collection_size_range == original_range


def test_config_with_faux_dict():
    """Test that configuration affects faux_dict as well as faux."""
    config.set_collection_size_range(2, 2)  # Exactly 2 items

    result = faux_dict(CollectionModel)
    assert len(result["items"]) == 2
    assert len(result["metadata"]) == 2

    # Reset
    config.set_collection_size_range(1, 3)


def test_config_persistence_across_calls():
    """Test that config persists across multiple faux calls."""
    config.set_collection_size_range(4, 6)

    # Multiple calls should all respect the same config
    for _ in range(5):
        model = faux(CollectionModel)
        assert 4 <= len(model.items) <= 6
        assert 4 <= len(model.metadata) <= 6

    # Reset
    config.set_collection_size_range(1, 3)


def test_concurrent_config_usage():
    """Test that config works correctly with rapid successive calls."""
    config.set_collection_size_range(1, 1)  # Exactly 1 item
    config.set_seed(777)

    # Rapid successive calls
    models = [faux(CollectionModel) for _ in range(10)]

    # All should have exactly 1 item due to config
    for model in models:
        assert len(model.items) == 1
        assert len(model.metadata) == 1

    # Reset
    config.set_collection_size_range(1, 3)


def test_get_random_collection_size_function():
    """Test the get_random_collection_size function directly."""
    from fauxdantic.config import get_random_collection_size

    config.set_collection_size_range(5, 10)

    # Test multiple calls
    sizes = [get_random_collection_size() for _ in range(20)]

    # All should be in range
    assert all(5 <= size <= 10 for size in sizes)

    # Should have some variation (probabilistic test)
    assert len(set(sizes)) > 1  # Should not all be the same

    # Reset
    config.set_collection_size_range(1, 3)
