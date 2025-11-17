-- Migration: 011_structured_enrichment_profiles
-- Description: Create structured enrichment profiles for companies and candidates (for headhunting system)
-- Date: 2025-01-08
-- 
-- This migration creates tables for storing AI-structured enrichment data
-- from Brave Search, organized for a headhunting/recruitment system.
-- Data from Brave Search is structured by AI into JSON before storage.

-- =============================================================================
-- COMPANY PROFILES (Structured for Headhunting)
-- =============================================================================

-- Company profiles table
-- Stores comprehensive, AI-structured company profiles built from Brave Search data
CREATE TABLE company_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Reference to base company (if exists)
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    
    -- Company identification
    company_name TEXT NOT NULL,
    normalized_name TEXT, -- Normalized/standardized name for deduplication
    
    -- Basic information (from AI structuring)
    basic_info JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "website": "...",
    --   "description": "...",
    --   "industry": "...",
    --   "sector": "...",
    --   "company_size": "...", // e.g., "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"
    --   "founded_year": 2020,
    --   "headquarters": {...}, // {"city": "...", "country": "...", "address": "..."}
    --   "employee_count": 150,
    --   "revenue": {...}, // {"currency": "EUR", "amount": 1000000, "period": "annual"}
    --   "legal_status": "...", // "LLC", "Corporation", "Startup", etc.
    --   "funding": [...], // Array of funding rounds
    -- }
    
    -- Contact information
    contact_info JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "website": "...",
    --   "email": "...",
    --   "phone": "...",
    --   "address": {...}, // Full address object
    --   "social_media": {...}, // {"linkedin": "...", "twitter": "...", "facebook": "...", "github": "..."}
    -- }
    
    -- Company culture and values (from AI analysis)
    culture JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "values": [...], // Array of company values
    --   "mission": "...",
    --   "vision": "...",
    --   "culture_keywords": [...], // Keywords describing company culture
    --   "benefits": [...], // Array of benefits/perks
    --   "work_environment": "...", // "remote", "hybrid", "onsite"
    --   "work_life_balance": "...", // AI assessment
    -- }
    
    -- Technologies and stack (for tech companies)
    technologies JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "tech_stack": [...], // Technologies used
    --   "tools": [...], // Development tools, platforms
    --   "methodologies": [...], // Agile, Scrum, etc.
    --   "cloud_providers": [...], // AWS, Azure, GCP
    -- }
    
    -- Recent news and developments
    recent_activity JSONB DEFAULT '[]'::jsonb,
    -- Structure: Array of {
    --   "type": "news" | "funding" | "acquisition" | "product_launch" | "hiring",
    --   "title": "...",
    --   "description": "...",
    --   "url": "...",
    --   "date": "...",
    --   "source": "..."
    -- }
    
    -- Hiring patterns and job postings (aggregated)
    hiring_info JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "active_openings": 0,
    --   "recent_postings": [...], // Array of job titles frequently posted
    --   "hiring_team_size": 0,
    --   "average_time_to_hire": 0, // days
    --   "common_locations": [...], // Locations where they hire
    --   "remote_policy": "...", // "fully_remote", "hybrid", "onsite_only"
    -- }
    
    -- AI-generated summary and insights
    ai_summary TEXT,
    ai_insights JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "growth_trajectory": "...", // "growing", "stable", "declining"
    --   "reputation_score": 0-100,
    --   "key_strengths": [...],
    --   "potential_concerns": [...],
    --   "recommendation_notes": "..."
    -- }
    
    -- Social media and reputation risk analysis
    reputation_risk_analysis JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "overall_risk_score": 0-100, // 0 = no risk, 100 = high risk
    --   "risk_level": "low" | "medium" | "high" | "critical",
    --   "public_incidents": [
    --     {
    --       "type": "scandal" | "lawsuit" | "controversy" | "negative_news" | "social_media_post",
    --       "title": "...",
    --       "description": "...",
    --       "date": "...",
    --       "source": "...",
    --       "url": "...",
    --       "severity": "low" | "medium" | "high",
    --       "relevance": "..." // How relevant for recruitment
    --     }
    --   ],
    --   "social_media_behavior": {
    --     "platform": "linkedin" | "twitter" | "facebook" | "instagram" | "other",
    --     "tone_analysis": "...", // "professional", "casual", "controversial", "polarizing"
    --     "post_frequency": "...", // "low", "moderate", "high"
    --     "controversial_topics": [...], // Topics that might be problematic
    --     "engagement_pattern": "..." // Type of engagement with others
    --   },
    --   "red_flags": [
    --     {
    --       "type": "discrimination" | "harassment" | "unethical_behavior" | "legal_issues" | "reputation_damage",
    --       "description": "...",
    --       "evidence_urls": [...],
    --       "severity": "low" | "medium" | "high" | "critical"
    --     }
    --   ],
    --   "positive_indicators": [
    --     {
    --       "type": "community_engagement" | "thought_leadership" | "awards" | "positive_coverage",
    --       "description": "...",
    --       "evidence_urls": [...]
    --     }
    --   ],
    --   "recommendations": "...", // AI-generated recommendations for hiring team
    --   "last_analyzed": "..." // ISO timestamp
    -- }
    
    -- Raw Brave Search data (for reference and re-processing)
    raw_brave_data JSONB DEFAULT '{}'::jsonb,
    -- Structure: Original data from Brave Search before AI structuring
    
    -- Metadata
    enrichment_source TEXT, -- "brave_search", "manual", "chatbot"
    enriched_by_session_id UUID, -- If enriched via chatbot session
    enriched_by_user_id UUID, -- If manually enriched
    
    -- Quality and validation
    data_quality_score INTEGER CHECK (data_quality_score >= 0 AND data_quality_score <= 100),
    is_verified BOOLEAN DEFAULT FALSE, -- Manually verified
    verification_notes TEXT,
    
    -- Timestamps
    enriched_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Deduplication (via unique index below)
);

