#!/usr/bin/env python3
"""
Demonstration of Atobusu template management system.
"""

import tempfile
import shutil
from pathlib import Path

from atobusu.templates.template_manager import TemplateManager


def main():
    print("🎨 Atobusu Template Management System Demo")
    print("=" * 60)
    
    # Create temporary directory for templates
    temp_dir = tempfile.mkdtemp()
    template_dir = Path(temp_dir)
    
    try:
        # Initialize template manager
        manager = TemplateManager(str(template_dir))
        
        # Sample data for demonstrations
        demo_data = {
            'title': 'Product Review Demo',
            'product_code': 'DEMO123456',
            'product_name': 'Demo Product Name',
            'category': 'Demo Category',
            'reviewer_name': 'Demo Reviewer',
            'rating': 5,
            'post_date': '2025/01/15',
            'short_date': '25/01/15',
            'content': 'This is demo content with <strong>HTML</strong>',
            'description': 'Demo product description'
        }
        
        # Demo 1: HTML Template
        print("\n1. HTML Template Rendering")
        print("-" * 40)
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head><title>{{title}}</title></head>
        <body>
            <h1>{{title}}</h1>
            <p>Product: product_code ({{product_name}})</p>
            <p>Category: {{category}}</p>
            <p>Date: 2025/00/00</p>
            <p>Rating: {{rating}}/5</p>
            <div>{{content|safe}}</div>
        </body>
        </html>
        """
        
        # Create template file
        html_path = template_dir / "demo.html"
        html_path.write_text(html_template.strip(), encoding='utf-8')
        
        result = manager.render_html("demo.html", demo_data)
        print("HTML Template Result:")
        print(result[:300] + "..." if len(result) > 300 else result)
        
        # Demo 2: PHP Template
        print("\n2. PHP Template Rendering")
        print("-" * 40)
        
        php_template = """
        <?php
            $title = "{{title}}";
            $product_code = "{{product_code}}";
        ?>
        <h1><?php echo $title; ?></h1>
        <p>Product: <?=prod_info("product_code", "pname")?></p>
        <p>Image: <img src="<?=prod_info("test_code", "mimg")?>" alt="{{product_name}}"></p>
        <p>Date: 2025/00/00</p>
        <div class="rating">Rating: {{rating}}/5</div>
        """
        
        # Create PHP template file
        php_path = template_dir / "demo.php"
        php_path.write_text(php_template.strip(), encoding='utf-8')
        
        result = manager.render_php("demo.php", demo_data)
        print("PHP Template Result:")
        print(result[:400] + "..." if len(result) > 400 else result)
        
        # Demo 3: Mixed Content Template
        print("\n3. Mixed Content Template")
        print("-" * 40)
        
        mixed_template = """
        <div class="product-review">
            <h2>{{title}}</h2>
            <div class="product-info">
                <p>Product: product_code</p>
                <p>Name: {{product_name}}</p>
                <p>Category: {{category}}</p>
            </div>
            <div class="review-date">
                <span>Posted: 2025/00/00</span>
                <span>Short: '25/00/00</span>
            </div>
            <div class="php-section">
                <img src="<?=prod_info("demo_code", "mimg")?>" alt="Product Image">
                <?php echo "Dynamic PHP content"; ?>
            </div>
            <div class="rating">
                <span>Rating: {{rating}}/5</span>
                <div class="stars">
                    {% for i in range(rating) %}★{% endfor %}
                </div>
            </div>
        </div>
        """
        
        # Create mixed template file
        mixed_path = template_dir / "mixed.html"
        mixed_path.write_text(mixed_template.strip(), encoding='utf-8')
        
        result = manager.render_mixed_template("mixed.html", demo_data)
        print("Mixed Template Result:")
        print(result)
        
        # Demo 4: Template from String
        print("\n4. Template from String")
        print("-" * 40)
        
        string_template = """
        <article>
            <h3>{{title}}</h3>
            <p>Product Code: product_code</p>
            <p>Reviewer: {{reviewer_name}}</p>
            <p>Date: 2025/00/00</p>
        </article>
        """
        
        result = manager.create_template_from_string(string_template.strip(), demo_data)
        print("String Template Result:")
        print(result)
        
        # Demo 5: Template Validation
        print("\n5. Template Validation")
        print("-" * 40)
        
        # Validate existing templates
        templates = ["demo.html", "demo.php", "mixed.html"]
        for template_name in templates:
            validation = manager.validate_template(template_name)
            print(f"Template '{template_name}':")
            print(f"  Valid: {validation['is_valid']}")
            print(f"  Type: {validation['template_type']}")
            if 'placeholder_stats' in validation:
                stats = validation['placeholder_stats']
                print(f"  Placeholders: {sum(stats.values())} total")
            if validation['errors']:
                print(f"  Errors: {validation['errors']}")
            print()
        
        # Demo 6: Template Management Features
        print("\n6. Template Management Features")
        print("-" * 40)
        
        # Get template list
        template_list = manager.get_template_list()
        print(f"Available templates: {template_list}")
        
        # Check template existence
        print(f"demo.html exists: {manager.template_exists('demo.html')}")
        print(f"nonexistent.html exists: {manager.template_exists('nonexistent.html')}")
        
        # Cache statistics
        cache_stats = manager.get_cache_stats()
        print(f"Cache stats: {cache_stats}")
        
        # Demo 7: Auto-detection Rendering
        print("\n7. Auto-detection Rendering")
        print("-" * 40)
        
        # Test auto-detection for different file types
        auto_results = {}
        for template_name in ["demo.html", "demo.php", "mixed.html"]:
            result = manager.render_template(template_name, demo_data, "auto")
            auto_results[template_name] = len(result)
            print(f"Auto-rendered {template_name}: {len(result)} characters")
        
        # Demo 8: Japanese Content
        print("\n8. Japanese Content Processing")
        print("-" * 40)
        
        japanese_template = """
        <div class="japanese-review">
            <h2>{{title}}</h2>
            <p>商品名：{{product_name}}</p>
            <p>カテゴリ：{{category}}</p>
            <p>レビュアー：{{reviewer_name}}</p>
            <p>投稿日：2025/00/00</p>
            <p>評価：{{rating}}/5</p>
        </div>
        """
        
        japanese_data = {
            'title': 'テスト商品レビュー',
            'product_name': 'テスト商品名',
            'category': 'テストカテゴリ',
            'reviewer_name': 'テスト評価者',
            'rating': 5,
            'post_date': '2025/01/15'
        }
        
        result = manager.create_template_from_string(japanese_template.strip(), japanese_data)
        print("Japanese Template Result:")
        print(result)
        
        # Demo 9: Error Handling
        print("\n9. Error Handling Demo")
        print("-" * 40)
        
        try:
            manager.render_html("nonexistent.html", demo_data)
        except Exception as e:
            print(f"Expected error for nonexistent template: {type(e).__name__}")
        
        # Invalid template syntax
        invalid_template = "{{invalid template syntax"
        invalid_path = template_dir / "invalid.html"
        invalid_path.write_text(invalid_template, encoding='utf-8')
        
        try:
            manager.load_template("invalid.html")
        except Exception as e:
            print(f"Expected error for invalid syntax: {type(e).__name__}")
        
        print("\n" + "=" * 60)
        print("✨ Template management system demo completed!")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()