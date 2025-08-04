"""
Placeholder processing system for Atobusu application.

Handles template variable replacement, product code processing, date placeholders,
and PHP function parameter replacement while preserving syntax.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date
from pathlib import Path

from atobusu.core.logging_config import get_logger
from atobusu.core.exceptions import ProcessingError, TemplateError


class PlaceholderProcessor:
    """
    Processes template placeholders and variables for Atobusu.
    
    Handles product codes, date placeholders, PHP function parameters,
    and comprehensive pattern recognition and replacement.
    """
    
    def __init__(self):
        """Initialize the placeholder processor."""
        self.logger = get_logger(__name__)
        
        # Placeholder patterns based on the design document
        self.placeholder_patterns = {
            'product_code': r'[^/]*コード[^/]*',  # Matches product code patterns
            'date_full': r'2025/00/00',  # Full date format
            'date_short': r"'25/00/00",  # Short date format
            'php_function': r'<\?=prod_info\("([^"]*)", "([^"]*)"\)\?>',  # PHP function calls
            'category_placeholder': r'カテゴリ[^}]*',  # Category placeholders
        }
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
        
        # Default date formats
        self.date_formats = {
            'full': '%Y/%m/%d',      # 2025/01/15
            'short': "'%y/%m/%d",    # '25/01/15
            'iso': '%Y-%m-%d',       # 2025-01-15
            'japanese': '%Y年%m月%d日'  # 2025年01月15日
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        try:
            self.compiled_patterns = {}
            
            # Product code pattern
            self.compiled_patterns['product_code'] = re.compile(
                self.placeholder_patterns['product_code']
            )
            
            # Date patterns
            self.compiled_patterns['date_full'] = re.compile(
                re.escape(self.placeholder_patterns['date_full'])
            )
            self.compiled_patterns['date_short'] = re.compile(
                re.escape(self.placeholder_patterns['date_short'])
            )
            
            # PHP function pattern
            self.compiled_patterns['php_function'] = re.compile(
                self.placeholder_patterns['php_function']
            )
            
            # Category pattern
            self.compiled_patterns['category_placeholder'] = re.compile(
                self.placeholder_patterns['category_placeholder']
            )
            
            # Generic placeholder pattern for {{variable}} style
            self.compiled_patterns['generic_placeholder'] = re.compile(
                r'\{\{([^}]+)\}\}'
            )
            
            # Template variable pattern for ${variable} style
            self.compiled_patterns['template_variable'] = re.compile(
                r'\$\{([^}]+)\}'
            )
            
        except re.error as e:
            raise ProcessingError("Failed to compile placeholder patterns", str(e))
    
    def process_product_codes(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process product code placeholders with pattern matching.
        
        Args:
            content: Template content containing product code placeholders
            data: Data dictionary containing product information
            
        Returns:
            Content with product codes replaced
        """
        if not content or not data:
            return content
        
        try:
            result = content
            product_code = data.get('product_code', '')
            
            # Handle specific product code placeholders (more targeted approach)
            if product_code:
                # Only replace exact placeholder matches, not patterns
                pass  # Skip pattern matching for now to avoid over-replacement
            
            # Handle specific product code placeholders
            placeholders = [
                '商品コード', 'product_code', 'PRODUCT_CODE',
                '製品コード', 'item_code', 'code'
            ]
            
            for placeholder in placeholders:
                if placeholder in result and product_code:
                    result = result.replace(placeholder, product_code)
                    self.logger.debug(f"Replaced placeholder '{placeholder}' with '{product_code}'")
            
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to process product codes", str(e))
    
    def process_date_placeholders(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process date placeholders for multiple date formats.
        
        Args:
            content: Template content containing date placeholders
            data: Data dictionary containing date information
            
        Returns:
            Content with date placeholders replaced
        """
        if not content or not data:
            return content
        
        try:
            result = content
            
            # Get dates from data
            dates = data.get('dates', {})
            if not dates and 'date' in data:
                dates = {'date': data['date']}
            
            # Process full date format (2025/00/00)
            if self.placeholder_patterns['date_full'] in result:
                replacement_date = self._get_date_replacement(dates, 'full')
                result = result.replace(
                    self.placeholder_patterns['date_full'], 
                    replacement_date
                )
                self.logger.debug(f"Replaced full date placeholder with '{replacement_date}'")
            
            # Process short date format ('25/00/00)
            if self.placeholder_patterns['date_short'] in result:
                replacement_date = self._get_date_replacement(dates, 'short')
                result = result.replace(
                    self.placeholder_patterns['date_short'], 
                    replacement_date
                )
                self.logger.debug(f"Replaced short date placeholder with '{replacement_date}'")
            
            # Process named date placeholders
            date_placeholders = {
                'post_date': dates.get('post_date', ''),
                'update_date': dates.get('update_date', ''),
                'publish_date': dates.get('publish_date', ''),
                'review_date': dates.get('review_date', ''),
                'short_date': dates.get('short_date', ''),
                'current_date': self._format_current_date('full'),
                'current_short_date': self._format_current_date('short')
            }
            
            for placeholder, value in date_placeholders.items():
                if value and placeholder in result:
                    result = result.replace(placeholder, str(value))
                    self.logger.debug(f"Replaced date placeholder '{placeholder}' with '{value}'")
            
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to process date placeholders", str(e))
    
    def process_php_function_params(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process PHP function parameter replacement while preserving syntax.
        
        Args:
            content: Template content containing PHP function calls
            data: Data dictionary containing replacement values
            
        Returns:
            Content with PHP function parameters replaced
        """
        if not content or not data:
            return content
        
        try:
            result = content
            pattern = self.compiled_patterns['php_function']
            
            def replace_php_function(match):
                param1 = match.group(1)  # First parameter
                param2 = match.group(2)  # Second parameter
                
                # Replace parameters with actual values from data
                new_param1 = self._replace_parameter_value(param1, data)
                new_param2 = param2  # Keep second parameter as-is (usually field name)
                
                # Reconstruct the PHP function call
                return f'<?=prod_info("{new_param1}", "{new_param2}")?>'
            
            result = pattern.sub(replace_php_function, result)
            
            # Log the number of replacements made
            matches = pattern.findall(content)
            if matches:
                self.logger.debug(f"Processed {len(matches)} PHP function calls")
            
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to process PHP function parameters", str(e))
    
    def _replace_parameter_value(self, param: str, data: Dict[str, Any]) -> str:
        """Replace parameter value with data from dictionary."""
        # Check if parameter matches product code pattern
        if 'コード' in param or 'code' in param.lower():
            return data.get('product_code', param)
        
        # Check for other common patterns
        replacements = {
            'product_name': data.get('product_name', param),
            'category': data.get('category', param),
            'reviewer_name': data.get('reviewer_name', param),
        }
        
        for key, value in replacements.items():
            if key in param.lower() or param in value:
                return value
        
        return param  # Return original if no replacement found
    
    def _get_date_replacement(self, dates: Dict[str, str], format_type: str) -> str:
        """Get appropriate date replacement based on format type."""
        if format_type == 'full':
            return dates.get('post_date', dates.get('date', self._format_current_date('full')))
        elif format_type == 'short':
            return dates.get('short_date', dates.get('date', self._format_current_date('short')))
        else:
            return dates.get('date', self._format_current_date('full'))
    
    def _format_current_date(self, format_type: str) -> str:
        """Format current date according to specified type."""
        current_date = datetime.now()
        
        if format_type == 'full':
            return current_date.strftime('%Y/%m/%d')
        elif format_type == 'short':
            return current_date.strftime("'%y/%m/%d")
        elif format_type == 'iso':
            return current_date.strftime('%Y-%m-%d')
        elif format_type == 'japanese':
            return current_date.strftime('%Y年%m月%d日')
        else:
            return current_date.strftime('%Y/%m/%d')
    
    def process_generic_placeholders(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process generic {{variable}} style placeholders.
        
        Args:
            content: Template content containing generic placeholders
            data: Data dictionary containing replacement values
            
        Returns:
            Content with generic placeholders replaced
        """
        if not content or not data:
            return content
        
        try:
            result = content
            pattern = self.compiled_patterns['generic_placeholder']
            
            def replace_placeholder(match):
                variable_name = match.group(1).strip()
                
                # Look for the variable in data
                if variable_name in data:
                    return str(data[variable_name])
                
                # Try nested access (e.g., template_data.product_name)
                if '.' in variable_name:
                    parts = variable_name.split('.')
                    value = data
                    try:
                        for part in parts:
                            value = value[part]
                        return str(value)
                    except (KeyError, TypeError):
                        pass
                
                # Return original placeholder if not found
                self.logger.warning(f"Placeholder '{variable_name}' not found in data")
                return match.group(0)
            
            result = pattern.sub(replace_placeholder, result)
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to process generic placeholders", str(e))
    
    def process_template_variables(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process ${variable} style template variables.
        
        Args:
            content: Template content containing template variables
            data: Data dictionary containing replacement values
            
        Returns:
            Content with template variables replaced
        """
        if not content or not data:
            return content
        
        try:
            result = content
            pattern = self.compiled_patterns['template_variable']
            
            def replace_variable(match):
                variable_name = match.group(1).strip()
                
                if variable_name in data:
                    return str(data[variable_name])
                
                # Return original if not found
                self.logger.warning(f"Template variable '{variable_name}' not found in data")
                return match.group(0)
            
            result = pattern.sub(replace_variable, result)
            return result
            
        except Exception as e:
            raise ProcessingError(f"Failed to process template variables", str(e))
    
    def apply_all_replacements(self, content: str, data: Dict[str, Any]) -> str:
        """
        Apply all placeholder replacements in the correct order.
        
        Args:
            content: Template content to process
            data: Data dictionary containing replacement values
            
        Returns:
            Content with all placeholders replaced
        """
        if not content:
            return content
        
        if not data:
            return content  # Return unchanged if no data
        
        try:
            self.logger.debug(f"Starting placeholder processing for content: {content[:100]}...")
            
            result = content
            
            # Step 1: Process product codes
            result = self.process_product_codes(result, data)
            
            # Step 2: Process date placeholders
            result = self.process_date_placeholders(result, data)
            
            # Step 3: Process PHP function parameters
            result = self.process_php_function_params(result, data)
            
            # Step 4: Process generic placeholders
            result = self.process_generic_placeholders(result, data)
            
            # Step 5: Process template variables
            result = self.process_template_variables(result, data)
            
            if result != content:
                self.logger.info("Placeholder processing completed with changes")
            else:
                self.logger.debug("Placeholder processing completed with no changes")
            
            return result
            
        except ProcessingError:
            raise
        except Exception as e:
            raise ProcessingError(f"Failed to apply placeholder replacements", str(e))
    
    def get_placeholder_stats(self, content: str) -> Dict[str, int]:
        """
        Get statistics about placeholders in content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with placeholder statistics
        """
        if not content:
            return {}
        
        stats = {
            'product_code_patterns': 0,
            'date_placeholders': 0,
            'php_functions': 0,
            'generic_placeholders': 0,
            'template_variables': 0
        }
        
        # Count product code patterns
        stats['product_code_patterns'] = len(
            self.compiled_patterns['product_code'].findall(content)
        )
        
        # Count date placeholders
        stats['date_placeholders'] = (
            content.count(self.placeholder_patterns['date_full']) +
            content.count(self.placeholder_patterns['date_short'])
        )
        
        # Count PHP functions
        stats['php_functions'] = len(
            self.compiled_patterns['php_function'].findall(content)
        )
        
        # Count generic placeholders
        stats['generic_placeholders'] = len(
            self.compiled_patterns['generic_placeholder'].findall(content)
        )
        
        # Count template variables
        stats['template_variables'] = len(
            self.compiled_patterns['template_variable'].findall(content)
        )
        
        return stats
    
    def add_custom_pattern(self, name: str, pattern: str):
        """
        Add a custom placeholder pattern.
        
        Args:
            name: Pattern name
            pattern: Regex pattern string
        """
        try:
            self.placeholder_patterns[name] = pattern
            self.compiled_patterns[name] = re.compile(pattern)
            self.logger.info(f"Added custom pattern '{name}': {pattern}")
        except re.error as e:
            raise ProcessingError(f"Invalid regex pattern '{pattern}'", str(e))