"""
Script to update existing prompts in the database with explicit language instructions.

This script updates all active default prompts to include the new
"IMPORTANT: You must respond in {language}" instructions at the beginning.

Usage:
    python -m scripts.update_prompts_language
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database.prompt_service import get_prompt_service
from services.ai.prompts import (
    CV_EXTRACTION_PROMPT,
    JOB_POSTING_NORMALIZATION_PROMPT,
    WEIGHTING_RECOMMENDATION_PROMPT,
    CV_SUMMARY_PROMPT,
    INTERVIEWER_ANALYSIS_PROMPT,
    CANDIDATE_ANALYSIS_PROMPT,
    EXECUTIVE_RECOMMENDATION_PROMPT
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Map of prompt keys to their updated prompt constants
PROMPT_UPDATES = {
    "cv_extraction": CV_EXTRACTION_PROMPT,
    "job_posting_normalization": JOB_POSTING_NORMALIZATION_PROMPT,
    "weighting_recommendation": WEIGHTING_RECOMMENDATION_PROMPT,
    "cv_summary": CV_SUMMARY_PROMPT,
    "interviewer_analysis": INTERVIEWER_ANALYSIS_PROMPT,
    "candidate_analysis": CANDIDATE_ANALYSIS_PROMPT,
    "executive_recommendation": EXECUTIVE_RECOMMENDATION_PROMPT,
}


async def update_prompts():
    """
    Update all active default prompts with explicit language instructions.
    """
    service = get_prompt_service()
    
    logger.info("Starting prompt updates...")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for prompt_key, new_content in PROMPT_UPDATES.items():
        try:
            # Get existing prompt (default version in English)
            existing = await service.get_prompt_by_key(prompt_key, "en")
            
            if not existing:
                logger.warning(f"Prompt '{prompt_key}' (en) not found, skipping")
                skipped_count += 1
                continue
            
            # Check if content already has the language instruction
            if "IMPORTANT: You must respond in {language}" in existing.get("content", ""):
                logger.info(f"Prompt '{prompt_key}' already has language instruction, skipping")
                skipped_count += 1
                continue
            
            # Update the prompt with new content
            result = await service.update_prompt(
                prompt_id=existing["id"],
                content=new_content,
                updated_by="system_update",
                change_description="Added explicit language instruction at the beginning of prompt",
                create_new_version=True
            )
            
            if result:
                logger.info(f"✓ Updated prompt '{prompt_key}' (version {result.get('version')})")
                updated_count += 1
            else:
                logger.error(f"✗ Failed to update prompt '{prompt_key}'")
                error_count += 1
                
        except Exception as e:
            logger.error(f"✗ Error updating prompt '{prompt_key}': {e}")
            error_count += 1
    
    logger.info("\n" + "="*60)
    logger.info("Prompt Update Complete!")
    logger.info(f"  Updated: {updated_count}")
    logger.info(f"  Skipped (already updated or not found): {skipped_count}")
    logger.info(f"  Errors: {error_count}")
    logger.info("="*60)
    
    if error_count > 0:
        logger.warning("\n⚠️ Some prompts failed to update. Please check the logs above.")
    elif updated_count > 0:
        logger.info("\n✓ All prompts updated successfully!")
    else:
        logger.info("\n→ No prompts needed updating. Database is up to date.")


if __name__ == "__main__":
    try:
        logger.info("="*60)
        logger.info("AI Prompts Language Instruction Update Script")
        logger.info("="*60 + "\n")
        
        asyncio.run(update_prompts())
        
    except KeyboardInterrupt:
        logger.info("\n\nUpdate interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

