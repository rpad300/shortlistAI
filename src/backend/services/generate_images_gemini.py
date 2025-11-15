"""
Generate brand images using Google Gemini Imagen API.

This script uses the Gemini API to generate hero images, OG images,
and other visual assets for ShortlistAI.
"""

import os
import sys
from pathlib import Path
import logging
from typing import Optional
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def discover_gemini_models():
    """Discover available Gemini models, especially image generation ones."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment")
            return []
        
        genai.configure(api_key=api_key)
        
        logger.info("🔍 Discovering available Gemini models...")
        
        all_models = []
        image_models = []
        
        for model in genai.list_models():
            model_name = model.name
            supported_methods = getattr(model, 'supported_generation_methods', []) or []
            
            all_models.append({
                'name': model_name,
                'methods': supported_methods
            })
            
            # Look for image generation models
            if 'generateImage' in supported_methods or 'imagen' in model_name.lower():
                image_models.append(model_name)
                logger.info(f"✅ Found image model: {model_name}")
        
        logger.info(f"\n📊 Total models found: {len(all_models)}")
        logger.info(f"🎨 Image generation models: {len(image_models)}")
        
        if not image_models:
            logger.warning("\n⚠️  No dedicated image generation models found")
            logger.info("\n📝 All available models:")
            for model in all_models[:20]:  # Show first 20
                logger.info(f"  - {model['name']}: {', '.join(model['methods'])}")
        
        return image_models
        
    except ImportError:
        logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        return []
    except Exception as e:
        logger.error(f"Error discovering models: {e}")
        return []


def generate_image_with_gemini(prompt: str, output_path: str, model_name: Optional[str] = None):
    """
    Generate image using Gemini API.
    
    Args:
        prompt: Text prompt for image generation
        output_path: Where to save the generated image
        model_name: Specific model to use (auto-detect if None)
    """
    try:
        import google.generativeai as genai
        from PIL import Image
        import io
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        # Try to generate with Gemini's image generation capability
        # Note: As of now, Gemini might not have direct image generation via API
        # This is a placeholder for when it becomes available
        
        logger.info(f"🎨 Generating: {output_path}")
        logger.info(f"📝 Prompt: {prompt[:100]}...")
        
        # Try different approaches
        try:
            # Approach 1: Try imagen-specific model if available
            if model_name:
                model = genai.ImageGenerationModel(model_name)
            else:
                # Try common Imagen model names
                for model_candidate in [
                    "imagen-3.0-generate-001",
                    "imagen-2.0-generate-001",
                    "imagegeneration@006",
                    "imagegeneration@005"
                ]:
                    try:
                        model = genai.ImageGenerationModel(model_candidate)
                        logger.info(f"✅ Using model: {model_candidate}")
                        break
                    except:
                        continue
            
            # Generate image
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
            )
            
            # Save image
            if response.images:
                response.images[0].save(output_path)
                logger.info(f"✅ Saved: {output_path}")
                return True
                
        except AttributeError:
            logger.warning("⚠️  ImageGenerationModel not available in current Gemini API version")
            
        # Approach 2: Try using text model to generate image description
        # and provide instructions for manual creation
        logger.info("💡 Using Gemini to generate enhanced image description...")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        meta_prompt = f"""You are an expert at creating detailed image generation prompts for AI art tools.

Original prompt: {prompt}

Enhance this prompt to be more detailed and effective for image generation tools like DALL-E, Midjourney, or Stable Diffusion.

