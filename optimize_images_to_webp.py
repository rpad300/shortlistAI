"""
Convert brand PNG images to WebP format for better performance.

WebP provides ~25-35% better compression than PNG while maintaining quality.
"""

import os
from pathlib import Path
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def convert_to_webp(png_path: Path, quality: int = 85) -> bool:
    """
    Convert PNG image to WebP format.
    
    Args:
        png_path: Path to PNG file
        quality: WebP quality (0-100, 85 is good balance)
    
    Returns:
        True if successful
    """
    try:
        webp_path = png_path.with_suffix('.webp')
        
        # Open PNG
        img = Image.open(png_path)
        
        # Convert and save as WebP
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        
        # Get file sizes
        png_size = png_path.stat().st_size / 1024  # KB
        webp_size = webp_path.stat().st_size / 1024  # KB
        savings = ((png_size - webp_size) / png_size) * 100
        
        logger.info(f"✅ {png_path.name}")
        logger.info(f"   PNG:  {png_size:,.1f} KB")
        logger.info(f"   WebP: {webp_size:,.1f} KB ({savings:.1f}% smaller)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to convert {png_path.name}: {e}")
        return False


def optimize_all_images():
    """Convert all brand PNG images to WebP."""
    
    logger.info("="*70)
    logger.info("🎨 Image Optimization - PNG to WebP Converter")
    logger.info("="*70)
    logger.info("")
    
    # Find all PNG images in public/assets
    assets_dir = Path("public/assets")
    
    if not assets_dir.exists():
        logger.error(f"❌ Assets directory not found: {assets_dir}")
        return False
    
    # Find all PNGs
    png_files = list(assets_dir.rglob("*.png"))
    
    if not png_files:
        logger.warning("⚠️  No PNG files found to convert")
        return True
    
    logger.info(f"📦 Found {len(png_files)} PNG images to convert")
    logger.info("="*70)
    logger.info("")
    
    successful = 0
    failed = 0
    total_png_size = 0
    total_webp_size = 0
    
    for png_file in png_files:
        # Skip prompt files
        if '_PROMPT' in png_file.name:
            continue
        
        logger.info(f"🔄 Converting: {png_file.relative_to(assets_dir)}")
        
        if convert_to_webp(png_file, quality=85):
            successful += 1
            # Calculate sizes for summary
            png_size = png_file.stat().st_size
            webp_path = png_file.with_suffix('.webp')
            webp_size = webp_path.stat().st_size
            total_png_size += png_size
            total_webp_size += webp_size
        else:
            failed += 1
        
        logger.info("")  # Blank line between conversions
    
    # Summary
    logger.info("="*70)
    logger.info("📊 OPTIMIZATION SUMMARY")
    logger.info("="*70)
    logger.info(f"✅ Successfully converted: {successful}/{len(png_files)}")
    logger.info(f"❌ Failed: {failed}/{len(png_files)}")
    
    if successful > 0:
        total_savings = ((total_png_size - total_webp_size) / total_png_size) * 100
        logger.info("")
        logger.info(f"💾 Total size reduction:")
        logger.info(f"   Original (PNG):  {total_png_size/1024/1024:.2f} MB")
        logger.info(f"   Optimized (WebP): {total_webp_size/1024/1024:.2f} MB")
        logger.info(f"   Savings: {(total_png_size - total_webp_size)/1024/1024:.2f} MB ({total_savings:.1f}%)")
        logger.info("")
        logger.info("💡 To use WebP images in your HTML:")
        logger.info("")
        logger.info("  <picture>")
        logger.info("    <source srcset=\"image.webp\" type=\"image/webp\">")
        logger.info("    <img src=\"image.png\" alt=\"Fallback for older browsers\">")
        logger.info("  </picture>")
        logger.info("")
        logger.info("📝 Note: Keep original PNGs for compatibility with older browsers")
    
    logger.info("="*70)
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = optimize_all_images()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Optimization interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Unexpected error: {e}")
        exit(1)

