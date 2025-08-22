"""Custom exceptions for fauxdantic."""

from typing import Any, List, Optional, Set


class FauxdanticError(Exception):
    """Base exception for all fauxdantic errors."""
    pass


class InvalidKwargsError(FauxdanticError):
    """Raised when invalid kwargs are passed to faux() or faux_dict()."""
    
    def __init__(self, invalid_fields: Set[str], model_name: str, valid_fields: List[str]):
        self.invalid_fields = invalid_fields
        self.model_name = model_name
        self.valid_fields = valid_fields
        
        invalid_list = sorted(invalid_fields)
        valid_list = sorted(valid_fields)
        
        message = f"Invalid field(s) for {model_name}: {', '.join(invalid_list)}"
        if valid_fields:
            message += f"\nValid fields: {', '.join(valid_list)}"
        
        super().__init__(message)


class UnsupportedTypeError(FauxdanticError):
    """Raised when fauxdantic encounters an unsupported type."""
    
    def __init__(self, field_type: Any, field_name: str = "", suggestions: Optional[List[str]] = None):
        self.field_type = field_type
        self.field_name = field_name
        self.suggestions = suggestions or []
        
        type_name = getattr(field_type, '__name__', str(field_type))
        
        if field_name:
            message = f"Unsupported type '{type_name}' for field '{field_name}'"
        else:
            message = f"Unsupported type '{type_name}'"
            
        if self.suggestions:
            message += f"\nSuggestions: {', '.join(self.suggestions)}"
            
        message += "\nConsider using a supported type or implementing a custom generator."
        
        super().__init__(message)


class ConfigurationError(FauxdanticError):
    """Raised when there's an error with fauxdantic configuration."""
    pass


class GenerationError(FauxdanticError):
    """Raised when value generation fails."""
    
    def __init__(self, field_name: str, field_type: Any, original_error: Exception):
        self.field_name = field_name
        self.field_type = field_type
        self.original_error = original_error
        
        type_name = getattr(field_type, '__name__', str(field_type))
        
        message = f"Failed to generate value for field '{field_name}' of type '{type_name}'"
        message += f"\nOriginal error: {original_error}"
        
        super().__init__(message)