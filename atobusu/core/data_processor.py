"""
Data processing engine for Atobusu application.

Handles parsing, validation, and processing of data from various sources
including JSON, YAML, and structured input data.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

from atobusu.core.logging_config import get_logger
from atobusu.core.exceptions import InputError, ProcessingError
from atobusu.core.data_models import InputData, ProcessedData, TemplateData, ValidationResult
from atobusu.core.character_converter import CharacterConverter


class DataProcessor:
    """
    Main data processing engine for Atobusu.
    
    Handles parsing of JSON/YAML files, data validation, character conversion,
    and preparation of data for template rendering.
    """
    
    def __init__(self, character_converter: Optional[CharacterConverter] = None):
        """
        Initialize the data processor.
        
        Args:
            character_converter: Optional CharacterConverter instance
        """
        self.logger = get_logger(__name__)
        self.character_converter = character_converter or CharacterConverter()
        
        # Supported file extensions
        self.json_extensions = {'.json'}
        self.yaml_extensions = {'.yaml', '.yml'}
        
        # Template type mappings
        self.template_type_mappings = {
            'page': ['page', 'detail', 'content'],
            'index': ['index', 'list', 'listing'],
            'content': ['content', 'article', 'post']
        }
    
    def parse_json(self, file_path: str) -> Dict[str, Any]:
        """
        Parse JSON file and return data dictionary.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            InputError: If file cannot be read or parsed
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise InputError(f"JSON file not found: {file_path}")
            
            if file_path.suffix.lower() not in self.json_extensions:
                raise InputError(f"Invalid JSON file extension: {file_path.suffix}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Successfully parsed JSON file: {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            raise InputError(f"Invalid JSON format in file: {file_path}", str(e))
        except Exception as e:
            raise InputError(f"Failed to parse JSON file: {file_path}", str(e))
    
    def parse_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Parse YAML file and return data dictionary.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Parsed YAML data as dictionary
            
        Raises:
            InputError: If file cannot be read or parsed
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise InputError(f"YAML file not found: {file_path}")
            
            if file_path.suffix.lower() not in self.yaml_extensions:
                raise InputError(f"Invalid YAML file extension: {file_path.suffix}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Handle case where YAML file is empty or contains only None
            if data is None:
                data = {}
            
            self.logger.info(f"Successfully parsed YAML file: {file_path}")
            return data
            
        except yaml.YAMLError as e:
            raise InputError(f"Invalid YAML format in file: {file_path}", str(e))
        except Exception as e:
            raise InputError(f"Failed to parse YAML file: {file_path}", str(e))
    
    def parse_file(self, file_path: str) -> InputData:
        """
        Parse a file (JSON or YAML) and return InputData.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            InputData object with parsed content
            
        Raises:
            InputError: If file format is unsupported or parsing fails
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        try:
            if extension in self.json_extensions:
                data = self.parse_json(str(file_path))
                source_type = 'json'
            elif extension in self.yaml_extensions:
                data = self.parse_yaml(str(file_path))
                source_type = 'yaml'
            else:
                raise InputError(f"Unsupported file format: {extension}")
            
            # Convert parsed data to InputData
            input_data = InputData(
                content=json.dumps(data, ensure_ascii=False, indent=2),
                metadata={
                    'file_path': str(file_path),
                    'file_size': file_path.stat().st_size,
                    'parsed_data': data
                },
                source_type=source_type,
                timestamp=datetime.now()
            )
            
            return input_data
            
        except Exception as e:
            if isinstance(e, InputError):
                raise
            raise InputError(f"Failed to parse file: {file_path}", str(e))
    
    def validate_data(self, data: Union[InputData, Dict[str, Any]]) -> ValidationResult:
        """
        Validate input data structure and content.
        
        Args:
            data: InputData object or dictionary to validate
            
        Returns:
            ValidationResult with validation status and messages
        """
        result = ValidationResult(is_valid=True)
        
        try:
            if isinstance(data, InputData):
                # Validate InputData object
                if not data.validate():
                    result.add_error("Invalid InputData structure")
                
                # Validate content
                if not data.content:
                    result.add_warning("Empty content")
                
                # Validate source type
                if data.source_type not in ['json', 'yaml', 'gui', 'word']:
                    result.add_warning(f"Unknown source type: {data.source_type}")
                
                # Try to parse metadata if it contains parsed_data
                if 'parsed_data' in data.metadata:
                    parsed_data = data.metadata['parsed_data']
                    self._validate_parsed_data(parsed_data, result)
                
            elif isinstance(data, dict):
                # Validate dictionary data
                self._validate_parsed_data(data, result)
                
            else:
                result.add_error(f"Unsupported data type: {type(data)}")
            
            self.logger.debug(f"Data validation completed: {result.is_valid}")
            return result
            
        except Exception as e:
            result.add_error(f"Validation failed: {str(e)}")
            return result
    
    def _validate_parsed_data(self, data: Dict[str, Any], result: ValidationResult):
        """Validate parsed data structure."""
        # Check for required fields based on template type
        if 'template_type' in data:
            template_type = data['template_type']
            if template_type not in ['page', 'index', 'content']:
                result.add_warning(f"Unknown template type: {template_type}")
        
        # Validate template data if present
        if 'template_data' in data:
            template_data_dict = data['template_data']
            if isinstance(template_data_dict, dict):
                template_data = TemplateData.from_dict(template_data_dict)
                if not template_data.validate():
                    result.add_error("Invalid template data structure")
            else:
                result.add_error("Template data must be a dictionary")
        
        # Check for content field
        if 'content' not in data and 'text' not in data:
            result.add_warning("No content or text field found")
    
    def determine_template_type(self, data: Dict[str, Any], file_path: Optional[str] = None) -> str:
        """
        Determine template type from data or file path.
        
        Args:
            data: Parsed data dictionary
            file_path: Optional file path for hints
            
        Returns:
            Template type ('page', 'index', 'content')
        """
        # Check explicit template_type in data
        if 'template_type' in data:
            template_type = data['template_type'].lower()
            if template_type in ['page', 'index', 'content']:
                return template_type
        
        # Infer from file path
        if file_path:
            file_path_lower = str(file_path).lower()
            for template_type, keywords in self.template_type_mappings.items():
                if any(keyword in file_path_lower for keyword in keywords):
                    return template_type
        
        # Infer from data structure
        if 'items' in data or 'list' in data:
            return 'index'
        elif 'product_code' in data or 'product_name' in data:
            return 'page'
        
        # Default to page
        return 'page'
    
    def process_data(self, input_data: InputData) -> ProcessedData:
        """
        Process InputData and return ProcessedData ready for template rendering.
        
        Args:
            input_data: InputData object to process
            
        Returns:
            ProcessedData object with converted content and template variables
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            self.logger.info(f"Processing data from {input_data.source_type} source")
            
            # Validate input data
            validation_result = self.validate_data(input_data)
            if not validation_result.is_valid:
                raise ProcessingError(
                    "Data validation failed", 
                    validation_result.get_error_summary()
                )
            
            # Apply character conversion to content
            converted_content = self.character_converter.apply_all_conversions(
                input_data.content, 
                input_data.encoding
            )
            
            # Extract template data if available
            template_data = None
            parsed_data = input_data.metadata.get('parsed_data', {})
            
            if 'template_data' in parsed_data:
                template_data = TemplateData.from_dict(parsed_data['template_data'])
            
            # Determine template type
            template_type = self.determine_template_type(
                parsed_data, 
                input_data.metadata.get('file_path')
            )
            
            # Determine output format
            output_format = parsed_data.get('output_format', 'html')
            if output_format not in ['html', 'php', 'mixed']:
                output_format = 'html'
            
            # Create processed data
            processed_data = ProcessedData.from_input_data(
                input_data=input_data,
                converted_content=converted_content,
                template_data=template_data,
                output_format=output_format,
                template_type=template_type
            )
            
            # Add template variables from parsed data
            if 'variables' in parsed_data:
                processed_data.template_variables.update(parsed_data['variables'])
            
            # Add conversion statistics
            conversion_stats = self.character_converter.get_conversion_stats(input_data.content)
            processed_data.processing_metadata['conversion_stats'] = conversion_stats
            
            # Add validation warnings if any
            if validation_result.has_warnings():
                processed_data.processing_metadata['warnings'] = validation_result.warnings
            
            self.logger.info(f"Data processing completed successfully")
            return processed_data
            
        except ProcessingError:
            raise
        except Exception as e:
            raise ProcessingError(f"Failed to process data", str(e))
    
    def process_file(self, file_path: str) -> ProcessedData:
        """
        Process a file directly and return ProcessedData.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            ProcessedData object ready for template rendering
        """
        try:
            # Parse file to InputData
            input_data = self.parse_file(file_path)
            
            # Process the data
            processed_data = self.process_data(input_data)
            
            return processed_data
            
        except Exception as e:
            if isinstance(e, (InputError, ProcessingError)):
                raise
            raise ProcessingError(f"Failed to process file: {file_path}", str(e))
    
    def create_template_data_from_dict(self, data: Dict[str, Any]) -> TemplateData:
        """
        Create TemplateData from a dictionary.
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            TemplateData object
        """
        return TemplateData.from_dict(data)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the data processor.
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            'supported_json_extensions': list(self.json_extensions),
            'supported_yaml_extensions': list(self.yaml_extensions),
            'template_types': list(self.template_type_mappings.keys()),
            'character_converter_available': self.character_converter is not None
        }