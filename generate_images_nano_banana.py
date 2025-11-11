"""
Generate brand images using Gemini Nano Banana (gemini-2.5-flash-image).
Based on: https://ai.google.dev/gemini-api/docs/image-generation?hl=pt-br

Run from project root: python generate_images_nano_banana.py
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


def generate_image_nano_banana(prompt: str, output_path: str, aspect_ratio="1:1"):
    """
    Generate image using Gemini Nano Banana (gemini-2.5-flash-image).
    
    Args:
        prompt: Text description of the image
        output_path: Where to save the generated image
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 3:2, 2:3, etc.)
    """
    try:
        from google import genai
        from PIL import Image
        import io
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        client = genai.Client(api_key=api_key)
        
        logger.info(f"🎨 Generating: {os.path.basename(output_path)}")
        logger.info(f"📐 Aspect ratio: {aspect_ratio}")
        logger.info(f"📝 Prompt: {prompt[:100]}...")
        
        # Generate content with image config
        # Note: aspect_ratio configuration might not be supported yet in google-genai SDK
        # Trying simple generation first
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt],
            )
        except Exception as e:
            logger.warning(f"⚠️  Generation failed: {e}")
            raise
        
        # Process response parts
        image_saved = False
        for part in response.parts:
            if part.text is not None and part.text.strip():
                logger.info(f"💬 Model response: {part.text}")
            elif part.inline_data is not None:
                # Save image from inline data
                image_data = part.inline_data.data
                
                # Decode base64 if needed
                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = image_data
                
                # Save using PIL
                image = Image.open(io.BytesIO(image_bytes))
                image.save(output_path)
                
                logger.info(f"✅ SUCCESS! Image saved: {output_path}")
                logger.info(f"   Size: {image.size[0]}x{image.size[1]}px")
                image_saved = True
        
        if not image_saved:
            logger.warning(f"⚠️  No image data received in response")
            return False
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("💡 Install: pip install google-genai pillow")
        return False
    except Exception as e:
        logger.error(f"❌ Error generating image: {e}")
        return False


def generate_all_brand_images():
    """Generate all ShortlistAI brand images using Nano Banana."""
    
    assets_dir = Path("public/assets")
    
    logger.info("="*70)
    logger.info("🍌 ShortlistAI Image Generator - Nano Banana Edition")
    logger.info("="*70)
    logger.info("Model: gemini-2.5-flash-image")
    logger.info("="*70)
    logger.info("")
    
    # Define all images to generate with prompts
    images_to_generate = []
    
    # Load prompts from files
    prompt_files = {
        'heroes/hero-home-light.png': ('heroes/hero-home-light_PROMPT.txt', '16:9'),
        'heroes/hero-home-dark.png': ('heroes/hero-home-dark_PROMPT.txt', '16:9'),
        'social/og-default.png': ('social/og-default_PROMPT.txt', '16:9'),
        'illustrations/feature-interviewer.png': ('illustrations/feature-interviewer_PROMPT.txt', '1:1'),
        'illustrations/feature-candidate.png': ('illustrations/feature-candidate_PROMPT.txt', '1:1'),
        'logos/app-icon-512.png': ('logos/app-icon-512_PROMPT.txt', '1:1'),
    }
    
    for output_file, (prompt_file, aspect_ratio) in prompt_files.items():
        prompt_path = assets_dir / prompt_file
        
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract enhanced prompt
            if "=== ENHANCED PROMPT ===" in content:
                prompt = content.split("=== ENHANCED PROMPT ===")[1].split("===")[0].strip()
            else:
                # Fallback to original brief if enhanced not found
                if "=== ORIGINAL BRIEF ===" in content:
                    prompt = content.split("=== ORIGINAL BRIEF ===")[1].split("===")[0].strip()
                else:
                    logger.warning(f"⚠️  Could not extract prompt from {prompt_file}")
                    continue
            
            images_to_generate.append({
                'file': output_file,
                'prompt': prompt,
                'aspect_ratio': aspect_ratio
            })
        else:
            logger.warning(f"⚠️  Prompt file not found: {prompt_file}")
    
    if not images_to_generate:
        logger.error("❌ No prompt files found. Run 'python generate_brand_images.py' first.")
        return
    
    logger.info(f"📦 Loaded {len(images_to_generate)} prompts")
    logger.info("="*70)
    
    # Generate each image
    successful = 0
    failed = 0
    
    for i, image_data in enumerate(images_to_generate, 1):
        logger.info(f"\n[{i}/{len(images_to_generate)}] {image_data['file']}")
        logger.info("-"*70)
        
        output_path = assets_dir / image_data['file']
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        success = generate_image_nano_banana(
            prompt=image_data['prompt'],
            output_path=str(output_path),
            aspect_ratio=image_data['aspect_ratio']
        )
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Rate limiting - be nice to the API
        if i < len(images_to_generate):
            logger.info("⏳ Waiting 5 seconds before next image...")
            time.sleep(5)
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 GENERATION SUMMARY")
    logger.info("="*70)
    logger.info(f"✅ Successfully generated: {successful}/{len(images_to_generate)}")
    logger.info(f"❌ Failed: {failed}/{len(images_to_generate)}")
    logger.info(f"📁 Output directory: {assets_dir.absolute()}")
    
    if successful > 0:
        logger.info("\n🎉 SUCCESS! Brand images generated!")
        logger.info("\n📂 Check these folders:")
        logger.info("   - public/assets/heroes/")
        logger.info("   - public/assets/social/")
        logger.info("   - public/assets/illustrations/")
        logger.info("   - public/assets/logos/")
        
        logger.info("\n📋 Next Steps:")
        logger.info("   1. Review generated images")
        logger.info("   2. Optimize if needed (compress, resize)")
        logger.info("   3. Update frontend to use new images")
        logger.info("   4. Test on different devices")
    
    if failed > 0:
        logger.info(f"\n⚠️  {failed} image(s) failed to generate")
        logger.info("   - Check your GEMINI_API_KEY")
        logger.info("   - Check API rate limits")
        logger.info("   - Try regenerating failed images individually")
    
    logger.info("="*70)
    
    # Show aspect ratios reference
    logger.info("\n📐 Aspect Ratio Reference:")
    logger.info("   1:1   = 1024x1024 (square)")
    logger.info("   16:9  = 1344x768  (landscape)")
    logger.info("   9:16  = 768x1344  (portrait)")
    logger.info("   3:2   = 1248x832  (landscape)")
    logger.info("   2:3   = 832x1248  (portrait)")
    logger.info("="*70)


if __name__ == "__main__":
    logger.info("🍌 Starting Nano Banana Image Generation...")
    logger.info("📚 Based on: https://ai.google.dev/gemini-api/docs/image-generation\n")
    
    # Check dependencies
    try:
        from google import genai
        from PIL import Image
        logger.info("✅ Dependencies OK (google-genai, Pillow)")
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("\n💡 Install required packages:")
        logger.info("   pip install google-genai pillow python-dotenv")
        exit(1)
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("❌ GEMINI_API_KEY not found")
        logger.info("\n💡 Set it in your .env file or:")
        logger.info("   Windows: $env:GEMINI_API_KEY='your_key_here'")
        logger.info("   Linux/Mac: export GEMINI_API_KEY='your_key_here'")
        exit(1)
    
    logger.info("✅ API Key found\n")
    
    # Generate images
    generate_all_brand_images()

