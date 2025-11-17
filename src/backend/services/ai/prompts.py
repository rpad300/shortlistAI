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


# =============================================================================
# CHATBOT-SPECIFIC PROMPTS
# =============================================================================

# Chatbot Profile Extraction Prompt
CHATBOT_PROFILE_EXTRACTION_PROMPT = """You are an expert at extracting structured profile information from conversational text.

IMPORTANT: You must respond in {language}. All extracted text must be in {language}.

Extract profile information from the following user message. Return ONLY valid JSON with this structure:
{{
  "name": "Full name if mentioned, or null",
  "email": "Email address if mentioned, or null",
  "phone": "Phone number if mentioned, or null",
  "location": "City and country if mentioned, or null",
  "links": {{
    "linkedin": "LinkedIn URL if mentioned, or null",
    "github": "GitHub URL if mentioned, or null",
    "portfolio": "Portfolio/website URL if mentioned, or null",
    "behance": "Behance URL if mentioned, or null",
    "dribbble": "Dribbble URL if mentioned, or null",
    "facebook": "Facebook URL if mentioned, or null",
    "instagram": "Instagram URL if mentioned, or null",
    "twitter": "Twitter/X URL if mentioned, or null",
    "telegram": "Telegram URL if mentioned, or null",
    "whatsapp": "WhatsApp link if mentioned, or null"
  }}
}}

User Message:
{text}

Return ONLY the JSON, no additional text or explanation. If information is missing, use null for that field."""

# Chatbot Question Generation Prompt
CHATBOT_QUESTION_GENERATION_PROMPT = """You are an expert recruiter helping a candidate prepare their CV for a specific job opportunity.

IMPORTANT: You must respond in {language}. All questions must be in {language}.

Based on the CV and job opportunity analysis, generate adaptive questions to gather missing information or strengthen the candidate's profile.

CV Summary:
{cv_summary}

Job Opportunity Requirements:
{job_requirements}

Gaps Identified:
{gaps}

Generate 3-10 targeted questions (prioritize the most important gaps). Return ONLY valid JSON:
{{
  "questions": [
    {{
      "id": "unique_question_id",
      "question": "Question text",
      "category": "work_experience|skills|projects|education|other",
      "priority": "high|medium|low",
      "context": "Why this question is important for this job opportunity"
    }}
  ],
  "total_questions": 5,
  "focus_areas": ["area1", "area2"]
}}

Return ONLY the JSON, no additional text."""

# Chatbot CV Generation Prompt (ATS Friendly)
CHATBOT_CV_GENERATION_ATS_PROMPT = """You are a CV optimization expert specializing in ATS (Applicant Tracking System) compatibility.

IMPORTANT: You must respond in {language}. The generated CV must be in {language}.

Optimize the candidate's CV for ATS systems while keeping it relevant to the job opportunity. Focus on:
- Keyword optimization matching job requirements
- Clear section headers (Summary, Experience, Education, Skills)
- Plain text format (avoid tables, images, complex formatting)
- Chronological consistency
- Standard date formats

Original CV Data:
{original_cv}

Job Opportunity Requirements:
{job_requirements}

Target Language: {language}

Generate an ATS-friendly CV. Return ONLY valid JSON:
{{
  "cv_content": "Full CV text in plain format",
  "structured_data": {{
    "summary": "Professional summary optimized for ATS",
    "experience": [...],
    "education": [...],
    "skills": {...}
  }},
  "keyword_matches": ["keyword1", "keyword2"],
  "changes_made": [
    "Reorganized experience section",
    "Added keyword X in summary",
    "Clarified Y skill"
  ]
}}

Return ONLY the JSON."""

