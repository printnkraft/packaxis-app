"""
Script to replace 'PackAxis Canada' with 'PackAxis Packaging Canada' in all template files
"""
import os
import glob

def update_files():
    """Replace PackAxis Canada with PackAxis Packaging Canada in all HTML files"""
    templates_dir = r'c:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App\core\templates'
    
    # Find all HTML files recursively
    html_files = glob.glob(os.path.join(templates_dir, '**', '*.html'), recursive=True)
    
    updated_count = 0
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'PackAxis Canada' in content:
                new_content = content.replace('PackAxis Canada', 'PackAxis Packaging Canada')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✓ Updated: {os.path.basename(filepath)}")
                updated_count += 1
            else:
                print(f"  No changes: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"✗ Error updating {filepath}: {e}")
    
    print(f"\n✓ Updated {updated_count} file(s)")

if __name__ == '__main__':
    update_files()