CREATE UNIQUE INDEX idx_company_profiles_normalized_name_unique ON company_profiles(normalized_name) WHERE normalized_name IS NOT NULL;
CREATE INDEX idx_company_profiles_company_id ON company_profiles(company_id) WHERE company_id IS NOT NULL;
CREATE INDEX idx_company_profiles_company_name ON company_profiles(company_name);
CREATE INDEX idx_company_profiles_industry ON company_profiles((basic_info->>'industry')) WHERE basic_info->>'industry' IS NOT NULL;
CREATE INDEX idx_company_profiles_enriched_at ON company_profiles(enriched_at DESC);
CREATE INDEX idx_company_profiles_data_quality ON company_profiles(data_quality_score DESC) WHERE data_quality_score IS NOT NULL;

-- =============================================================================
-- JOB POSITIONS (Linked to Companies)
-- =============================================================================

-- Job positions table
-- Stores specific job positions posted by companies (for headhunting matching)
CREATE TABLE company_job_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Company reference
    company_profile_id UUID NOT NULL REFERENCES company_profiles(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    
    -- Job identification
    job_title TEXT NOT NULL,
    normalized_title TEXT, -- Normalized title for deduplication
    
    -- Job details (AI-structured)
    job_details JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "location": {...}, // {"city": "...", "country": "...", "remote": true/false}
    --   "contract_type": "...", // "full_time", "part_time", "contract", "internship"
    --   "salary_range": {...}, // {"min": 0, "max": 0, "currency": "EUR", "period": "annual"}
    --   "experience_level": "...", // "entry", "mid", "senior", "lead", "executive"
    --   "department": "...",
    --   "team_size": 0,
    -- }
    
    -- Requirements (AI-extracted)
    requirements JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "required_skills": [...], // Hard skills
    --   "preferred_skills": [...],
    --   "soft_skills": [...],
    --   "education": [...], // Required education levels/degrees
    --   "certifications": [...],
    --   "years_experience": 0,
    --   "languages": [...], // Required languages
    --   "hard_blockers": [...], // Must-have requirements
    -- }
    
    -- Job description (structured)
    description JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "summary": "...",
    --   "responsibilities": [...],
    --   "requirements_text": "...",
    --   "benefits": [...],
    --   "company_culture_fit": [...], // Culture keywords
    -- }
    
    -- Source information
    source_url TEXT, -- Original job posting URL
    source_type TEXT, -- "job_board", "company_website", "linkedin", "chatbot"
    source_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- AI analysis
    ai_analysis JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "quality_score": 0-100,
    --   "risk_assessment": {...}, // Risk factors
    --   "competitive_advantage": [...], // What makes this position attractive
    --   "red_flags": [...], // Potential concerns
    --   "matching_keywords": [...], // Keywords for candidate matching
    -- }
    
    -- Status and dates
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed', 'filled', 'cancelled')),
    posted_date DATE,
    closing_date DATE,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW() -- When we last saw this position
    
);

