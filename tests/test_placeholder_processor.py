"""
Tests for placeholder processing system.
"""

import pytest
from datetime import datetime

from atobusu.templates.placeholder_processor import PlaceholderProcessor
from atobusu.core.exceptions import ProcessingError


class TestPlaceholderProcessor:
    """Test cases for PlaceholderProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = PlaceholderProcessor()
        
        # Sample data for testing
        self.test_data = {
            'product_code': 'サンプル商品コード123456',
            'product_name': 'テスト商品名',
            'category': 'テストカテゴリ',
            'reviewer_name': 'テスト評価者名前',
            'rating': 5,
            'dates': {
                'post_date': '2025/01/15',
                'short_date': '25/01/15',
                'update_date': '2025/01/20'
            },
            'title': 'Test Title',
            'description': 'Test Description'
        }
    
    def test_processor_initialization(self):
        """Test PlaceholderProcessor initialization."""
        assert self.processor is not None
        assert hasattr(self.processor, 'placeholder_patterns')
        assert hasattr(self.processor, 'compiled_patterns')
        assert 'product_code' in self.processor.placeholder_patterns
        assert 'date_full' in self.processor.placeholder_patterns
        assert 'php_function' in self.processor.placeholder_patterns
    
    def test_process_product_codes_basic(self):
        """Test basic product code processing."""
        content = "Product code: 商品コード here"
        result = self.processor.process_product_codes(content, self.test_data)
        
        assert self.test_data['product_code'] in result
        assert result != content  # Should be changed
    
    def test_process_product_codes_multiple_patterns(self):
        """Test product code processing with multiple patterns."""
        content = "商品コード and product_code and 製品コード"
        result = self.processor.process_product_codes(content, self.test_data)
        
        # Should replace all patterns
        expected_code = self.test_data['product_code']
        assert result.count(expected_code) >= 1
    
    def test_process_product_codes_empty_data(self):
        """Test product code processing with empty data."""
        content = "Product code: 商品コード here"
        empty_data = {}
        result = self.processor.process_product_codes(content, empty_data)
        
        # Should not crash, content might be unchanged
        assert isinstance(result, str)
    
    def test_process_date_placeholders_full_format(self):
        """Test full date format processing."""
        content = "Date: 2025/00/00 here"
        result = self.processor.process_date_placeholders(content, self.test_data)
        
        assert '2025/01/15' in result or '2025/' in result  # Should contain actual date
        assert '2025/00/00' not in result  # Placeholder should be replaced
    
    def test_process_date_placeholders_short_format(self):
        """Test short date format processing."""
        content = "Short date: '25/00/00 here"
        result = self.processor.process_date_placeholders(content, self.test_data)
        
        assert "25/01/15" in result or "25/" in result  # Should contain actual short date
        assert "'25/00/00" not in result  # Placeholder should be replaced
    
    def test_process_date_placeholders_named(self):
        """Test named date placeholder processing."""
        content = "Posted on post_date and updated on update_date"
        result = self.processor.process_date_placeholders(content, self.test_data)
        
        assert '2025/01/15' in result  # post_date
        assert '2025/01/20' in result  # update_date
        assert 'post_date' not in result  # Placeholder should be replaced
    
    def test_process_date_placeholders_current_date(self):
        """Test current date processing."""
        content = "Current: current_date and current_short_date"
        # Pass empty dates dict to trigger current date logic
        data_with_empty_dates = {'dates': {}}
        result = self.processor.process_date_placeholders(content, data_with_empty_dates)
        
        # Should contain current year
        current_year = str(datetime.now().year)
        assert current_year in result
        assert 'current_date' not in result  # Should be replaced
    
    def test_process_php_function_params_basic(self):
        """Test basic PHP function parameter processing."""
        content = '<?=prod_info("商品コード123", "pname")?>'
        result = self.processor.process_php_function_params(content, self.test_data)
        
        # Should replace the product code parameter
        assert self.test_data['product_code'] in result
        assert 'pname' in result  # Second parameter should be preserved
        assert '<?=' in result and '?>' in result  # PHP syntax preserved
    
    def test_process_php_function_params_multiple(self):
        """Test multiple PHP function processing."""
        content = '''
        <?=prod_info("商品コード123", "pname")?>
        <?=prod_info("商品コード456", "price")?>
        '''
        result = self.processor.process_php_function_params(content, self.test_data)
        
        # Should replace both instances
        assert result.count(self.test_data['product_code']) == 2
        assert 'pname' in result and 'price' in result
    
    def test_process_php_function_params_no_match(self):
        """Test PHP function processing with no matches."""
        content = "No PHP functions here"
        result = self.processor.process_php_function_params(content, self.test_data)
        
        assert result == content  # Should be unchanged
    
    def test_process_generic_placeholders(self):
        """Test generic {{variable}} placeholder processing."""
        content = "Title: {{title}} and Description: {{description}}"
        result = self.processor.process_generic_placeholders(content, self.test_data)
        
        assert 'Test Title' in result
        assert 'Test Description' in result
        assert '{{title}}' not in result
        assert '{{description}}' not in result
    
    def test_process_generic_placeholders_nested(self):
        """Test nested generic placeholder processing."""
        nested_data = {
            'template_data': {
                'product_name': 'Nested Product'
            }
        }
        content = "Product: {{template_data.product_name}}"
        result = self.processor.process_generic_placeholders(content, nested_data)
        
        assert 'Nested Product' in result
        assert '{{template_data.product_name}}' not in result
    
    def test_process_generic_placeholders_missing(self):
        """Test generic placeholder processing with missing variables."""
        content = "Missing: {{missing_variable}}"
        result = self.processor.process_generic_placeholders(content, self.test_data)
        
        # Should keep original placeholder when variable not found
        assert '{{missing_variable}}' in result
    
    def test_process_template_variables(self):
        """Test ${variable} template variable processing."""
        content = "Title: ${title} and Rating: ${rating}"
        result = self.processor.process_template_variables(content, self.test_data)
        
        assert 'Test Title' in result
        assert '5' in result  # Rating converted to string
        assert '${title}' not in result
        assert '${rating}' not in result
    
    def test_process_template_variables_missing(self):
        """Test template variable processing with missing variables."""
        content = "Missing: ${missing_var}"
        result = self.processor.process_template_variables(content, self.test_data)
        
        # Should keep original variable when not found
        assert '${missing_var}' in result
    
    def test_apply_all_replacements_comprehensive(self):
        """Test comprehensive placeholder replacement."""
        content = '''
        Product: product_code
        Date: 2025/00/00
        PHP: <?=prod_info("test_code", "pname")?>
        Generic: {{title}}
        Template: ${rating}
        '''
        
        result = self.processor.apply_all_replacements(content, self.test_data)
        
        # Check all types of replacements
        assert self.test_data['product_code'] in result  # Product code
        assert '2025/01/15' in result or '2025/' in result  # Date
        assert 'Test Title' in result  # Generic placeholder
        assert '5' in result  # Template variable
        assert '<?=' in result and '?>' in result  # PHP syntax preserved
    
    def test_apply_all_replacements_empty_content(self):
        """Test replacement with empty content."""
        result = self.processor.apply_all_replacements("", self.test_data)
        assert result == ""
        
        result = self.processor.apply_all_replacements(None, self.test_data)
        assert result is None
    
    def test_apply_all_replacements_empty_data(self):
        """Test replacement with empty data."""
        content = "Test {{title}} content"
        result = self.processor.apply_all_replacements(content, {})
        
        # Should not crash, placeholders might remain
        assert isinstance(result, str)
    
    def test_get_placeholder_stats(self):
        """Test placeholder statistics."""
        content = '''
        商品コード and product_code
        2025/00/00 and '25/00/00
        <?=prod_info("test", "pname")?>
        {{title}} and {{description}}
        ${rating} and ${category}
        '''
        
        stats = self.processor.get_placeholder_stats(content)
        
        assert isinstance(stats, dict)
        assert 'product_code_patterns' in stats
        assert 'date_placeholders' in stats
        assert 'php_functions' in stats
        assert 'generic_placeholders' in stats
        assert 'template_variables' in stats
        
        # Check some expected counts
        assert stats['date_placeholders'] == 2  # Two date formats
        assert stats['php_functions'] == 1  # One PHP function
        assert stats['generic_placeholders'] == 2  # Two generic placeholders
        assert stats['template_variables'] == 2  # Two template variables
    
    def test_get_placeholder_stats_empty(self):
        """Test placeholder statistics with empty content."""
        stats = self.processor.get_placeholder_stats("")
        assert all(count == 0 for count in stats.values())
        
        stats = self.processor.get_placeholder_stats(None)
        assert stats == {}
    
    def test_add_custom_pattern(self):
        """Test adding custom placeholder patterns."""
        custom_pattern = r'\[custom:([^]]+)\]'
        self.processor.add_custom_pattern('custom', custom_pattern)
        
        assert 'custom' in self.processor.placeholder_patterns
        assert 'custom' in self.processor.compiled_patterns
        assert self.processor.placeholder_patterns['custom'] == custom_pattern
    
    def test_add_custom_pattern_invalid(self):
        """Test adding invalid custom pattern."""
        invalid_pattern = r'[invalid regex ('
        
        with pytest.raises(ProcessingError):
            self.processor.add_custom_pattern('invalid', invalid_pattern)
    
    def test_real_world_template_content(self):
        """Test with real-world template content similar to provided examples."""
        # Based on the index_template.html provided
        content = '''
        <a href="/review-product_code" target="_self">
            <img src="<?=prod_info("test_code", "mimg")?>" alt="<?=prod_info("test_code", "pname")?>">
        </a>
        <div class="item_post_date">2025/00/00</div>
        <div class="item_post_name">全体：{{reviewer_name}}</div>
        '''
        
        result = self.processor.apply_all_replacements(content, self.test_data)
        
        # Check replacements
        assert self.test_data['product_code'] in result
        assert '2025/01/15' in result or '2025/' in result
        assert self.test_data['reviewer_name'] in result
        assert '<?=' in result and '?>' in result  # PHP preserved
    
    def test_japanese_content_processing(self):
        """Test processing with Japanese content."""
        japanese_data = {
            'product_code': 'テスト商品コード001',
            'product_name': 'テスト商品名',
            'dates': {'post_date': '2025/01/15'},
            'category': 'テストカテゴリ'
        }
        
        content = '''
        商品名：{{product_name}}
        カテゴリ：{{category}}
        投稿日：2025/00/00
        '''
        
        result = self.processor.apply_all_replacements(content, japanese_data)
        
        assert 'テスト商品名' in result
        assert 'テストカテゴリ' in result
        assert '2025/01/15' in result
    
    def test_mixed_php_html_content(self):
        """Test processing mixed PHP and HTML content."""
        content = '''
        <li>
            <a href="/review-<?=prod_info("test_code", "pname")?>" target="_self">
                <?=prod_info("test_code", "pname")?>
            </a> 
            【{{category}}】'25/00/00 UP
        </li>
        '''
        
        result = self.processor.apply_all_replacements(content, self.test_data)
        
        # Check that HTML structure is preserved
        assert '<li>' in result and '</li>' in result
        assert '<a href=' in result
        
        # Check replacements
        assert self.test_data['category'] in result
        assert "25/01/15" in result or "25/" in result
    
    def test_error_handling(self):
        """Test error handling in placeholder processing."""
        # Test with invalid data types
        result = self.processor.apply_all_replacements("test", None)
        assert result == "test"  # Should handle gracefully
        
        # Test with complex nested data
        complex_data = {
            'nested': {'deep': {'value': 'test'}}
        }
        content = "Value: {{nested.deep.value}}"
        result = self.processor.process_generic_placeholders(content, complex_data)
        assert 'test' in result
    
    def test_performance_large_content(self):
        """Test performance with large content."""
        # Create large content with various placeholders
        large_content = '''
        Product: 商品コード
        Date: 2025/00/00
        PHP: <?=prod_info("商品コード123", "pname")?>
        Generic: {{title}}
        Template: ${rating}
        ''' * 100  # Repeat 100 times
        
        # Should complete without issues
        result = self.processor.apply_all_replacements(large_content, self.test_data)
        assert len(result) > len(large_content)  # Should be longer due to replacements
        assert self.test_data['product_code'] in result
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        edge_cases = [
            "",  # Empty string
            " ",  # Whitespace only
            "No placeholders here",  # No placeholders
            "{{}}",  # Empty placeholder
            "${}",  # Empty template variable
            "<?=prod_info(\"\", \"\")?>"  # Empty PHP function params
        ]
        
        for content in edge_cases:
            # Should not raise exceptions
            result = self.processor.apply_all_replacements(content, self.test_data)
            assert isinstance(result, str) or result is None