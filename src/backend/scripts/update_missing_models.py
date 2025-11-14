"""
Script to update missing model information in analyses table.

For old records without model information, we can try to infer the model
based on the provider and other available information.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Load environment variables
from dotenv import load_dotenv
project_root = Path(__file__).parent.parent.parent
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)

from database import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def infer_model_from_provider(provider: str) -> str:
    """
    Infer most likely model based on provider.
    This is a fallback for old records where model wasn't tracked.
    """
    # Default models per provider (most commonly used)
    default_models = {
        "gemini": "models/gemini-2.5-flash-lite",
        "openai": "gpt-4o-mini",
        "claude": "claude-3-5-sonnet-20241022",
        "kimi": "kimi-k2-0905",
        "minimax": "abab6.5-chat"
    }
    return default_models.get(provider.lower(), None)


async def update_missing_models():
    """Update analyses that are missing model information."""
    client = get_supabase_client()
    
    try:
        # Get all analyses without model
        result = client.table("analyses")\
            .select("id, provider, model")\
            .is_("model", "null")\
            .execute()
        
        analyses = result.data or []
        logger.info(f"Found {len(analyses)} analyses without model information")
        
        if not analyses:
            logger.info("All analyses have model information")
            return
        
        updated = 0
        errors = 0
        
        for analysis in analyses:
            try:
                analysis_id = analysis["id"]
                provider = analysis.get("provider", "unknown")
                
                # Skip if provider is unknown or error
                if provider in ["unknown", "error", "timeout"]:
                    continue
                
                # Infer model from provider
                inferred_model = infer_model_from_provider(provider)
                
                if not inferred_model:
                    logger.warning(f"Cannot infer model for provider: {provider}")
                    continue
                
                # Update analysis with inferred model
                update_result = client.table("analyses")\
                    .update({"model": inferred_model})\
                    .eq("id", analysis_id)\
                    .execute()
                
                if update_result.data:
                    updated += 1
                    if updated % 10 == 0:
                        logger.info(f"Updated {updated} analyses...")
                else:
                    errors += 1
                    logger.warning(f"Failed to update analysis {analysis_id}")
                    
            except Exception as e:
                errors += 1
                logger.error(f"Error updating analysis {analysis.get('id')}: {e}")
        
        logger.info(f"Model update complete: {updated} updated, {errors} errors")
        logger.info("Note: Inferred models are best guesses. For accurate model tracking, new analyses will have the correct model.")
        
    except Exception as e:
        logger.error(f"Error updating missing models: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(update_missing_models())

