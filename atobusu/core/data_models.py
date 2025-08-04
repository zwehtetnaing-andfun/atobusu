"""
Data models for Atobusu application.

Contains dataclass models for structured data handling throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, Union
import json


@dataclass
class InputData:
    """
    Model for input data from various sources.
    
    Represents data coming from JSON, YAML, GUI, or Word documents
    with metadata about the source and processing context.
    """
    
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_type: str = "unknown"  # 'json', 'yaml', 'gui', 'word'
    timestamp: datetime = field(default_factory=datetime.now)
    encoding: str = "utf-8"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'content': self.content,
            'metadata': self.metadata,
            'source_type': self.source_type,
            'timestamp': self.timestamp.isoformat(),
            'encoding': self.encoding
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputData':
        """Create InputData from dictionary."""
        # Handle timestamp conversion
        timestamp_str = data.get('timestamp')
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = timestamp_str or datetime.now()
        
        return cls(
            content=data.get('content', ''),
            metadata=data.get('metadata', {}),
            source_type=data.get('source_type', 'unknown'),
            timestamp=timestamp,
            encoding=data.get('encoding', 'utf-8')
        )
    
    def validate(self) -> bool:
        """Validate the input data."""
        if not isinstance(self.content, str):
            return False
        if not isinstance(self.metadata, dict):
            return False
        if self.source_type not in ['json', 'yaml', 'gui', 'word', 'unknown']:
            return False
        return True


@dataclass
class TemplateData:
    """
    Model for template-specific data.
    
    Contains structured data that will be used for template variable replacement
    and placeholder processing.
    """
    
    product_code: str = ""
    product_name: str = ""
    dates: Dict[str, str] = field(default_factory=dict)  # {'post_date': '2025/01/15', 'short_date': '25/01/15'}
    category: str = ""
    reviewer_name: str = ""
    rating: int = 0
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_placeholder_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for placeholder replacement."""
        placeholder_dict = {
            'product_code': self.product_code,
            'product_name': self.product_name,
            'category': self.category,
            'reviewer_name': self.reviewer_name,
            'rating': self.rating,
        }
        
        # Add date fields
        placeholder_dict.update(self.dates)
        
        # Add additional data
        placeholder_dict.update(self.additional_data)
        
        return placeholder_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateData':
        """Create TemplateData from dictionary."""
        return cls(
            product_code=data.get('product_code', ''),
            product_name=data.get('product_name', ''),
            dates=data.get('dates', {}),
            category=data.get('category', ''),
            reviewer_name=data.get('reviewer_name', ''),
            rating=data.get('rating', 0),
            additional_data=data.get('additional_data', {})
        )
    
    def validate(self) -> bool:
        """Validate the template data."""
        if not isinstance(self.dates, dict):
            return False
        if not isinstance(self.additional_data, dict):
            return False
        if not isinstance(self.rating, int) or self.rating < 0:
            return False
        return True


@dataclass
class ProcessedData:
    """
    Model for processed data ready for template rendering.
    
    Contains the converted content, template variables, and metadata
    about the processing and output format.
    """
    
    converted_content: str
    template_variables: Dict[str, Any] = field(default_factory=dict)
    output_format: str = "html"  # 'html', 'php', 'mixed'
    template_type: str = "page"  # 'page', 'index', 'content'
    original_input: Optional[InputData] = None
    template_data: Optional[TemplateData] = None
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_template_context(self) -> Dict[str, Any]:
        """Convert to template context dictionary for rendering."""
        context = {
            'content': self.converted_content,
            'output_format': self.output_format,
            'template_type': self.template_type,
        }
        
        # Add template variables
        context.update(self.template_variables)
        
        # Add template data if available
        if self.template_data:
            context.update(self.template_data.to_placeholder_dict())
        
        # Add processing metadata
        context['metadata'] = self.processing_metadata
        
        return context
    
    @classmethod
    def from_input_data(
        cls, 
        input_data: InputData, 
        converted_content: str,
        template_data: Optional[TemplateData] = None,
        output_format: str = "html",
        template_type: str = "page"
    ) -> 'ProcessedData':
        """Create ProcessedData from InputData and conversion results."""
        return cls(
            converted_content=converted_content,
            template_variables={},
            output_format=output_format,
            template_type=template_type,
            original_input=input_data,
            template_data=template_data,
            processing_metadata={
                'source_type': input_data.source_type,
                'processed_at': datetime.now().isoformat(),
                'encoding': input_data.encoding
            }
        )
    
    def validate(self) -> bool:
        """Validate the processed data."""
        if not isinstance(self.converted_content, str):
            return False
        if not isinstance(self.template_variables, dict):
            return False
        if self.output_format not in ['html', 'php', 'mixed']:
            return False
        if self.template_type not in ['page', 'index', 'content']:
            return False
        return True


@dataclass
class ValidationResult:
    """
    Model for validation results.
    
    Contains information about data validation including
    success status, error messages, and warnings.
    """
    
    is_valid: bool
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    validation_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, message: str, field: Optional[str] = None):
        """Add an error message."""
        error_info = {'message': message}
        if field:
            error_info['field'] = field
        self.errors.append(error_info)
        self.is_valid = False
    
    def add_warning(self, message: str, field: Optional[str] = None):
        """Add a warning message."""
        warning_info = {'message': message}
        if field:
            warning_info['field'] = field
        self.warnings.append(warning_info)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> str:
        """Get a summary of all errors."""
        if not self.has_errors():
            return "No errors"
        
        error_messages = [error['message'] for error in self.errors]
        return "; ".join(error_messages)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'validation_metadata': self.validation_metadata
        }