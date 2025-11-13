"""
Script to update long prompts in the database with explicit language instructions.

This script updates interviewer_analysis, candidate_analysis, and executive_recommendation
prompts to include the new "IMPORTANT: You must respond in {language}" instructions.

Usage:
    python -m scripts.update_long_prompts
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database.prompt_service import get_prompt_service
from services.ai.prompts import (
    INTERVIEWER_ANALYSIS_PROMPT,
    CANDIDATE_ANALYSIS_PROMPT,
    EXECUTIVE_RECOMMENDATION_PROMPT
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_prompts():
    """Update long prompts in the database."""
    prompt_service = get_prompt_service()
    
    prompts_to_update = [
        ("interviewer_analysis", INTERVIEWER_ANALYSIS_PROMPT, "en"),
        ("candidate_analysis", CANDIDATE_ANALYSIS_PROMPT, "en"),
        ("executive_recommendation", EXECUTIVE_RECOMMENDATION_PROMPT, "en"),
    ]
    
    for prompt_key, prompt_content, language in prompts_to_update:
        try:
            logger.info(f"Updating prompt: {prompt_key} (language: {language})")
            
            # Get existing prompt
            existing = await prompt_service.get_prompt_by_key(
                prompt_key=prompt_key,
                language=language
            )
            
            if existing:
                # Update existing prompt
                await prompt_service.update_prompt(
                    prompt_id=existing["id"],
                    content=prompt_content,
                    version=existing.get("version", 1) + 1
                )
                logger.info(f"✓ Updated {prompt_key} (version {existing.get('version', 1) + 1})")
            else:
                logger.warning(f"Prompt {prompt_key} not found in database, skipping")
                
        except Exception as e:
            logger.error(f"Error updating {prompt_key}: {e}", exc_info=True)
    
    logger.info("Done updating prompts!")


if __name__ == "__main__":
    asyncio.run(update_prompts())

