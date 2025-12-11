#!/usr/bin/env python3
"""
Generate multiple sizes of Niya help bot avatar
Creates optimized versions for different use cases
"""

from PIL import Image
import os

def generate_niya_sizes():
    """Generate multiple sizes of Niya avatar"""
    
    # Input image
    input_path = 'static/niya_help_bot.png'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found!")
        return
    
    # Open original image
    original = Image.open(input_path)
    print(f"Original image size: {original.size}")
    print(f"Original mode: {original.mode}")
    
    # Convert to RGBA if needed (for transparency)
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
        print("Converted to RGBA mode")
    
    # Sizes needed for different use cases
    sizes = {
        'niya_avatar_60x60.png': (60, 60),      # Floating button
        'niya_avatar_50x50.png': (50, 50),      # Small button
        'niya_avatar_80x80.png': (80, 80),      # Header avatar
        'niya_avatar_100x100.png': (100, 100),  # Medium display
        'niya_avatar_200x200.png': (200, 200),  # Large display
    }
    
    # Ensure output directory exists
    output_dir = 'static'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate each size
    for filename, size in sizes.items():
        output_path = os.path.join(output_dir, filename)
        
        # Resize with high-quality resampling
        try:
            resized = original.resize(size, Image.Resampling.LANCZOS)
        except AttributeError:
            # Fallback for older PIL versions
            resized = original.resize(size, Image.LANCZOS)
        
        # Save with optimization
        resized.save(output_path, 'PNG', optimize=True)
        print(f"Created: {output_path} ({size[0]}x{size[1]})")
    
    print("\n✅ All sizes generated successfully!")
    print("\nGenerated files:")
    for filename in sizes.keys():
        print(f"  - static/{filename}")

if __name__ == '__main__':
    generate_niya_sizes()