# Chatbot CV Generation Prompt (Human Friendly)
CHATBOT_CV_GENERATION_HUMAN_PROMPT = """You are a CV optimization expert creating a human-readable, compelling CV.

IMPORTANT: You must respond in {language}. The generated CV must be in {language}.

Optimize the candidate's CV for human recruiters. Focus on:
- Engaging professional summary
- Clear achievements and impact
- Storytelling approach (but factual)
- Professional yet personable tone
- Well-organized sections

Original CV Data:
{original_cv}

Job Opportunity Requirements:
{job_requirements}

Target Language: {language}

Generate a human-friendly CV. Return ONLY valid JSON:
{{
  "cv_content": "Full CV text with narrative elements",
  "structured_data": {{
    "summary": "Engaging professional summary",
    "experience": [...],
    "education": [...],
    "skills": {...}
  }},
  "tone": "professional|marketing|neutral",
  "changes_made": [
    "Enhanced summary with impact statements",
    "Reorganized experience by relevance",
    "Added achievement-focused language"
  ]
}}

Return ONLY the JSON."""

# Chatbot Digital Footprint Analysis Prompt
CHATBOT_DIGITAL_FOOTPRINT_ANALYSIS_PROMPT = """You are an expert at analyzing professional online profiles and identifying inconsistencies.

IMPORTANT: You must respond in {language}. All analysis must be in {language}.

Analyze the candidate's digital footprint from their CV and provided links. Identify:
- Inconsistencies between CV and online profiles
- Missing information that should be added
- Recommendations for profile improvement

CV Summary:
{cv_summary}

LinkedIn Profile (if available):
{linkedin_data}

GitHub Profile (if available):
{github_data}

Portfolio (if available):
{portfolio_data}

Return ONLY valid JSON:
{{
  "linkedin_analysis": {{
    "headline_match": true|false,
    "summary_match": true|false,
    "experience_inconsistencies": ["inconsistency1", "inconsistency2"],
    "skills_gaps": ["missing skill1", "missing skill2"],
    "recommendations": ["recommendation1", "recommendation2"]
  }},
  "github_analysis": {{
    "main_languages": ["Python", "JavaScript"],
    "recent_activity": "Active|Inactive",
    "projects_highlighted": true|false,
    "cv_match": true|false,
    "recommendations": ["recommendation1"]
  }},
  "inconsistencies": [
    {{
      "type": "experience|skills|dates|other",
      "description": "What is inconsistent",
      "cv_value": "Value in CV",
      "profile_value": "Value in profile",
      "recommendation": "What to fix"
    }}
  ],
  "recommendations": [
    "Update LinkedIn headline to match CV",
    "Add missing project to CV",
    "Synchronize dates"
  ]
}}

Return ONLY the JSON."""

# Chatbot Interview Preparation Prompt
CHATBOT_INTERVIEW_PREP_PROMPT = """You are an expert interview coach preparing a candidate for a job interview.

IMPORTANT: You must respond in {language}. All interview prep materials must be in {language}.

Based on the CV and job opportunity, create comprehensive interview preparation materials.

CV Summary:
{cv_summary}

Job Opportunity:
{job_opportunity}

Candidate's Experience Highlights:
{experience_highlights}

Return ONLY valid JSON:
{{
  "likely_questions": [
    {{
      "question": "Question text",
      "category": "technical|behavioral|cultural|experience",
      "importance": "high|medium|low",
      "reasoning": "Why this question is likely"
    }}
  ],
  "suggested_answers": [
    {{
      "question_id": "question_id",
      "answer_template": "Answer using candidate's experience",
      "key_points": ["point1", "point2"],
      "example_story": "Specific story from candidate's background"
    }}
  ],
  "key_stories": [
    {{
      "title": "Story title",
      "context": "Situation/Context",
      "action": "What candidate did",
      "result": "Outcome and impact",
      "skills_demonstrated": ["skill1", "skill2"],
      "when_to_use": "Which questions this story answers"
    }}
  ],
  "questions_to_ask": [
    "Question candidate should ask about the role",
    "Question about company culture",
    "Question about team structure"
  ],
  "preparation_summary": "Overall preparation strategy and focus areas"
}}

Return ONLY the JSON."""

