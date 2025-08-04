"""
Template management system for Atobusu application.

Handles Jinja2 template loading, caching, and rendering for HTML, PHP, and mixed content.
Integrates with PlaceholderProcessor for comprehensive template processing.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound, TemplateSyntaxError
import re

from atobusu.core.logging_config import get_logger
from atobusu.core.exceptions import TemplateError, ProcessingError
from atobusu.templates.placeholder_processor import PlaceholderProcessor


class TemplateManager:
    """
    Manages Jinja2 templates for Atobusu application.
    
    Handles template loading, caching, rendering, and integration with
    placeholder processing for HTML, PHP, and mixed content templates.
    """
    
    def __init__(self, template_dir: str, placeholder_processor: Optional[PlaceholderProcessor] = None):
        """
        Initialize the template manager.
        
        Args:
            template_dir: Directory containing template files
            placeholder_processor: Optional PlaceholderProcessor instance
        """
        self.logger = get_logger(__name__)
        self.template_dir = Path(template_dir)
        self.placeholder_processor = placeholder_processor or PlaceholderProcessor()
        
        # Create template directory if it doesn't exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self._setup_jinja_environment()
        
        # Template cache
        self._template_cache: Dict[str, Template] = {}
        
        # Supported template types
        self.template_types = {
            'html': ['.html', '.htm'],
            'php': ['.php'],
            'mixed': ['.html', '.htm', '.php', '.tpl']
        }
        
        # PHP preservation patterns
        self.php_patterns = {
            'php_tags': re.compile(r'<\?(?:php)?\s.*?\?>', re.DOTALL | re.IGNORECASE),
            'php_echo': re.compile(r'<\?=.*?\?>', re.DOTALL),
            'php_short': re.compile(r'<\?.*?\?>', re.DOTALL)
        }
    
    def _setup_jinja_environment(self):
        """Set up Jinja2 environment with custom settings."""
        try:
            # Create file system loader
            loader = FileSystemLoader(str(self.template_dir))
            
            # Configure environment
            self.jinja_env = Environment(
                loader=loader,
                autoescape=False,  # Disable auto-escaping for PHP content
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
            
            # Add custom filters
            self._add_custom_filters()
            
            self.logger.info(f"Jinja2 environment initialized with template directory: {self.template_dir}")
            
        except Exception as e:
            raise TemplateError(f"Failed to initialize Jinja2 environment", str(e))
    
    def _add_custom_filters(self):
        """Add custom Jinja2 filters for Atobusu."""
        
        def preserve_php(value):
            """Filter to preserve PHP code blocks."""
            if not isinstance(value, str):
                return value
            return value  # PHP preservation is handled elsewhere
        
        def format_date(value, format_str='%Y/%m/%d'):
            """Filter to format dates."""
            if isinstance(value, str):
                return value  # Already formatted
            try:
                return value.strftime(format_str)
            except (AttributeError, ValueError):
                return str(value)
        
        def japanese_format(value):
            """Filter for Japanese text formatting."""
            if not isinstance(value, str):
                return str(value)
            return value  # Character conversion is handled by CharacterConverter
        
        # Register filters
        self.jinja_env.filters['preserve_php'] = preserve_php
        self.jinja_env.filters['format_date'] = format_date
        self.jinja_env.filters['japanese_format'] = japanese_format
    
    def load_template(self, template_name: str) -> Template:
        """
        Load a template by name with caching.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Jinja2 Template object
            
        Raises:
            TemplateError: If template cannot be loaded
        """
        try:
            # Check cache first
            if template_name in self._template_cache:
                self.logger.debug(f"Template '{template_name}' loaded from cache")
                return self._template_cache[template_name]
            
            # Load template from file system
            template = self.jinja_env.get_template(template_name)
            
            # Cache the template
            self._template_cache[template_name] = template
            
            self.logger.info(f"Template '{template_name}' loaded and cached")
            return template
            
        except TemplateNotFound:
            raise TemplateError(f"Template not found: {template_name}")
        except TemplateSyntaxError as e:
            raise TemplateError(f"Template syntax error in '{template_name}'", str(e))
        except Exception as e:
            raise TemplateError(f"Failed to load template '{template_name}'", str(e))
    
    def render_html(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render HTML template with data.
        
        Args:
            template_name: Name of the HTML template
            data: Data dictionary for template rendering
            
        Returns:
            Rendered HTML content
        """
        try:
            self.logger.debug(f"Rendering HTML template: {template_name}")
            
            # Load template
            template = self.load_template(template_name)
            
            # Get template source content
            template_content = self.jinja_env.loader.get_source(self.jinja_env, template_name)[0]
            processed_content = self.placeholder_processor.apply_all_replacements(template_content, data)
            
            # Create new template from processed content
            processed_template = self.jinja_env.from_string(processed_content)
            
            # Render with Jinja2
            result = processed_template.render(**data)
            
            self.logger.info(f"HTML template '{template_name}' rendered successfully")
            return result
            
        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to render HTML template '{template_name}'", str(e))
    
    def render_php(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render PHP template with data while preserving PHP syntax.
        
        Args:
            template_name: Name of the PHP template
            data: Data dictionary for template rendering
            
        Returns:
            Rendered PHP content with preserved PHP syntax
        """
        try:
            self.logger.debug(f"Rendering PHP template: {template_name}")
            
            # Load template and get source content
            template = self.load_template(template_name)
            template_content = self.jinja_env.loader.get_source(self.jinja_env, template_name)[0]
            
            # Preserve PHP code blocks
            php_blocks, protected_content = self._preserve_php_blocks(template_content)
            
            # Apply placeholder processing to protected content
            processed_content = self.placeholder_processor.apply_all_replacements(protected_content, data)
            
            # Create new template from processed content
            processed_template = self.jinja_env.from_string(processed_content)
            
            # Render with Jinja2
            rendered_content = processed_template.render(**data)
            
            # Restore PHP code blocks
            result = self._restore_php_blocks(rendered_content, php_blocks)
            
            self.logger.info(f"PHP template '{template_name}' rendered successfully")
            return result
            
        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to render PHP template '{template_name}'", str(e))
    
    def render_mixed_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render mixed content template (HTML + PHP).
        
        Args:
            template_name: Name of the mixed template
            data: Data dictionary for template rendering
            
        Returns:
            Rendered mixed content
        """
        try:
            self.logger.debug(f"Rendering mixed template: {template_name}")
            
            # Determine template type based on content
            template = self.load_template(template_name)
            template_content = self.jinja_env.loader.get_source(self.jinja_env, template_name)[0]
            
            # Check if template contains PHP
            if self._contains_php(template_content):
                return self.render_php(template_name, data)
            else:
                return self.render_html(template_name, data)
                
        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to render mixed template '{template_name}'", str(e))
    
    def _preserve_php_blocks(self, content: str) -> tuple[Dict[str, str], str]:
        """
        Preserve PHP code blocks by replacing them with placeholders.
        
        Args:
            content: Template content containing PHP
            
        Returns:
            Tuple of (php_blocks_dict, protected_content)
        """
        php_blocks = {}
        protected_content = content
        
        # Find and replace PHP blocks
        for pattern_name, pattern in self.php_patterns.items():
            matches = pattern.findall(content)
            for i, match in enumerate(matches):
                placeholder = f"__PHP_{pattern_name.upper()}_{i}__"
                php_blocks[placeholder] = match
                protected_content = protected_content.replace(match, placeholder, 1)
        
        return php_blocks, protected_content
    
    def _restore_php_blocks(self, content: str, php_blocks: Dict[str, str]) -> str:
        """
        Restore PHP code blocks from placeholders.
        
        Args:
            content: Content with PHP placeholders
            php_blocks: Dictionary mapping placeholders to PHP code
            
        Returns:
            Content with restored PHP blocks
        """
        result = content
        for placeholder, php_code in php_blocks.items():
            result = result.replace(placeholder, php_code)
        return result
    
    def _contains_php(self, content: str) -> bool:
        """Check if content contains PHP code."""
        return any(pattern.search(content) for pattern in self.php_patterns.values())
    
    def process_php_functions(self, content: str, data: Dict[str, Any]) -> str:
        """
        Process PHP function calls with parameter replacement.
        
        Args:
            content: Content containing PHP functions
            data: Data for parameter replacement
            
        Returns:
            Content with processed PHP functions
        """
        try:
            return self.placeholder_processor.process_php_function_params(content, data)
        except Exception as e:
            raise TemplateError(f"Failed to process PHP functions", str(e))
    
    def create_template_from_string(self, template_string: str, data: Dict[str, Any]) -> str:
        """
        Create and render template from string content.
        
        Args:
            template_string: Template content as string
            data: Data dictionary for rendering
            
        Returns:
            Rendered content
        """
        try:
            # Apply placeholder processing
            processed_content = self.placeholder_processor.apply_all_replacements(template_string, data)
            
            # Create template from string
            template = self.jinja_env.from_string(processed_content)
            
            # Render template
            result = template.render(**data)
            
            return result
            
        except Exception as e:
            raise TemplateError(f"Failed to create template from string", str(e))
    
    def get_template_list(self) -> List[str]:
        """
        Get list of available templates.
        
        Returns:
            List of template file names
        """
        try:
            templates = []
            for file_path in self.template_dir.rglob('*'):
                if file_path.is_file():
                    # Get relative path from template directory
                    relative_path = file_path.relative_to(self.template_dir)
                    templates.append(str(relative_path))
            
            return sorted(templates)
            
        except Exception as e:
            self.logger.warning(f"Failed to get template list: {e}")
            return []
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            template_name: Name of the template to check
            
        Returns:
            True if template exists, False otherwise
        """
        try:
            template_path = self.template_dir / template_name
            return template_path.exists() and template_path.is_file()
        except Exception:
            return False
    
    def clear_cache(self):
        """Clear the template cache."""
        self._template_cache.clear()
        self.logger.info("Template cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get template cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_templates': len(self._template_cache),
            'template_names': list(self._template_cache.keys()),
            'template_directory': str(self.template_dir),
            'available_templates': len(self.get_template_list())
        }
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validate a template for syntax errors.
        
        Args:
            template_name: Name of the template to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'template_type': 'unknown'
        }
        
        try:
            # Check if template exists
            if not self.template_exists(template_name):
                result['errors'].append(f"Template '{template_name}' not found")
                return result
            
            # Try to load template
            template = self.load_template(template_name)
            template_content = self.jinja_env.loader.get_source(self.jinja_env, template_name)[0]
            
            # Determine template type
            if self._contains_php(template_content):
                result['template_type'] = 'php' if template_name.endswith('.php') else 'mixed'
            else:
                result['template_type'] = 'html'
            
            # Check for common issues
            if not template_content.strip():
                result['warnings'].append("Template is empty")
            
            # Validate placeholder syntax
            placeholder_stats = self.placeholder_processor.get_placeholder_stats(template_content)
            if sum(placeholder_stats.values()) == 0:
                result['warnings'].append("No placeholders found in template")
            
            result['is_valid'] = True
            result['placeholder_stats'] = placeholder_stats
            
        except TemplateError as e:
            result['errors'].append(str(e))
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
        
        return result
    
    def render_template(self, template_name: str, data: Dict[str, Any], output_format: str = 'auto') -> str:
        """
        Render template with automatic format detection.
        
        Args:
            template_name: Name of the template
            data: Data dictionary for rendering
            output_format: Output format ('html', 'php', 'mixed', 'auto')
            
        Returns:
            Rendered content
        """
        try:
            if output_format == 'auto':
                # Auto-detect format based on file extension and content
                if template_name.endswith('.php'):
                    return self.render_php(template_name, data)
                elif template_name.endswith(('.html', '.htm')):
                    template = self.load_template(template_name)
                    template_content = self.jinja_env.loader.get_source(self.jinja_env, template_name)[0]
                    if self._contains_php(template_content):
                        return self.render_mixed_template(template_name, data)
                    else:
                        return self.render_html(template_name, data)
                else:
                    return self.render_mixed_template(template_name, data)
            elif output_format == 'html':
                return self.render_html(template_name, data)
            elif output_format == 'php':
                return self.render_php(template_name, data)
            elif output_format == 'mixed':
                return self.render_mixed_template(template_name, data)
            else:
                raise TemplateError(f"Unsupported output format: {output_format}")
                
        except TemplateError:
            raise
        except Exception as e:
            raise TemplateError(f"Failed to render template '{template_name}'", str(e))