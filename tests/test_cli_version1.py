"""
Integration tests for Version 1 CLI interface.
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from atobusu.cli.version1 import validate_cli_arguments, determine_template_and_output, run_version1_cli
from atobusu.core.config import AtobusuConfig
from atobusu.core.exceptions import InputError


class TestCLIValidation:
    """Test CLI argument validation."""
    
    def test_validate_cli_arguments_success(self):
        """Test successful CLI argument validation."""
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_file = f.name
        
        try:
            # Mock args
            args = MagicMock()
            args.input = temp_file
            args.template = None
            args.output = None
            
            # Mock logger
            logger = MagicMock()
            
            # Test validation
            result = validate_cli_arguments(args, logger)
            
            assert result['errors'] == []
            assert result['input_file'] == str(Path(temp_file).resolve())
            assert result['template_file'] is None
            assert result['output_file'] is None
            
        finally:
            Path(temp_file).unlink()
    
    def test_validate_cli_arguments_missing_input(self):
        """Test validation with missing input file."""
        args = MagicMock()
        args.input = None
        args.template = None
        args.output = None
        
        logger = MagicMock()
        
        result = validate_cli_arguments(args, logger)
        
        assert len(result['errors']) == 1
        assert "Input file is required" in result['errors'][0]
    
    def test_validate_cli_arguments_invalid_input_extension(self):
        """Test validation with invalid input file extension."""
        # Create temporary file with wrong extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            args = MagicMock()
            args.input = temp_file
            args.template = None
            args.output = None
            
            logger = MagicMock()
            
            result = validate_cli_arguments(args, logger)
            
            assert len(result['errors']) == 1
            assert "Input file must be JSON or YAML" in result['errors'][0]
            
        finally:
            Path(temp_file).unlink()


class TestTemplateAndOutputDetermination:
    """Test template and output file determination."""
    
    def test_determine_template_and_output_defaults(self):
        """Test default template and output determination."""
        # Mock template data
        template_data = MagicMock()
        template_data.template_type = 'page'
        
        # Mock logger
        logger = MagicMock()
        
        # Create templates directory for test
        templates_dir = Path("templates")
        if not templates_dir.exists():
            templates_dir.mkdir()
        
        # Create a test template file
        test_template = templates_dir / "base_page.html"
        if not test_template.exists():
            test_template.write_text("<html>{{title}}</html>")
        
        try:
            result = determine_template_and_output(template_data, None, None, logger)
            
            assert result['template_file'] == 'base_page.html'
            assert result['output_file'].startswith('output/')
            assert result['output_file'].endswith('.html')
            
        finally:
            # Clean up if we created the template
            if test_template.exists() and test_template.read_text() == "<html>{{title}}</html>":
                test_template.unlink()


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_cli_with_json_input(self):
        """Test CLI with JSON input file."""
        # Create temporary JSON input file
        test_data = {
            "template_type": "page",
            "title": "Test Page",
            "product_name": "Test Product",
            "product_code": "TEST-001",
            "content": "Test content with \"quotes\"",
            "data": [{"test": "item"}]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            input_file = f.name
        
        try:
            # Mock args
            args = MagicMock()
            args.input = input_file
            args.template = None
            args.output = "test_output.html"
            
            # Mock config
            config = AtobusuConfig()
            
            # Mock logger
            logger = MagicMock()
            
            # Ensure templates directory exists
            templates_dir = Path("templates")
            if not templates_dir.exists():
                templates_dir.mkdir()
            
            # Create a minimal test template
            test_template = templates_dir / "base_page.html"
            template_content = """
<!DOCTYPE html>
<html>
<head><title>{{title|default('Test')}}</title></head>
<body>
    <h1>{{product_name|default('No Product')}}</h1>
    <p>{{content|default('No Content')}}</p>
</body>
</html>
"""
            test_template.write_text(template_content)
            
            try:
                # Test CLI execution
                run_version1_cli(args, config, logger)
                
                # Check that output file was created
                output_file = Path("output/test_output.html")
                assert output_file.exists()
                
                # Check output content
                output_content = output_file.read_text()
                assert "Test Product" in output_content
                assert "Test Page" in output_content
                
            finally:
                # Clean up
                if test_template.exists():
                    test_template.unlink()
                
                output_file = Path("output/test_output.html")
                if output_file.exists():
                    output_file.unlink()
                    
        finally:
            Path(input_file).unlink()
    
    def test_cli_with_yaml_input(self):
        """Test CLI with YAML input file."""
        # Create temporary YAML input file
        test_data = {
            "template_type": "page",
            "title": "YAML Test Page",
            "product_name": "YAML Product",
            "product_code": "YAML-001",
            "content": "YAML content",
            "data": [{"yaml": "item"}]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_data, f)
            input_file = f.name
        
        try:
            # Mock args
            args = MagicMock()
            args.input = input_file
            args.template = None
            args.output = "yaml_test_output.html"
            
            # Mock config
            config = AtobusuConfig()
            
            # Mock logger
            logger = MagicMock()
            
            # Ensure templates directory exists
            templates_dir = Path("templates")
            if not templates_dir.exists():
                templates_dir.mkdir()
            
            # Create a minimal test template
            test_template = templates_dir / "base_page.html"
            template_content = """
<!DOCTYPE html>
<html>
<head><title>{{title|default('Test')}}</title></head>
<body>
    <h1>{{product_name|default('No Product')}}</h1>
    <p>{{content|default('No Content')}}</p>
</body>
</html>
"""
            test_template.write_text(template_content)
            
            try:
                # Test CLI execution
                run_version1_cli(args, config, logger)
                
                # Check that output file was created
                output_file = Path("output/yaml_test_output.html")
                assert output_file.exists()
                
                # Check output content
                output_content = output_file.read_text()
                assert "YAML Product" in output_content
                assert "YAML Test Page" in output_content
                
            finally:
                # Clean up
                if test_template.exists():
                    test_template.unlink()
                
                output_file = Path("output/yaml_test_output.html")
                if output_file.exists():
                    output_file.unlink()
                    
        finally:
            Path(input_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__])