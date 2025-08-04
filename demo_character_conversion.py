#!/usr/bin/env python3
"""
Demonstration of Atobusu character conversion system.
"""

from atobusu.core.character_converter import CharacterConverter

def main():
    print("🔄 Atobusu Character Conversion Demo")
    print("=" * 50)
    
    # Initialize converter
    converter = CharacterConverter()
    
    # Test cases based on the template files provided
    test_cases = [
        'Hello "world" with quotes',
        'Product ① has ◎ rating',
        'Music ♪ and ハート symbols',
        'Keep ※ reference mark as-is',
        'Complex: "Product ①②③" with ◎♪ and ※ note',
        'Japanese: テスト "商品①" は◎評価でハート付き',
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Input:  {text}")
        
        # Get conversion statistics
        stats = converter.get_conversion_stats(text)
        print(f"   Stats:  {stats}")
        
        # Apply conversions
        result = converter.apply_all_conversions(text)
        print(f"   Output: {result}")
        
        # Show what changed
        if result != text:
            print(f"   ✅ Converted!")
        else:
            print(f"   ➡️  No changes needed")
    
    print("\n" + "=" * 50)
    print("✨ Character conversion demo completed!")

if __name__ == "__main__":
    main()