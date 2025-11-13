"""
AI Prompts Management.

This module provides access to AI prompts stored in the database.
Prompts can be managed through the Admin UI (/admin/prompts).

Fallback: If database prompts are not available, default prompts are used.
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# CV Extraction Prompt
CV_EXTRACTION_PROMPT = """You are a CV analysis expert. Extract structured information from the following CV text.

IMPORTANT: You must respond in {language}. All extracted text, descriptions, and content must be in {language}.

CV Text:
{cv_text}

Extract and return ONLY valid JSON with this structure:
{{
  "personal_info": {{
    "name": "Full name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "city, country"
  }},
  "summary": "Brief professional summary",
  "work_experience": [
    {{
      "company": "Company name",
      "position": "Job title",
      "duration": "Start - End dates",
      "responsibilities": ["Key responsibility 1", "Key responsibility 2"]
    }}
  ],
  "education": [
    {{
      "institution": "School/University",
      "degree": "Degree type and field",
      "year": "Graduation year"
    }}
  ],
  "skills": {{
    "technical": ["Skill 1", "Skill 2"],
    "soft": ["Skill 1", "Skill 2"],
    "languages": ["Language: Level"]
  }},
  "certifications": ["Certification 1", "Certification 2"]
}}

Return ONLY the JSON, no additional text."""

# Job Posting Normalization Prompt
JOB_POSTING_NORMALIZATION_PROMPT = """You are a recruitment expert. Extract structured information from this job posting.

IMPORTANT: You must respond in {language}. All extracted text, descriptions, and content must be in {language}.

Job Posting:
{job_posting_text}

{enrichment_context}

Extract and return ONLY valid JSON:
{{
  "title": "Job title",
  "company": "Company name if mentioned",
  "location": "Location",
  "type": "Full-time/Part-time/Contract",
  "experience_level": "Junior/Mid/Senior",
  "required_skills": ["Skill 1", "Skill 2"],
  "preferred_skills": ["Skill 1", "Skill 2"],
  "responsibilities": ["Responsibility 1", "Responsibility 2"],
  "qualifications": ["Requirement 1", "Requirement 2"],
  "languages": ["Language 1", "Language 2"],
  "salary_range": "If mentioned",
  "benefits": ["Benefit 1", "Benefit 2"],
  "company_info": {{
    "industry": "Industry sector if mentioned",
    "size": "Company size if mentioned (startup, SME, enterprise)",
    "stage": "Company stage if mentioned (seed, series A, established, public)"
  }}
}}

Return ONLY the JSON."""

# Weighting Recommendation Prompt
WEIGHTING_RECOMMENDATION_PROMPT = """You are acting as a lead technical recruiter.

IMPORTANT: You must respond in {language}. All recommendations, explanations, and content must be in {language}.

Use the information below to recommend category weights (that sum to 100%), critical hard blockers, and nice-to-have differentiators for candidate evaluation.

Job Posting (raw):
{job_posting}

Structured Job Posting Data (if available):
{structured_job_posting}

Key Requirements Highlighted by Interviewer:
{key_points}

{enrichment_context}

Respond ONLY with valid JSON (no extra text) using this structure in {language}:
{{
  "weights": {{
    "technical_skills": 0-100,
    "experience": 0-100,
    "soft_skills": 0-100,
    "languages": 0-100,
    "education": 0-100
  }},
  "hard_blockers": [
    "Must have ...",
    "Must ... if absolutely non-negotiable"
  ],
  "nice_to_have": [
    "Preferred but not mandatory requirement",
    "Another useful differentiator"
  ],
  "summary": "Short explanation of the weighting logic"
}}

Rules:
- Weights must total 100.
- Include only requirements that can be evaluated from CVs or screening.
- Hard blockers should be truly mandatory. If unsure, leave the array empty.
- Nice to have items should be concrete skills or experiences that differentiate top candidates.
- If information is missing, make reasonable assumptions and mention them in the summary.

Return ONLY the JSON in {language}."""

# CV Summary Prompt
CV_SUMMARY_PROMPT = """You are an expert resume analyst. Summarize the following CV content and extract key identifiers.

IMPORTANT: You must respond in {language}. All summaries, descriptions, and content must be in {language}.

CV File Name: {file_name}

