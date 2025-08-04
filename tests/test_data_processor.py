"""
Tests for data processing engine.
"""

import pytest
import json
import yaml
import tempfile
from pathlib import Path
from datetime import datetime

from atobusu.core.data_processor import DataProcessor
from atobusu.core.data_models import InputData, ProcessedData, TemplateData, ValidationResult
from atobusu.core.character_converter import CharacterConverter
from atobusu.core.exceptions import InputError, ProcessingError


class TestDataModels:
    """Test cases for data models."""
    
    def test_input_data_creation(self):
        """Test InputData creation and methods."""
        input_data = InputData(
            content="Test content",
            metadata={"key": "value"},
            source_type="json"
        )
        
        assert input_data.content == "Test content"
        assert input_data.metadata["key"] == "value"
        assert input_data.source_type == "json"
        assert input_data.validate()
    
    def test_input_data_to_from_dict(self):
        """Test InputData serialization."""
        original = InputData(
            content="Test content",
            metadata={"test": True},
            source_type="yaml"
        )
        
        data_dict = original.to_dict()
        restored = InputData.from_dict(data_dict)
        
        assert restored.content == original.content
        assert restored.metadata == original.metadata
        assert restored.source_type == original.source_type
    
    def test_template_data_creation(self):
        """Test TemplateData creation and methods."""
        template_data = TemplateData(
            product_code="TEST123",
            product_name="Test Product",
            dates={"post_date": "2025/01/15"},
            category="Test Category",
            rating=5
        )
        
        assert template_data.product_code == "TEST123"
        assert template_data.validate()
        
        placeholder_dict = template_data.to_placeholder_dict()
        assert placeholder_dict["product_code"] == "TEST123"
        assert placeholder_dict["post_date"] == "2025/01/15"
    
    def test_processed_data_creation(self):
        """Test ProcessedData creation and methods."""
        input_data = InputData(content="test", source_type="json")
        processed_data = ProcessedData.from_input_data(
            input_data=input_data,
            converted_content="converted test",
            output_format="html",
            template_type="page"
        )
        
        assert processed_data.converted_content == "converted test"
        assert processed_data.output_format == "html"
        assert processed_data.template_type == "page"
        assert processed_data.validate()
        
        context = processed_data.to_template_context()
        assert context["content"] == "converted test"
        assert context["output_format"] == "html"
    
    def test_validation_result(self):
        """Test ValidationResult functionality."""
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid
        assert not result.has_errors()
        assert not result.has_warnings()
        
        result.add_error("Test error", "test_field")
        assert not result.is_valid
        assert result.has_errors()
        
        result.add_warning("Test warning")
        assert result.has_warnings()
        
        assert "Test error" in result.get_error_summary()


