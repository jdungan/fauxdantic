"""Configuration and optimization settings for fauxdantic."""

import random
from typing import Optional, Tuple

from faker import Faker


class FauxConfig:
    """Global configuration for fauxdantic generation."""
    
    def __init__(self) -> None:
        self._faker = Faker()
        self._collection_size_range = (1, 3)
        self._random_seed: Optional[int] = None
        
    @property
    def faker(self) -> Faker:
        """Get the global faker instance."""
        return self._faker
    
    @property 
    def collection_size_range(self) -> Tuple[int, int]:
        """Get the range for random collection sizes."""
        return self._collection_size_range
        
    def set_locale(self, locale: str) -> None:
        """Set faker locale."""
        self._faker = Faker(locale)
        
    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducible generation."""
        self._random_seed = seed
        self._faker.seed_instance(seed)
        random.seed(seed)
        
    def set_collection_size_range(self, min_size: int, max_size: int) -> None:
        """Set the range for random collection sizes."""
        if min_size < 0 or max_size < min_size:
            raise ValueError("Invalid collection size range")
        self._collection_size_range = (min_size, max_size)
        
    def get_random_collection_size(self) -> int:
        """Get a random collection size within the configured range."""
        min_size, max_size = self._collection_size_range
        return random.randint(min_size, max_size)


# Global configuration instance
config = FauxConfig()


def get_faker() -> Faker:
    """Get the global faker instance."""
    return config.faker


def get_random_collection_size() -> int:
    """Get a random collection size using global config."""
    return config.get_random_collection_size()