"""
Default AI prompts for the platform.

These are the initial prompt templates used for various AI tasks.
In production, these should be stored in the database and managed through Admin UI.
"""

# CV Extraction Prompt
CV_EXTRACTION_PROMPT = """You are a CV analysis expert. Extract structured information from the following CV text.

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

Job Posting:
{job_posting_text}

Extract and return ONLY valid JSON:
{{
  "title": "Job title",
  "company": "Company name",
  "location": "Location",
  "type": "Full-time/Part-time/Contract",
  "experience_level": "Junior/Mid/Senior",
  "required_skills": ["Skill 1", "Skill 2"],
  "preferred_skills": ["Skill 1", "Skill 2"],
  "responsibilities": ["Responsibility 1", "Responsibility 2"],
  "qualifications": ["Requirement 1", "Requirement 2"],
  "languages": ["Language 1", "Language 2"],
  "salary_range": "If mentioned",
  "benefits": ["Benefit 1", "Benefit 2"]
}}

Return ONLY the JSON."""

# Interviewer Analysis Prompt
INTERVIEWER_ANALYSIS_PROMPT = """You are a professional recruiter analyzing candidates for a job opening.

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

Analyze this candidate and return ONLY valid JSON in {language}:
{{
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
    "Question to assess key skill 1",
    "Question to probe gap or inconsistency",
    "Question about specific experience"
  ],
  "hard_blocker_violations": ["Blocker 1 if violated"],
  "recommendation": "Brief hiring recommendation"
}}

Use scores 1-5 where:
1 = Very weak
2 = Below expectations
3 = Meets basic requirements
4 = Strong fit
5 = Exceptional fit

Return ONLY the JSON in {language}."""

# Candidate Analysis Prompt  
CANDIDATE_ANALYSIS_PROMPT = """You are a career coach helping a candidate prepare for an interview.

Job Posting:
{job_posting}

Candidate CV:
{cv_text}

Analyze the candidate's fit and provide preparation guidance in {language}.

Return ONLY valid JSON:
{{
  "categories": {{
    "technical_skills": 1-5,
    "experience": 1-5,
    "soft_skills": 1-5,
    "languages": 1-5,
    "education": 1-5
  }},
  "strengths": ["Your strength 1", "Your strength 2"],
  "gaps": ["Gap to address 1", "Gap to address 2"],
  "likely_questions": [
    "Question you'll likely be asked 1",
    "Question you'll likely be asked 2",
    "Question you'll likely be asked 3"
  ],
  "intro_pitch": "A 2-3 sentence introduction pitch for you to use at the start of the interview",
  "preparation_tips": [
    "Specific preparation advice 1",
    "Specific preparation advice 2"
  ]
}}

Be supportive and constructive. Return ONLY the JSON in {language}."""

# Translation Prompt
TRANSLATION_PROMPT = """Translate the following text from English to {target_language}.

Maintain the tone, meaning, and structure. For technical or legal terms, use appropriate professional language.

English text:
{text}

Translated {target_language} text:"""


def get_prompt(prompt_type: str) -> str:
    """
    Get prompt template by type.
    
    Args:
        prompt_type: Type of prompt (cv_extraction, job_posting_normalization, etc.)
        
    Returns:
        Prompt template string
    """
    prompts = {
        "cv_extraction": CV_EXTRACTION_PROMPT,
        "job_posting_normalization": JOB_POSTING_NORMALIZATION_PROMPT,
        "interviewer_analysis": INTERVIEWER_ANALYSIS_PROMPT,
        "candidate_analysis": CANDIDATE_ANALYSIS_PROMPT,
        "translation": TRANSLATION_PROMPT
    }
    
    return prompts.get(prompt_type, "")