Extract and return ONLY valid JSON:
{{
  "full_name": "Full candidate name if present",
  "current_role": "Most recent job title or a short headline describing the candidate",
  "experience_years": "Approximate years of relevant experience as integer",
  "primary_skills": ["Top hard skills", "Technologies", "Frameworks"],
  "soft_skills": ["Key soft or leadership skills"],
  "languages": ["Language - Level"],
  "education": [
    {{
      "degree": "Degree or certification",
      "institution": "Institution name",
      "year": "Graduation year or range if available"
    }}
  ],
  "notable_achievements": [
    "Impactful achievement or metric",
    "Award or recognition",
    "Open-source or community leadership"
  ],
  "summary": "2-3 sentence narrative summarizing the candidate’s profile"
}}

Rules:
- If a field is missing, use null (for single values) or an empty array.
- Be concise, factual, and base everything on the CV content.
- Use the CV file name only as a hint when necessary (e.g., to infer candidate name).
- Do not invent details not present in the CV.

Return ONLY the JSON in {language}."""

# Interviewer Analysis Prompt
INTERVIEWER_ANALYSIS_PROMPT = """You are a professional recruiter analyzing candidates for a job opening. You must perform a meticulous, comprehensive analysis following the detailed structure below.

IMPORTANT: You must respond in {language}. All analysis, descriptions, justifications, questions, and content must be in {language}. Do not use any other language.

Job Posting:
{job_posting}

Key Requirements (from interviewer):
{key_points}

Candidate CV:
{cv_text}

Weights for evaluation:
{weights}

Hard Blockers:
{hard_blockers}

Nice To Have (preferred but optional differentiators):
{nice_to_have}

{enrichment_context}

INSTRUCTIONS:
1. Compare meticulously the candidate's competencies and experiences with the job posting requirements.
2. Identify strong matches, partial matches, and gaps for this candidate.
3. Evaluate the overall suitability of the candidate for the position.
4. Analyze career progression and professional stability.
5. Identify notable achievements and relevant projects.
6. Evaluate academic background and professional certifications.

Return ONLY valid JSON in {language} following this EXACT structure:
{{
  "profile_summary": "3-4 sentence summary of the candidate's profile",
  "swot_analysis": {{
    "strengths": ["Strength 1", "Strength 2", "Strength 3", "Strength 4"],
    "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "threats": ["Threat 1", "Threat 2"]
  }},
  "technical_skills_detailed": [
    {{
      "skill": "Skill name",
      "score": 1-5,
      "justification": "Detailed explanation citing specific CV evidence"
    }}
  ],
  "soft_skills_detailed": [
    {{
      "skill": "Soft skill name",
      "score": 1-5,
      "justification": "Detailed explanation with specific CV examples"
    }}
  ],
  "missing_critical_technical_skills": ["Critical skill 1 missing", "Critical skill 2 missing"],
  "missing_important_soft_skills": ["Important soft skill 1 missing", "Important soft skill 2 missing"],
  "professional_experience_analysis": {{
    "relevance_to_position": "Analysis of how experience matches position requirements",
    "career_progression": "Analysis of career progression trajectory",
    "professional_stability": "Analysis of job stability and tenure patterns"
  }},
  "education_and_certifications": {{
    "relevance": "Analysis of education relevance to position",
    "adequacy": "Assessment of whether education meets requirements",
    "certifications": ["Certification 1", "Certification 2"]
  }},
  "notable_achievements": [
    {{
      "achievement": "Achievement description",
      "impact": "Analysis of impact and relevance"
    }}
  ],
  "culture_fit_assessment": {{
    "score": 1-5,
    "justification": "Detailed justification of cultural fit assessment"
  }},
  "categories": {{
    "technical_skills": 1-5,
    "experience": 1-5,
    "soft_skills": 1-5,
    "languages": 1-5,
    "education": 1-5,
    "culture_fit": 1-5
  }},
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "risks": ["Risk/Gap 1", "Risk/Gap 2"],
  "custom_questions": [
    "Question 1",
    "Question 2",
    "Question 3",
    "Question 4",
    "Question 5",
    "Question 6",
    "Question 7"
  ],
  "hard_blocker_violations": ["Blocker 1 if violated"],
  "recommendation": "Brief hiring recommendation",
  "intro_pitch": "A 30-second introduction pitch for this candidate to use during interviews",
  "gap_strategies": [
    "Strategy 1 to address identified gaps/risks",
    "Strategy 2 to address identified gaps/risks"
  ],
  "preparation_tips": [
    "Topic 1 to study for the interview",
    "Topic 2 to study for the interview",
    "Topic 3 to study for the interview"
  ],
  "score_breakdown": {{
    "technical_skills": {{
      "weight_percent": 0-100,
      "score": 0-100,
      "justification": "Justification for technical skills score"
    }},
    "soft_skills": {{
      "weight_percent": 0-100,
      "score": 0-100,
      "justification": "Justification for soft skills score"
    }},
    "professional_experience": {{
      "weight_percent": 0-100,
      "score": 0-100,
      "justification": "Justification for experience score"
    }},
    "education_certifications": {{
      "weight_percent": 0-100,
      "score": 0-100,
      "justification": "Justification for education score"
    }},
    "culture_fit": {{
      "weight_percent": 0-100,
      "score": 0-100,
      "justification": "Justification for culture fit score"
    }},
    "global_score": 0-100,
    "global_score_justification": "Detailed justification of the global score considering all factors"
  }}
}}