# Chatbot Employability Score Prompt
CHATBOT_EMPLOYABILITY_SCORE_PROMPT = """You are an expert recruiter evaluating a candidate's fit for a specific job opportunity.

IMPORTANT: You must respond in {language}. All analysis must be in {language}.

Evaluate the candidate's employability score based on CV and job requirements. Provide detailed breakdown.

CV Summary:
{cv_summary}

Job Requirements:
{job_requirements}

Structured Analysis:
{structured_analysis}

Return ONLY valid JSON:
{{
  "overall_score": 75,
  "technical_skills_score": 80,
  "experience_score": 70,
  "communication_score": 75,
  "strengths": [
    "Strong experience in X",
    "Relevant certifications",
    "Clear career progression"
  ],
  "weaknesses": [
    "Missing skill Y",
    "Limited experience in Z"
  ],
  "recommendations": [
    "Add project showcasing skill Y",
    "Highlight relevant experience in Z area",
    "Update LinkedIn with keywords from job"
  ],
  "explanation": "Human-readable explanation of the score and reasoning"
}}

Scores must be between 0 and 100. Return ONLY the JSON."""

# Structure Company Enrichment Prompt
STRUCTURE_COMPANY_ENRICHMENT_PROMPT = """You are an expert data analyst structuring company enrichment data from Brave Search API results.

IMPORTANT: You must respond in {language}. All extracted text must be in {language}.

Based on the Brave Search enrichment data provided below, structure the information into a comprehensive JSON format matching the company_profiles database schema.

Brave Search Enrichment Data:
{brave_enrichment_data}

Additional Context (if available):
{additional_context}

Extract and return ONLY valid JSON with this EXACT structure:
{{
  "basic_info": {{
    "website": "..." or null,
    "description": "..." or null,
    "industry": "..." or null,
    "sector": "..." or null,
    "company_size": "..." or null, // e.g., "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"
    "founded_year": 2020 or null,
    "headquarters": {{"city": "...", "country": "...", "address": "..."}} or null,
    "employee_count": 150 or null,
    "revenue": {{"currency": "EUR", "amount": 1000000, "period": "annual"}} or null,
    "legal_status": "..." or null, // "LLC", "Corporation", "Startup", etc.
    "funding": [] // Array of funding rounds if available
  }},
  "contact_info": {{
    "website": "..." or null,
    "email": "..." or null,
    "phone": "..." or null,
    "address": {{"street": "...", "city": "...", "country": "...", "postal_code": "..."}} or null,
    "social_media": {{
      "linkedin": "..." or null,
      "twitter": "..." or null,
      "facebook": "..." or null,
      "github": "..." or null
    }}
  }},
  "culture": {{
    "values": [], // Array of company values if found
    "mission": "..." or null,
    "vision": "..." or null,
    "culture_keywords": [], // Keywords describing company culture
    "benefits": [], // Array of benefits/perks if mentioned
    "work_environment": "..." or null, // "remote", "hybrid", "onsite"
    "work_life_balance": "..." or null // AI assessment
  }},
  "technologies": {{
    "tech_stack": [], // Technologies used
    "tools": [], // Development tools, platforms
    "methodologies": [], // Agile, Scrum, etc.
    "cloud_providers": [] // AWS, Azure, GCP
  }},
  "recent_activity": [
    {{
      "type": "news" | "funding" | "acquisition" | "product_launch" | "hiring",
      "title": "...",
      "description": "...",
      "url": "...",
      "date": "...",
      "source": "..."
    }}
  ],
  "hiring_info": {{
    "active_openings": 0 or null,
    "recent_postings": [], // Array of job titles frequently posted
    "hiring_team_size": 0 or null,
    "average_time_to_hire": 0 or null, // days
    "common_locations": [], // Locations where they hire
    "remote_policy": "..." or null // "fully_remote", "hybrid", "onsite_only"
  }},
  "ai_insights": {{
    "growth_trajectory": "..." or null, // "growing", "stable", "declining"
    "reputation_score": 0-100 or null,
    "key_strengths": [],
    "potential_concerns": [],
    "recommendation_notes": "..." or null
  }},
  "normalized_name": "..." // Normalized/standardized company name for deduplication
}}

Return ONLY the JSON, no additional text. Use null for missing fields, empty arrays [] for missing lists, and empty objects {{}} for missing nested objects."""

