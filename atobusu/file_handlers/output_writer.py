"""
File output operations for Atobusu application.

Handles writing HTML, PHP, JSON, YAML, and mixed template files with proper
error handling, validation, and directory management.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

from atobusu.core.logging_config import get_logger
from atobusu.core.exceptions import OutputError


class OutputWriter:
    """
    Handles file output operations for Atobusu application.
    
    Manages writing HTML, PHP, JSON, YAML, and mixed content files with
    proper error handling, validation, and directory management.
    """
    
    def __init__(self, output_dir: str = "output", create_dirs: bool = True):
        """
        Initialize the output writer.
        
        Args:
            output_dir: Base directory for output files
            create_dirs: Whether to create directories automatically
        """
        self.logger = get_logger(__name__)
        self.output_dir = Path(output_dir)
        self.create_dirs = create_dirs
        
        # Create output directory if it doesn't exist
        if self.create_dirs:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported file formats and their extensions
        self.format_extensions = {
            'html': ['.html', '.htm'],
            'php': ['.php'],
            'json': ['.json'],
            'yaml': ['.yaml', '.yml'],
            'mixed': ['.html', '.htm', '.php', '.tpl']
        }
        
        # Default encodings for different file types
        self.default_encodings = {
            'html': 'utf-8',
            'php': 'utf-8',
            'json': 'utf-8',
            'yaml': 'utf-8',
            'mixed': 'utf-8'
        }
        
        # File write statistics
        self.write_stats = {
            'files_written': 0,
            'total_bytes': 0,
            'formats': {},
            'last_write': None
        }
    
    def write_html(self, content: str, output_path: str, encoding: str = 'utf-8') -> bool:
        """
        Write HTML content to file.
        
        Args:
            content: HTML content to write
            output_path: Path to output file
            encoding: File encoding (default: utf-8)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            OutputError: If writing fails
        """
        try:
            self.logger.debug(f"Writing HTML file: {output_path}")
            
            # Validate content
            if not isinstance(content, str):
                raise OutputError("HTML content must be a string")
            
            # Ensure proper file extension
            output_path = self._ensure_extension(output_path, 'html')
            
            # Write file
            success = self._write_file(content, output_path, encoding)
            
            if success:
                self._update_stats('html', len(content.encode(encoding)))
                self.logger.info(f"HTML file written successfully: {output_path}")
            
            return success
            
        except Exception as e:
            raise OutputError(f"Failed to write HTML file: {output_path}", str(e))
    
    def write_php(self, content: str, output_path: str, encoding: str = 'utf-8') -> bool:
        """
        Write PHP content to file.
        
        Args:
            content: PHP content to write
            output_path: Path to output file
            encoding: File encoding (default: utf-8)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            OutputError: If writing fails
        """
        try:
            self.logger.debug(f"Writing PHP file: {output_path}")
            
            # Validate content
            if not isinstance(content, str):
                raise OutputError("PHP content must be a string")
            
            # Ensure proper file extension
            output_path = self._ensure_extension(output_path, 'php')
            
            # Write file
            success = self._write_file(content, output_path, encoding)
            
            if success:
                self._update_stats('php', len(content.encode(encoding)))
                self.logger.info(f"PHP file written successfully: {output_path}")
            
            return success
            
        except Exception as e:
            raise OutputError(f"Failed to write PHP file: {output_path}", str(e))
    
    def write_json(self, data: Union[Dict[str, Any], List, str], output_path: str, 
                   encoding: str = 'utf-8', indent: int = 2) -> bool:
        """
        Write JSON data to file.
        
        Args:
            data: Data to write as JSON (dict, list, or JSON string)
            output_path: Path to output file
            encoding: File encoding (default: utf-8)
            indent: JSON indentation (default: 2)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            OutputError: If writing fails
        """
        try:
            self.logger.debug(f"Writing JSON file: {output_path}")
            
            # Convert data to JSON string if needed
            if isinstance(data, str):
                # Validate that it's valid JSON
                try:
                    json.loads(data)
                    json_content = data
                except json.JSONDecodeError:
                    raise OutputError("Invalid JSON string provided")
            else:
                # Convert to JSON string
                json_content = json.dumps(data, indent=indent, ensure_ascii=False)
            
            # Ensure proper file extension
            output_path = self._ensure_extension(output_path, 'json')
            
            # Write file
            success = self._write_file(json_content, output_path, encoding)
            
            if success:
                self._update_stats('json', len(json_content.encode(encoding)))
                self.logger.info(f"JSON file written successfully: {output_path}")
            
            return success
            
        except Exception as e:
            raise OutputError(f"Failed to write JSON file: {output_path}", str(e))
    
    def write_yaml(self, data: Union[Dict[str, Any], List, str], output_path: str, 
                   encoding: str = 'utf-8') -> bool:
        """
        Write YAML data to file.
        
        Args:
            data: Data to write as YAML (dict, list, or YAML string)
            output_path: Path to output file
            encoding: File encoding (default: utf-8)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            OutputError: If writing fails
        """
        try:
            self.logger.debug(f"Writing YAML file: {output_path}")
            
            # Convert data to YAML string if needed
            if isinstance(data, str):
                # Validate that it's valid YAML
                try:
                    yaml.safe_load(data)
                    yaml_content = data
                except yaml.YAMLError:
                    raise OutputError("Invalid YAML string provided")
            else:
                # Convert to YAML string
                yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            
            # Ensure proper file extension
            output_path = self._ensure_extension(output_path, 'yaml')
            
            # Write file
            success = self._write_file(yaml_content, output_path, encoding)
            
            if success:
                self._update_stats('yaml', len(yaml_content.encode(encoding)))
                self.logger.info(f"YAML file written successfully: {output_path}")
            
            return success
            
        except Exception as e:
            raise OutputError(f"Failed to write YAML file: {output_path}", str(e))
    
    def write_mixed_template(self, content: str, output_path: str, 
                           template_format: str = 'html', encoding: str = 'utf-8') -> bool:
        """
        Write mixed template content to file.
        
        Args:
            content: Mixed template content to write
            output_path: Path to output file
            template_format: Template format hint ('html', 'php', 'mixed')
            encoding: File encoding (default: utf-8)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            OutputError: If writing fails
        """
        try:
            self.logger.debug(f"Writing mixed template file: {output_path}")
            
            # Validate content
            if not isinstance(content, str):
                raise OutputError("Mixed template content must be a string")
            
            # Determine appropriate extension based on format
            if template_format == 'php' or '<?php' in content or '<?=' in content:
                output_path = self._ensure_extension(output_path, 'php')
            else:
                output_path = self._ensure_extension(output_path, 'html')
            
            # Write file
            success = self._write_file(content, output_path, encoding)
            
            if success:
                self._update_stats('mixed', len(content.encode(encoding)))
                self.logger.info(f"Mixed template file written successfully: {output_path}")
            
            return success
            
        except Exception as e:
            raise OutputError(f"Failed to write mixed template file: {output_path}", str(e))
    
    def write_file(self, content: str, output_path: str, file_format: str = 'auto', 
                   encoding: str = 'utf-8', **kwargs) -> bool:
        """
        Write file with automatic format detection.
        
        Args:
            content: Content to write
            output_path: Path to output file
            file_format: File format ('html', 'php', 'json', 'yaml', 'mixed', 'auto')
            encoding: File encoding (default: utf-8)
            **kwargs: Additional arguments for specific formats
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if file_format == 'auto':
                # Auto-detect format based on file extension
                file_format = self._detect_format(output_path)
            
            # Route to appropriate write method
            if file_format == 'html':
                return self.write_html(content, output_path, encoding)
            elif file_format == 'php':
                return self.write_php(content, output_path, encoding)
            elif file_format == 'json':
                return self.write_json(content, output_path, encoding, 
                                     kwargs.get('indent', 2))
            elif file_format == 'yaml':
                return self.write_yaml(content, output_path, encoding)
            elif file_format == 'mixed':
                return self.write_mixed_template(content, output_path, 
                                               kwargs.get('template_format', 'html'), encoding)
            else:
                raise OutputError(f"Unsupported file format: {file_format}")
                
        except OutputError:
            raise
        except Exception as e:
            raise OutputError(f"Failed to write file: {output_path}", str(e))
    
    def _write_file(self, content: str, output_path: str, encoding: str) -> bool:
        """
        Internal method to write content to file.
        
        Args:
            content: Content to write
            output_path: Path to output file
            encoding: File encoding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Resolve full output path
            full_path = self._resolve_output_path(output_path)
            
            # Create directory if needed
            if self.create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            self.logger.debug(f"File written: {full_path} ({len(content)} characters)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write file {output_path}: {e}")
            return False
    
    def _resolve_output_path(self, output_path: str) -> Path:
        """Resolve output path relative to output directory."""
        path = Path(output_path)
        
        if path.is_absolute():
            return path
        else:
            return self.output_dir / path
    
    def _ensure_extension(self, output_path: str, file_format: str) -> str:
        """Ensure file has appropriate extension for format."""
        path = Path(output_path)
        
        # Get expected extensions for format
        expected_extensions = self.format_extensions.get(file_format, [])
        
        if expected_extensions and path.suffix.lower() not in expected_extensions:
            # Add default extension
            default_ext = expected_extensions[0]
            output_path = str(path.with_suffix(default_ext))
        
        return output_path
    
    def _detect_format(self, output_path: str) -> str:
        """Detect file format from extension."""
        path = Path(output_path)
        extension = path.suffix.lower()
        
        for file_format, extensions in self.format_extensions.items():
            if extension in extensions:
                return file_format
        
        # Default to mixed if unknown
        return 'mixed'
    
    def _update_stats(self, file_format: str, byte_count: int):
        """Update write statistics."""
        self.write_stats['files_written'] += 1
        self.write_stats['total_bytes'] += byte_count
        self.write_stats['last_write'] = datetime.now().isoformat()
        
        if file_format not in self.write_stats['formats']:
            self.write_stats['formats'][file_format] = {'count': 0, 'bytes': 0}
        
        self.write_stats['formats'][file_format]['count'] += 1
        self.write_stats['formats'][file_format]['bytes'] += byte_count
    
    def create_directory(self, dir_path: str) -> bool:
        """
        Create directory structure.
        
        Args:
            dir_path: Directory path to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = self._resolve_output_path(dir_path)
            full_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Directory created: {full_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create directory {dir_path}: {e}")
            return False
    
    def validate_output_path(self, output_path: str) -> Dict[str, Any]:
        """
        Validate output path and return information.
        
        Args:
            output_path: Path to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': False,
            'exists': False,
            'is_writable': False,
            'directory_exists': False,
            'full_path': None,
            'errors': []
        }
        
        try:
            full_path = self._resolve_output_path(output_path)
            result['full_path'] = str(full_path)
            
            # Check if file exists
            result['exists'] = full_path.exists()
            
            # Check if directory exists
            result['directory_exists'] = full_path.parent.exists()
            
            # Check if path is writable
            if result['directory_exists']:
                result['is_writable'] = os.access(full_path.parent, os.W_OK)
            elif self.create_dirs:
                # Check if we can create the directory
                try:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    result['directory_exists'] = True
                    result['is_writable'] = os.access(full_path.parent, os.W_OK)
                except Exception as e:
                    result['errors'].append(f"Cannot create directory: {e}")
            
            # Overall validation
            result['is_valid'] = result['is_writable'] and (
                result['directory_exists'] or self.create_dirs
            )
            
        except Exception as e:
            result['errors'].append(f"Path validation error: {e}")
        
        return result
    
    def get_write_stats(self) -> Dict[str, Any]:
        """
        Get file writing statistics.
        
        Returns:
            Dictionary with write statistics
        """
        return self.write_stats.copy()
    
    def reset_stats(self):
        """Reset write statistics."""
        self.write_stats = {
            'files_written': 0,
            'total_bytes': 0,
            'formats': {},
            'last_write': None
        }
        self.logger.info("Write statistics reset")
    
    def list_output_files(self, pattern: str = "*") -> List[str]:
        """
        List files in output directory.
        
        Args:
            pattern: File pattern to match (default: all files)
            
        Returns:
            List of file paths relative to output directory
        """
        try:
            if not self.output_dir.exists():
                return []
            
            files = []
            for file_path in self.output_dir.rglob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.output_dir)
                    files.append(str(relative_path))
            
            return sorted(files)
            
        except Exception as e:
            self.logger.error(f"Failed to list output files: {e}")
            return []
    
    def cleanup_output_dir(self, pattern: str = "*", dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up output directory.
        
        Args:
            pattern: File pattern to match for deletion
            dry_run: If True, only report what would be deleted
            
        Returns:
            Dictionary with cleanup results
        """
        result = {
            'files_found': 0,
            'files_deleted': 0,
            'errors': [],
            'deleted_files': []
        }
        
        try:
            if not self.output_dir.exists():
                return result
            
            files_to_delete = list(self.output_dir.rglob(pattern))
            result['files_found'] = len([f for f in files_to_delete if f.is_file()])
            
            if not dry_run:
                for file_path in files_to_delete:
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            result['files_deleted'] += 1
                            result['deleted_files'].append(str(file_path.relative_to(self.output_dir)))
                        except Exception as e:
                            result['errors'].append(f"Failed to delete {file_path}: {e}")
            
            action = "Would delete" if dry_run else "Deleted"
            self.logger.info(f"{action} {result['files_found']} files from output directory")
            
        except Exception as e:
            result['errors'].append(f"Cleanup failed: {e}")
        
        return result
    
    def backup_file(self, file_path: str, backup_suffix: str = ".bak") -> bool:
        """
        Create backup of existing file.
        
        Args:
            file_path: Path to file to backup
            backup_suffix: Suffix for backup file
            
        Returns:
            True if backup created successfully
        """
        try:
            full_path = self._resolve_output_path(file_path)
            
            if not full_path.exists():
                self.logger.warning(f"File does not exist for backup: {full_path}")
                return False
            
            backup_path = full_path.with_suffix(full_path.suffix + backup_suffix)
            
            # Copy file content
            content = full_path.read_text(encoding='utf-8')
            backup_path.write_text(content, encoding='utf-8')
            
            self.logger.info(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {e}")
            return False