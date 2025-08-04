#!/usr/bin/env python3
"""
Demonstration of Atobusu data processing engine.
"""

import json
import yaml
import tempfile
from pathlib import Path

from atobusu.core.data_processor import DataProcessor
from atobusu.core.data_models import InputData, TemplateData


def main():
    print("🔧 Atobusu Data Processing Engine Demo")
    print("=" * 50)
    
    # Initialize processor
    processor = DataProcessor()
    
    # Demo 1: Process JSON file
    print("\n1. Processing JSON File")
    print("-" * 30)
    
    json_data = {
        "content": 'Product "Test①" has ◎ rating',
        "template_type": "page",
        "output_format": "html",
        "template_data": {
            "product_code": "サンプル商品コード123456",
            "product_name": "テスト商品名",
            "dates": {
                "post_date": "2025/01/15",
                "short_date": "25/01/15"
            },
            "category": "テストカテゴリ",
            "reviewer_name": "テスト評価者名前",
            "rating": 5
        },
        "variables": {
            "title": "Product Review",
            "author": "Test Reviewer"
        }
    }
    
    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
        json_path = f.name
    
    try:
        processed_data = processor.process_file(json_path)
        
        print(f"✅ File processed successfully!")
        print(f"   Template Type: {processed_data.template_type}")
        print(f"   Output Format: {processed_data.output_format}")
        print(f"   Product Code: {processed_data.template_data.product_code}")
        print(f"   Rating: {processed_data.template_data.rating}")
        print(f"   Variables: {list(processed_data.template_variables.keys())}")
        
        # Show character conversion
        print(f"\n   Original content: {json_data['content']}")
        print(f"   Converted content: {processed_data.converted_content}")
        
        # Show conversion stats
        stats = processed_data.processing_metadata.get('conversion_stats', {})
        print(f"   Conversion stats: {stats}")
        
    finally:
        Path(json_path).unlink()
    
    # Demo 2: Process YAML file
    print("\n2. Processing YAML File")
    print("-" * 30)
    
    yaml_data = {
        "content": 'Japanese: テスト "商品①" は◎評価でハート付き',
        "template_type": "index",
        "output_format": "php",
        "template_data": {
            "product_code": "YAML_TEST_001",
            "product_name": "YAML Test Product",
            "rating": 4
        }
    }
    
    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False)
        yaml_path = f.name
    
    try:
        processed_data = processor.process_file(yaml_path)
        
        print(f"✅ YAML file processed successfully!")
        print(f"   Template Type: {processed_data.template_type}")
        print(f"   Output Format: {processed_data.output_format}")
        print(f"   Product Code: {processed_data.template_data.product_code}")
        
        # Show character conversion with Japanese text
        print(f"\n   Original content: {yaml_data['content']}")
        print(f"   Converted content: {processed_data.converted_content}")
        
        # Show template context
        context = processed_data.to_template_context()
        print(f"   Template context keys: {list(context.keys())}")
        
    finally:
        Path(yaml_path).unlink()
    
    # Demo 3: Direct data processing
    print("\n3. Direct Data Processing")
    print("-" * 30)
    
    input_data = InputData(
        content='Complex example: "Product ①②③" with ◎♪ and ※ note',
        metadata={
            "parsed_data": {
                "template_type": "content",
                "output_format": "mixed",
                "template_data": {
                    "product_code": "DIRECT_001",
                    "product_name": "Direct Processing Test",
                    "dates": {
                        "post_date": "2025/08/04",
                        "short_date": "25/08/04"
                    },
                    "rating": 3
                }
            }
        },
        source_type="gui"
    )
    
    processed_data = processor.process_data(input_data)
    
    print(f"✅ Direct processing completed!")
    print(f"   Source Type: {processed_data.original_input.source_type}")
    print(f"   Template Type: {processed_data.template_type}")
    print(f"   Output Format: {processed_data.output_format}")
    
    # Show all conversions
    print(f"\n   Original: {input_data.content}")
    print(f"   Converted: {processed_data.converted_content}")
    
    # Demo 4: Template data creation
    print("\n4. Template Data Creation")
    print("-" * 30)
    
    template_dict = {
        "product_code": "TEMPLATE_001",
        "product_name": "Template Demo Product",
        "dates": {
            "post_date": "2025/01/15",
            "short_date": "25/01/15"
        },
        "category": "Demo Category",
        "reviewer_name": "Demo Reviewer",
        "rating": 5,
        "additional_data": {
            "color": "blue",
            "size": "large"
        }
    }
    
    template_data = processor.create_template_data_from_dict(template_dict)
    placeholder_dict = template_data.to_placeholder_dict()
    
    print(f"✅ Template data created!")
    print(f"   Product Code: {template_data.product_code}")
    print(f"   Rating: {template_data.rating}")
    print(f"   Placeholder keys: {list(placeholder_dict.keys())}")
    
    # Demo 5: Processing statistics
    print("\n5. Processing Statistics")
    print("-" * 30)
    
    stats = processor.get_processing_stats()
    print(f"✅ Processing statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 50)
    print("✨ Data processing engine demo completed!")


if __name__ == "__main__":
    main()