# Structure Candidate Enrichment Prompt
STRUCTURE_CANDIDATE_ENRICHMENT_PROMPT = """You are an expert data analyst structuring candidate enrichment data from CV and Brave Search API results.

IMPORTANT: You must respond in {language}. All extracted text must be in {language}.

Based on the CV data and Brave Search enrichment data provided below, structure the information into a comprehensive JSON format matching the candidate_profiles database schema.

CV Data:
{cv_data}

Brave Search Enrichment Data:
{brave_enrichment_data}

Additional Context (if available):
{additional_context}

Extract and return ONLY valid JSON with this EXACT structure:
{{
  "basic_info": {{
    "email": "..." or null,
    "phone": "..." or null,
    "location": {{"city": "...", "country": "...", "address": "..."}} or null,
    "current_location": "..." or null,
    "willing_to_relocate": true or false or null,
    "preferred_locations": [], // Array of preferred locations
    "nationality": "..." or null,
    "languages": [
      {{"language": "...", "level": "native" | "fluent" | "proficient" | "basic"}}
    ], // Array of languages with proficiency levels
    "date_of_birth": "..." or null // Only if available with consent
  }},
  "contact_info": {{
    "email": "..." or null,
    "phone": "..." or null,
    "social_media": {{
      "linkedin": "..." or null,
      "github": "..." or null,
      "portfolio": "..." or null,
      "twitter": "..." or null
    }},
    "professional_websites": [] // Array of URLs
  }},
  "professional_summary_structured": {{
    "current_role": "..." or null,
    "years_experience": 0 or null,
    "expertise_areas": [], // Main areas of expertise
    "career_level": "..." or null, // "entry", "mid", "senior", "lead", "executive"
    "summary_text": "..." // Full summary text
  }},
  "work_experience": [
    {{
      "company": "...",
      "company_normalized": "..." or null,
      "company_linkedin": "..." or null,
      "position": "...",
      "location": "..." or null,
      "start_date": "...", // Format: "YYYY-MM" or "YYYY-MM-DD"
      "end_date": "..." or null, // null if current, format: "YYYY-MM" or "YYYY-MM-DD"
      "is_current": true or false,
      "duration_months": 0,
      "responsibilities": [],
      "achievements": [],
      "technologies_used": [],
      "team_size": 0 or null,
      "reports_to": "..." or null,
      "enrichment": {{}} // Additional data from Brave Search about company/role
    }}
  ],
  "education": [
    {{
      "institution": "...",
      "degree": "..." or null,
      "field_of_study": "..." or null,
      "level": "..." or null, // "high_school", "bachelor", "master", "phd", "certification"
      "start_date": "..." or null,
      "end_date": "..." or null,
      "grade": "..." or null,
      "honors": []
    }}
  ],
  "skills": {{
    "hard_skills": [], // Technical skills
    "soft_skills": [],
    "languages": [], // Programming languages
    "frameworks": [],
    "tools": [],
    "platforms": [], // Cloud platforms, etc.
    "certifications": [
      {{"name": "...", "issuer": "...", "date": "..."}}
    ],
    "skill_levels": {{}} // {{"skill_name": "expert" | "advanced" | "intermediate" | "beginner"}}
  }},
  "projects": [
    {{
      "name": "...",
      "description": "...",
      "url": "..." or null,
      "technologies": [],
      "date": "..." or null,
      "role": "..." or null // Role in project
    }}
  ],
  "publications": [
    {{
      "title": "...",
      "type": "article" | "paper" | "blog_post" | "book" | "presentation",
      "url": "..." or null,
      "date": "..." or null,
      "authors": [],
      "venue": "..." or null
    }}
  ],
  "awards": [
    {{
      "title": "...",
      "issuer": "...",
      "date": "..." or null,
      "description": "..." or null,
      "url": "..." or null
    }}
  ],
  "career_preferences": {{
    "target_roles": [], // Desired job titles
    "target_industries": [],
    "target_companies": [], // Companies interested in
    "salary_expectations": {{"min": 0, "max": 0, "currency": "EUR"}} or null,
    "work_environment": "..." or null, // "remote", "hybrid", "onsite"
    "preferred_locations": [],
    "availability": "..." or null // "immediately", "1_month", "3_months", "6_months", "open"
  }},
  "ai_insights": {{
    "market_value": 0-100 or null, // Estimated market value score
    "strengths": [],
    "areas_for_improvement": [],
    "recommendation_notes": "..." or null,
    "matching_keywords": [], // Keywords for job matching
    "unique_selling_points": []
  }},
  "normalized_name": "..." // Normalized/standardized name for deduplication
}}

Return ONLY the JSON, no additional text. Use null for missing fields, empty arrays [] for missing lists, and empty objects {{}} for missing nested objects."""

