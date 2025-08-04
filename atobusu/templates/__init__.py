"""
Template processing components for Atobusu.

This module contains template management classes including
TemplateManager and PlaceholderProcessor for handling Jinja2 templates.
"""

from .placeholder_processor import PlaceholderProcessor
from .template_manager import TemplateManager

__all__ = [
    'PlaceholderProcessor',
    'TemplateManager'
]