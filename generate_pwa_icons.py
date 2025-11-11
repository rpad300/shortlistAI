"""
Generate additional PWA icon sizes from the base app-icon-512.png
Uses PIL to resize the generated image to required sizes.
"""

import os
from pathlib import Path
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_pwa_icons():
    """Generate all required PWA icon sizes."""
    
    # Source image
    source_image = Path("public/assets/logos/app-icon-512.png")
    
    if not source_image.exists():
        logger.error(f"❌ Source image not found: {source_image}")
        logger.info("💡 Run 'python generate_images_nanobanan.py' first")
        return False
    
    # Output directory
    output_dir = Path("src/frontend/public/icons")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Required sizes for PWA
    sizes = [
        16,   # Favicon
        32,   # Favicon
        48,   # Favicon
        72,   # Android
        96,   # Android
        128,  # Android
        144,  # Apple touch, Android
        152,  # Apple touch
        180,  # Apple touch
        192,  # Android, PWA standard
        384,  # Android
        512,  # Android, PWA splash
    ]
    
    logger.info("="*70)
    logger.info("🎨 PWA Icon Generator")
    logger.info("="*70)
    logger.info(f"Source: {source_image}")
    logger.info(f"Output: {output_dir}")
    logger.info(f"Sizes to generate: {len(sizes)}")
    logger.info("="*70)
    logger.info("")
    
    # Load source image
    try:
        img = Image.open(source_image)
        logger.info(f"✅ Loaded source image: {img.size[0]}x{img.size[1]}px")
    except Exception as e:
        logger.error(f"❌ Failed to load image: {e}")
        return False
    
    # Generate each size
    successful = 0
    failed = 0
    
    for size in sizes:
        try:
            # Resize image
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save
            output_file = output_dir / f"icon-{size}x{size}.png"
            resized.save(output_file, "PNG", optimize=True)
            
            file_size = output_file.stat().st_size / 1024  # KB
            logger.info(f"✅ {size}x{size}px → {output_file.name} ({file_size:.1f} KB)")
            successful += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to generate {size}x{size}px: {e}")
            failed += 1
    
    # Also copy the 512 version
    try:
        img.save(output_dir / "icon-512x512.png", "PNG", optimize=True)
        logger.info(f"✅ 512x512px → icon-512x512.png (original)")
        successful += 1
    except Exception as e:
        logger.error(f"❌ Failed to copy 512x512: {e}")
    
    # Generate favicon.ico (multi-size)
    try:
        favicon_sizes = [(16, 16), (32, 32), (48, 48)]
        favicon_images = [img.resize(size, Image.Resampling.LANCZOS) for size in favicon_sizes]
        
        favicon_path = Path("src/frontend/public/favicon.ico")
        favicon_images[0].save(
            favicon_path,
            format="ICO",
            sizes=favicon_sizes,
            append_images=favicon_images[1:]
        )
        logger.info(f"✅ Multi-size favicon.ico generated")
        successful += 1
    except Exception as e:
        logger.error(f"❌ Failed to generate favicon.ico: {e}")
    
    # Generate apple-touch-icon.png (180x180 is standard)
    try:
        apple_icon = img.resize((180, 180), Image.Resampling.LANCZOS)
        apple_path = Path("src/frontend/public/apple-touch-icon.png")
        apple_icon.save(apple_path, "PNG", optimize=True)
        logger.info(f"✅ apple-touch-icon.png (180x180) generated")
        successful += 1
    except Exception as e:
        logger.error(f"❌ Failed to generate apple-touch-icon: {e}")
    
    # Summary
    logger.info("")
    logger.info("="*70)
    logger.info("📊 SUMMARY")
    logger.info("="*70)
    logger.info(f"✅ Successfully generated: {successful}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📁 Output directory: {output_dir.absolute()}")
    logger.info("="*70)
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = generate_pwa_icons()
        exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)