class TestDataProcessor:
    """Test cases for DataProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DataProcessor()
    
    def test_processor_initialization(self):
        """Test DataProcessor initialization."""
        assert self.processor.character_converter is not None
        assert isinstance(self.processor.character_converter, CharacterConverter)
        
        # Test with custom character converter
        custom_converter = CharacterConverter()
        processor = DataProcessor(custom_converter)
        assert processor.character_converter is custom_converter
    
    def test_parse_json_file(self):
        """Test JSON file parsing."""
        test_data = {
            "content": "Test content with \"quotes\"",
            "template_data": {
                "product_code": "TEST123",
                "product_name": "Test Product"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            parsed_data = self.processor.parse_json(temp_path)
            assert parsed_data["content"] == test_data["content"]
            assert parsed_data["template_data"]["product_code"] == "TEST123"
        finally:
            Path(temp_path).unlink()
    
    def test_parse_yaml_file(self):
        """Test YAML file parsing."""
        test_data = {
            "content": "Test content with special chars ①",
            "template_type": "page",
            "output_format": "html"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_data, f)
            temp_path = f.name
        
        try:
            parsed_data = self.processor.parse_yaml(temp_path)
            assert parsed_data["content"] == test_data["content"]
            assert parsed_data["template_type"] == "page"
        finally:
            Path(temp_path).unlink()
    
    def test_parse_file_json(self):
        """Test generic file parsing with JSON."""
        test_data = {"content": "JSON test content"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            input_data = self.processor.parse_file(temp_path)
            assert isinstance(input_data, InputData)
            assert input_data.source_type == "json"
            assert "JSON test content" in input_data.content
            assert input_data.metadata["parsed_data"]["content"] == "JSON test content"
        finally:
            Path(temp_path).unlink()
    
    def test_parse_file_yaml(self):
        """Test generic file parsing with YAML."""
        test_data = {"content": "YAML test content"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(test_data, f)
            temp_path = f.name
        
        try:
            input_data = self.processor.parse_file(temp_path)
            assert isinstance(input_data, InputData)
            assert input_data.source_type == "yaml"
            assert "YAML test content" in input_data.content
        finally:
            Path(temp_path).unlink()
    
    def test_parse_unsupported_file(self):
        """Test parsing unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            with pytest.raises(InputError):
                self.processor.parse_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file."""
        with pytest.raises(InputError):
            self.processor.parse_json("nonexistent.json")
        
        with pytest.raises(InputError):
            self.processor.parse_yaml("nonexistent.yaml")
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with pytest.raises(InputError):
                self.processor.parse_json(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name
        
        try:
            with pytest.raises(InputError):
                self.processor.parse_yaml(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_validate_data_input_data(self):
        """Test data validation with InputData."""
        input_data = InputData(
            content="Test content",
            source_type="json"
        )
        
        result = self.processor.validate_data(input_data)
        assert result.is_valid
    
    def test_validate_data_dict(self):
        """Test data validation with dictionary."""
        data = {
            "content": "Test content",
            "template_type": "page",
            "template_data": {
                "product_code": "TEST123",
                "rating": 5
            }
        }
        
        result = self.processor.validate_data(data)
        assert result.is_valid
    
    def test_validate_data_invalid(self):
        """Test data validation with invalid data."""
        # Test with invalid template data
        data = {
            "template_data": "invalid_not_dict"
        }
        
        result = self.processor.validate_data(data)
        assert not result.is_valid
        assert result.has_errors()
    
    def test_determine_template_type(self):
        """Test template type determination."""
        # Test explicit template_type
        data = {"template_type": "index"}
        assert self.processor.determine_template_type(data) == "index"
        
        # Test inference from file path
        data = {}
        assert self.processor.determine_template_type(data, "page_template.html") == "page"
        assert self.processor.determine_template_type(data, "index_list.html") == "index"
        
        # Test inference from data structure
        data = {"items": []}
        assert self.processor.determine_template_type(data) == "index"
        
        data = {"product_code": "TEST123"}
        assert self.processor.determine_template_type(data) == "page"
        
        # Test default
        data = {}
        assert self.processor.determine_template_type(data) == "page"
    
    def test_process_data(self):
        """Test data processing."""
        input_data = InputData(
            content='Test "content" with ① symbol',
            metadata={
                "parsed_data": {
                    "template_type": "page",
                    "output_format": "html",
                    "template_data": {
                        "product_code": "TEST123",
                        "product_name": "Test Product"
                    },
                    "variables": {
                        "title": "Test Title"
                    }
                }
            },
            source_type="json"
        )
        
        processed_data = self.processor.process_data(input_data)
        
        assert isinstance(processed_data, ProcessedData)
        assert processed_data.template_type == "page"
        assert processed_data.output_format == "html"
        assert processed_data.template_data is not None
        assert processed_data.template_data.product_code == "TEST123"
        assert processed_data.template_variables["title"] == "Test Title"
        
        # Check character conversion was applied
        assert '\u201C' in processed_data.converted_content  # Curly quote
        assert '&#9312;' in processed_data.converted_content  # Circled number
    
    def test_process_data_invalid(self):
        """Test processing invalid data."""
        # Create invalid InputData
        input_data = InputData(content="", source_type="invalid")
        
        # Should raise ProcessingError due to validation failure
        with pytest.raises(ProcessingError):
            self.processor.process_data(input_data)
    
    def test_process_file_integration(self):
        """Test complete file processing integration."""
        test_data = {
            "content": 'Product "Test①" review',
            "template_type": "page",
            "output_format": "html",
            "template_data": {
                "product_code": "TEST123",
                "product_name": "Test Product",
                "rating": 5
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            processed_data = self.processor.process_file(temp_path)
            
            assert isinstance(processed_data, ProcessedData)
            assert processed_data.template_type == "page"
            assert processed_data.output_format == "html"
            
            # Check character conversion
            assert '\u201C' in processed_data.converted_content
            assert '&#9312;' in processed_data.converted_content
            
            # Check template data
            assert processed_data.template_data.product_code == "TEST123"
            assert processed_data.template_data.rating == 5
            
        finally:
            Path(temp_path).unlink()
    
    def test_create_template_data_from_dict(self):
        """Test template data creation from dictionary."""
        data = {
            "product_code": "TEST123",
            "product_name": "Test Product",
            "dates": {"post_date": "2025/01/15"},
            "rating": 4
        }
        
        template_data = self.processor.create_template_data_from_dict(data)
        
        assert isinstance(template_data, TemplateData)
        assert template_data.product_code == "TEST123"
        assert template_data.dates["post_date"] == "2025/01/15"
        assert template_data.rating == 4
    
    def test_get_processing_stats(self):
        """Test processing statistics."""
        stats = self.processor.get_processing_stats()
        
        assert "supported_json_extensions" in stats
        assert "supported_yaml_extensions" in stats
        assert "template_types" in stats
        assert "character_converter_available" in stats
        
        assert '.json' in stats["supported_json_extensions"]
        assert '.yaml' in stats["supported_yaml_extensions"]
        assert 'page' in stats["template_types"]
        assert stats["character_converter_available"] is True
    
    def test_multiple_template_types(self):
        """Test processing different template types."""
        # Test page template
        page_data = {"product_code": "TEST123", "content": "Page content"}
        result = self.processor.determine_template_type(page_data)
        assert result == "page"
        
        # Test index template
        index_data = {"items": ["item1", "item2"], "content": "Index content"}
        result = self.processor.determine_template_type(index_data)
        assert result == "index"
        
        # Test content template (default)
        content_data = {"title": "Article", "content": "Article content"}
        result = self.processor.determine_template_type(content_data)
        assert result == "page"  # Default
    
    def test_character_conversion_integration(self):
        """Test integration with character conversion."""
        input_data = InputData(
            content='Japanese: テスト "商品①" は◎評価',
            source_type="json"
        )
        
        processed_data = self.processor.process_data(input_data)
        
        # Check that character conversion was applied
        converted = processed_data.converted_content
        assert '\u201C' in converted  # Curly quote
        assert '&#9312;' in converted  # Circled number ①
        assert '&#9678;' in converted  # Symbol ◎
        assert 'テスト' in converted  # Japanese preserved
        
        # Check conversion stats in metadata
        assert 'conversion_stats' in processed_data.processing_metadata
        stats = processed_data.processing_metadata['conversion_stats']
        assert stats['japanese_chars'] > 0
        assert stats['circled_numbers'] > 0