CREATE INDEX idx_company_job_positions_company_profile_id ON company_job_positions(company_profile_id);
CREATE INDEX idx_company_job_positions_company_id ON company_job_positions(company_id) WHERE company_id IS NOT NULL;
CREATE INDEX idx_company_job_positions_job_title ON company_job_positions(job_title);
CREATE INDEX idx_company_job_positions_normalized_title ON company_job_positions(normalized_title) WHERE normalized_title IS NOT NULL;
CREATE INDEX idx_company_job_positions_status ON company_job_positions(status) WHERE status = 'active';
CREATE INDEX idx_company_job_positions_posted_date ON company_job_positions(posted_date DESC);
CREATE INDEX idx_company_job_positions_location ON company_job_positions((job_details->'location'->>'country')) WHERE job_details->'location'->>'country' IS NOT NULL;

-- =============================================================================
-- CANDIDATE PROFILES (Structured for Headhunting)
-- =============================================================================

-- Candidate profiles table
-- Stores comprehensive, AI-structured candidate profiles built from CV + Brave Search data
CREATE TABLE candidate_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Reference to base candidate
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    
    -- Candidate identification
    full_name TEXT NOT NULL,
    normalized_name TEXT, -- Normalized name for deduplication
    
    -- Basic information (from AI structuring)
    basic_info JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "email": "...",
    --   "phone": "...",
    --   "location": {...}, // {"city": "...", "country": "...", "address": "..."}
    --   "current_location": "...",
    --   "willing_to_relocate": true/false,
    --   "preferred_locations": [...],
    --   "nationality": "...",
    --   "languages": [...], // Array of {"language": "...", "level": "native|fluent|proficient|basic"}
    --   "date_of_birth": "...", // If available (with consent)
    -- }
    
    -- Contact and online presence
    contact_info JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "email": "...",
    --   "phone": "...",
    --   "social_media": {...}, // {"linkedin": "...", "github": "...", "portfolio": "...", "twitter": "..."}
    --   "professional_websites": [...], // Array of URLs
    -- }
    
    -- Professional summary (AI-generated from CV + Brave Search)
    professional_summary TEXT,
    professional_summary_structured JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "current_role": "...",
    --   "years_experience": 0,
    --   "expertise_areas": [...], // Main areas of expertise
    --   "career_level": "...", // "entry", "mid", "senior", "lead", "executive"
    --   "summary_text": "...", // Full summary text
    -- }
    
    -- Work experience (AI-structured from CV + Brave Search)
    work_experience JSONB DEFAULT '[]'::jsonb,
    -- Structure: Array of {
    --   "company": "...",
    --   "company_normalized": "...",
    --   "company_linkedin": "...",
    --   "position": "...",
    --   "location": "...",
    --   "start_date": "...",
    --   "end_date": "...", // null if current
    --   "is_current": true/false,
    --   "duration_months": 0,
    --   "responsibilities": [...],
    --   "achievements": [...],
    --   "technologies_used": [...],
    --   "team_size": 0,
    --   "reports_to": "...",
    --   "enrichment": {...}, // Additional data from Brave Search about company/role
    -- }
    
    -- Education (AI-structured)
    education JSONB DEFAULT '[]'::jsonb,
    -- Structure: Array of {
    --   "institution": "...",
    --   "degree": "...",
    --   "field_of_study": "...",
    --   "level": "...", // "high_school", "bachelor", "master", "phd", "certification"
    --   "start_date": "...",
    --   "end_date": "...",
    --   "grade": "...",
    --   "honors": [...],
    -- }
    
    -- Skills (AI-extracted and structured)
    skills JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "hard_skills": [...], // Technical skills
    --   "soft_skills": [...],
    --   "languages": [...], // Programming languages
    --   "frameworks": [...],
    --   "tools": [...],
    --   "platforms": [...], // Cloud platforms, etc.
    --   "certifications": [...], // Array of {"name": "...", "issuer": "...", "date": "..."}
    --   "skill_levels": {...}, // {"skill_name": "expert|advanced|intermediate|beginner"}
    -- }
    
    -- Projects and portfolio (from CV + Brave Search)
    projects JSONB DEFAULT '[]'::jsonb,
    -- Structure: Array of {
    --   "name": "...",
    --   "description": "...",
    --   "url": "...",
    --   "technologies": [...],
    --   "date": "...",
    --   "role": "...", // Role in project
    -- }
    
    -- Publications and achievements (from Brave Search)
    publications JSONB DEFAULT '[]'::jsonb,
    -- Structure: Array of {
    --   "title": "...",
    --   "type": "article" | "paper" | "blog_post" | "book" | "presentation",
    --   "url": "...",
    --   "date": "...",
    --   "authors": [...],
    --   "venue": "...",
    -- }
    
    awards JSONB DEFAULT '[]'::jsonb,
    -- Structure: Array of {
    --   "title": "...",
    --   "issuer": "...",
    --   "date": "...",
    --   "description": "...",
    --   "url": "...",
    -- }
    
    -- Career preferences (from chatbot or analysis)
    career_preferences JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "target_roles": [...], // Desired job titles
    --   "target_industries": [...],
    --   "target_companies": [...], // Companies interested in
    --   "salary_expectations": {...}, // {"min": 0, "max": 0, "currency": "EUR"}
    --   "work_environment": "...", // "remote", "hybrid", "onsite"
    --   "preferred_locations": [...],
    --   "availability": "...", // "immediately", "1_month", "3_months", "6_months", "open"
    -- }
    
    -- AI-generated summary and insights
    ai_summary TEXT,
    ai_insights JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "market_value": 0-100, // Estimated market value score
    --   "strengths": [...],
    --   "areas_for_improvement": [...],
    --   "recommendation_notes": "...",
    --   "matching_keywords": [...], // Keywords for job matching
    --   "unique_selling_points": [...],
    -- }
    
    -- Social media and online behavior risk analysis
    social_media_risk_analysis JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "overall_risk_score": 0-100, // 0 = no risk, 100 = high risk
    --   "risk_level": "low" | "medium" | "high" | "critical",
    --   "professional_social_media": {
    --     "linkedin": {
    --       "risk_score": 0-100,
    --       "tone_analysis": "...", // "professional", "casual", "controversial", "polarizing"
    --       "post_frequency": "...", // "low", "moderate", "high"
    --       "content_quality": "...", // "excellent", "good", "average", "poor"
    --       "engagement_pattern": "...", // Type of engagement with others
    --       "controversial_posts": [...], // Array of concerning posts
    --       "positive_indicators": [] // Professional achievements, thought leadership
    --     },
    --     "github": {
    --       "risk_score": 0-100,
    --       "activity_level": "...",
    --       "contribution_quality": "...",
    --       "community_interaction": "...",
    --       "concerning_repositories": [...], // Repos that might be problematic
    --       "positive_indicators": [] // Open source contributions, well-maintained projects
    --     },
    --     "portfolio_website": {
    --       "risk_score": 0-100,
    --       "content_quality": "...",
    --       "professionalism": "...",
    --       "concerning_content": [...],
    --       "positive_indicators": []
    --     }
    --   },
    --   "personal_social_media": {
    --     "twitter": {
    --       "risk_score": 0-100,
    --       "visibility": "public" | "protected" | "private" | "unknown",
    --       "tone_analysis": "...",
    --       "controversial_topics": [...], // Topics that might be problematic
    --       "red_flag_posts": [...], // Posts that could be concerning
    --       "last_analyzed": "..."
    --     },
    --     "facebook": {
    --       "risk_score": 0-100,
    --       "visibility": "public" | "protected" | "private" | "unknown",
    --       "public_activity": "...",
    --       "concerning_content": [...],
    --       "last_analyzed": "..."
    --     },
    --     "instagram": {
    --       "risk_score": 0-100,
    --       "visibility": "public" | "protected" | "private" | "unknown",
    --       "content_analysis": "...",
    --       "concerning_content": [...],
    --       "last_analyzed": "..."
    --     }
    --   },
    --   "public_incidents": [
    --     {
    --       "type": "scandal" | "lawsuit" | "controversy" | "negative_news" | "social_media_post",
    --       "platform": "...",
    --       "title": "...",
    --       "description": "...",
    --       "date": "...",
    --       "source": "...",
    --       "url": "...",
    --       "severity": "low" | "medium" | "high" | "critical",
    --       "relevance": "..." // How relevant for employment/recruitment
    --     }
    --   ],
    --   "red_flags": [
    --     {
    --       "type": "discrimination" | "harassment" | "unethical_behavior" | "legal_issues" | "reputation_damage" | "inappropriate_content",
    --       "description": "...",
    --       "platform": "...",
    --       "evidence_urls": [...],
    --       "severity": "low" | "medium" | "high" | "critical",
    --       "context": "..." // Additional context about the red flag
    --     }
    --   ],
    --   "positive_indicators": [
    --     {
    --       "type": "community_engagement" | "thought_leadership" | "awards" | "positive_coverage" | "professional_achievements",
    --       "description": "...",
    --       "platform": "...",
    --       "evidence_urls": [...],
    --       "impact": "..." // How positive this is for reputation
    --     }
    --   ],
    --   "recommendations": "...", // AI-generated recommendations for hiring team
    --   "privacy_notes": "...", // Notes about privacy settings and visibility
    --   "last_analyzed": "..." // ISO timestamp
    -- }
    
    -- Raw Brave Search data (for reference)
    raw_brave_data JSONB DEFAULT '{}'::jsonb,
    -- Structure: Original data from Brave Search before AI structuring
    
    -- Source CV data (reference)
    source_cv_id UUID REFERENCES cvs(id) ON DELETE SET NULL,
    source_session_id UUID, -- If created via chatbot session
    
    -- Metadata
    enrichment_source TEXT, -- "brave_search", "cv_upload", "chatbot", "manual"
    data_quality_score INTEGER CHECK (data_quality_score >= 0 AND data_quality_score <= 100),
    is_verified BOOLEAN DEFAULT FALSE, -- Manually verified
    verification_notes TEXT,
    
    -- Timestamps
    enriched_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Ensure one profile per candidate (or allow multiple versions?)
    CONSTRAINT unique_candidate_profile UNIQUE (candidate_id)
);

