"""
Tests for configuration management.
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path

from atobusu.core.config import AtobusuConfig
from atobusu.core.exceptions import ConfigurationError


class TestAtobusuConfig:
    """Test cases for AtobusuConfig class."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = AtobusuConfig()
        
        assert config.template_directory == "templates"
        assert config.output_directory == "output"
        assert config.gui_framework == "tkinter"
        assert config.log_level == "INFO"
        assert "quotes" in config.character_conversion_rules
        assert "circled_numbers" in config.character_conversion_rules
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = AtobusuConfig()
        assert config.validate() is True
        
        # Test invalid GUI framework
        config.gui_framework = "invalid"
        with pytest.raises(ValueError):
            config.validate()
    
    def test_load_from_json(self):
        """Test loading configuration from JSON file."""
        test_config = {
            "template_directory": "test_templates",
            "output_directory": "test_output",
            "gui_framework": "pyqt5",
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name
        
        try:
            config = AtobusuConfig.load_from_file(temp_path)
            assert config.template_directory == "test_templates"
            assert config.gui_framework == "pyqt5"
            assert config.log_level == "DEBUG"
        finally:
            Path(temp_path).unlink()
    
    def test_load_from_yaml(self):
        """Test loading configuration from YAML file."""
        test_config = {
            "template_directory": "test_templates",
            "output_directory": "test_output",
            "gui_framework": "pyqt5"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_path = f.name
        
        try:
            config = AtobusuConfig.load_from_file(temp_path)
            assert config.template_directory == "test_templates"
            assert config.gui_framework == "pyqt5"
        finally:
            Path(temp_path).unlink()
    
    def test_save_to_file(self):
        """Test saving configuration to file."""
        config = AtobusuConfig(
            template_directory="test_templates",
            gui_framework="pyqt5"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save_to_file(temp_path)
            
            # Load and verify
            loaded_config = AtobusuConfig.load_from_file(temp_path)
            assert loaded_config.template_directory == "test_templates"
            assert loaded_config.gui_framework == "pyqt5"
        finally:
            Path(temp_path).unlink()
    
    def test_path_methods(self):
        """Test path utility methods."""
        config = AtobusuConfig(
            template_directory="test_templates",
            output_directory="test_output"
        )
        
        template_path = config.get_template_path("test.html")
        assert str(template_path) == "test_templates/test.html"
        
        output_path = config.get_output_path("result.html")
        assert str(output_path) == "test_output/result.html"