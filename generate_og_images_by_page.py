"""
Generate Open Graph images for different pages (home, about, pricing, features).

Creates page-specific OG images with translated text for each supported language.
Run from project root: python generate_og_images_by_page.py
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


# Page-specific translations
PAGE_TRANSLATIONS = {
    "about": {
        "en": {
            "title": "ShortlistAI",
            "tagline": "How It Works",
            "features": "About Our Platform"
        },
        "pt": {
            "title": "ShortlistAI",
            "tagline": "Como Funciona",
            "features": "Sobre Nossa Plataforma"
        },
        "fr": {
            "title": "ShortlistAI",
            "tagline": "Comment Ça Marche",
            "features": "À Propos de Notre Plateforme"
        },
        "es": {
            "title": "ShortlistAI",
            "tagline": "Cómo Funciona",
            "features": "Acerca de Nuestra Plataforma"
        }
    },
    "pricing": {
        "en": {
            "title": "ShortlistAI",
            "tagline": "100% Free Forever",
            "features": "No Credit Card • No Signup • Free"
        },
        "pt": {
            "title": "ShortlistAI",
            "tagline": "100% Grátis Para Sempre",
            "features": "Sem Cartão • Sem Cadastro • Grátis"
        },
        "fr": {
            "title": "ShortlistAI",
            "tagline": "100% Gratuit Pour Toujours",
            "features": "Sans Carte • Sans Inscription • Gratuit"
        },
        "es": {
            "title": "ShortlistAI",
            "tagline": "100% Gratis Para Siempre",
            "features": "Sin Tarjeta • Sin Registro • Gratis"
        }
    },
    "features": {
        "en": {
            "title": "ShortlistAI",
            "tagline": "Powerful Features",
            "features": "AI Analysis • Batch Upload • PDF Reports"
        },
        "pt": {
            "title": "ShortlistAI",
            "tagline": "Recursos Poderosos",
            "features": "Análise IA • Upload em Lote • Relatórios PDF"
        },
        "fr": {
            "title": "ShortlistAI",
            "tagline": "Fonctionnalités Puissantes",
            "features": "Analyse IA • Téléchargement Groupé • Rapports PDF"
        },
        "es": {
            "title": "ShortlistAI",
            "tagline": "Funciones Poderosas",
            "features": "Análisis IA • Carga por Lotes • Informes PDF"
        }
    }
}


def load_base_og_image(base_path: str) -> Image.Image:
    """Load the base OG image (without text)."""
    if os.path.exists(base_path):
        return Image.open(base_path).convert("RGBA")
    else:
        logger.warning(f"Base image not found: {base_path}. Creating fallback...")
        img = Image.new("RGB", (1200, 630), color=AI_BLUE)
        return img.convert("RGBA")


def find_font(font_size: int, bold: bool = False):
    """Try to find a suitable font, with fallbacks."""
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    
    if bold:
        for path in font_paths[1::2]:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, font_size)
                except:
                    continue
    
    for path in font_paths[0::2]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except:
                continue
    
    logger.warning("No suitable font found, using default")
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except:
        return ImageFont.load_default()


def add_text_to_image(
    img: Image.Image,
    title: str,
    tagline: str,
    features: str
) -> Image.Image:
    """Add page-specific text to the OG image."""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Title position (top center)
    title_y = 100
    title_font_size = 72
    title_font = find_font(title_font_size, bold=True)
    
    # Tagline position (below title)
    tagline_y = title_y + 90
    tagline_font_size = 36
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
    
    # Add text shadow
    shadow_offset = 3
    shadow_color = (0, 0, 0, 128)
    
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


def generate_page_og_image(page: str, lang: str, base_image_path: str, output_path: str) -> bool:
    """Generate OG image for a specific page and language."""
    try:
        logger.info(f"📄 Generating OG image: {page}-{lang}")
        
        # Load base image
        img = load_base_og_image(base_image_path)
        
        # Get translations
        if page not in PAGE_TRANSLATIONS:
            logger.warning(f"⚠️  No translations for page: {page}")
            return False
        
        translations = PAGE_TRANSLATIONS[page].get(lang, PAGE_TRANSLATIONS[page]["en"])
        title = translations["title"]
        tagline = translations["tagline"]
        features = translations["features"]
        
        # Add text to image
        img_with_text = add_text_to_image(img, title, tagline, features)
        
        # Convert back to RGB
        img_rgb = Image.new("RGB", img_with_text.size, (255, 255, 255))
        img_rgb.paste(img_with_text, mask=img_with_text.split()[3])
        
        # Save image
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        img_rgb.save(output_path, "PNG", optimize=True)
        
        logger.info(f"✅ Saved: {output_path}\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating OG image for {page}-{lang}: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_all_page_images():
    """Generate OG images for all pages and languages."""
    
    assets_dir = Path("public/assets/social")
    base_image_path = assets_dir / "og-default.png"
    
    logger.info("="*70)
    logger.info("📄 ShortlistAI - Page-Specific OG Image Generator")
    logger.info("="*70)
    logger.info(f"📂 Base image: {base_image_path}")
    logger.info(f"📂 Output directory: {assets_dir}\n")
    
    if not base_image_path.exists():
        logger.warning(f"⚠️  Base image not found: {base_image_path}")
        logger.info("💡 Using fallback gradient image\n")
    
    # Generate images for each page and language
    pages = ["about", "pricing", "features"]
    languages = ["en", "pt", "fr", "es"]
    results = {}
    
    for page in pages:
        for lang in languages:
            output_path = assets_dir / f"og-{page}-{lang}.png"
            success = generate_page_og_image(page, lang, str(base_image_path), str(output_path))
            results[f"{page}-{lang}"] = success
    
    # Summary
    logger.info("="*70)
    logger.info("📊 Summary")
    logger.info("="*70)
    
    for page in pages:
        logger.info(f"\n📄 {page.upper()}:")
        for lang in languages:
            key = f"{page}-{lang}"
            status = "✅" if results.get(key) else "❌"
            logger.info(f"  {status} {lang.upper()}")
    
    total = len(results)
    successful = sum(1 for s in results.values() if s)
    logger.info(f"\n✅ Success: {successful}/{total}")
    
    if successful == total:
        logger.info("\n🎉 All page-specific OG images generated successfully!")
    else:
        logger.warning(f"\n⚠️  {total - successful} image(s) failed to generate")


if __name__ == "__main__":
    generate_all_page_images()