SCORING SCALES (MUST BE EXPLICITLY EXPLAINED):

Technical Skills (Hard Skills) - Scale 1-5:
1 = Básico (Basic) - Limited knowledge or experience
2 = Intermediário (Intermediate) - Some practical experience
3 = Avançado (Advanced) - Solid experience and proficiency
4 = Proficiente (Proficient) - Strong expertise and depth
5 = Especialista (Expert) - Exceptional mastery and leadership

Soft Skills (Interpersonal Skills) - Scale 1-5:
1 = Pouco evidente (Not evident) - No clear demonstration in CV
2 = Parcialmente demonstrada (Partially demonstrated) - Some indirect evidence
3 = Adequadamente demonstrada (Adequately demonstrated) - Clear evidence in CV
4 = Bem demonstrada (Well demonstrated) - Strong evidence with examples
5 = Fortemente demonstrada (Strongly demonstrated) - Exceptional evidence with multiple examples

Culture Fit - Scale 1-5:
1 = Pouco adequado (Not suitable) - Poor cultural fit
2 = Parcialmente adequado (Partially suitable) - Some concerns about fit
3 = Adequado (Suitable) - Good cultural fit
4 = Bem adequado (Well suited) - Strong cultural alignment
5 = Altamente adequado (Highly suitable) - Exceptional cultural match

Categories (Overall) - Scale 1-5:
1 = Very weak
2 = Below expectations
3 = Meets basic requirements
4 = Strong fit
5 = Exceptional fit

REQUIREMENTS:
- All scores must include detailed justifications citing specific CV evidence.
- Technical skills must be evaluated individually with specific justifications.
- Soft skills must be inferred from CV content with specific examples.
- Missing critical skills must be identified if they are crucial for the position.
- SWOT analysis must be comprehensive and based only on CV information.
- Professional experience analysis must evaluate relevance, progression, and stability.
- Education analysis must assess relevance and adequacy.
- Notable achievements must include impact analysis.
- Culture fit must be assessed based on available information.
- Score breakdown must use the weights provided and justify each component.
- Global score (0-100) must be calculated considering all weighted factors.
- All candidates with global score below 75 should be flagged for potential exclusion.
- Questions must cover technical skills, soft skills, and address gaps not evident in CV.
- All text, analysis, and content must be in {language}.

Return ONLY the JSON in {language}, no additional text."""

# Candidate Analysis Prompt  
CANDIDATE_ANALYSIS_PROMPT = """You are a professional recruiter analyzing a candidate for a job opening.

IMPORTANT: You must respond in {language}. All analysis, descriptions, questions, answers, and content must be in {language}. Do not use any other language.

Job Posting:
{job_posting}

Candidate CV:
{cv_text}

{enrichment_context}

Analyze this candidate and return ONLY valid JSON in {language}:
{{
  "categories": {{
    "technical_skills": 1-5,
    "experience": 1-5,
    "soft_skills": 1-5,
    "languages": 1-5,
    "education": 1-5
  }},
  "strengths": ["Strength 1", "Strength 2", "Strength 3", "Strength 4", "Strength 5"],
  "risks": ["Risk or missing skill 1", "Risk 2", "Risk 3"],
  "custom_questions": [
    "Question 1 about technical skills",
    "Question 2 about experience",
    "Question 3 about soft skills",
    "Question 4 about languages",
    "Question 5 about education",
    "Question 6 about motivation",
    "Question 7 about problem solving",
    "Question 8 additional"
  ],
  "answers": [
    "Answer 1 based on CV",
    "Answer 2 based on CV",
    "Answer 3 based on CV",
    "Answer 4 based on CV",
    "Answer 5 based on CV",
    "Answer 6 based on CV",
    "Answer 7 based on CV",
    "Answer 8 based on CV"
  ],
  "recommendation": "Brief summary of fit and readiness",
  "intro_pitch": "A 30-second introduction pitch for this candidate",
  "notes": [
    "Note 1 for success",
    "Note 2 for success",
    "Note 3 for success"
  ]
}}

