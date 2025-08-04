"""
Configuration management for Atobusu application.
"""

import json
import yaml
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class AtobusuConfig:
    """Configuration class for Atobusu application."""
    
    template_directory: str = "templates"
    output_directory: str = "output"
    gui_framework: str = "tkinter"  # 'tkinter' or 'pyqt5'
    character_conversion_rules: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        'quotes': {'"': '"', '"': '"'},
        'symbols': {'※': '※'},  # Keep as-is
        'circled_numbers': {
            '①': '&#9312;', '②': '&#9313;', '③': '&#9314;',
            '④': '&#9315;', '⑤': '&#9316;', '⑥': '&#9317;',
            '⑦': '&#9318;', '⑧': '&#9319;', '⑨': '&#9320;',
            '⑩': '&#9321;'
        },
        'special_symbols': {
            '◎': '&#9678;',
            'ハート': '&#9825;',
            '♪': '&#9834;'
        }
    })
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Template processing settings
    template_encoding: str = "utf-8"
    output_encoding: str = "utf-8"
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'AtobusuConfig':
        """
        Load configuration from a JSON or YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            AtobusuConfig instance with loaded settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    data = json.load(f)
                elif config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            return cls(**data)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to a JSON or YAML file.
        
        Args:
            config_path: Path where to save the configuration file
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert dataclass to dictionary
        data = {
            'template_directory': self.template_directory,
            'output_directory': self.output_directory,
            'gui_framework': self.gui_framework,
            'character_conversion_rules': self.character_conversion_rules,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'template_encoding': self.template_encoding,
            'output_encoding': self.output_encoding
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.suffix.lower() == '.json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if self.gui_framework not in ['tkinter', 'pyqt5']:
            raise ValueError(f"Invalid GUI framework: {self.gui_framework}")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f"Invalid log level: {self.log_level}")
        
        # Validate directories exist or can be created
        for directory in [self.template_directory, self.output_directory]:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create directory {directory}: {e}")
        
        return True
    
    def get_template_path(self, template_name: str) -> Path:
        """Get full path to a template file."""
        return Path(self.template_directory) / template_name
    
    def get_output_path(self, output_name: str) -> Path:
        """Get full path to an output file."""
        return Path(self.output_directory) / output_name