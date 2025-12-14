"""
Script to update all templates from 'product' to 'product_category'
"""
import os
import re

def update_template_file(filepath):
    """Update a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace template variable names
        content = re.sub(r'for product in products', r'for product_category in product_categories', content)
        content = re.sub(r'\{\{\s*product\.', r'{{ product_category.', content)
        content = re.sub(r'product\.slug', r'product_category.slug', content)
        content = re.sub(r'product\.title', r'product_category.title', content)
        content = re.sub(r'product\.description', r'product_category.description', content)
        content = re.sub(r'product\.image', r'product_category.image', content)
        content = re.sub(r'product\.order', r'product_category.order', content)
        
        # Update "No products" messages
        content = content.replace('No products available', 'No product categories available')
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {filepath}")
            return True
        else:
            print(f"  No changes: {filepath}")
            return False
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        return False

def main():
    """Update all template files"""
    templates_dir = r'c:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App\core\templates\core'
    
    files_to_update = [
        'products.html',
        'industry-pages/restaurant.html',
        'industry-pages/retail.html',
        'industry-pages/boutique.html',
        'industry-pages/grocery.html',
        'industry-pages/bakery.html',
    ]
    
    updated_count = 0
    for file in files_to_update:
        filepath = os.path.join(templates_dir, file)
        if os.path.exists(filepath):
            if update_template_file(filepath):
                updated_count += 1
        else:
            print(f"✗ File not found: {filepath}")
    
    print(f"\n✓ Updated {updated_count} template file(s)")

if __name__ == '__main__':
    main()
