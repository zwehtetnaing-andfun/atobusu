"""
Character conversion system for Atobusu application.

Handles conversion of special characters, quotes, circled numbers,
and Japanese text according to the specified rules.
"""

import re
from typing import Dict, Any, Optional
from atobusu.core.logging_config import get_logger
from atobusu.core.exceptions import ProcessingError


class CharacterConverter:
    """
    Handles character conversion and text processing for Atobusu.
    
    Converts special characters, quotes, circled numbers, and handles
    Japanese character encoding according to the application requirements.
    """
    
    def __init__(self, conversion_rules: Optional[Dict[str, Dict[str, str]]] = None):
        """
        Initialize the character converter.
        
        Args:
            conversion_rules: Optional custom conversion rules dictionary
        """
        self.logger = get_logger(__name__)
        
        # Default conversion rules
        self.default_rules = {
            'quotes': {
                '"': '\u201C'   # Straight quote to opening curly quote (U+201C)
            },
            'symbols': {
                '※': '※'  # Keep reference mark as-is
            },
            'circled_numbers': {
                '①': '&#9312;', '②': '&#9313;', '③': '&#9314;',
                '④': '&#9315;', '⑤': '&#9316;', '⑥': '&#9317;',
                '⑦': '&#9318;', '⑧': '&#9319;', '⑨': '&#9320;',
                '⑩': '&#9321;', '⑪': '&#9322;', '⑫': '&#9323;',
                '⑬': '&#9324;', '⑭': '&#9325;', '⑮': '&#9326;',
                '⑯': '&#9327;', '⑰': '&#9328;', '⑱': '&#9329;',
                '⑲': '&#9330;', '⑳': '&#9331;'
            },
            'special_symbols': {
                '◎': '&#9678;',    # Black circle
                'ハート': '&#9825;',  # Heart symbol
                '♪': '&#9834;'     # Musical note
            }
        }
        
        # Use provided rules or defaults
        self.conversion_rules = conversion_rules or self.default_rules
        
        # Compile regex patterns for efficient processing
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient character matching."""
        try:
            # Pattern for straight quotes (but not already converted curly quotes)
            self.quote_pattern = re.compile(r'(?<!")(?<!")\"(?!")(?!")')
            
            # Pattern for circled numbers
            circled_chars = ''.join(self.conversion_rules.get('circled_numbers', {}).keys())
            if circled_chars:
                self.circled_pattern = re.compile(f'[{re.escape(circled_chars)}]')
            else:
                self.circled_pattern = None
            
            # Pattern for special symbols
            special_chars = ''.join(self.conversion_rules.get('special_symbols', {}).keys())
            if special_chars:
                self.special_pattern = re.compile(f'[{re.escape(special_chars)}]')
            else:
                self.special_pattern = None
                
        except re.error as e:
            raise ProcessingError("Failed to compile regex patterns", str(e))
    
    def convert_quotes(self, text: str) -> str:
        """
        Convert straight quotes to curly quotes.
        
        Args:
            text: Input text containing quotes
            
        Returns:
            Text with converted quotes
        """
        if not text:
            return text
        
        try:
            quote_rules = self.conversion_rules.get('quotes', {})
            
            # Simple approach: convert all straight quotes to opening curly quotes
            # In a more sophisticated implementation, you might want to alternate
            # between opening and closing quotes based on context
            result = text
            if '"' in quote_rules:
                opening_quote = quote_rules['"']
                result = result.replace('"', opening_quote)
            
            self.logger.debug(f"Quote conversion: '{text}' -> '{result}'")
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to convert quotes in text: {text[:50]}...", str(e))
    
    def convert_circled_numbers(self, text: str) -> str:
        """
        Convert circled numbers to HTML entities.
        
        Args:
            text: Input text containing circled numbers
            
        Returns:
            Text with circled numbers converted to HTML entities
        """
        if not text or not self.circled_pattern:
            return text
        
        try:
            circled_rules = self.conversion_rules.get('circled_numbers', {})
            
            def replace_circled(match):
                char = match.group(0)
                return circled_rules.get(char, char)
            
            result = self.circled_pattern.sub(replace_circled, text)
            
            if result != text:
                self.logger.debug(f"Circled number conversion: '{text}' -> '{result}'")
            
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to convert circled numbers in text: {text[:50]}...", str(e))
    
    def convert_symbols(self, text: str) -> str:
        """
        Convert special symbols to HTML entities.
        
        Args:
            text: Input text containing special symbols
            
        Returns:
            Text with special symbols converted
        """
        if not text:
            return text
        
        try:
            # Handle symbols that should be kept as-is
            symbol_rules = self.conversion_rules.get('symbols', {})
            special_rules = self.conversion_rules.get('special_symbols', {})
            
            result = text
            
            # Apply special symbol conversions
            for old_char, new_char in special_rules.items():
                if old_char in result:
                    result = result.replace(old_char, new_char)
                    self.logger.debug(f"Symbol conversion: '{old_char}' -> '{new_char}'")
            
            # Note: symbols in 'symbols' rules are kept as-is (like ※)
            # so we don't need to process them
            
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to convert symbols in text: {text[:50]}...", str(e))
    
    def handle_japanese_encoding(self, text: str, encoding: str = 'utf-8') -> str:
        """
        Handle Japanese character encoding and validation.
        
        Args:
            text: Input text with Japanese characters
            encoding: Target encoding (default: utf-8)
            
        Returns:
            Properly encoded text
        """
        if not text:
            return text
        
        try:
            # Ensure text is properly encoded
            if isinstance(text, bytes):
                # Decode bytes to string
                text = text.decode(encoding, errors='replace')
            elif isinstance(text, str):
                # Encode and decode to ensure proper encoding
                text = text.encode(encoding, errors='replace').decode(encoding)
            
            # Validate that Japanese characters are properly handled
            # This is a basic check - you might want more sophisticated validation
            japanese_chars = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text)
            if japanese_chars:
                self.logger.debug(f"Found {len(japanese_chars)} Japanese characters")
            
            return text
            
        except Exception as e:
            raise ProcessingError(f"Failed to handle Japanese encoding for text: {text[:50]}...", str(e))
    
    def apply_all_conversions(self, text: str, encoding: str = 'utf-8') -> str:
        """
        Apply all character conversions in the correct order.
        
        Args:
            text: Input text to process
            encoding: Character encoding to use
            
        Returns:
            Text with all conversions applied
        """
        if not text:
            return text
        
        try:
            self.logger.debug(f"Starting character conversion for text: {text[:100]}...")
            
            # Step 1: Handle Japanese encoding
            result = self.handle_japanese_encoding(text, encoding)
            
            # Step 2: Convert quotes
            result = self.convert_quotes(result)
            
            # Step 3: Convert circled numbers
            result = self.convert_circled_numbers(result)
            
            # Step 4: Convert special symbols
            result = self.convert_symbols(result)
            
            if result != text:
                self.logger.info("Character conversion completed with changes")
            else:
                self.logger.debug("Character conversion completed with no changes")
            
            return result
            
        except ProcessingError:
            # Re-raise processing errors
            raise
        except Exception as e:
            raise ProcessingError(f"Failed to apply character conversions", str(e))
    
    def add_conversion_rule(self, category: str, old_char: str, new_char: str):
        """
        Add a new conversion rule.
        
        Args:
            category: Rule category ('quotes', 'symbols', 'circled_numbers', 'special_symbols')
            old_char: Character to convert from
            new_char: Character to convert to
        """
        if category not in self.conversion_rules:
            self.conversion_rules[category] = {}
        
        self.conversion_rules[category][old_char] = new_char
        
        # Recompile patterns if necessary
        if category in ['circled_numbers', 'special_symbols']:
            self._compile_patterns()
        
        self.logger.info(f"Added conversion rule: {category}['{old_char}'] -> '{new_char}'")
    
    def get_conversion_stats(self, text: str) -> Dict[str, int]:
        """
        Get statistics about potential conversions in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with conversion statistics
        """
        if not text:
            return {}
        
        stats = {
            'straight_quotes': len(re.findall(r'"', text)),
            'circled_numbers': 0,
            'special_symbols': 0,
            'japanese_chars': len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
        }
        
        # Count circled numbers
        circled_rules = self.conversion_rules.get('circled_numbers', {})
        for char in circled_rules.keys():
            stats['circled_numbers'] += text.count(char)
        
        # Count special symbols
        special_rules = self.conversion_rules.get('special_symbols', {})
        for char in special_rules.keys():
            stats['special_symbols'] += text.count(char)
        
        return stats