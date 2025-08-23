"""Tests for enhanced error handling functionality."""

from typing import Any, Callable, List

import pytest
from pydantic import BaseModel

from fauxdantic import (
    FauxdanticError,
    GenerationError,
    InvalidKwargsError,
    UnsupportedTypeError,
    faux,
    faux_dict,
)


class SimpleModel(BaseModel):
    name: str
    age: int
    email: str


class ComplexModel(BaseModel):
    items: List[str]
    callback: Callable[[int], str]  # Unsupported type


def test_invalid_kwargs_single_field():
    """Test InvalidKwargsError with single invalid field."""
    with pytest.raises(InvalidKwargsError) as exc_info:
        faux(SimpleModel, invalid_field="test")

    error = exc_info.value
    assert "invalid_field" in str(error)
    assert "SimpleModel" in str(error)
    assert "Valid fields: age, email, name" in str(error)
    assert error.invalid_fields == {"invalid_field"}
    assert set(error.valid_fields) == {"name", "age", "email"}


def test_invalid_kwargs_multiple_fields():
    """Test InvalidKwargsError with multiple invalid fields."""
    with pytest.raises(InvalidKwargsError) as exc_info:
        faux(SimpleModel, bad1="test", bad2="test", bad3="test")

    error = exc_info.value
    assert "bad1" in str(error)
    assert "bad2" in str(error)
    assert "bad3" in str(error)
    assert error.invalid_fields == {"bad1", "bad2", "bad3"}


def test_invalid_kwargs_mixed_valid_invalid():
    """Test InvalidKwargsError when mixing valid and invalid fields."""
    with pytest.raises(InvalidKwargsError) as exc_info:
        faux(SimpleModel, name="John", invalid_field="test")

    error = exc_info.value
    assert "invalid_field" in str(error)
    # Valid field will appear in "Valid fields:" section, which is expected
    assert error.invalid_fields == {"invalid_field"}


def test_invalid_kwargs_faux_dict():
    """Test that faux_dict also validates kwargs."""
    with pytest.raises(InvalidKwargsError) as exc_info:
        faux_dict(SimpleModel, invalid_field="test")

    error = exc_info.value
    assert "invalid_field" in str(error)


def test_valid_kwargs_still_work():
    """Test that valid kwargs continue to work normally."""
    result = faux(SimpleModel, name="John", age=30)
    assert result.name == "John"
    assert result.age == 30
    assert isinstance(result.email, str)

    result_dict = faux_dict(SimpleModel, name="Jane")
    assert result_dict["name"] == "Jane"


def test_unsupported_type_error_callable():
    """Test UnsupportedTypeError for callable types."""
    with pytest.raises(UnsupportedTypeError) as exc_info:
        faux(ComplexModel)

    error = exc_info.value
    assert "Callable" in str(error)
    assert "callback" in str(error)
    assert "Functions/callables are not supported" in str(error)
    assert error.field_name == "callback"
    assert error.field_type is Callable[[int], str]


def test_unsupported_type_numpy_like():
    """Test UnsupportedTypeError with numpy-like module suggestion."""

    # Create a mock numpy type that can't be used in Pydantic models
    class CustomType:
        __name__ = "CustomArray"
        __module__ = "numpy.core"

    # Test the error handling directly without Pydantic model creation
    with pytest.raises(UnsupportedTypeError) as exc_info:
        from fauxdantic.value_generation import faux_value

        faux_value(CustomType, "array")

    error = exc_info.value
    assert "CustomType" in str(error)  # Class name appears in error
    assert "array" in str(error)
    assert "numpy" in str(error).lower()


def test_unsupported_type_pandas_like():
    """Test UnsupportedTypeError with pandas-like module suggestion."""

    class PandasType:
        __name__ = "DataFrame"
        __module__ = "pandas.core.frame"

    # Test the error handling directly without Pydantic model creation
    with pytest.raises(UnsupportedTypeError) as exc_info:
        from fauxdantic.value_generation import faux_value

        faux_value(PandasType, "df")

    error = exc_info.value
    assert "PandasType" in str(error)  # Class name appears in error
    assert "df" in str(error)
    assert "pandas" in str(error).lower() or "Python built-in" in str(error)


def test_graceful_fallback_any_type():
    """Test graceful fallback for Any type."""

    class AnyModel(BaseModel):
        anything: Any

    # Should not raise an error, should generate a string
    result = faux(AnyModel)
    assert isinstance(result.anything, str)


def test_exception_inheritance():
    """Test that all custom exceptions inherit from FauxdanticError."""
    assert issubclass(InvalidKwargsError, FauxdanticError)
    assert issubclass(UnsupportedTypeError, FauxdanticError)
    assert issubclass(GenerationError, FauxdanticError)


def test_error_attributes_preserved():
    """Test that error objects preserve all relevant attributes."""
    # Test InvalidKwargsError attributes
    with pytest.raises(InvalidKwargsError) as exc_info:
        faux(SimpleModel, bad="field")

    error = exc_info.value
    assert hasattr(error, "invalid_fields")
    assert hasattr(error, "model_name")
    assert hasattr(error, "valid_fields")

    # Test UnsupportedTypeError attributes
    with pytest.raises(UnsupportedTypeError) as exc_info:
        faux(ComplexModel)

    error = exc_info.value
    assert hasattr(error, "field_type")
    assert hasattr(error, "field_name")
    assert hasattr(error, "suggestions")


def test_no_kwargs_validation_skip():
    """Test that validation is skipped when no kwargs provided."""
    # This should work without any validation overhead
    result = faux(SimpleModel)
    assert isinstance(result.name, str)
    assert isinstance(result.age, int)
    assert isinstance(result.email, str)


def test_empty_model():
    """Test error handling with empty model."""

    class EmptyModel(BaseModel):
        pass

    with pytest.raises(InvalidKwargsError) as exc_info:
        faux(EmptyModel, some_field="value")

    error = exc_info.value
    # For empty models, there are no valid fields, so message should indicate that
    assert "some_field" in str(error)
    assert error.invalid_fields == {"some_field"}
    assert error.valid_fields == []


def test_error_messages_helpful():
    """Test that error messages are genuinely helpful for developers."""
    # Test that error messages contain actionable information
    with pytest.raises(InvalidKwargsError) as exc_info:
        faux(SimpleModel, nam="John")  # Common typo

    error_msg = str(exc_info.value)
    assert "nam" in error_msg  # Shows the wrong field
    assert "name" in error_msg  # Shows the correct field
    assert "Valid fields:" in error_msg  # Provides alternatives