CREATE INDEX idx_candidate_profiles_candidate_id ON candidate_profiles(candidate_id);
CREATE INDEX idx_candidate_profiles_full_name ON candidate_profiles(full_name);
CREATE INDEX idx_candidate_profiles_normalized_name ON candidate_profiles(normalized_name) WHERE normalized_name IS NOT NULL;
CREATE INDEX idx_candidate_profiles_email ON candidate_profiles((basic_info->>'email')) WHERE basic_info->>'email' IS NOT NULL;
CREATE INDEX idx_candidate_profiles_location ON candidate_profiles((basic_info->'location'->>'country')) WHERE basic_info->'location'->>'country' IS NOT NULL;
CREATE INDEX idx_candidate_profiles_enriched_at ON candidate_profiles(enriched_at DESC);
CREATE INDEX idx_candidate_profiles_data_quality ON candidate_profiles(data_quality_score DESC) WHERE data_quality_score IS NOT NULL;

-- GIN indexes for JSONB fields (for efficient searching)
CREATE INDEX idx_candidate_profiles_skills_gin ON candidate_profiles USING GIN (skills);
CREATE INDEX idx_candidate_profiles_work_experience_gin ON candidate_profiles USING GIN (work_experience);
CREATE INDEX idx_candidate_profiles_preferences_gin ON candidate_profiles USING GIN (career_preferences);

