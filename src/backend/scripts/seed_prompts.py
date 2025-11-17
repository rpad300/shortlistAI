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
    EXECUTIVE_RECOMMENDATION_PROMPT,
    # Chatbot prompts
    CHATBOT_PROFILE_EXTRACTION_PROMPT,
    CHATBOT_QUESTION_GENERATION_PROMPT,
    CHATBOT_CV_GENERATION_ATS_PROMPT,
    CHATBOT_CV_GENERATION_HUMAN_PROMPT,
    CHATBOT_DIGITAL_FOOTPRINT_ANALYSIS_PROMPT,
    CHATBOT_INTERVIEW_PREP_PROMPT,
    CHATBOT_EMPLOYABILITY_SCORE_PROMPT,
    CHATBOT_JOB_RISK_ASSESSMENT_PROMPT,
    # Enrichment structuring prompts
    STRUCTURE_COMPANY_ENRICHMENT_PROMPT,
    STRUCTURE_CANDIDATE_ENRICHMENT_PROMPT,
    # Social media risk analysis prompts
    ANALYZE_COMPANY_SOCIAL_MEDIA_RISK_PROMPT,
    ANALYZE_CANDIDATE_SOCIAL_MEDIA_RISK_PROMPT
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
        "description": "Normalizes and structures job posting data including requirements, skills, responsibilities, and company information. Uses company enrichment data to enhance normalization accuracy when company name is available.",
        "content": JOB_POSTING_NORMALIZATION_PROMPT,
        "category": "job_analysis",
        "variables": ["job_posting_text", "enrichment_context"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Used to standardize job posting data for analysis. Uses enrichment_context to improve normalization accuracy. When company enrichment data is available, it helps identify company-specific terminology, industry standards, and company size/type. Variables: job_posting_text (required), enrichment_context (optional)."
    },
    {
        "prompt_key": "weighting_recommendation",
        "name": "Weighting Recommendation",
        "description": "Recommends category weights and hard blockers based on job requirements and interviewer input. Uses company enrichment data to tailor recommendations based on company industry, size, and culture.",
        "content": WEIGHTING_RECOMMENDATION_PROMPT,
        "category": "job_analysis",
        "variables": ["job_posting", "structured_job_posting", "key_points", "enrichment_context", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.5,
            "max_tokens": 1500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Weights must sum to 100. Uses enrichment_context to consider company information when recommending weights. For example, startups may prioritize technical skills more, while enterprises may value experience and soft skills. Variables: job_posting (required), structured_job_posting (optional), key_points (required), enrichment_context (optional), language (required)."
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
        "description": "Creates executive summary and hiring recommendation for top candidates. Uses company and candidate enrichment data to provide more informed recommendations based on company culture, industry, and candidate professional background.",
        "content": EXECUTIVE_RECOMMENDATION_PROMPT,
        "category": "reporting",
        "variables": [
            "job_posting_summary",
            "candidate_count",
            "candidates_summary",
            "weights",
            "hard_blockers",
            "enrichment_context",
            "language"
        ],
        "language": "en",
        "model_preferences": {
            "temperature": 0.7,
            "max_tokens": 2500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "High-level summary for decision makers. Uses enrichment_context to consider company information and candidate professional profiles when making recommendations. This helps tailor recommendations to company culture and candidate fit. Variables: job_posting_summary (required), candidate_count (required), candidates_summary (required), weights (required), hard_blockers (required), enrichment_context (optional), language (required)."
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
    },
    # ============================================================================
    # CHATBOT PROMPTS
    # ============================================================================
    {
        "prompt_key": "chatbot_profile_extraction",
        "name": "Chatbot - Profile Extraction",
        "description": "Extracts structured profile information from conversational user messages. Used in chatbot flow to collect candidate data from natural language input.",
        "content": CHATBOT_PROFILE_EXTRACTION_PROMPT,
        "category": "chatbot",
        "variables": ["text", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.3,
            "max_tokens": 500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Extracts profile data from conversational text. Requires valid JSON output. Keep temperature low for consistency. Variables: text (required), language (required)."
    },
    {
        "prompt_key": "chatbot_question_generation",
        "name": "Chatbot - Adaptive Question Generation",
        "description": "Generates adaptive questions based on CV, job opportunity, and identified gaps. Used to collect missing information during chatbot conversation.",
        "content": CHATBOT_QUESTION_GENERATION_PROMPT,
        "category": "chatbot",
        "variables": ["cv_summary", "job_requirements", "gaps", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.5,
            "max_tokens": 1500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Generates 3-10 targeted questions. Prioritizes most important gaps. Returns JSON with question list. Variables: cv_summary (required), job_requirements (required), gaps (required), language (required)."
    },
    {
        "prompt_key": "chatbot_cv_generation_ats",
        "name": "Chatbot - CV Generation (ATS Friendly)",
        "description": "Generates ATS-friendly CV optimized for Applicant Tracking Systems. Focuses on keyword matching, plain text format, and clear structure.",
        "content": CHATBOT_CV_GENERATION_ATS_PROMPT,
        "category": "chatbot",
        "variables": ["original_cv", "job_requirements", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.4,
            "max_tokens": 3000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Optimizes CV for ATS compatibility. Focuses on keywords, plain text, clear sections. Returns JSON with CV content and changes summary. Variables: original_cv (required), job_requirements (required), language (required)."
    },
    {
        "prompt_key": "chatbot_cv_generation_human",
        "name": "Chatbot - CV Generation (Human Friendly)",
        "description": "Generates human-readable, compelling CV optimized for human recruiters. Focuses on narrative, achievements, and engaging presentation.",
        "content": CHATBOT_CV_GENERATION_HUMAN_PROMPT,
        "category": "chatbot",
        "variables": ["original_cv", "job_requirements", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.6,
            "max_tokens": 3000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Optimizes CV for human readers. Focuses on narrative, achievements, engaging tone. Returns JSON with CV content and changes summary. Variables: original_cv (required), job_requirements (required), language (required)."
    },
    {
        "prompt_key": "chatbot_digital_footprint_analysis",
        "name": "Chatbot - Digital Footprint Analysis",
        "description": "Analyzes candidate's digital footprint from LinkedIn, GitHub, portfolio, and other online profiles. Identifies inconsistencies and provides recommendations.",
        "content": CHATBOT_DIGITAL_FOOTPRINT_ANALYSIS_PROMPT,
        "category": "chatbot",
        "variables": ["cv_summary", "linkedin_data", "github_data", "portfolio_data", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.4,
            "max_tokens": 2000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Analyzes online profiles and identifies inconsistencies with CV. Returns JSON with analysis and recommendations. Variables: cv_summary (required), linkedin_data (optional), github_data (optional), portfolio_data (optional), language (required)."
    },
    {
        "prompt_key": "chatbot_interview_prep",
        "name": "Chatbot - Interview Preparation",
        "description": "Creates comprehensive interview preparation materials including likely questions, suggested answers, key stories (STAR format), and preparation summary.",
        "content": CHATBOT_INTERVIEW_PREP_PROMPT,
        "category": "chatbot",
        "variables": ["cv_summary", "job_opportunity", "experience_highlights", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.5,
            "max_tokens": 2500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Generates interview prep materials based on CV and job opportunity. Returns JSON with questions, answers, stories, and summary. Variables: cv_summary (required), job_opportunity (required), experience_highlights (optional), language (required)."
    },
    {
        "prompt_key": "chatbot_employability_score",
        "name": "Chatbot - Employability Score",
        "description": "Calculates employability score and detailed analysis based on CV and job requirements. Provides breakdown by technical skills, experience, and communication.",
        "content": CHATBOT_EMPLOYABILITY_SCORE_PROMPT,
        "category": "chatbot",
        "variables": ["cv_summary", "job_requirements", "structured_analysis", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.4,
            "max_tokens": 2000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Calculates fit score (0-100) with detailed breakdown. Returns JSON with scores, strengths, weaknesses, and recommendations. Variables: cv_summary (required), job_requirements (required), structured_analysis (optional), language (required)."
    },
    {
        "prompt_key": "chatbot_job_risk_assessment",
        "name": "Chatbot - Job Risk Assessment",
        "description": "Analyzes job opportunity quality and identifies potential red flags. Provides positive points, risks, and questions candidate should ask.",
        "content": CHATBOT_JOB_RISK_ASSESSMENT_PROMPT,
        "category": "chatbot",
        "variables": ["job_posting", "company_info", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.4,
            "max_tokens": 1500,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Analyzes job posting quality and risks. Returns JSON with quality score, positive points, red flags, and questions to ask. Variables: job_posting (required), company_info (optional), language (required)."
    },
    # ============================================================================
    # ENRICHMENT STRUCTURING PROMPTS
    # ============================================================================
    {
        "prompt_key": "structure_company_enrichment",
        "name": "Structure Company Enrichment",
        "description": "Structures company enrichment data from Brave Search API results into comprehensive JSON format matching company_profiles database schema. Used to transform raw Brave Search data into structured profiles for headhunting system.",
        "content": STRUCTURE_COMPANY_ENRICHMENT_PROMPT,
        "category": "enrichment",
        "variables": ["brave_enrichment_data", "additional_context", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.3,
            "max_tokens": 4000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Structures company enrichment data from Brave Search into JSON matching company_profiles schema. Returns structured JSON with basic_info, contact_info, culture, technologies, recent_activity, hiring_info, ai_insights, and normalized_name. Variables: brave_enrichment_data (required), additional_context (optional), language (required)."
    },
    {
        "prompt_key": "structure_candidate_enrichment",
        "name": "Structure Candidate Enrichment",
        "description": "Structures candidate enrichment data from CV and Brave Search API results into comprehensive JSON format matching candidate_profiles database schema. Used to transform raw CV and Brave Search data into structured profiles for headhunting system.",
        "content": STRUCTURE_CANDIDATE_ENRICHMENT_PROMPT,
        "category": "enrichment",
        "variables": ["cv_data", "brave_enrichment_data", "additional_context", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.3,
            "max_tokens": 4000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Structures candidate enrichment data from CV + Brave Search into JSON matching candidate_profiles schema. Returns structured JSON with basic_info, contact_info, professional_summary_structured, work_experience, education, skills, projects, publications, awards, career_preferences, ai_insights, and normalized_name. Variables: cv_data (required), brave_enrichment_data (required), additional_context (optional), language (required)."
    },
    # ============================================================================
    # SOCIAL MEDIA RISK ANALYSIS PROMPTS
    # ============================================================================
    {
        "prompt_key": "analyze_company_social_media_risk",
        "name": "Analyze Company Social Media Risk",
        "description": "Analyzes company's social media presence and reputation for potential risks that could affect recruitment or candidate association. Identifies public incidents, red flags, and provides recommendations for hiring teams.",
        "content": ANALYZE_COMPANY_SOCIAL_MEDIA_RISK_PROMPT,
        "category": "enrichment",
        "variables": ["company_name", "brave_enrichment_data", "recent_news", "additional_context", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.4,
            "max_tokens": 3000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Analyzes company reputation and social media risks. Returns JSON with overall_risk_score, risk_level, public_incidents, social_media_behavior, red_flags, positive_indicators, and recommendations. Focus on risks affecting recruitment (discrimination, harassment, unethical behavior, legal issues, reputation damage). Variables: company_name (required), brave_enrichment_data (required), recent_news (optional), additional_context (optional), language (required)."
    },
    {
        "prompt_key": "analyze_candidate_social_media_risk",
        "name": "Analyze Candidate Social Media Risk",
        "description": "Analyzes candidate's social media presence (both professional and personal) for potential risks that could affect their employability or company reputation. Identifies red flags, public incidents, and provides recommendations for hiring teams.",
        "content": ANALYZE_CANDIDATE_SOCIAL_MEDIA_RISK_PROMPT,
        "category": "enrichment",
        "variables": ["cv_data", "brave_enrichment_data", "social_media_links", "additional_context", "language"],
        "language": "en",
        "model_preferences": {
            "temperature": 0.4,
            "max_tokens": 3000,
            "preferred_provider": "gemini"
        },
        "admin_notes": "Analyzes candidate social media and online behavior risks. Returns JSON with overall_risk_score, risk_level, professional_social_media (LinkedIn, GitHub, portfolio), personal_social_media (Twitter, Facebook, Instagram), public_incidents, red_flags, positive_indicators, recommendations, and privacy_notes. Focus on risks affecting employability (discrimination, harassment, unethical behavior, legal issues, inappropriate content). Variables: cv_data (required), brave_enrichment_data (required), social_media_links (optional), additional_context (optional), language (required)."
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

