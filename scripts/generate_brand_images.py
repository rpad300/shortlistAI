"""
Standalone script to generate brand images using Google Gemini API.
Run from project root: python scripts/generate_brand_images.py
"""

import os
from pathlib import Path
import logging
import time
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def discover_gemini_models():
    """Discover available Gemini models."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found in environment")
            logger.info("💡 Set it in your .env file or export GEMINI_API_KEY=your_key")
            return []
        
        genai.configure(api_key=api_key)
        
        logger.info("🔍 Discovering available Gemini models...\n")
        
        all_models = []
        text_models = []
        image_models = []
        
        for model in genai.list_models():
            model_name = model.name
            supported_methods = getattr(model, 'supported_generation_methods', []) or []
            
            all_models.append({
                'name': model_name,
                'methods': supported_methods
            })
            
            # Categorize models
            if 'generateContent' in supported_methods:
                text_models.append(model_name)
            
            if any(keyword in model_name.lower() for keyword in ['imagen', 'image', 'vision']):
                image_models.append(model_name)
                logger.info(f"🎨 Found potential image model: {model_name}")
        
        logger.info(f"\n📊 Discovery Summary:")
        logger.info(f"  Total models: {len(all_models)}")
        logger.info(f"  Text/Content models: {len(text_models)}")
        logger.info(f"  Potential image models: {len(image_models)}")
        
        if text_models:
            logger.info(f"\n✅ Available text models:")
            for model in text_models[:5]:
                logger.info(f"  - {model}")
        
        return text_models, image_models
        
    except ImportError:
        logger.error("❌ google-generativeai not installed")
        logger.info("💡 Install it: pip install google-generativeai")
        return [], []
    except Exception as e:
        logger.error(f"❌ Error discovering models: {e}")
        return [], []


def generate_enhanced_prompts():
    """Generate enhanced prompts using Gemini for manual image creation."""
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        # Use best available model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Using model: gemini-2.0-flash-exp\n")
        except:
            try:
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                logger.info("✅ Using model: gemini-1.5-pro-latest\n")
            except:
                model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Using model: gemini-pro\n")
        
        assets_dir = Path("public/assets")
        
        # Define images to generate
        images = {
            "heroes/hero-home-light.png": """Modern professional hero image for ShortlistAI AI-powered CV analysis platform. 
Clean minimal tech-forward geometric futuristic. Colors: vibrant blue #0066FF and purple #7C3AED gradient white background. 
Abstract neural network pattern, geometric shapes, light composition, professional. 16:9 landscape 1920x1080px. No text logos people.""",
            
            "heroes/hero-home-dark.png": """Modern professional hero dark mode for ShortlistAI. 
Tech-forward futuristic neon glow. Colors: blue #0066FF purple #7C3AED on dark #0A0A0B. 
Glowing neural network geometric shapes neon effects sophisticated dark. 16:9 1920x1080px. No text logos.""",
            
            "social/og-default.png": """Open Graph image ShortlistAI. Professional eye-catching. 
Blue #0066FF to purple #7C3AED diagonal gradient. Neural network pattern 20% opacity. 
Central space for text. Geometric corners AI data. 1200x630px. No actual text.""",
            
            "illustrations/feature-interviewer.png": """Flat design illustration Interviewer feature. 
Geometric minimal professional. Blue #0066FF accent purple #7C3AED. 
Multiple CVs stacked AI analyzing ranking 1,2,3 checkmarks. 400x400px. No faces text.""",
            
            "illustrations/feature-candidate.png": """Flat design illustration Candidate feature. 
Geometric minimal encouraging. Purple #7C3AED blue #0066FF. 
Single CV job posting AI connecting lightbulb upward arrow. 400x400px. No faces text.""",
            
            "logos/app-icon-512.png": """App icon ShortlistAI. Modern clean recognizable. 
Blue to purple gradient #0066FF to #7C3AED. White neural network centered. 
Simple works all sizes 16-512px. 512x512px. No text.""",
        }
        
        logger.info(f"🎨 Generating enhanced prompts for {len(images)} images...\n")
        logger.info("="*70)
        
        enhanced_prompts = {}
        
        for filename, base_prompt in images.items():
            logger.info(f"\n📝 Processing: {filename}")
            
            meta_prompt = f"""You are an expert at creating image generation prompts for AI art tools like DALL-E, Midjourney, and Stable Diffusion.

