#!/usr/bin/env python3
"""
Temporary script to generate multiple icon sizes from the original app icon
and update manifest.json with proper icon references.
"""

import json
import os
from PIL import Image

# Define icon sizes to generate
ICON_SIZES = [48, 72, 96, 144, 192, 512]

# Paths
STATIC_DIR = "static"
ORIGINAL_ICON = os.path.join(STATIC_DIR, "TutionTrack_appIcon.png")
MANIFEST_PATH = os.path.join(STATIC_DIR, "manifest.json")

def generate_icons():
    """Generate resized icons from the original app icon."""
    print(f"Reading original icon: {ORIGINAL_ICON}")
    
    if not os.path.exists(ORIGINAL_ICON):
        print(f"Error: Original icon not found at {ORIGINAL_ICON}")
        return False
    
    # Open the original image
    try:
        original = Image.open(ORIGINAL_ICON)
        print(f"Original icon size: {original.size}")
    except Exception as e:
        print(f"Error opening image: {e}")
        return False
    
    # Generate each size
    generated_files = []
    for size in ICON_SIZES:
        # Resize with high-quality resampling
        resized = original.resize((size, size), Image.LANCZOS)
        
        # Generate filename
        filename = f"TutionTrack_appIcon_{size}x{size}.png"
        filepath = os.path.join(STATIC_DIR, filename)
        
        # Save the resized icon
        resized.save(filepath, "PNG", optimize=True)
        generated_files.append((size, filename))
        print(f"Generated: {filename} ({size}x{size})")
    
    print(f"\n✓ Successfully generated {len(generated_files)} icon sizes")
    return generated_files

def update_manifest(generated_files):
    """Update manifest.json with proper icon references."""
    print(f"\nReading manifest: {MANIFEST_PATH}")
    
    if not os.path.exists(MANIFEST_PATH):
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        return False
    
    # Read current manifest
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    
    # Update icons array
    new_icons = []
    
    # Add maskable icons (192 and 512)
    for size in [192, 512]:
        filename = f"TutionTrack_appIcon_{size}x{size}.png"
        new_icons.append({
            "src": f"/static/{filename}",
            "sizes": f"{size}x{size}",
            "type": "image/png",
            "purpose": "maskable"
        })
    
    # Add regular icons (all sizes)
    for size in ICON_SIZES:
        filename = f"TutionTrack_appIcon_{size}x{size}.png"
        new_icons.append({
            "src": f"/static/{filename}",
            "sizes": f"{size}x{size}",
            "type": "image/png",
            "purpose": "any"
        })
    
    # Update manifest
    manifest["icons"] = new_icons
    
    # Update shortcut icons
    for shortcut in manifest.get("shortcuts", []):
        if "icons" in shortcut:
            shortcut["icons"] = [{
                "src": "/static/TutionTrack_appIcon_96x96.png",
                "sizes": "96x96"
            }]
    
    # Write updated manifest
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Updated manifest.json with {len(new_icons)} icon entries")
    return True

def main():
    """Main function."""
    print("=" * 60)
    print("Icon Generator for TuitionTrack")
    print("=" * 60)
    print()
    
    # Generate icons
    generated_files = generate_icons()
    if not generated_files:
        print("\n✗ Failed to generate icons")
        return
    
    # Update manifest
    if update_manifest(generated_files):
        print("\n" + "=" * 60)
        print("✓ All done! Icons generated and manifest updated.")
        print("=" * 60)
        print("\nGenerated files:")
        for size, filename in generated_files:
            filepath = os.path.join(STATIC_DIR, filename)
            file_size = os.path.getsize(filepath)
            print(f"  - {filename} ({file_size:,} bytes)")
    else:
        print("\n✗ Failed to update manifest")

if __name__ == "__main__":
    main()

