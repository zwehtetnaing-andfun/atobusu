#!/usr/bin/env python3
"""
Demonstration of Atobusu placeholder processing system.
"""

from atobusu.templates.placeholder_processor import PlaceholderProcessor


def main():
    print("🔧 Atobusu Placeholder Processing System Demo")
    print("=" * 60)
    
    # Initialize processor
    processor = PlaceholderProcessor()
    
    # Sample data for demonstrations
    demo_data = {
        'product_code': 'サンプル商品コード123456',
        'product_name': 'テスト商品名',
        'category': 'テストカテゴリ',
        'reviewer_name': 'テスト評価者名前',
        'rating': 5,
        'dates': {
            'post_date': '2025/01/15',
            'short_date': '25/01/15',
            'update_date': '2025/01/20'
        },
        'title': 'Product Review Demo',
        'description': 'This is a demo description'
    }
    
    # Demo 1: Product Code Processing
    print("\n1. Product Code Processing")
    print("-" * 40)
    
    product_content = "Product: 商品コード and product_code and 製品コード"
    result = processor.process_product_codes(product_content, demo_data)
    
    print(f"Original: {product_content}")
    print(f"Result:   {result}")
    
    # Demo 2: Date Placeholder Processing
    print("\n2. Date Placeholder Processing")
    print("-" * 40)
    
    date_content = "Posted: 2025/00/00, Updated: '25/00/00, Review: post_date"
    result = processor.process_date_placeholders(date_content, demo_data)
    
    print(f"Original: {date_content}")
    print(f"Result:   {result}")
    
    # Demo 3: PHP Function Processing
    print("\n3. PHP Function Processing")
    print("-" * 40)
    
    php_content = '''
    <img src="<?=prod_info("商品コード123", "mimg")?>" alt="<?=prod_info("商品コード456", "pname")?>">
    '''
    result = processor.process_php_function_params(php_content, demo_data)
    
    print(f"Original: {php_content.strip()}")
    print(f"Result:   {result.strip()}")
    
    # Demo 4: Generic Placeholders
    print("\n4. Generic Placeholder Processing")
    print("-" * 40)
    
    generic_content = "Title: {{title}}, Category: {{category}}, Rating: {{rating}}"
    result = processor.process_generic_placeholders(generic_content, demo_data)
    
    print(f"Original: {generic_content}")
    print(f"Result:   {result}")
    
    # Demo 5: Template Variables
    print("\n5. Template Variable Processing")
    print("-" * 40)
    
    template_content = "Product: ${product_name}, Description: ${description}"
    result = processor.process_template_variables(template_content, demo_data)
    
    print(f"Original: {template_content}")
    print(f"Result:   {result}")
    
    # Demo 6: Comprehensive Processing
    print("\n6. Comprehensive Processing")
    print("-" * 40)
    
    comprehensive_content = '''
    <div class="product-review">
        <h2>{{title}}</h2>
        <p>Product: product_code (${product_name})</p>
        <p>Category: {{category}}</p>
        <p>Posted: 2025/00/00</p>
        <p>Rating: {{rating}}/5</p>
        <img src="<?=prod_info("test_code", "mimg")?>" alt="Product Image">
    </div>
    '''
    
    result = processor.apply_all_replacements(comprehensive_content, demo_data)
    
    print("Original:")
    print(comprehensive_content.strip())
    print("\nResult:")
    print(result.strip())
    
    # Demo 7: Real-world Template (based on provided examples)
    print("\n7. Real-world Template Processing")
    print("-" * 40)
    
    real_world_content = '''
    <!--サンプル商品コード123456_サンプル商品名-->
    <li>
      <dl>
        <dt class="item_img">
            <a href="/review-product_code" target="_self">
                <img src="<?=prod_info("test_code", "mimg")?>" alt="{{product_name}}">
            </a>
          </dt>
        <dd class="item_user_box">
            <p class="item_name">{{product_name}}</p>
            <div class="item_date">
                <div class="item_post_date">2025/00/00</div>
                <div class="item_post_name">全体：{{reviewer_name}}</div>
            </div>
            <div class="item_star_box">
                <div class="item_star_tag">おすすめ度</div>
                <div class="item_star">★★★★★</div>
            </div>
        </dd>
      </dl>
    </li>
    '''
    
    result = processor.apply_all_replacements(real_world_content, demo_data)
    
    print("Real-world template processed:")
    print(result.strip())
    
    # Demo 8: Placeholder Statistics
    print("\n8. Placeholder Statistics")
    print("-" * 40)
    
    stats_content = '''
    Product: 商品コード and product_code
    Dates: 2025/00/00 and '25/00/00
    PHP: <?=prod_info("test", "pname")?> and <?=prod_info("test2", "price")?>
    Generic: {{title}}, {{category}}, {{rating}}
    Template: ${product_name}, ${description}
    '''
    
    stats = processor.get_placeholder_stats(stats_content)
    
    print("Content analyzed:")
    print(stats_content.strip())
    print("\nPlaceholder Statistics:")
    for key, count in stats.items():
        print(f"  {key}: {count}")
    
    # Demo 9: Custom Pattern
    print("\n9. Custom Pattern Processing")
    print("-" * 40)
    
    # Add a custom pattern
    processor.add_custom_pattern('custom_tag', r'\[custom:([^]]+)\]')
    
    custom_content = "Custom value: [custom:test_value] and normal {{title}}"
    # For demo purposes, we'll just show the pattern was added
    print(f"Added custom pattern: [custom:value]")
    print(f"Available patterns: {list(processor.placeholder_patterns.keys())}")
    
    print("\n" + "=" * 60)
    print("✨ Placeholder processing system demo completed!")


if __name__ == "__main__":
    main()