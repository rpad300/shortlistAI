"""
Seed script to populate the database with default AI prompts.

This script should be run after the database migration to initialize
all prompts that can later be managed through the Admin UI.

Usage:
    python -m src.backend.scripts.seed_prompts
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
    TRANSLATION_PROMPT,
    EXECUTIVE_RECOMMENDATION_PROMPT
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default prompts to seed
DEFAULT_PROMPTS = [
    {
        "prompt_key": "cv_extraction",
        "name": "CV Extraction",
        "description": "Extracts structured information from CV text including personal info, work experience, education, skills, and certifications.",
        "content": CV_EXTRACTION_PROMPT,
        "category": "cv_extraction",
        "variables": ["cv_text"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "This prompt requires valid JSON output. Keep temperature low for consistency."
    },
    {
        "prompt_key": "job_posting_normalization",
        "name": "Job Posting Normalization",
        "description": "Normalizes and structures job posting data including requirements, skills, responsibilities, and company information.",
        "content": JOB_POSTING_NORMALIZATION_PROMPT,
        "category": "job_analysis",
        "variables": ["job_posting_text"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Used to standardize job posting data for analysis. Requires JSON output."
    },
    {
        "prompt_key": "weighting_recommendation",
        "name": "Weighting Recommendation",
        "description": "Recommends category weights and hard blockers based on job requirements and interviewer input.",
        "content": WEIGHTING_RECOMMENDATION_PROMPT,
        "category": "job_analysis",
        "variables": ["job_posting", "structured_job_posting", "key_points", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.5,
            "max_tokens": 1500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Weights must sum to 100. Uses interviewer's key points as primary input."
    },
    {
        "prompt_key": "cv_summary",
        "name": "CV Summary",
        "description": "Creates a concise summary of a CV including key identifiers, skills, and achievements.",
        "content": CV_SUMMARY_PROMPT,
        "category": "cv_extraction",
        "variables": ["file_name", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.4,
            "max_tokens": 1000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Used for quick candidate overviews. Should be concise and factual."
    },
    {
        "prompt_key": "interviewer_analysis",
        "name": "Interviewer Analysis",
        "description": "Analyzes candidates for interviewers, including scores, strengths, risks, and custom questions.",
        "content": INTERVIEWER_ANALYSIS_PROMPT,
        "category": "candidate_evaluation",
        "variables": [
            "job_posting",
            "key_points",
            "cv_text",
            "weights",
            "hard_blockers",
            "nice_to_have",
            "enrichment_context",
            "language"
        ],
        "language": "en",
        "model_preferences": {
            "temperature": 0.6,
            "max_tokens": 3000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Main evaluation prompt for interviewer flow. Questions should be sequenced and actionable."
    },
    {
        "prompt_key": "candidate_analysis",
        "name": "Candidate Analysis",
        "description": "Analyzes candidates for self-assessment, including strengths, preparation tips, and intro pitch.",
        "content": CANDIDATE_ANALYSIS_PROMPT,
        "category": "candidate_evaluation",
        "variables": ["job_posting", "cv_text", "enrichment_context", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.6,
            "max_tokens": 3000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Used for candidate self-preparation. Should be encouraging and constructive."
    },
    {
        "prompt_key": "translation",
        "name": "Translation",
        "description": "Translates text from English to target language maintaining tone and professionalism.",
        "content": TRANSLATION_PROMPT,
        "category": "translation",
        "variables": ["target_language", "text"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Used for multi-language support. Keep temperature low for accuracy."
    },
    {
        "prompt_key": "executive_recommendation",
        "name": "Executive Recommendation",
        "description": "Creates executive summary and hiring recommendation for top candidates.",
        "content": EXECUTIVE_RECOMMENDATION_PROMPT,
        "category": "reporting",
        "variables": [
            "job_posting_summary",
            "candidate_count",
            "candidates_summary",
            "weights",
            "hard_blockers",
            "language"
        ],
        "language": "en",
        "model_preferences": {
            "temperature": 0.7,
            "max_tokens": 2500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "High-level summary for decision makers. Should be clear and actionable."
    },
    {
        "prompt_key": "brave_company_search",
        "name": "Brave Search - Company Query",
        "description": "Search query template for enriching company information via Brave Search API. Uses search operators to find: official website, company information, industry details, size, location, and business data. Optimized for comprehensive company data retrieval.",
        "content": "{company_name}{additional_context} (company OR corporation OR business) (website OR official OR about) (industry OR sector OR location OR headquarters OR employees OR size)",
        "category": "enrichment",
        "variables": ["company_name", "additional_context"],
        "language": "en",
        "model_preferences": {},
        "admin_notes": "Template for company search queries. Uses parentheses for grouping and OR operators to find multiple types of company information. Variables: company_name (required), additional_context (optional). Query structure optimized for Brave Search API operators (https://api-dashboard.search.brave.com/app/documentation/web-search/query)."
    },
    {
        "prompt_key": "brave_company_news",
        "name": "Brave Search - Company News Query",
        "description": "Search query template for finding recent company news via Brave Search API. Uses search operators to find: latest news, press releases, announcements, and industry updates from recent time periods. Optimized for freshness parameter.",
        "content": "{company_name} (news OR announcement OR press release OR update OR \"recent news\" OR \"latest news\") (2024 OR 2025 OR recent)",
        "category": "enrichment",
        "variables": ["company_name"],
        "language": "en",
        "model_preferences": {},
        "admin_notes": "Template for company news search. Uses OR operators and year filters to find recent news. Should be used with freshness=pw parameter for past week results. Query optimized for news-specific content discovery. Reference: https://api-dashboard.search.brave.com/app/documentation/web-search/query"
    },
    {
        "prompt_key": "brave_candidate_search",
        "name": "Brave Search - Candidate Query",
        "description": "Search query template for enriching candidate information via Brave Search API. Uses site: operators to target specific platforms (LinkedIn, GitHub, Medium) and keywords to find professional profiles, portfolios, and background information.",
        "content": "{candidate_name}{additional_keywords} (site:linkedin.com/in OR site:github.com OR site:medium.com OR \"portfolio\" OR \"professional profile\" OR \"about me\") (software OR developer OR engineer OR professional OR experience OR skills)",
        "category": "enrichment",
        "variables": ["candidate_name", "additional_keywords"],
        "language": "en",
        "model_preferences": {},
        "admin_notes": "Template for candidate search queries. Uses site: operators to target specific professional platforms. Variables: candidate_name (required), additional_keywords (optional). Query structure optimized to find professional online presence across multiple platforms. Reference: https://api-dashboard.search.brave.com/app/documentation/web-search/query"
    },
    {
        "prompt_key": "brave_candidate_publications",
        "name": "Brave Search - Candidate Publications Query",
        "description": "Search query template for finding candidate publications and research via Brave Search API. Uses site: operators to target academic platforms (Google Scholar, ResearchGate, arXiv, Academia.edu) and keywords to find research papers, articles, and academic work.",
        "content": "{candidate_name} (site:scholar.google.com OR site:researchgate.net OR site:arxiv.org OR site:academia.edu OR \"research paper\" OR \"academic paper\" OR \"publication\" OR \"journal article\") (research OR study OR paper OR article OR publication)",
        "category": "enrichment",
        "variables": ["candidate_name"],
        "language": "en",
        "model_preferences": {},
        "admin_notes": "Template for finding academic publications. Uses site: operators to target academic platforms specifically. Query structure optimized to find research papers, articles, and academic publications across multiple scholarly platforms. Reference: https://api-dashboard.search.brave.com/app/documentation/web-search/query"
    }
]


async def seed_prompts():
    """
    Seed the database with default prompts.
    
    This will create all default prompts if they don't exist.
    Existing prompts will not be modified.
    """
    service = get_prompt_service()
    
    logger.info("Starting prompt seeding...")
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for prompt_config in DEFAULT_PROMPTS:
        try:
            prompt_key = prompt_config["prompt_key"]
            language = prompt_config["language"]
            
            # Check if prompt already exists
            existing = await service.get_prompt_by_key(prompt_key, language)
            
            if existing:
                logger.info(f"Prompt '{prompt_key}' ({language}) already exists, skipping")
                skipped_count += 1
                continue
            
            # Create the prompt
            result = await service.create_prompt(
                prompt_key=prompt_config["prompt_key"],
                name=prompt_config["name"],
                content=prompt_config["content"],
                category=prompt_config["category"],
                description=prompt_config.get("description"),
                variables=prompt_config.get("variables", []),
                language=prompt_config["language"],
                model_preferences=prompt_config.get("model_preferences", {}),
                is_active=True,
                is_default=True,
                created_by="system_seed",
                admin_notes=prompt_config.get("admin_notes")
            )
            
            if result:
                logger.info(f"✓ Created prompt '{prompt_key}' ({language})")
                created_count += 1
            else:
                logger.error(f"✗ Failed to create prompt '{prompt_key}' ({language})")
                error_count += 1
                
        except Exception as e:
            logger.error(f"✗ Error creating prompt '{prompt_config['prompt_key']}': {e}")
            error_count += 1
    
    logger.info("\n" + "="*60)
    logger.info("Prompt Seeding Complete!")
    logger.info(f"  Created: {created_count}")
    logger.info(f"  Skipped (already exists): {skipped_count}")
    logger.info(f"  Errors: {error_count}")
    logger.info("="*60)
    
    if error_count > 0:
        logger.warning("\n⚠️ Some prompts failed to create. Please check the logs above.")
    elif created_count > 0:
        logger.info("\n✓ All new prompts created successfully!")
    else:
        logger.info("\n→ No new prompts to create. Database is up to date.")


if __name__ == "__main__":
    try:
        logger.info("="*60)
        logger.info("AI Prompts Seeding Script")
        logger.info("="*60 + "\n")
        
        asyncio.run(seed_prompts())
        
    except KeyboardInterrupt:
        logger.info("\n\nSeeding interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

