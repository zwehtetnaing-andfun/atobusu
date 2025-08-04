"""
Tests for template management system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from atobusu.templates.template_manager import TemplateManager
from atobusu.templates.placeholder_processor import PlaceholderProcessor
from atobusu.core.exceptions import TemplateError


class TestTemplateManager:
    """Test cases for TemplateManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir)
        
        # Initialize template manager
        self.manager = TemplateManager(str(self.template_dir))
        
        # Sample data for testing
        self.test_data = {
            'title': 'Test Product Review',
            'product_code': 'TEST123',
            'product_name': 'Test Product',
            'category': 'Test Category',
            'reviewer_name': 'Test Reviewer',
            'rating': 5,
            'post_date': '2025/01/15',
            'short_date': '25/01/15',
            'content': 'This is test content',
            'description': 'Test description'
        }
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_template(self, name: str, content: str):
        """Helper to create test template files."""
        template_path = self.template_dir / name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content, encoding='utf-8')
    
    def test_manager_initialization(self):
        """Test TemplateManager initialization."""
        assert self.manager.template_dir == self.template_dir
        assert self.manager.placeholder_processor is not None
        assert self.manager.jinja_env is not None
        assert isinstance(self.manager._template_cache, dict)
    
    def test_manager_initialization_with_custom_processor(self):
        """Test initialization with custom placeholder processor."""
        custom_processor = PlaceholderProcessor()
        manager = TemplateManager(str(self.template_dir), custom_processor)
        assert manager.placeholder_processor is custom_processor
    
    def test_load_template_basic(self):
        """Test basic template loading."""
        template_content = "<h1>{{title}}</h1>"
        self.create_test_template("test.html", template_content)
        
        template = self.manager.load_template("test.html")
        assert template is not None
        assert "test.html" in self.manager._template_cache
    
    def test_load_template_caching(self):
        """Test template caching."""
        template_content = "<h1>{{title}}</h1>"
        self.create_test_template("cached.html", template_content)
        
        # Load template twice
        template1 = self.manager.load_template("cached.html")
        template2 = self.manager.load_template("cached.html")
        
        # Should be the same object (cached)
        assert template1 is template2
        assert len(self.manager._template_cache) == 1
    
    def test_load_template_not_found(self):
        """Test loading non-existent template."""
        with pytest.raises(TemplateError):
            self.manager.load_template("nonexistent.html")
    
    def test_load_template_syntax_error(self):
        """Test loading template with syntax error."""
        invalid_content = "{{invalid template syntax"
        self.create_test_template("invalid.html", invalid_content)
        
        with pytest.raises(TemplateError):
            self.manager.load_template("invalid.html")
    
    def test_render_html_basic(self):
        """Test basic HTML template rendering."""
        template_content = "<h1>{{title}}</h1><p>Product: {{product_name}}</p>"
        self.create_test_template("basic.html", template_content)
        
        result = self.manager.render_html("basic.html", self.test_data)
        
        assert "Test Product Review" in result
        assert "Test Product" in result
        assert "<h1>" in result and "</h1>" in result
    
    def test_render_html_with_placeholders(self):
        """Test HTML rendering with placeholder processing."""
        template_content = """
        <h1>{{title}}</h1>
        <p>Product: product_code</p>
        <p>Date: 2025/00/00</p>
        <p>Generic: {{category}}</p>
        """
        self.create_test_template("placeholders.html", template_content)
        
        result = self.manager.render_html("placeholders.html", self.test_data)
        
        assert "Test Product Review" in result
        assert "TEST123" in result  # Product code replacement
        assert "2025/" in result  # Date replacement (current or test date)
        assert "Test Category" in result  # Generic placeholder
    
    def test_render_php_basic(self):
        """Test basic PHP template rendering."""
        template_content = """
        <h1>{{title}}</h1>
        <?php echo "PHP code preserved"; ?>
        <p>Product: {{product_name}}</p>
        """
        self.create_test_template("basic.php", template_content)
        
        result = self.manager.render_php("basic.php", self.test_data)
        
        assert "Test Product Review" in result
        assert "Test Product" in result
        assert "<?php echo" in result  # PHP preserved
        assert "?>" in result
    
    def test_render_php_with_functions(self):
        """Test PHP rendering with function processing."""
        template_content = """
        <h1>{{title}}</h1>
        <img src="<?=prod_info("test_code", "mimg")?>" alt="{{product_name}}">
        <p>Product: product_code</p>
        """
        self.create_test_template("php_functions.php", template_content)
        
        result = self.manager.render_php("php_functions.php", self.test_data)
        
        assert "Test Product Review" in result
        assert "TEST123" in result  # Product code and PHP function replacement
        assert "<?=prod_info(" in result  # PHP function preserved
        assert "Test Product" in result
    
    def test_render_mixed_template_html(self):
        """Test mixed template rendering (HTML content)."""
        template_content = "<h1>{{title}}</h1><p>No PHP here</p>"
        self.create_test_template("mixed_html.html", template_content)
        
        result = self.manager.render_mixed_template("mixed_html.html", self.test_data)
        
        assert "Test Product Review" in result
        assert "<h1>" in result
    
    def test_render_mixed_template_php(self):
        """Test mixed template rendering (PHP content)."""
        template_content = """
        <h1>{{title}}</h1>
        <?php echo "Mixed content"; ?>
        <p>{{product_name}}</p>
        """
        self.create_test_template("mixed_php.html", template_content)
        
        result = self.manager.render_mixed_template("mixed_php.html", self.test_data)
        
        assert "Test Product Review" in result
        assert "Test Product" in result
        assert "<?php echo" in result
    
    def test_php_block_preservation(self):
        """Test PHP code block preservation."""
        content = """
        <h1>Title</h1>
        <?php echo "test"; ?>
        <?=variable?>
        <p>Content</p>
        """
        
        php_blocks, protected = self.manager._preserve_php_blocks(content)
        
        assert len(php_blocks) > 0
        assert "<?php echo" not in protected  # Should be replaced with placeholder
        assert "__PHP_" in protected  # Should contain placeholders
        
        # Test restoration
        restored = self.manager._restore_php_blocks(protected, php_blocks)
        assert "<?php echo" in restored
        assert "<?=variable?>" in restored
    
    def test_contains_php(self):
        """Test PHP detection."""
        php_content = "<?php echo 'test'; ?>"
        html_content = "<h1>No PHP here</h1>"
        mixed_content = "<h1>Title</h1><?=variable?><p>Text</p>"
        
        assert self.manager._contains_php(php_content) is True
        assert self.manager._contains_php(html_content) is False
        assert self.manager._contains_php(mixed_content) is True
    
    def test_process_php_functions(self):
        """Test PHP function processing."""
        content = '<?=prod_info("test_code", "pname")?>'
        result = self.manager.process_php_functions(content, self.test_data)
        
        assert "TEST123" in result  # Product code should be replaced
        assert "<?=prod_info(" in result  # PHP syntax preserved
    
    def test_create_template_from_string(self):
        """Test creating template from string."""
        template_string = "<h1>{{title}}</h1><p>Product: product_code</p>"
        result = self.manager.create_template_from_string(template_string, self.test_data)
        
        assert "Test Product Review" in result
        assert "TEST123" in result
    
    def test_get_template_list(self):
        """Test getting list of available templates."""
        # Create some test templates
        self.create_test_template("template1.html", "<h1>Test</h1>")
        self.create_test_template("template2.php", "<?php echo 'test'; ?>")
        self.create_test_template("subdir/template3.html", "<p>Nested</p>")
        
        templates = self.manager.get_template_list()
        
        assert "template1.html" in templates
        assert "template2.php" in templates
        assert "subdir/template3.html" in templates or "subdir\\template3.html" in templates
        assert len(templates) >= 3
    
    def test_template_exists(self):
        """Test template existence check."""
        self.create_test_template("exists.html", "<h1>Exists</h1>")
        
        assert self.manager.template_exists("exists.html") is True
        assert self.manager.template_exists("nonexistent.html") is False
    
    def test_clear_cache(self):
        """Test cache clearing."""
        template_content = "<h1>{{title}}</h1>"
        self.create_test_template("cached.html", template_content)
        
        # Load template to cache it
        self.manager.load_template("cached.html")
        assert len(self.manager._template_cache) == 1
        
        # Clear cache
        self.manager.clear_cache()
        assert len(self.manager._template_cache) == 0
    
    def test_get_cache_stats(self):
        """Test cache statistics."""
        template_content = "<h1>{{title}}</h1>"
        self.create_test_template("stats.html", template_content)
        
        # Load template
        self.manager.load_template("stats.html")
        
        stats = self.manager.get_cache_stats()
        
        assert "cached_templates" in stats
        assert "template_names" in stats
        assert "template_directory" in stats
        assert "available_templates" in stats
        assert stats["cached_templates"] == 1
        assert "stats.html" in stats["template_names"]
    
    def test_validate_template_valid(self):
        """Test template validation for valid template."""
        template_content = "<h1>{{title}}</h1><p>Product: product_code</p>"
        self.create_test_template("valid.html", template_content)
        
        result = self.manager.validate_template("valid.html")
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["template_type"] == "html"
        assert "placeholder_stats" in result
    
    def test_validate_template_invalid(self):
        """Test template validation for invalid template."""
        result = self.manager.validate_template("nonexistent.html")
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert "not found" in result["errors"][0]
    
    def test_validate_template_php(self):
        """Test template validation for PHP template."""
        template_content = "<?php echo 'test'; ?><h1>{{title}}</h1>"
        self.create_test_template("php_template.php", template_content)
        
        result = self.manager.validate_template("php_template.php")
        
        assert result["is_valid"] is True
        assert result["template_type"] == "php"
    
    def test_validate_template_mixed(self):
        """Test template validation for mixed template."""
        template_content = "<h1>{{title}}</h1><?=variable?><p>Content</p>"
        self.create_test_template("mixed.html", template_content)
        
        result = self.manager.validate_template("mixed.html")
        
        assert result["is_valid"] is True
        assert result["template_type"] == "mixed"
    
    def test_render_template_auto_detection(self):
        """Test automatic template format detection."""
        # HTML template
        html_content = "<h1>{{title}}</h1>"
        self.create_test_template("auto.html", html_content)
        
        result = self.manager.render_template("auto.html", self.test_data, "auto")
        assert "Test Product Review" in result
        
        # PHP template
        php_content = "<?php echo 'test'; ?><h1>{{title}}</h1>"
        self.create_test_template("auto.php", php_content)
        
        result = self.manager.render_template("auto.php", self.test_data, "auto")
        assert "Test Product Review" in result
        assert "<?php echo" in result
    
    def test_render_template_explicit_format(self):
        """Test explicit format specification."""
        template_content = "<h1>{{title}}</h1><p>{{product_name}}</p>"
        self.create_test_template("explicit.html", template_content)
        
        # Test different explicit formats
        html_result = self.manager.render_template("explicit.html", self.test_data, "html")
        assert "Test Product Review" in html_result
        
        mixed_result = self.manager.render_template("explicit.html", self.test_data, "mixed")
        assert "Test Product Review" in mixed_result
    
    def test_render_template_unsupported_format(self):
        """Test unsupported format handling."""
        template_content = "<h1>{{title}}</h1>"
        self.create_test_template("unsupported.html", template_content)
        
        with pytest.raises(TemplateError):
            self.manager.render_template("unsupported.html", self.test_data, "unsupported")
    
    def test_custom_filters(self):
        """Test custom Jinja2 filters."""
        # Test that custom filters are available
        assert "preserve_php" in self.manager.jinja_env.filters
        assert "format_date" in self.manager.jinja_env.filters
        assert "japanese_format" in self.manager.jinja_env.filters
    
    def test_error_handling(self):
        """Test error handling in template operations."""
        # Test with invalid template name
        with pytest.raises(TemplateError):
            self.manager.render_html("nonexistent.html", self.test_data)
        
        # Test with invalid data
        template_content = "<h1>{{title}}</h1>"
        self.create_test_template("error_test.html", template_content)
        
        # Should handle gracefully
        result = self.manager.render_html("error_test.html", {})
        assert isinstance(result, str)
    
    def test_japanese_content_processing(self):
        """Test processing of Japanese content."""
        japanese_content = """
        <h1>{{title}}</h1>
        <p>商品名：{{product_name}}</p>
        <p>カテゴリ：{{category}}</p>
        <p>レビュアー：{{reviewer_name}}</p>
        """
        self.create_test_template("japanese.html", japanese_content)
        
        japanese_data = {
            'title': 'テスト商品レビュー',
            'product_name': 'テスト商品名',
            'category': 'テストカテゴリ',
            'reviewer_name': 'テスト評価者'
        }
        
        result = self.manager.render_html("japanese.html", japanese_data)
        
        assert 'テスト商品レビュー' in result
        assert 'テスト商品名' in result
        assert 'テストカテゴリ' in result
        assert 'テスト評価者' in result
    
    def test_complex_template_processing(self):
        """Test complex template with multiple features."""
        complex_content = """
        <h1>{{title}}</h1>
        <p>Product: product_code ({{product_name}})</p>
        <p>Date: 2025/00/00</p>
        <p>Rating: {{rating}}/5</p>
        <img src="<?=prod_info("test_code", "mimg")?>" alt="{{product_name}}">
        <div>{{content|safe}}</div>
        """
        self.create_test_template("complex.html", complex_content)
        
        result = self.manager.render_mixed_template("complex.html", self.test_data)
        
        # Check all types of processing
        assert "Test Product Review" in result  # Jinja2 variable
        assert "TEST123" in result  # Product code placeholder and PHP function
        assert "2025/" in result  # Date placeholder
        assert "5/5" in result  # Rating
        assert "<?=prod_info(" in result  # PHP function preserved
        assert "This is test content" in result  # Safe content