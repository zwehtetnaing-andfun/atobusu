#!/usr/bin/env python3
"""
Demonstration of Atobusu file I/O operations.
"""

import tempfile
import shutil
import json
from pathlib import Path

from atobusu.file_handlers.output_writer import OutputWriter


def main():
    print("📁 Atobusu File I/O Operations Demo")
    print("=" * 50)
    
    # Create temporary directory for demonstration
    temp_dir = tempfile.mkdtemp()
    output_dir = Path(temp_dir)
    
    try:
        # Initialize output writer
        writer = OutputWriter(str(output_dir))
        
        # Sample data for demonstrations
        demo_data = {
            'title': 'File I/O Demo',
            'product_code': 'DEMO123456',
            'product_name': 'Demo Product',
            'category': 'Demo Category',
            'reviewer_name': 'Demo Reviewer',
            'rating': 5,
            'post_date': '2025/01/15',
            'content': 'This is demo content for file I/O operations',
            'items': ['Item 1', 'Item 2', 'Item 3'],
            'metadata': {
                'author': 'Demo Author',
                'created': '2025-01-15',
                'version': '1.0'
            }
        }
        
        # Demo 1: HTML File Writing
        print("\n1. HTML File Writing")
        print("-" * 30)
        
        html_content = """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>Demo HTML File</title>
        </head>
        <body>
            <h1>Demo HTML Content</h1>
            <p>This is a demonstration of HTML file writing.</p>
            <p>Product: Demo Product (DEMO123456)</p>
            <p>Rating: 5/5 stars</p>
        </body>
        </html>
        """
        
        success = writer.write_html(html_content.strip(), "demo.html")
        print(f"HTML file written: {success}")
        print(f"File location: {output_dir / 'demo.html'}")
        
        # Demo 2: PHP File Writing
        print("\n2. PHP File Writing")
        print("-" * 30)
        
        php_content = """
        <?php
            $title = "Demo PHP Page";
            $product_code = "DEMO123456";
            $rating = 5;
        ?>
        <!DOCTYPE html>
        <html>
        <head><title><?php echo $title; ?></title></head>
        <body>
            <h1><?php echo $title; ?></h1>
            <p>Product Code: <?php echo $product_code; ?></p>
            <p>Rating: <?php echo $rating; ?>/5</p>
            <img src="<?=prod_info($product_code, 'mimg')?>" alt="Product Image">
        </body>
        </html>
        """
        
        success = writer.write_php(php_content.strip(), "demo.php")
        print(f"PHP file written: {success}")
        print(f"File location: {output_dir / 'demo.php'}")
        
        # Demo 3: JSON File Writing
        print("\n3. JSON File Writing")
        print("-" * 30)
        
        success = writer.write_json(demo_data, "demo_data.json")
        print(f"JSON file written: {success}")
        
        # Read back and display
        json_path = output_dir / "demo_data.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print(f"JSON data keys: {list(loaded_data.keys())}")
        
        # Demo 4: YAML File Writing
        print("\n4. YAML File Writing")
        print("-" * 30)
        
        success = writer.write_yaml(demo_data, "demo_data.yaml")
        print(f"YAML file written: {success}")
        
        # Show YAML content preview
        yaml_path = output_dir / "demo_data.yaml"
        yaml_content = yaml_path.read_text(encoding='utf-8')
        print("YAML content preview:")
        print(yaml_content[:200] + "..." if len(yaml_content) > 200 else yaml_content)
        
        # Demo 5: Mixed Template Writing
        print("\n5. Mixed Template Writing")
        print("-" * 30)
        
        mixed_content = """
        <div class="product-review">
            <h2>Product Review</h2>
            <div class="product-info">
                <p>Product: DEMO123456</p>
                <p>Name: Demo Product</p>
                <p>Category: Demo Category</p>
            </div>
            <div class="php-section">
                <?php echo "Dynamic PHP content"; ?>
                <img src="<?=prod_info('demo_code', 'mimg')?>" alt="Product">
            </div>
            <div class="rating">
                <span>Rating: 5/5</span>
            </div>
        </div>
        """
        
        success = writer.write_mixed_template(mixed_content.strip(), "mixed_demo")
        print(f"Mixed template written: {success}")
        
        # Check what extension was used
        mixed_files = list(output_dir.glob("mixed_demo.*"))
        if mixed_files:
            print(f"Mixed template saved as: {mixed_files[0].name}")
        
        # Demo 6: Auto-Format File Writing
        print("\n6. Auto-Format File Writing")
        print("-" * 30)
        
        # Write different formats with auto-detection
        formats_data = [
            ("auto_html.html", html_content, "auto"),
            ("auto_php.php", php_content, "auto"),
            ("auto_json.json", json.dumps(demo_data, indent=2), "auto"),
        ]
        
        for filename, content, format_type in formats_data:
            success = writer.write_file(content, filename, format_type)
            print(f"Auto-format {filename}: {success}")
        
        # Demo 7: Directory Management
        print("\n7. Directory Management")
        print("-" * 30)
        
        # Create nested directories
        nested_dirs = ["reviews/2025/january", "templates/html", "data/json"]
        for dir_path in nested_dirs:
            success = writer.create_directory(dir_path)
            print(f"Directory created {dir_path}: {success}")
        
        # Write files in nested directories
        writer.write_html("<h1>Nested HTML</h1>", "reviews/2025/january/review.html")
        writer.write_json({"nested": True}, "data/json/nested.json")
        
        # Demo 8: File Validation
        print("\n8. File Path Validation")
        print("-" * 30)
        
        test_paths = [
            "valid_file.html",
            "nested/deep/file.php",
            "data/output.json"
        ]
        
        for path in test_paths:
            validation = writer.validate_output_path(path)
            print(f"Path '{path}': Valid={validation['is_valid']}, Writable={validation['is_writable']}")
        
        # Demo 9: File Statistics
        print("\n9. File Writing Statistics")
        print("-" * 30)
        
        stats = writer.get_write_stats()
        print(f"Files written: {stats['files_written']}")
        print(f"Total bytes: {stats['total_bytes']:,}")
        print(f"Formats used: {list(stats['formats'].keys())}")
        print(f"Last write: {stats['last_write']}")
        
        # Show format breakdown
        for format_name, format_stats in stats['formats'].items():
            print(f"  {format_name}: {format_stats['count']} files, {format_stats['bytes']:,} bytes")
        
        # Demo 10: File Listing and Management
        print("\n10. File Listing and Management")
        print("-" * 30)
        
        # List all files
        all_files = writer.list_output_files()
        print(f"Total files created: {len(all_files)}")
        
        # List specific file types
        html_files = writer.list_output_files("*.html")
        php_files = writer.list_output_files("*.php")
        json_files = writer.list_output_files("*.json")
        
        print(f"HTML files: {len(html_files)}")
        print(f"PHP files: {len(php_files)}")
        print(f"JSON files: {len(json_files)}")
        
        # Show some file names
        print("Sample files created:")
        for file_path in all_files[:5]:  # Show first 5 files
            print(f"  - {file_path}")
        
        # Demo 11: File Backup
        print("\n11. File Backup Operations")
        print("-" * 30)
        
        # Create backup of important file
        backup_success = writer.backup_file("demo.html")
        print(f"Backup created for demo.html: {backup_success}")
        
        # Check if backup exists
        backup_files = writer.list_output_files("*.bak")
        print(f"Backup files: {backup_files}")
        
        # Demo 12: Cleanup Operations (Dry Run)
        print("\n12. Cleanup Operations")
        print("-" * 30)
        
        # Dry run cleanup
        cleanup_result = writer.cleanup_output_dir("*.html", dry_run=True)
        print(f"HTML files found for cleanup: {cleanup_result['files_found']}")
        print(f"Would delete: {cleanup_result['files_found']} files")
        
        # Demo 13: Encoding and International Content
        print("\n13. International Content Handling")
        print("-" * 30)
        
        japanese_content = """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>日本語テスト</title>
        </head>
        <body>
            <h1>商品レビュー</h1>
            <p>商品名：テスト商品</p>
            <p>カテゴリ：テストカテゴリ</p>
            <p>評価：★★★★★</p>
            <p>レビュアー：テスト評価者</p>
        </body>
        </html>
        """
        
        success = writer.write_html(japanese_content.strip(), "japanese_demo.html")
        print(f"Japanese content written: {success}")
        
        # Verify Japanese content
        japanese_file = output_dir / "japanese_demo.html"
        if japanese_file.exists():
            content = japanese_file.read_text(encoding='utf-8')
            print(f"Japanese characters preserved: {'商品レビュー' in content}")
        
        # Final Statistics
        print("\n" + "=" * 50)
        print("📊 Final Statistics")
        print("=" * 50)
        
        final_stats = writer.get_write_stats()
        final_files = writer.list_output_files()
        
        print(f"Total files created: {len(final_files)}")
        print(f"Total operations: {final_stats['files_written']}")
        print(f"Total data written: {final_stats['total_bytes']:,} bytes")
        print(f"Output directory: {output_dir}")
        
        print("\nFile breakdown by type:")
        for format_name, format_stats in final_stats['formats'].items():
            print(f"  {format_name.upper()}: {format_stats['count']} files")
        
        print("\n✨ File I/O operations demo completed!")
        
    finally:
        # Clean up temporary directory
        print(f"\n🧹 Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()