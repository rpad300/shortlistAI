"""
Generate multilingual Open Graph (OG) images for social sharing.

Creates OG images with translated text for each supported language:
- EN (English)
- PT (Portuguese)
- FR (French)
- ES (Spanish)

Run from project root: python scripts/generate_og_images_multilingual.py
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Brand colors
AI_BLUE = "#0066FF"
NEURAL_PURPLE = "#7C3AED"
WHITE = "#FFFFFF"
BLACK = "#111827"
GRAY_LIGHT = "#6B7280"


# Translations for OG images
TRANSLATIONS = {
    "en": {
        "title": "ShortlistAI",
        "tagline": "AI-Powered CV Analysis & Interview Preparation",
        "features": "Free • Multi-language • AI-Powered"
    },
    "pt": {
        "title": "ShortlistAI",
        "tagline": "Análise de CV com IA & Preparação para Entrevistas",
        "features": "Grátis • Multilíngue • Com IA"
    },
    "fr": {
        "title": "ShortlistAI",
        "tagline": "Analyse de CV par IA & Préparation aux Entretiens",
        "features": "Gratuit • Multilingue • Alimenté par IA"
    },
    "es": {
        "title": "ShortlistAI",
        "tagline": "Análisis de CV con IA & Preparación para Entrevistas",
        "features": "Gratis • Multilingüe • Con IA"
    }
}


def load_base_og_image(base_path: str) -> Image.Image:
    """Load the base OG image (without text)."""
    if os.path.exists(base_path):
        return Image.open(base_path).convert("RGBA")
    else:
        # Create a fallback gradient image if base doesn't exist
        logger.warning(f"Base image not found: {base_path}. Creating fallback...")
        img = Image.new("RGB", (1200, 630), color=AI_BLUE)
        return img.convert("RGBA")


def find_font(font_size: int, bold: bool = False):
    """Try to find a suitable font, with fallbacks."""
    font_paths = [
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",  # Bold
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/calibrib.ttf",  # Bold
        # macOS
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    
    if bold:
        # Try bold fonts first
        for path in font_paths[1::2]:  # Odd indices (bold)
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, font_size)
                except:
                    continue
    
    # Try regular fonts
    for path in font_paths[0::2]:  # Even indices (regular)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except:
                continue
    
    # Fallback to default font
    logger.warning("No suitable font found, using default")
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except:
        return ImageFont.load_default()


def add_text_to_image(
    img: Image.Image,
    title: str,
    tagline: str,
    features: str,
    lang: str
) -> Image.Image:
    """Add translated text to the OG image."""
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Define text positions (centered layout)
    width, height = img.size
    
    # Title position (top center)
    title_y = 120
    title_font_size = 72 if len(title) < 15 else 64
    title_font = find_font(title_font_size, bold=True)
    
    # Tagline position (below title)
    tagline_y = title_y + 90
    tagline_font_size = 32
    tagline_font = find_font(tagline_font_size, bold=False)
    
    # Features position (bottom)
    features_y = height - 80
    features_font_size = 24
    features_font = find_font(features_font_size, bold=False)
    
    # Get text bounding boxes for centering
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    
    tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    
    features_bbox = draw.textbbox((0, 0), features, font=features_font)
    features_width = features_bbox[2] - features_bbox[0]
    features_x = (width - features_width) // 2
    
    # Add text shadow (for better readability)
    shadow_offset = 3
    shadow_color = (0, 0, 0, 128)  # Semi-transparent black
    
    # Draw title with shadow
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title, 
              font=title_font, fill=shadow_color)
    draw.text((title_x, title_y), title, font=title_font, fill=WHITE)
    
    # Draw tagline with shadow
    draw.text((tagline_x + shadow_offset, tagline_y + shadow_offset), tagline,
              font=tagline_font, fill=shadow_color)
    draw.text((tagline_x, tagline_y), tagline, font=tagline_font, fill=WHITE)
    
    # Draw features with shadow
    draw.text((features_x + shadow_offset, features_y + shadow_offset), features,
              font=features_font, fill=shadow_color)
    draw.text((features_x, features_y), features, font=features_font, fill=WHITE)
    
    return img


def generate_og_image_for_language(lang: str, base_image_path: str, output_path: str) -> bool:
    """Generate OG image for a specific language."""
    try:
        logger.info(f"🌐 Generating OG image for: {lang.upper()}")
        
        # Load base image
        img = load_base_og_image(base_image_path)
        
        # Get translations
        translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
        title = translations["title"]
        tagline = translations["tagline"]
        features = translations["features"]
        
        # Add text to image
        img_with_text = add_text_to_image(img, title, tagline, features, lang)
        
        # Convert back to RGB for saving as PNG
        img_rgb = Image.new("RGB", img_with_text.size, (255, 255, 255))
        img_rgb.paste(img_with_text, mask=img_with_text.split()[3])  # Use alpha channel as mask
        
        # Save image
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        img_rgb.save(output_path, "PNG", optimize=True)
        
        logger.info(f"✅ Saved: {output_path}\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating OG image for {lang}: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_all_og_images():
    """Generate OG images for all supported languages."""
    
    assets_dir = Path("public/assets/social")
    base_image_path = assets_dir / "og-default.png"
    
    logger.info("="*70)
    logger.info("🌐 ShortlistAI - Multilingual OG Image Generator")
    logger.info("="*70)
    logger.info(f"📂 Base image: {base_image_path}")
    logger.info(f"📂 Output directory: {assets_dir}\n")
    
    # Check if base image exists
    if not base_image_path.exists():
        logger.warning(f"⚠️  Base image not found: {base_image_path}")
        logger.info("💡 Using fallback gradient image\n")
    
    # Generate images for each language
    languages = ["en", "pt", "fr", "es"]
    results = {}
    
    for lang in languages:
        output_path = assets_dir / f"og-{lang}.png"
        success = generate_og_image_for_language(lang, str(base_image_path), str(output_path))
        results[lang] = success
    
    # Summary
    logger.info("="*70)
    logger.info("📊 Summary")
    logger.info("="*70)
    
    for lang, success in results.items():
        status = "✅" if success else "❌"
        logger.info(f"{status} {lang.upper()}: {results[lang]}")
    
    total = len(results)
    successful = sum(1 for s in results.values() if s)
    logger.info(f"\n✅ Success: {successful}/{total}")
    
    if successful == total:
        logger.info("\n🎉 All OG images generated successfully!")
    else:
        logger.warning(f"\n⚠️  {total - successful} image(s) failed to generate")


if __name__ == "__main__":
    generate_all_og_images()