Original brief: {base_prompt}

Create a detailed, optimized prompt that includes:
- Specific visual style and composition
- Exact colors from ShortlistAI brand (AI Blue #0066FF, Neural Purple #7C3AED)
- Lighting, mood, and atmosphere
- Art style keywords (modern, tech, geometric, minimal, professional)
- Technical specs
- What to avoid

Make it concise but detailed. Output ONLY the enhanced prompt, no explanations."""

            try:
                response = model.generate_content(meta_prompt)
                enhanced = response.text.strip()
                enhanced_prompts[filename] = enhanced
                
                logger.info(f"✅ Generated enhanced prompt")
                logger.info(f"Preview: {enhanced[:100]}...")
                
                # Save to file
                output_path = assets_dir / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                prompt_file = str(output_path).replace('.png', '_PROMPT.txt')
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== SHORTLISTAI IMAGE GENERATION PROMPT ===\n\n")
                    f.write(f"File: {filename}\n")
                    f.write(f"Dimensions: {get_dimensions(filename)}\n\n")
                    f.write(f"=== ENHANCED PROMPT ===\n\n")
                    f.write(enhanced)
                    f.write(f"\n\n=== ORIGINAL BRIEF ===\n\n")
                    f.write(base_prompt)
                    f.write(f"\n\n=== USAGE INSTRUCTIONS ===\n\n")
                    f.write("1. Copy the ENHANCED PROMPT above\n")
                    f.write("2. Paste into your image generation tool:\n")
                    f.write("   - Google ImageFX: https://aitestkitchen.withgoogle.com/tools/image-fx\n")
                    f.write("   - ChatGPT DALL-E 3: https://chat.openai.com\n")
                    f.write("   - Midjourney: https://midjourney.com\n")
                    f.write(f"3. Generate and save as: {filename}\n")
                
                logger.info(f"💾 Saved prompt to: {prompt_file}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error for {filename}: {e}")
        
        return enhanced_prompts
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {}


def get_dimensions(filename):
    """Get recommended dimensions for each image type."""
    if 'hero-home' in filename and 'mobile' not in filename:
        return "1920x1080px (16:9 landscape)"
    elif 'mobile' in filename:
        return "800x1200px (2:3 portrait)"
    elif 'og-' in filename:
        return "1200x630px (OG standard)"
    elif 'feature-' in filename or 'app-icon' in filename:
        return "512x512px or 400x400px (square)"
    return "As specified in prompt"


def main():
    """Main execution."""
    logger.info("="*70)
    logger.info("🎨 ShortlistAI Brand Image Generator")
    logger.info("="*70)
    logger.info("")
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("❌ GEMINI_API_KEY not found in environment")
        logger.info("\n💡 Set it in your .env file or:")
        logger.info("   Windows: $env:GEMINI_API_KEY='your_key_here'")
        logger.info("   Linux/Mac: export GEMINI_API_KEY='your_key_here'")
        return
    
    # Discover models
    text_models, image_models = discover_gemini_models()
    
    logger.info("\n" + "="*70)
    logger.info("🚀 Starting Image Prompt Generation")
    logger.info("="*70)
    
    # Generate enhanced prompts
    enhanced_prompts = generate_enhanced_prompts()
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 SUMMARY")
    logger.info("="*70)
    logger.info(f"✅ Enhanced prompts created: {len(enhanced_prompts)}")
    logger.info(f"📁 Location: public/assets/")
    logger.info(f"📝 Files: *_PROMPT.txt")
    
    logger.info("\n" + "="*70)
    logger.info("📋 NEXT STEPS")
    logger.info("="*70)
    logger.info("1. Check public/assets/ folders for *_PROMPT.txt files")
    logger.info("2. Open each prompt file")
    logger.info("3. Copy the ENHANCED PROMPT")
    logger.info("4. Use with Google ImageFX, DALL-E, or Midjourney")
    logger.info("5. Save generated images to the specified locations")
    logger.info("\n🎯 Recommended tool: Google ImageFX")
    logger.info("   https://aitestkitchen.withgoogle.com/tools/image-fx")
    logger.info("="*70)


if __name__ == "__main__":
    main()

