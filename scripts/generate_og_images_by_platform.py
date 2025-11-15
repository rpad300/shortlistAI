"""
Generate platform-specific Open Graph images.

Creates optimized OG images for different platforms:
- Facebook: 1200x630px (standard OG)
- LinkedIn: 1200x627px (slightly different aspect ratio)
- Twitter: 1200x600px (wider aspect ratio)

Run from project root: python scripts/generate_og_images_by_platform.py
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Platform-specific dimensions
PLATFORM_DIMENSIONS = {
    "facebook": (1200, 630),  # Standard OG
    "linkedin": (1200, 627),  # LinkedIn optimized
    "twitter": (1200, 600),   # Twitter optimized
    "default": (1200, 630)    # Default OG
}


# Brand colors
AI_BLUE = "#0066FF"
NEURAL_PURPLE = "#7C3AED"
WHITE = "#FFFFFF"


def create_platform_image(platform: str, output_path: str, base_image_path: str = None) -> bool:
    """Create platform-specific OG image."""
    try:
        width, height = PLATFORM_DIMENSIONS.get(platform, PLATFORM_DIMENSIONS["default"])
        logger.info(f"🎨 Generating {platform.upper()} image: {width}x{height}")
        
        # Load base image if provided
        if base_image_path and os.path.exists(base_image_path):
            base_img = Image.open(base_image_path).convert("RGB")
            # Resize to platform dimensions
            img = base_img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            # Create gradient background
            img = Image.new("RGB", (width, height), color=AI_BLUE)
            draw = ImageDraw.Draw(img)
            
            # Draw gradient (simplified - diagonal gradient)
            for y in range(height):
                # Create gradient from blue to purple
                ratio = y / height
                r1, g1, b1 = 0, 102, 255  # #0066FF
                r2, g2, b2 = 124, 58, 237  # #7C3AED
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
        
        # Save image
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG", optimize=True)
        
        logger.info(f"✅ Saved: {output_path}\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating {platform} image: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_all_platform_images():
    """Generate OG images for all platforms."""
    
    assets_dir = Path("public/assets/social")
    base_image_path = assets_dir / "og-default.png"
    
    logger.info("="*70)
    logger.info("🌐 ShortlistAI - Platform-Specific OG Image Generator")
    logger.info("="*70)
    logger.info(f"📂 Base image: {base_image_path}")
    logger.info(f"📂 Output directory: {assets_dir}\n")
    
    # Generate images for each platform
    platforms = ["facebook", "linkedin", "twitter"]
    results = {}
    
    for platform in platforms:
        output_path = assets_dir / f"og-{platform}.png"
        success = create_platform_image(platform, str(output_path), str(base_image_path))
        results[platform] = success
    
    # Summary
    logger.info("="*70)
    logger.info("📊 Summary")
    logger.info("="*70)
    
    for platform, success in results.items():
        width, height = PLATFORM_DIMENSIONS[platform]
        status = "✅" if success else "❌"
        logger.info(f"{status} {platform.upper()}: {width}x{height}px")
    
    total = len(results)
    successful = sum(1 for s in results.values() if s)
    logger.info(f"\n✅ Success: {successful}/{total}")
    
    if successful == total:
        logger.info("\n🎉 All platform-specific OG images generated successfully!")
        logger.info("\n💡 Note: These images use the same design but are optimized for each platform's dimensions.")
    else:
        logger.warning(f"\n⚠️  {total - successful} image(s) failed to generate")


if __name__ == "__main__":
    generate_all_platform_images()

