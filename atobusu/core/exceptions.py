"""
Custom exception classes for Atobusu application.
"""


class AtobusuError(Exception):
    """Base exception for Atobusu application."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class InputError(AtobusuError):
    """Errors related to input processing."""
    pass


class ProcessingError(AtobusuError):
    """Errors during data processing."""
    pass


class TemplateError(AtobusuError):
    """Errors in template rendering."""
    pass


class OutputError(AtobusuError):
    """Errors during output generation."""
    pass


class ConfigurationError(AtobusuError):
    """Errors in configuration loading or validation."""
    pass


class GUIError(AtobusuError):
    """Errors in GUI operations."""
    pass