# Social Media Risk Analysis Prompt (for Companies)
ANALYZE_COMPANY_SOCIAL_MEDIA_RISK_PROMPT = """You are an expert risk analyst specializing in reputation and social media risk assessment for recruitment and headhunting.

IMPORTANT: You must respond in {language}. All analysis must be in {language}.

Based on the Brave Search enrichment data and company information provided below, analyze the company's social media presence and reputation for potential risks that could affect recruitment or candidate association.

Company Information:
{company_name}

Brave Search Enrichment Data:
{brave_enrichment_data}

Recent News and Activities:
{recent_news}

Additional Context:
{additional_context}

Analyze and return ONLY valid JSON with this EXACT structure:
{{
  "overall_risk_score": 0-100, // 0 = no risk, 100 = high risk
  "risk_level": "low" | "medium" | "high" | "critical",
  "public_incidents": [
    {{
      "type": "scandal" | "lawsuit" | "controversy" | "negative_news" | "social_media_post",
      "title": "...",
      "description": "...",
      "date": "...",
      "source": "...",
      "url": "...",
      "severity": "low" | "medium" | "high",
      "relevance": "..." // How relevant for recruitment (e.g., "Employee treatment", "Ethical concerns", "Financial stability")
    }}
  ],
  "social_media_behavior": {{
    "platform": "linkedin" | "twitter" | "facebook" | "instagram" | "other",
    "tone_analysis": "...", // "professional", "casual", "controversial", "polarizing"
    "post_frequency": "...", // "low", "moderate", "high"
    "controversial_topics": [], // Topics that might be problematic
    "engagement_pattern": "..." // Type of engagement with others
  }},
  "red_flags": [
    {{
      "type": "discrimination" | "harassment" | "unethical_behavior" | "legal_issues" | "reputation_damage",
      "description": "...",
      "evidence_urls": [],
      "severity": "low" | "medium" | "high" | "critical",
      "relevance_for_recruitment": "..." // Why this matters for candidates
    }}
  ],
  "positive_indicators": [
    {{
      "type": "community_engagement" | "thought_leadership" | "awards" | "positive_coverage",
      "description": "...",
      "evidence_urls": []
    }}
  ],
  "recommendations": "...", // AI-generated recommendations for hiring team (e.g., "Proceed with caution", "Monitor ongoing", "Low risk")
  "last_analyzed": "..." // ISO timestamp
}}

Focus on risks that could:
- Damage candidate's reputation if associated with company
- Create legal/compliance issues
- Reflect poor company culture or values
- Indicate financial instability or business risks
- Show discrimination or unethical behavior

Return ONLY the JSON, no additional text."""

