"""
Generate brand images directly using Google Imagen models.
Run from project root: python generate_images_with_imagen.py
"""

import os
from pathlib import Path
import logging
from dotenv import load_dotenv
import time

# Load .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_image_with_imagen(prompt: str, output_path: str, aspect_ratio="1:1"):
    """Generate image using Imagen models."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        # Try different Imagen models in order of preference
        imagen_models = [
            "models/imagen-4.0-ultra-generate-001",  # Best quality
            "models/imagen-4.0-generate-001",
            "models/imagen-4.0-fast-generate-001",   # Fastest
            "models/imagen-3.0-generate-002",
            "models/gemini-2.5-flash-image",
        ]
        
        logger.info(f"🎨 Generating: {os.path.basename(output_path)}")
        logger.info(f"📐 Aspect ratio: {aspect_ratio}")
        logger.info(f"📝 Prompt: {prompt[:80]}...")
        
        for model_name in imagen_models:
            try:
                logger.info(f"🔄 Trying model: {model_name}")
                
                # Try to use the model
                model = genai.ImageGenerationModel(model_name)
                
                # Generate image
                result = model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                    safety_filter_level="block_few",  # Less restrictive
                )
                
                # Save the image
                if result and hasattr(result, 'images') and result.images:
                    # Save image
                    result.images[0].save(output_path)
                    logger.info(f"✅ SUCCESS! Saved to: {output_path}")
                    logger.info(f"   Model used: {model_name}\n")
                    return True
                else:
                    logger.warning(f"⚠️  No image returned from {model_name}")
                    
            except AttributeError as e:
                logger.warning(f"⚠️  {model_name} - API method not available: {e}")
                continue
            except Exception as e:
                logger.warning(f"⚠️  {model_name} failed: {str(e)[:100]}")
                continue
        
        logger.error(f"❌ All Imagen models failed for: {output_path}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def generate_all_images():
    """Generate all brand images."""
    
    assets_dir = Path("public/assets")
    
    logger.info("="*70)
    logger.info("🎨 ShortlistAI Image Generator (Using Imagen)")
    logger.info("="*70)
    logger.info("")
    
    # Read enhanced prompts from files
    images_to_generate = []
    
    # Hero images
    hero_light_prompt_file = assets_dir / "heroes" / "hero-home-light_PROMPT.txt"
    if hero_light_prompt_file.exists():
        with open(hero_light_prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract enhanced prompt
            if "=== ENHANCED PROMPT ===" in content:
                prompt = content.split("=== ENHANCED PROMPT ===")[1].split("===")[0].strip()
                images_to_generate.append({
                    'file': 'heroes/hero-home-light.png',
                    'prompt': prompt,
                    'aspect_ratio': '16:9'
                })
    
    hero_dark_prompt_file = assets_dir / "heroes" / "hero-home-dark_PROMPT.txt"
    if hero_dark_prompt_file.exists():
        with open(hero_dark_prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "=== ENHANCED PROMPT ===" in content:
                prompt = content.split("=== ENHANCED PROMPT ===")[1].split("===")[0].strip()
                images_to_generate.append({
                    'file': 'heroes/hero-home-dark.png',
                    'prompt': prompt,
                    'aspect_ratio': '16:9'
                })
    
    # OG image
    og_prompt_file = assets_dir / "social" / "og-default_PROMPT.txt"
    if og_prompt_file.exists():
        with open(og_prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "=== ENHANCED PROMPT ===" in content:
                prompt = content.split("=== ENHANCED PROMPT ===")[1].split("===")[0].strip()
                images_to_generate.append({
                    'file': 'social/og-default.png',
                    'prompt': prompt,
                    'aspect_ratio': '16:9'  # Closest to 1200:630
                })
    
    # Feature illustrations
    for feature in ['interviewer', 'candidate']:
        prompt_file = assets_dir / "illustrations" / f"feature-{feature}_PROMPT.txt"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "=== ENHANCED PROMPT ===" in content:
                    prompt = content.split("=== ENHANCED PROMPT ===")[1].split("===")[0].strip()
                    images_to_generate.append({
                        'file': f'illustrations/feature-{feature}.png',
                        'prompt': prompt,
                        'aspect_ratio': '1:1'
                    })
    
    # App icon
    icon_prompt_file = assets_dir / "logos" / "app-icon-512_PROMPT.txt"
    if icon_prompt_file.exists():
        with open(icon_prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "=== ENHANCED PROMPT ===" in content:
                prompt = content.split("=== ENHANCED PROMPT ===")[1].split("===")[0].strip()
                images_to_generate.append({
                    'file': 'logos/app-icon-512.png',
                    'prompt': prompt,
                    'aspect_ratio': '1:1'
                })
    
    logger.info(f"📦 Found {len(images_to_generate)} prompts to generate\n")
    logger.info("="*70)
    
    # Generate each image
    successful = 0
    failed = 0
    
    for i, image_data in enumerate(images_to_generate, 1):
        logger.info(f"\n[{i}/{len(images_to_generate)}] Processing: {image_data['file']}")
        logger.info("-"*70)
        
        output_path = assets_dir / image_data['file']
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        success = generate_image_with_imagen(
            prompt=image_data['prompt'],
            output_path=str(output_path),
            aspect_ratio=image_data['aspect_ratio']
        )
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Rate limiting
        time.sleep(3)
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 GENERATION SUMMARY")
    logger.info("="*70)
    logger.info(f"✅ Successfully generated: {successful}/{len(images_to_generate)}")
    logger.info(f"❌ Failed: {failed}/{len(images_to_generate)}")
    logger.info(f"📁 Output directory: {assets_dir.absolute()}")
    
    if successful > 0:
        logger.info("\n🎉 Images generated successfully!")
        logger.info("Check the public/assets/ folders for your brand images.")
    
    if failed > 0:
        logger.info("\n⚠️  Some images failed to generate.")
        logger.info("You can try generating them manually with the prompts in *_PROMPT.txt files.")
    
    logger.info("="*70)


if __name__ == "__main__":
    generate_all_images()