-- =============================================================================
-- RLS POLICIES
-- =============================================================================

-- Enable RLS on all new tables
ALTER TABLE company_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_job_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidate_profiles ENABLE ROW LEVEL SECURITY;

-- Service role can manage all data (backend handles access control)
CREATE POLICY "Service role can manage company profiles" ON company_profiles
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage job positions" ON company_job_positions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage candidate profiles" ON candidate_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Admin can view all
CREATE POLICY "Admin can view company profiles" ON company_profiles
    FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view job positions" ON company_job_positions
    FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view candidate profiles" ON candidate_profiles
    FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Update updated_at timestamps
CREATE OR REPLACE FUNCTION update_profile_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_company_profiles_updated_at
    BEFORE UPDATE ON company_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profile_updated_at();

CREATE TRIGGER trigger_company_job_positions_updated_at
    BEFORE UPDATE ON company_job_positions
    FOR EACH ROW
    EXECUTE FUNCTION update_profile_updated_at();

CREATE TRIGGER trigger_candidate_profiles_updated_at
    BEFORE UPDATE ON candidate_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profile_updated_at();

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE company_profiles IS 'Structured company profiles built from Brave Search enrichment data, AI-structured for headhunting system';
COMMENT ON TABLE company_job_positions IS 'Job positions posted by companies, linked to company profiles for matching';
COMMENT ON TABLE candidate_profiles IS 'Structured candidate profiles built from CV + Brave Search enrichment data, AI-structured for headhunting system';

COMMENT ON COLUMN company_profiles.basic_info IS 'AI-structured basic company information (industry, size, location, etc.)';
COMMENT ON COLUMN company_profiles.raw_brave_data IS 'Original Brave Search data before AI structuring (for reference/re-processing)';
COMMENT ON COLUMN candidate_profiles.basic_info IS 'AI-structured basic candidate information (contact, location, languages, etc.)';
COMMENT ON COLUMN candidate_profiles.raw_brave_data IS 'Original Brave Search data before AI structuring (for reference/re-processing)';