# Social Media Risk Analysis Prompt (for Candidates)
ANALYZE_CANDIDATE_SOCIAL_MEDIA_RISK_PROMPT = """You are an expert risk analyst specializing in social media and online behavior assessment for recruitment and headhunting.

IMPORTANT: You must respond in {language}. All analysis must be in {language}.

Based on the CV data and Brave Search enrichment data provided below, analyze the candidate's social media presence (both professional and personal) for potential risks that could affect their employability or company reputation.

CV Data Summary:
{cv_data}

Brave Search Enrichment Data:
{brave_enrichment_data}

Social Media Links:
{social_media_links}

Additional Context:
{additional_context}

Analyze and return ONLY valid JSON with this EXACT structure:
{{
  "overall_risk_score": 0-100, // 0 = no risk, 100 = high risk
  "risk_level": "low" | "medium" | "high" | "critical",
  "professional_social_media": {{
    "linkedin": {{
      "risk_score": 0-100,
      "tone_analysis": "...", // "professional", "casual", "controversial", "polarizing"
      "post_frequency": "...", // "low", "moderate", "high"
      "content_quality": "...", // "excellent", "good", "average", "poor"
      "engagement_pattern": "...", // Type of engagement with others
      "controversial_posts": [], // Array of concerning posts with URLs if available
      "positive_indicators": [] // Professional achievements, thought leadership, positive engagement
    }},
    "github": {{
      "risk_score": 0-100,
      "activity_level": "...",
      "contribution_quality": "...",
      "community_interaction": "...",
      "concerning_repositories": [], // Repos that might be problematic (e.g., controversial content, unethical projects)
      "positive_indicators": [] // Open source contributions, well-maintained projects
    }},
    "portfolio_website": {{
      "risk_score": 0-100,
      "content_quality": "...",
      "professionalism": "...",
      "concerning_content": [], // Any concerning content found
      "positive_indicators": []
    }}
  }},
  "personal_social_media": {{
    "twitter": {{
      "risk_score": 0-100,
      "visibility": "public" | "protected" | "private" | "unknown",
      "tone_analysis": "...",
      "controversial_topics": [], // Topics that might be problematic (politics, discrimination, etc.)
      "red_flag_posts": [], // Posts that could be concerning for employers
      "last_analyzed": "..."
    }},
    "facebook": {{
      "risk_score": 0-100,
      "visibility": "public" | "protected" | "private" | "unknown",
      "public_activity": "...",
      "concerning_content": [],
      "last_analyzed": "..."
    }},
    "instagram": {{
      "risk_score": 0-100,
      "visibility": "public" | "protected" | "private" | "unknown",
      "content_analysis": "...",
      "concerning_content": [],
      "last_analyzed": "..."
    }}
  }},
  "public_incidents": [
    {{
      "type": "scandal" | "lawsuit" | "controversy" | "negative_news" | "social_media_post",
      "platform": "...",
      "title": "...",
      "description": "...",
      "date": "...",
      "source": "...",
      "url": "...",
      "severity": "low" | "medium" | "high" | "critical",
      "relevance": "..." // How relevant for employment/recruitment
    }}
  ],
  "red_flags": [
    {{
      "type": "discrimination" | "harassment" | "unethical_behavior" | "legal_issues" | "reputation_damage" | "inappropriate_content",
      "description": "...",
      "platform": "...",
      "evidence_urls": [],
      "severity": "low" | "medium" | "high" | "critical",
      "context": "..." // Additional context about the red flag
    }}
  ],
  "positive_indicators": [
    {{
      "type": "community_engagement" | "thought_leadership" | "awards" | "positive_coverage" | "professional_achievements",
      "description": "...",
      "platform": "...",
      "evidence_urls": [],
      "impact": "..." // How positive this is for reputation
    }}
  ],
  "recommendations": "...", // AI-generated recommendations for hiring team
  "privacy_notes": "...", // Notes about privacy settings and visibility (e.g., "Most personal profiles are private")
  "last_analyzed": "..." // ISO timestamp
}}

Focus on risks that could:
- Damage company reputation if candidate is hired
- Create legal/compliance issues
- Indicate poor judgment or unprofessional behavior
- Show discrimination, harassment, or unethical behavior
- Conflict with company values or culture

Return ONLY the JSON, no additional text."""

