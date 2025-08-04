"""
Tests for character conversion system.
"""

import pytest
from atobusu.core.character_converter import CharacterConverter
from atobusu.core.exceptions import ProcessingError


class TestCharacterConverter:
    """Test cases for CharacterConverter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = CharacterConverter()
    
    def test_convert_quotes_basic(self):
        """Test basic quote conversion."""
        text = 'Hello "world" test'
        result = self.converter.convert_quotes(text)
        assert '\u201C' in result  # Should contain left double quotation mark
        assert result != text  # Should be changed
    
    def test_convert_quotes_empty(self):
        """Test quote conversion with empty text."""
        assert self.converter.convert_quotes("") == ""
        assert self.converter.convert_quotes(None) == None
    
    def test_convert_quotes_no_quotes(self):
        """Test quote conversion with no quotes."""
        text = "Hello world test"
        result = self.converter.convert_quotes(text)
        assert result == text  # Should be unchanged
    
    def test_convert_circled_numbers(self):
        """Test circled number conversion."""
        test_cases = [
            ("Test ① item", "Test &#9312; item"),
            ("Items ②③④", "Items &#9313;&#9314;&#9315;"),
            ("Number ⑩ is ten", "Number &#9321; is ten"),
            ("No circled numbers", "No circled numbers"),  # No change
        ]
        
        for input_text, expected in test_cases:
            result = self.converter.convert_circled_numbers(input_text)
            assert result == expected, f"Failed for input: {input_text}"
    
    def test_convert_symbols(self):
        """Test special symbol conversion."""
        test_cases = [
            ("Symbol ◎ test", "Symbol &#9678; test"),
            ("Heart ハート symbol", "Heart &#9825; symbol"),
            ("Music ♪ note", "Music &#9834; note"),
            ("Keep ※ as-is", "Keep ※ as-is"),  # Should not change
            ("No special symbols", "No special symbols"),  # No change
        ]
        
        for input_text, expected in test_cases:
            result = self.converter.convert_symbols(input_text)
            assert result == expected, f"Failed for input: {input_text}"
    
    def test_handle_japanese_encoding(self):
        """Test Japanese character encoding handling."""
        japanese_text = "こんにちは世界"
        result = self.converter.handle_japanese_encoding(japanese_text)
        assert result == japanese_text
        assert isinstance(result, str)
    
    def test_handle_japanese_encoding_bytes(self):
        """Test Japanese encoding with bytes input."""
        japanese_text = "こんにちは世界"
        bytes_input = japanese_text.encode('utf-8')
        result = self.converter.handle_japanese_encoding(bytes_input)
        assert result == japanese_text
    
    def test_apply_all_conversions(self):
        """Test applying all conversions together."""
        input_text = 'Test "quote" with ① and ◎ symbols'
        result = self.converter.apply_all_conversions(input_text)
        
        # Should contain converted elements
        assert '&#9312;' in result  # Circled number
        assert '&#9678;' in result  # Special symbol
        assert '\u201C' in result  # Converted quote
    
    def test_apply_all_conversions_complex(self):
        """Test complex text with multiple conversion types."""
        input_text = 'Review "Product ①" has ◎ rating with ♪ sound and ※ note'
        result = self.converter.apply_all_conversions(input_text)
        
        # Check all conversions
        assert '&#9312;' in result  # ①
        assert '&#9678;' in result  # ◎
        assert '&#9834;' in result  # ♪
        assert '※' in result       # Should remain unchanged
        assert '\u201C' in result  # Quote conversion
    
    def test_apply_all_conversions_japanese(self):
        """Test conversions with Japanese text."""
        input_text = 'テスト "商品①" は◎評価でハート付き'
        result = self.converter.apply_all_conversions(input_text)
        
        # Check Japanese characters are preserved
        assert 'テスト' in result
        assert '商品' in result
        assert '評価' in result
        
        # Check conversions
        assert '&#9312;' in result  # ①
        assert '&#9678;' in result  # ◎
        assert '&#9825;' in result  # ハート
    
    def test_add_conversion_rule(self):
        """Test adding custom conversion rules."""
        self.converter.add_conversion_rule('special_symbols', '★', '&#9733;')
        
        text = "Star ★ symbol"
        result = self.converter.convert_symbols(text)
        assert '&#9733;' in result
    
    def test_get_conversion_stats(self):
        """Test conversion statistics."""
        text = 'Text with "quotes" and ① ② numbers plus ◎ symbol'
        stats = self.converter.get_conversion_stats(text)
        
        assert stats['straight_quotes'] == 2
        assert stats['circled_numbers'] == 2
        assert stats['special_symbols'] == 1
        assert isinstance(stats['japanese_chars'], int)
    
    def test_get_conversion_stats_japanese(self):
        """Test conversion statistics with Japanese text."""
        text = 'テスト文字列 with "quotes" and ①'
        stats = self.converter.get_conversion_stats(text)
        
        assert stats['japanese_chars'] > 0
        assert stats['straight_quotes'] == 2
        assert stats['circled_numbers'] == 1
    
    def test_custom_conversion_rules(self):
        """Test converter with custom rules."""
        custom_rules = {
            'quotes': {'"': '「'},  # Only opening quote rule
            'special_symbols': {'★': '&#9733;'}
        }
        
        converter = CharacterConverter(custom_rules)
        text = 'Test "quote" with ★'
        result = converter.apply_all_conversions(text)
        
        assert '「' in result
        assert '&#9733;' in result
    
    def test_error_handling(self):
        """Test error handling in character conversion."""
        # Test with None input (should handle gracefully)
        result = self.converter.apply_all_conversions(None)
        assert result is None
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        test_cases = [
            "",  # Empty string
            " ",  # Whitespace only
            "No special characters",  # No conversions needed
            "①②③④⑤⑥⑦⑧⑨⑩",  # Only circled numbers
            '""""',  # Multiple quotes
            "◎◎◎",  # Repeated symbols
        ]
        
        for text in test_cases:
            # Should not raise exceptions
            result = self.converter.apply_all_conversions(text)
            assert isinstance(result, str) or result is None
    
    def test_performance_large_text(self):
        """Test performance with large text."""
        # Create a large text with various characters
        large_text = ('Test "text" with ① and ◎ symbols. ' * 1000)
        
        # Should complete without issues
        result = self.converter.apply_all_conversions(large_text)
        assert len(result) > len(large_text)  # Should be longer due to HTML entities
    
    def test_regex_pattern_compilation(self):
        """Test regex pattern compilation."""
        # Should not raise exceptions during initialization
        converter = CharacterConverter()
        assert converter.quote_pattern is not None
        assert converter.circled_pattern is not None
        assert converter.special_pattern is not None
    
    def test_preserve_html_entities(self):
        """Test that existing HTML entities are preserved."""
        text = "Already has &#9312; entity and new ② number"
        result = self.converter.convert_circled_numbers(text)
        
        # Should preserve existing entity and convert new number
        assert '&#9312;' in result
        assert '&#9313;' in result
    
    def test_mixed_content_conversion(self):
        """Test conversion of mixed content similar to template files."""
        # Similar to content from the provided template files
        template_content = '''
        <h4 class="h4_tit">商品名が入ります</h4>
        <p>基本文章が入ります with "quotes" and ① rating ◎</p>
        '''
        
        result = self.converter.apply_all_conversions(template_content)
        
        # Check that HTML structure is preserved
        assert '<h4' in result
        assert '</p>' in result
        
        # Check conversions
        assert '&#9312;' in result  # ①
        assert '&#9678;' in result  # ◎
        assert '\u201C' in result  # Quote conversion