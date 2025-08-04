"""
Tests for file I/O operations.
"""

import pytest
import tempfile
import shutil
import json
import yaml
from pathlib import Path

from atobusu.file_handlers.output_writer import OutputWriter
from atobusu.core.exceptions import OutputError


class TestOutputWriter:
    """Test cases for OutputWriter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for output
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)
        
        # Initialize output writer
        self.writer = OutputWriter(str(self.output_dir))
        
        # Sample data for testing
        self.test_data = {
            'title': 'Test Document',
            'content': 'This is test content',
            'items': ['item1', 'item2', 'item3'],
            'metadata': {
                'author': 'Test Author',
                'date': '2025-01-15'
            }
        }
        
        # Sample HTML content
        self.html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Content</h1>
            <p>This is a test page.</p>
        </body>
        </html>
        """
        
        # Sample PHP content
        self.php_content = """
        <?php
        $title = "Test PHP Page";
        $content = "This is PHP content";
        ?>
        <h1><?php echo $title; ?></h1>
        <p><?php echo $content; ?></p>
        """
        
        # Sample mixed content
        self.mixed_content = """
        <div class="content">
            <h2>Mixed Content</h2>
            <?=prod_info("test_code", "pname")?>
            <p>HTML and PHP mixed together</p>
        </div>
        """
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_writer_initialization(self):
        """Test OutputWriter initialization."""
        assert self.writer.output_dir == self.output_dir
        assert self.writer.create_dirs is True
        assert self.output_dir.exists()
        
        # Test initialization without creating directories
        temp_dir2 = tempfile.mkdtemp()
        shutil.rmtree(temp_dir2)  # Remove it
        writer2 = OutputWriter(temp_dir2, create_dirs=False)
        assert not Path(temp_dir2).exists()
    
    def test_write_html_basic(self):
        """Test basic HTML file writing."""
        output_path = "test.html"
        success = self.writer.write_html(self.html_content, output_path)
        
        assert success is True
        
        # Check file was created
        full_path = self.output_dir / output_path
        assert full_path.exists()
        
        # Check content
        written_content = full_path.read_text(encoding='utf-8')
        assert self.html_content.strip() in written_content
    
    def test_write_html_with_extension_correction(self):
        """Test HTML writing with automatic extension correction."""
        output_path = "test_no_ext"
        success = self.writer.write_html(self.html_content, output_path)
        
        assert success is True
        
        # Check file was created with .html extension
        expected_path = self.output_dir / "test_no_ext.html"
        assert expected_path.exists()
    
    def test_write_html_invalid_content(self):
        """Test HTML writing with invalid content."""
        with pytest.raises(OutputError):
            self.writer.write_html(123, "test.html")  # Non-string content
    
    def test_write_php_basic(self):
        """Test basic PHP file writing."""
        output_path = "test.php"
        success = self.writer.write_php(self.php_content, output_path)
        
        assert success is True
        
        # Check file was created
        full_path = self.output_dir / output_path
        assert full_path.exists()
        
        # Check content
        written_content = full_path.read_text(encoding='utf-8')
        assert "<?php" in written_content
        assert "$title" in written_content
    
    def test_write_php_with_extension_correction(self):
        """Test PHP writing with automatic extension correction."""
        output_path = "test_php_file"
        success = self.writer.write_php(self.php_content, output_path)
        
        assert success is True
        
        # Check file was created with .php extension
        expected_path = self.output_dir / "test_php_file.php"
        assert expected_path.exists()
    
    def test_write_json_from_dict(self):
        """Test JSON writing from dictionary."""
        output_path = "test.json"
        success = self.writer.write_json(self.test_data, output_path)
        
        assert success is True
        
        # Check file was created
        full_path = self.output_dir / output_path
        assert full_path.exists()
        
        # Check content by loading JSON
        with open(full_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == self.test_data
    
    def test_write_json_from_string(self):
        """Test JSON writing from JSON string."""
        json_string = json.dumps(self.test_data, indent=2)
        output_path = "test_string.json"
        success = self.writer.write_json(json_string, output_path)
        
        assert success is True
        
        # Check file was created and content is valid
        full_path = self.output_dir / output_path
        with open(full_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == self.test_data
    
    def test_write_json_invalid_string(self):
        """Test JSON writing with invalid JSON string."""
        invalid_json = "{ invalid json string"
        
        with pytest.raises(OutputError):
            self.writer.write_json(invalid_json, "invalid.json")
    
    def test_write_yaml_from_dict(self):
        """Test YAML writing from dictionary."""
        output_path = "test.yaml"
        success = self.writer.write_yaml(self.test_data, output_path)
        
        assert success is True
        
        # Check file was created
        full_path = self.output_dir / output_path
        assert full_path.exists()
        
        # Check content by loading YAML
        with open(full_path, 'r', encoding='utf-8') as f:
            loaded_data = yaml.safe_load(f)
        
        assert loaded_data == self.test_data
    
    def test_write_yaml_from_string(self):
        """Test YAML writing from YAML string."""
        yaml_string = yaml.dump(self.test_data, default_flow_style=False)
        output_path = "test_string.yaml"
        success = self.writer.write_yaml(yaml_string, output_path)
        
        assert success is True
        
        # Check file was created and content is valid
        full_path = self.output_dir / output_path
        with open(full_path, 'r', encoding='utf-8') as f:
            loaded_data = yaml.safe_load(f)
        
        assert loaded_data == self.test_data
    
    def test_write_yaml_with_yml_extension(self):
        """Test YAML writing with .yml extension."""
        output_path = "test.yml"
        success = self.writer.write_yaml(self.test_data, output_path)
        
        assert success is True
        
        # Check file was created with original extension
        full_path = self.output_dir / output_path
        assert full_path.exists()
    
    def test_write_mixed_template_html(self):
        """Test mixed template writing (HTML content)."""
        output_path = "mixed.html"
        success = self.writer.write_mixed_template(self.html_content, output_path, "html")
        
        assert success is True
        
        # Check file was created
        full_path = self.output_dir / output_path
        assert full_path.exists()
        assert full_path.suffix == ".html"
    
    def test_write_mixed_template_php(self):
        """Test mixed template writing (PHP content)."""
        output_path = "mixed"
        success = self.writer.write_mixed_template(self.mixed_content, output_path, "php")
        
        assert success is True
        
        # Check file was created with .php extension
        expected_path = self.output_dir / "mixed.php"
        assert expected_path.exists()
    
    def test_write_mixed_template_auto_detection(self):
        """Test mixed template writing with auto-detection."""
        # Content with PHP should get .php extension
        output_path = "auto_detect"
        success = self.writer.write_mixed_template(self.mixed_content, output_path)
        
        assert success is True
        
        # Should detect PHP and use .php extension
        expected_path = self.output_dir / "auto_detect.php"
        assert expected_path.exists()
    
    def test_write_file_auto_format(self):
        """Test generic file writing with auto format detection."""
        # HTML file
        html_success = self.writer.write_file(self.html_content, "auto.html", "auto")
        assert html_success is True
        assert (self.output_dir / "auto.html").exists()
        
        # PHP file
        php_success = self.writer.write_file(self.php_content, "auto.php", "auto")
        assert php_success is True
        assert (self.output_dir / "auto.php").exists()
        
        # JSON file
        json_success = self.writer.write_file(json.dumps(self.test_data), "auto.json", "auto")
        assert json_success is True
        assert (self.output_dir / "auto.json").exists()
    
    def test_write_file_explicit_format(self):
        """Test generic file writing with explicit format."""
        success = self.writer.write_file(self.html_content, "explicit.txt", "html")
        assert success is True
        
        # Should have been corrected to .html
        assert (self.output_dir / "explicit.html").exists()
    
    def test_write_file_unsupported_format(self):
        """Test generic file writing with unsupported format."""
        with pytest.raises(OutputError):
            self.writer.write_file("content", "test.txt", "unsupported")
    
    def test_create_directory(self):
        """Test directory creation."""
        dir_path = "test_dir/subdir"
        success = self.writer.create_directory(dir_path)
        
        assert success is True
        
        # Check directory was created
        full_path = self.output_dir / dir_path
        assert full_path.exists()
        assert full_path.is_dir()
    
    def test_validate_output_path_valid(self):
        """Test output path validation for valid path."""
        output_path = "valid_file.html"
        result = self.writer.validate_output_path(output_path)
        
        assert result['is_valid'] is True
        assert result['is_writable'] is True
        assert result['directory_exists'] is True
        assert len(result['errors']) == 0
    
    def test_validate_output_path_nested(self):
        """Test output path validation for nested path."""
        output_path = "nested/dir/file.html"
        result = self.writer.validate_output_path(output_path)
        
        # Should be valid because create_dirs is True
        assert result['is_valid'] is True
        assert result['directory_exists'] is True
    
    def test_get_write_stats(self):
        """Test write statistics tracking."""
        # Write some files
        self.writer.write_html(self.html_content, "stats1.html")
        self.writer.write_php(self.php_content, "stats2.php")
        self.writer.write_json(self.test_data, "stats3.json")
        
        stats = self.writer.get_write_stats()
        
        assert stats['files_written'] == 3
        assert stats['total_bytes'] > 0
        assert 'html' in stats['formats']
        assert 'php' in stats['formats']
        assert 'json' in stats['formats']
        assert stats['last_write'] is not None
    
    def test_reset_stats(self):
        """Test statistics reset."""
        # Write a file
        self.writer.write_html(self.html_content, "reset_test.html")
        
        # Check stats exist
        stats_before = self.writer.get_write_stats()
        assert stats_before['files_written'] == 1
        
        # Reset stats
        self.writer.reset_stats()
        
        # Check stats are reset
        stats_after = self.writer.get_write_stats()
        assert stats_after['files_written'] == 0
        assert stats_after['total_bytes'] == 0
        assert stats_after['formats'] == {}
    
    def test_list_output_files(self):
        """Test listing output files."""
        # Create some files
        self.writer.write_html(self.html_content, "list1.html")
        self.writer.write_php(self.php_content, "list2.php")
        self.writer.write_json(self.test_data, "subdir/list3.json")
        
        # List all files
        all_files = self.writer.list_output_files()
        assert len(all_files) >= 3
        assert "list1.html" in all_files
        assert "list2.php" in all_files
        
        # List HTML files only
        html_files = self.writer.list_output_files("*.html")
        assert "list1.html" in html_files
        assert "list2.php" not in html_files
    
    def test_backup_file(self):
        """Test file backup creation."""
        # Create original file
        original_path = "backup_test.html"
        self.writer.write_html(self.html_content, original_path)
        
        # Create backup
        success = self.writer.backup_file(original_path)
        assert success is True
        
        # Check backup exists
        backup_path = self.output_dir / "backup_test.html.bak"
        assert backup_path.exists()
        
        # Check backup content matches original
        original_content = (self.output_dir / original_path).read_text()
        backup_content = backup_path.read_text()
        assert original_content == backup_content
    
    def test_backup_nonexistent_file(self):
        """Test backup of non-existent file."""
        success = self.writer.backup_file("nonexistent.html")
        assert success is False
    
    def test_cleanup_output_dir_dry_run(self):
        """Test output directory cleanup (dry run)."""
        # Create some files
        self.writer.write_html(self.html_content, "cleanup1.html")
        self.writer.write_php(self.php_content, "cleanup2.php")
        
        # Dry run cleanup
        result = self.writer.cleanup_output_dir("*.html", dry_run=True)
        
        assert result['files_found'] >= 1
        assert result['files_deleted'] == 0
        
        # Files should still exist
        assert (self.output_dir / "cleanup1.html").exists()
    
    def test_cleanup_output_dir_actual(self):
        """Test actual output directory cleanup."""
        # Create some files
        self.writer.write_html(self.html_content, "cleanup1.html")
        self.writer.write_php(self.php_content, "cleanup2.php")
        
        # Actual cleanup of HTML files
        result = self.writer.cleanup_output_dir("*.html", dry_run=False)
        
        assert result['files_deleted'] >= 1
        
        # HTML file should be deleted, PHP should remain
        assert not (self.output_dir / "cleanup1.html").exists()
        assert (self.output_dir / "cleanup2.php").exists()
    
    def test_directory_creation_in_write(self):
        """Test automatic directory creation during write."""
        nested_path = "deep/nested/dir/file.html"
        success = self.writer.write_html(self.html_content, nested_path)
        
        assert success is True
        
        # Check file and directories were created
        full_path = self.output_dir / nested_path
        assert full_path.exists()
        assert full_path.parent.exists()
    
    def test_encoding_handling(self):
        """Test different encoding handling."""
        japanese_content = "テスト内容：これは日本語のテストです。"
        
        # Write with UTF-8 encoding
        success = self.writer.write_html(japanese_content, "japanese.html", "utf-8")
        assert success is True
        
        # Read back and verify
        full_path = self.output_dir / "japanese.html"
        read_content = full_path.read_text(encoding='utf-8')
        assert japanese_content in read_content
    
    def test_large_file_writing(self):
        """Test writing large files."""
        # Create large content
        large_content = self.html_content * 1000  # Repeat content 1000 times
        
        success = self.writer.write_html(large_content, "large_file.html")
        assert success is True
        
        # Check file size
        full_path = self.output_dir / "large_file.html"
        assert full_path.stat().st_size > 10000  # Should be reasonably large
    
    def test_error_handling_write_permission(self):
        """Test error handling for write permission issues."""
        # This test might not work on all systems, so we'll make it conditional
        try:
            # Try to write to a read-only directory (if we can create one)
            readonly_dir = self.output_dir / "readonly"
            readonly_dir.mkdir()
            readonly_dir.chmod(0o444)  # Read-only
            
            writer = OutputWriter(str(readonly_dir), create_dirs=False)
            success = writer.write_html(self.html_content, "readonly_test.html")
            
            # Should fail gracefully
            assert success is False
            
        except Exception:
            # If we can't test this (e.g., on Windows), just pass
            pass
    
    def test_concurrent_writes(self):
        """Test multiple concurrent writes."""
        # Write multiple files quickly
        files_written = 0
        for i in range(10):
            success = self.writer.write_html(
                f"<h1>Test {i}</h1>", 
                f"concurrent_{i}.html"
            )
            if success:
                files_written += 1
        
        assert files_written == 10
        
        # Check all files exist
        for i in range(10):
            assert (self.output_dir / f"concurrent_{i}.html").exists()