# Chatbot Job Risk Assessment Prompt
CHATBOT_JOB_RISK_ASSESSMENT_PROMPT = """You are an expert recruiter analyzing a job opportunity for quality and potential red flags.

IMPORTANT: You must respond in {language}. All analysis must be in {language}.

Analyze the job posting and company information to identify positive points and potential risks.

Job Posting:
{job_posting}

Company Information:
{company_info}

Return ONLY valid JSON:
{{
  "quality_score": 85,
  "positive_points": [
    "Clear job responsibilities",
    "Detailed benefits package",
    "Well-defined company mission"
  ],
  "red_flags": [
    "Many functions in one role",
    "Unrealistic requirements for junior level"
  ],
  "questions_to_ask": [
    "What is the team structure?",
    "What are growth opportunities?",
    "What is the work-life balance culture?"
  ],
  "company_summary": "Brief summary of what the company does, size, and culture"
}}

Scores must be between 0 and 100. Return ONLY the JSON."""


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
        "executive_recommendation": EXECUTIVE_RECOMMENDATION_PROMPT,
        # Chatbot prompts
        "chatbot_profile_extraction": CHATBOT_PROFILE_EXTRACTION_PROMPT,
        "chatbot_question_generation": CHATBOT_QUESTION_GENERATION_PROMPT,
        "chatbot_cv_generation": CHATBOT_CV_GENERATION_ATS_PROMPT,  # Default to ATS
        "chatbot_cv_generation_ats": CHATBOT_CV_GENERATION_ATS_PROMPT,
        "chatbot_cv_generation_human": CHATBOT_CV_GENERATION_HUMAN_PROMPT,
        "chatbot_digital_footprint_analysis": CHATBOT_DIGITAL_FOOTPRINT_ANALYSIS_PROMPT,
        "chatbot_interview_prep": CHATBOT_INTERVIEW_PREP_PROMPT,
        "chatbot_employability_score": CHATBOT_EMPLOYABILITY_SCORE_PROMPT,
        "chatbot_job_risk_assessment": CHATBOT_JOB_RISK_ASSESSMENT_PROMPT,
        # Enrichment structuring prompts
        "structure_company_enrichment": STRUCTURE_COMPANY_ENRICHMENT_PROMPT,
        "structure_candidate_enrichment": STRUCTURE_CANDIDATE_ENRICHMENT_PROMPT,
        # Social media risk analysis prompts
        "analyze_company_social_media_risk": ANALYZE_COMPANY_SOCIAL_MEDIA_RISK_PROMPT,
        "analyze_candidate_social_media_risk": ANALYZE_CANDIDATE_SOCIAL_MEDIA_RISK_PROMPT
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
        "executive_recommendation": EXECUTIVE_RECOMMENDATION_PROMPT,
        # Chatbot prompts
        "chatbot_profile_extraction": CHATBOT_PROFILE_EXTRACTION_PROMPT,
        "chatbot_question_generation": CHATBOT_QUESTION_GENERATION_PROMPT,
        "chatbot_cv_generation": CHATBOT_CV_GENERATION_ATS_PROMPT,
        "chatbot_cv_generation_ats": CHATBOT_CV_GENERATION_ATS_PROMPT,
        "chatbot_cv_generation_human": CHATBOT_CV_GENERATION_HUMAN_PROMPT,
        "chatbot_digital_footprint_analysis": CHATBOT_DIGITAL_FOOTPRINT_ANALYSIS_PROMPT,
        "chatbot_interview_prep": CHATBOT_INTERVIEW_PREP_PROMPT,
        "chatbot_employability_score": CHATBOT_EMPLOYABILITY_SCORE_PROMPT,
        "chatbot_job_risk_assessment": CHATBOT_JOB_RISK_ASSESSMENT_PROMPT,
        # Enrichment structuring prompts
        "structure_company_enrichment": STRUCTURE_COMPANY_ENRICHMENT_PROMPT,
        "structure_candidate_enrichment": STRUCTURE_CANDIDATE_ENRICHMENT_PROMPT,
        # Social media risk analysis prompts
        "analyze_company_social_media_risk": ANALYZE_COMPANY_SOCIAL_MEDIA_RISK_PROMPT,
        "analyze_candidate_social_media_risk": ANALYZE_CANDIDATE_SOCIAL_MEDIA_RISK_PROMPT
    }
    
    return prompts.get(prompt_type, "")

