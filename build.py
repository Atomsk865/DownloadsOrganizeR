#!/usr/bin/env python3
"""
Build script to minify CSS and create production-ready assets
Reduces file sizes by 30-50% for faster loading
"""

import os
import re
from pathlib import Path

def minify_css(css_content):
    """Simple CSS minifier - removes comments, whitespace, and unnecessary characters"""
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Remove whitespace around operators
    css = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css)
    # Remove multiple spaces
    css = re.sub(r'\s+', ' ', css)
    # Remove spaces after colons
    css = re.sub(r':\s', ':', css)
    # Remove trailing semicolons before }
    css = re.sub(r';\}', '}', css)
    # Remove leading/trailing whitespace
    css = css.strip()
    return css

def minify_file(input_path, output_path):
    """Minify a CSS file"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        minified = minify_css(content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        
        original_size = len(content)
        minified_size = len(minified)
        reduction = ((original_size - minified_size) / original_size) * 100
        
        print(f"✓ Minified {input_path.name}")
        print(f"  {original_size:,} bytes → {minified_size:,} bytes ({reduction:.1f}% reduction)")
        return True
    except Exception as e:
        print(f"✗ Error minifying {input_path}: {e}")
        return False

def main():
    """Main build script"""
    print("🚀 DownloadsOrganizeR Build Script")
    print("=" * 50)
    
    root = Path(__file__).parent
    static_css = root / 'static' / 'css'
    
    # Ensure directories exist
    static_css.mkdir(parents=True, exist_ok=True)
    
    # Files to minify
    files_to_minify = [
        (root / 'static' / 'css' / 'dashboard.css', 
         root / 'static' / 'css' / 'dashboard.min.css'),
    ]
    
    success_count = 0
    for input_file, output_file in files_to_minify:
        if input_file.exists():
            if minify_file(input_file, output_file):
                success_count += 1
        else:
            print(f"⚠ Skipping {input_file.name} (not found)")
    
    print("=" * 50)
    print(f"✅ Build complete! {success_count} file(s) minified")
    print("\nTo use minified assets in production:")
    print("  Set ASSET_VERSION environment variable")
    print("  Update dashboard_base.html to use .min.css files")

if __name__ == '__main__':
    main()