Include:
- Specific art style and composition details
- Color palette (must use ShortlistAI brand colors: AI Blue #0066FF and Neural Purple #7C3AED)
- Lighting and mood
- Technical details (resolution, perspective)
- What to avoid

Provide only the enhanced prompt, nothing else."""

        response = model.generate_content(meta_prompt)
        enhanced_prompt = response.text
        
        logger.info(f"\n✨ Enhanced prompt for {os.path.basename(output_path)}:")
        logger.info(f"{enhanced_prompt}\n")
        
        # Save enhanced prompt to file
        prompt_file = output_path.replace('.png', '.txt').replace('.webp', '.txt').replace('.svg', '.txt')
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(f"Original prompt:\n{prompt}\n\n")
            f.write(f"Enhanced prompt:\n{enhanced_prompt}\n")
        
        logger.info(f"📝 Saved enhanced prompt to: {prompt_file}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error generating image: {e}")
        return False


def generate_all_brand_images():
    """Generate all brand images using Gemini."""
    
    project_root = Path(__file__).parent.parent.parent.parent
    assets_dir = project_root / "public" / "assets"
    
    logger.info("="*60)
    logger.info("🎨 ShortlistAI Brand Image Generator (Gemini)")
    logger.info("="*60)
    
    # First, discover available models
    image_models = discover_gemini_models()
    
    # Define all images to generate
    images_to_generate = {
        "heroes/hero-home-light.png": """Create a modern, professional hero image for ShortlistAI, an AI-powered 
CV analysis platform. Style: Clean, minimal, tech-forward, geometric, futuristic. 
Colors: Vibrant blue (#0066FF) and purple (#7C3AED) gradient on white background. 
Elements: Abstract neural network pattern, geometric shapes suggesting data flow, 
light airy composition, professional aesthetic, modern gradient accents. 
16:9 landscape format. High quality, 1920x1080px. 
No text, logos, people, or stock photos.""",
        
        "heroes/hero-home-dark.png": """Create a modern, professional hero image for ShortlistAI - DARK MODE version. 
Style: Clean, tech-forward, futuristic, with neon glow effects. 
Colors: Blue (#0066FF) and purple (#7C3AED) gradient on dark background (#0A0A0B). 
Elements: Glowing neural network pattern, geometric shapes with neon glow, 
dark sophisticated composition, floating data particles, depth and layering. 
16:9 landscape format. High quality, 1920x1080px. 
No text or logos.""",
        
        "social/og-default.png": """Create an Open Graph social media image for ShortlistAI. 
Professional, eye-catching design. Blue (#0066FF) to purple (#7C3AED) diagonal gradient background. 
Abstract neural network pattern overlay at 20% opacity. 
Central area reserved for text (leave space for logo and tagline). 
Geometric shapes in corners suggesting AI and data processing. 
Modern, clean composition. High contrast. 1200x630px. 
No actual text content.""",
        
        "illustrations/feature-interviewer.png": """Create a flat design illustration for the Interviewer feature. 
Style: Geometric, minimal, professional. Colors: Blue (#0066FF) accent, purple (#7C3AED). 
Elements: Multiple CV documents stacked or arranged, AI element analyzing them, 
ranking indicators (1, 2, 3 or stars), checkmarks for selection. 
Clean geometric shapes only, no realistic elements. 400x400px square. 
No faces or actual text.""",
        
        "illustrations/feature-candidate.png": """Create a flat design illustration for the Candidate feature. 
Style: Geometric, minimal, encouraging. Colors: Purple (#7C3AED) accent, blue (#0066FF). 
Elements: Single CV document, job posting document, AI element connecting them, 
lightbulb for insights, upward arrow for progress, positive symbols. 
Clean geometric shapes only. 400x400px square. 
No faces or actual text.""",
        
        "logos/app-icon-512.png": """Create an app icon for ShortlistAI. 
Modern, clean, instantly recognizable square icon. 
Blue to purple gradient background (#0066FF to #7C3AED). 
White neural network symbol or AI brain icon centered. 
Simple design that works at all sizes from 16px to 512px. 
High contrast, professional appearance. 512x512px. 
No text.""",
    }
    
    logger.info(f"\n📦 Generating {len(images_to_generate)} brand images...\n")
    
    generated = 0
    enhanced_prompts_created = 0
    
    for filename, prompt in images_to_generate.items():
        output_path = assets_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        success = generate_image_with_gemini(prompt, str(output_path))
        
        if success:
            generated += 1
        else:
            enhanced_prompts_created += 1
        
        # Rate limiting
        time.sleep(2)
    
    logger.info("\n" + "="*60)
    logger.info("📊 GENERATION SUMMARY")
    logger.info("="*60)
    logger.info(f"✅ Images directly generated: {generated}")
    logger.info(f"📝 Enhanced prompts created: {enhanced_prompts_created}")
    logger.info(f"📁 Output directory: {assets_dir}")
    
    if enhanced_prompts_created > 0:
        logger.info("\n💡 Next Steps:")
        logger.info("="*60)
        logger.info("Since Gemini Imagen API is not yet available for direct image generation,")
        logger.info("enhanced prompts have been created and saved as .txt files.")
        logger.info("\nYou can use these enhanced prompts with:")
        logger.info("  1. 🌐 Google ImageFX (https://aitestkitchen.withgoogle.com/tools/image-fx)")
        logger.info("  2. 🤖 ChatGPT DALL-E 3 (https://chat.openai.com)")
        logger.info("  3. 🎨 Midjourney (https://midjourney.com)")
        logger.info("  4. 🖼️  Stable Diffusion")
        logger.info("\nCopy the enhanced prompts from the .txt files and paste into your")
        logger.info("preferred image generation tool, then save the results to the")
        logger.info("corresponding locations in public/assets/")
    
    logger.info("="*60)


if __name__ == "__main__":
    generate_all_brand_images()