Use scores 1-5 where:
1 = Very weak
2 = Below expectations
3 = Meets basic requirements
4 = Strong fit
5 = Exceptional fit

Return ONLY the JSON in {language}."""

# Translation Prompt
TRANSLATION_PROMPT = """Translate the following text from English to {target_language}.

Maintain the tone, meaning, and structure. For technical or legal terms, use appropriate professional language.

English text:
{text}

Translated {target_language} text:"""

# Executive Recommendation Prompt
EXECUTIVE_RECOMMENDATION_PROMPT = """You are a senior recruitment consultant preparing an executive summary for hiring managers.

IMPORTANT: You must respond in {language}. All recommendations, summaries, insights, and content must be in {language}. Do not use any other language.

Job Position Overview:
{job_posting_summary}

Candidates Analyzed: {candidate_count}

Top Candidates (with scores and key data):
{candidates_summary}

Evaluation Criteria (weights):
{weights}

Hard Blockers:
{hard_blockers}

{enrichment_context}

Write a concise executive recommendation in {language} that:
1. Identifies the top 1-2 candidates and explains WHY they stand out
2. Highlights the key differentiators between top candidates
3. Mentions any concerns or trade-offs to consider
4. Provides a clear hiring recommendation

Return ONLY valid JSON:
{{
  "top_recommendation": {{
    "candidate_name": "Name of #1 candidate",
    "candidate_index": 0,
    "summary": "2-3 sentence recommendation explaining why this candidate is the best fit"
  }},
  "executive_summary": "A 3-4 paragraph executive summary covering: (1) overview of candidate pool quality, (2) detailed analysis of top candidate(s) with specific strengths, (3) any concerns or trade-offs, (4) final recommendation",
  "key_insights": [
    "Insight 1: Important pattern or finding",
    "Insight 2: Another key observation",
    "Insight 3: Strategic consideration"
  ]
}}

Return ONLY the JSON in {language}."""


async def get_prompt(prompt_type: str, language: str = "en") -> str:
    """
    Get prompt template by type from database.
    
    Falls back to default prompts if database is not available.
    
    Args:
        prompt_type: Type of prompt (cv_extraction, job_posting_normalization, etc.)
        language: Language code (default: "en")
        
    Returns:
        Prompt template string
    """
    # Try to get from database first
    try:
        from services.database.prompt_service import get_prompt_service
        
        service = get_prompt_service()
        prompt_data = await service.get_prompt_by_key(
            prompt_key=prompt_type,
            language=language
        )
        
        if prompt_data:
            logger.info(f"Loaded prompt '{prompt_type}' from database (v{prompt_data.get('version')})")
            return prompt_data.get("content", "")
    
    except Exception as e:
        logger.warning(f"Failed to load prompt from database, using default: {e}")
    
    # Fallback to default prompts
    prompts = {
        "cv_extraction": CV_EXTRACTION_PROMPT,
        "job_posting_normalization": JOB_POSTING_NORMALIZATION_PROMPT,
        "weighting_recommendation": WEIGHTING_RECOMMENDATION_PROMPT,
        "cv_summary": CV_SUMMARY_PROMPT,
        "interviewer_analysis": INTERVIEWER_ANALYSIS_PROMPT,
        "candidate_analysis": CANDIDATE_ANALYSIS_PROMPT,
        "translation": TRANSLATION_PROMPT,
        "executive_recommendation": EXECUTIVE_RECOMMENDATION_PROMPT
    }
    
    logger.info(f"Using default prompt for '{prompt_type}'")
    return prompts.get(prompt_type, "")


def get_prompt_sync(prompt_type: str) -> str:
    """
    Get prompt template by type (synchronous version for backward compatibility).
    
    Args:
        prompt_type: Type of prompt (cv_extraction, job_posting_normalization, etc.)
        
    Returns:
        Prompt template string
        
    Note:
        This is a synchronous wrapper that uses default prompts.
        For database prompts, use the async get_prompt() function.
    """
    prompts = {
        "cv_extraction": CV_EXTRACTION_PROMPT,
        "job_posting_normalization": JOB_POSTING_NORMALIZATION_PROMPT,
        "weighting_recommendation": WEIGHTING_RECOMMENDATION_PROMPT,
        "cv_summary": CV_SUMMARY_PROMPT,
        "interviewer_analysis": INTERVIEWER_ANALYSIS_PROMPT,
        "candidate_analysis": CANDIDATE_ANALYSIS_PROMPT,
        "translation": TRANSLATION_PROMPT,
        "executive_recommendation": EXECUTIVE_RECOMMENDATION_PROMPT
    }
    
    return prompts.get(prompt_type, "")

