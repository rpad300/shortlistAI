"""
Script to calculate and update tokens for existing analyses that don't have token data.

This script estimates tokens based on:
- Provider used
- Analysis content (raw_text, categories, etc.)
- Average token usage patterns

Run with: python -m scripts.calculate_retroactive_tokens
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables (same as connection.py)
from dotenv import load_dotenv, find_dotenv
env_file = find_dotenv()
if env_file:
    load_dotenv(dotenv_path=env_file)
else:
    # Try common locations
    project_root = backend_dir.parent.parent
    possible_paths = [
        project_root / '.env',
        Path.cwd() / '.env',
    ]
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            break

from database import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def estimate_tokens_from_content(text: str) -> int:
    """
    Estimate token count from text content.
    Uses average of 4 characters per token (approximate for most models).
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def estimate_tokens_for_analysis(analysis: dict) -> tuple[int, int]:
    """
    Estimate input and output tokens for an analysis based on its content.
    
    Returns:
        (input_tokens, output_tokens)
    """
    provider = analysis.get("provider", "unknown")
    
    # Get analysis content
    raw_text = ""
    if analysis.get("detailed_analysis"):
        import json
        raw_text = json.dumps(analysis.get("detailed_analysis", {}))
    
    # Estimate output tokens from response content
    output_tokens = estimate_tokens_from_content(raw_text)
    
    # Estimate input tokens based on typical prompt sizes
    # Typical analysis prompts are large (job posting + CV + instructions)
    # Average: 2000-5000 tokens for input
    base_input_tokens = 3000  # Base estimate
    
    # Adjust based on provider (some providers have different tokenization)
    if provider == "gemini":
        # Gemini uses character-based estimation
        base_input_tokens = 2500
    elif provider == "openai":
        base_input_tokens = 3000
    elif provider == "claude":
        base_input_tokens = 3500
    elif provider == "kimi":
        base_input_tokens = 3000
    elif provider == "minimax":
        base_input_tokens = 2800
    
    # Add variation based on output size (larger outputs suggest larger inputs)
    if output_tokens > 2000:
        base_input_tokens += 1000
    elif output_tokens > 1000:
        base_input_tokens += 500
    
    input_tokens = base_input_tokens
    
    return (input_tokens, output_tokens)


async def calculate_retroactive_tokens():
    """Calculate and update tokens for all analyses missing token data."""
    client = get_supabase_client()
    
    try:
        # Get all analyses without tokens
        logger.info("Fetching analyses without token data...")
        result = client.table("analyses")\
            .select("*")\
            .is_("input_tokens", "null")\
            .execute()
        
        analyses = result.data or []
        total = len(analyses)
        
        if total == 0:
            logger.info("No analyses found without token data. All up to date!")
            return
        
        logger.info(f"Found {total} analyses without token data. Calculating tokens...")
        
        updated = 0
        errors = 0
        
        for idx, analysis in enumerate(analyses, 1):
            try:
                analysis_id = analysis["id"]
                provider = analysis.get("provider", "unknown")
                
                # Skip error/timeout analyses
                if provider in ["error", "timeout"]:
                    logger.debug(f"Skipping {analysis_id} (provider: {provider})")
                    continue
                
                # Estimate tokens
                input_tokens, output_tokens = estimate_tokens_for_analysis(analysis)
                
                # Update analysis
                update_result = client.table("analyses")\
                    .update({
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens
                    })\
                    .eq("id", analysis_id)\
                    .execute()
                
                if update_result.data:
                    updated += 1
                    if idx % 10 == 0:
                        logger.info(f"Progress: {idx}/{total} ({updated} updated, {errors} errors)")
                else:
                    errors += 1
                    logger.warning(f"Failed to update analysis {analysis_id}")
                    
            except Exception as e:
                errors += 1
                logger.error(f"Error processing analysis {analysis.get('id', 'unknown')}: {e}")
        
        logger.info("=" * 60)
        logger.info(f"✅ COMPLETE!")
        logger.info(f"Total analyses processed: {total}")
        logger.info(f"Successfully updated: {updated}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Skipped (error/timeout): {total - updated - errors}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error calculating retroactive tokens: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(calculate_retroactive_tokens())

