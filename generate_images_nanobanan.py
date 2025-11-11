"""
Generate brand images using Gemini Nano Banana (gemini-2.5-flash-image).
Based on: https://ai.google.dev/gemini-api/docs/image-generation

Run from project root: python generate_images_nanobanan.py
"""

import os
from pathlib import Path
import logging
from dotenv import load_dotenv
import time
import base64

# Load .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_image_with_nanobanan(prompt: str, output_path: str, aspect_ratio="1:1"):
    """
    Generate image using Gemini Nano Banana (gemini-2.5-flash-image).
    
    Reference: https://ai.google.dev/gemini-api/docs/image-generation
    """
    try:
        from google import genai
        from PIL import Image
        import io
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        logger.info(f"🎨 Generating: {os.path.basename(output_path)}")
        logger.info(f"📐 Aspect ratio: {aspect_ratio}")
        logger.info(f"📝 Prompt: {prompt[:100]}...")
        logger.info(f"🔧 Using model: gemini-2.5-flash-image")
        
        # Generate content with image
        # Note: aspect_ratio config might not be supported yet in Python SDK
        # Trying simple call first
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt]
        )
        
        # Extract and save image
        image_saved = False
        for part in response.parts:
            if part.text is not None:
                logger.info(f"📄 Text response: {part.text[:100]}...")
            elif part.inline_data is not None:
                # Save the image
                image = part.as_image()
                image.save(output_path)
                logger.info(f"✅ SUCCESS! Image saved to: {output_path}\n")
                image_saved = True
        
        return image_saved
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("💡 Install: pip install google-genai pillow")
        return False
    except Exception as e:
        logger.error(f"❌ Error generating image: {e}")
        logger.error(f"   Full error: {str(e)}")
        return False


def load_prompt_from_file(prompt_file_path):
    """Load enhanced prompt from _PROMPT.txt file."""
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "=== ENHANCED PROMPT ===" in content:
                prompt = content.split("=== ENHANCED PROMPT ===")[1].split("===")[0].strip()
                return prompt
            else:
                # Fallback to full content
                return content
    except Exception as e:
        logger.error(f"❌ Error reading prompt file: {e}")
        return None


def generate_all_brand_images():
    """Generate all brand images using Nano Banana."""
    
    assets_dir = Path("public/assets")
    
    logger.info("="*70)
    logger.info("🍌 ShortlistAI - Nano Banana Image Generator")
    logger.info("="*70)
    logger.info("Model: gemini-2.5-flash-image")
    logger.info("API: https://ai.google.dev/gemini-api/docs/image-generation")
    logger.info("="*70)
    logger.info("")
    
    # Define all images to generate with their aspect ratios
    images_config = [
        {
            'name': 'Hero Home Light',
            'file': 'heroes/hero-home-light.png',
            'prompt_file': 'heroes/hero-home-light_PROMPT.txt',
            'aspect_ratio': '16:9',  # 1344x768
            'priority': '🔴 HIGH'
        },
        {
            'name': 'Hero Home Dark',
            'file': 'heroes/hero-home-dark.png',
            'prompt_file': 'heroes/hero-home-dark_PROMPT.txt',
            'aspect_ratio': '16:9',  # 1344x768
            'priority': '🔴 HIGH'
        },
        {
            'name': 'OG Social Image',
            'file': 'social/og-default.png',
            'prompt_file': 'social/og-default_PROMPT.txt',
            'aspect_ratio': '16:9',  # 1344x768 (closest to 1200x630)
            'priority': '🟡 MEDIUM'
        },
        {
            'name': 'Feature Interviewer',
            'file': 'illustrations/feature-interviewer.png',
            'prompt_file': 'illustrations/feature-interviewer_PROMPT.txt',
            'aspect_ratio': '1:1',  # 1024x1024
            'priority': '🟡 MEDIUM'
        },
        {
            'name': 'Feature Candidate',
            'file': 'illustrations/feature-candidate.png',
            'prompt_file': 'illustrations/feature-candidate_PROMPT.txt',
            'aspect_ratio': '1:1',  # 1024x1024
            'priority': '🟡 MEDIUM'
        },
        {
            'name': 'App Icon',
            'file': 'logos/app-icon-512.png',
            'prompt_file': 'logos/app-icon-512_PROMPT.txt',
            'aspect_ratio': '1:1',  # 1024x1024
            'priority': '🟢 LOW'
        },
    ]
    
    logger.info(f"📦 Images to generate: {len(images_config)}\n")
    logger.info("="*70)
    
    successful = 0
    failed = 0
    
    for i, config in enumerate(images_config, 1):
        logger.info(f"\n[{i}/{len(images_config)}] {config['name']} {config['priority']}")
        logger.info("-"*70)
        
        # Load prompt from file
        prompt_file = assets_dir / config['prompt_file']
        if not prompt_file.exists():
            logger.error(f"❌ Prompt file not found: {prompt_file}")
            failed += 1
            continue
        
        prompt = load_prompt_from_file(prompt_file)
        if not prompt:
            logger.error(f"❌ Could not load prompt from: {prompt_file}")
            failed += 1
            continue
        
        # Generate image
        output_path = assets_dir / config['file']
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        success = generate_image_with_nanobanan(
            prompt=prompt,
            output_path=str(output_path),
            aspect_ratio=config['aspect_ratio']
        )
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Rate limiting (avoid hitting API limits)
        if i < len(images_config):  # Don't wait after last image
            logger.info("⏳ Waiting 5 seconds (rate limiting)...")
            time.sleep(5)
    
    # Final Summary
    logger.info("\n" + "="*70)
    logger.info("📊 GENERATION SUMMARY")
    logger.info("="*70)
    logger.info(f"✅ Successfully generated: {successful}/{len(images_config)}")
    logger.info(f"❌ Failed: {failed}/{len(images_config)}")
    logger.info(f"📁 Output directory: {assets_dir.absolute()}")
    
    if successful > 0:
        logger.info("\n🎉 BRAND IMAGES GENERATED!")
        logger.info("-"*70)
        logger.info("Check public/assets/ folders:")
        for config in images_config:
            output_file = assets_dir / config['file']
            if output_file.exists():
                logger.info(f"  ✅ {config['file']}")
            else:
                logger.info(f"  ❌ {config['file']}")
    
    if failed > 0:
        logger.info("\n⚠️  Some images failed to generate")
        logger.info("Possible reasons:")
        logger.info("  - API key issues")
        logger.info("  - Rate limiting (try again in a few minutes)")
        logger.info("  - Network issues")
        logger.info("  - Prompt safety filters")
    
    logger.info("\n💡 Next Steps:")
    logger.info("-"*70)
    logger.info("1. Check generated images in public/assets/")
    logger.info("2. Update frontend to use new images")
    logger.info("3. Update PWA manifest with app icon")
    logger.info("4. Add OG meta tags for social sharing")
    
    logger.info("="*70)
    
    return successful, failed


if __name__ == "__main__":
    try:
        successful, failed = generate_all_brand_images()
        
        # Exit code
        if failed > 0:
            exit(1)
        else:
            exit(0)
            
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Generation interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Unexpected error: {e}")
        exit(1)

