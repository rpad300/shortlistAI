-- Migration: 010_chatbot_schema
-- Description: Create database schema for Chatbot CV Preparation feature
-- Date: 2025-01-08
-- 
-- This migration creates tables for the conversational chatbot feature
-- that guides candidates through CV preparation for specific job opportunities.
-- All tables are separate from existing flows to avoid interference.

-- =============================================================================
-- CHATBOT SESSION AND MESSAGES
-- =============================================================================

-- Chatbot sessions table
-- Stores conversation sessions for the chatbot CV preparation flow
CREATE TABLE chatbot_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    -- Session state
    current_step TEXT NOT NULL DEFAULT 'welcome',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    language TEXT NOT NULL DEFAULT 'en',
    
    -- Collected data (JSONB for flexibility)
    profile_data JSONB DEFAULT '{}',
    cv_data JSONB DEFAULT '{}',
    job_opportunity_data JSONB DEFAULT '{}',
    digital_footprint_data JSONB DEFAULT '{}',
    additional_questions_data JSONB DEFAULT '{}',
    generated_cv_data JSONB DEFAULT '{}',
    interview_prep_data JSONB DEFAULT '{}',
    
    -- Metadata
    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
    consent_timestamp TIMESTAMPTZ,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chatbot_sessions_candidate_id ON chatbot_sessions(candidate_id);
CREATE INDEX idx_chatbot_sessions_status ON chatbot_sessions(status);
CREATE INDEX idx_chatbot_sessions_current_step ON chatbot_sessions(current_step);
CREATE INDEX idx_chatbot_sessions_created_at ON chatbot_sessions(created_at DESC);

-- Chatbot messages table
-- Stores all messages in the conversation (both user and bot)
CREATE TABLE chatbot_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chatbot_sessions(id) ON DELETE CASCADE,
    
    -- Message content
    role TEXT NOT NULL CHECK (role IN ('user', 'bot', 'system')),
    content TEXT NOT NULL,
    message_type TEXT NOT NULL DEFAULT 'text' CHECK (message_type IN ('text', 'file_upload', 'confirmation', 'summary', 'cv_preview', 'recommendation')),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chatbot_messages_session_id ON chatbot_messages(session_id);
CREATE INDEX idx_chatbot_messages_created_at ON chatbot_messages(created_at);
CREATE INDEX idx_chatbot_messages_role ON chatbot_messages(role);

-- =============================================================================
-- CHATBOT DATA AND GENERATED CONTENT
-- =============================================================================

-- Chatbot CV versions table
-- Stores generated CV versions (ATS friendly, human friendly, etc.)
CREATE TABLE chatbot_cv_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chatbot_sessions(id) ON DELETE CASCADE,
    
    -- CV content
    version_type TEXT NOT NULL CHECK (version_type IN ('ats_friendly', 'human_friendly', 'original')),
    cv_content TEXT NOT NULL,
    structured_data JSONB,
    
    -- Analysis
    ats_score INTEGER CHECK (ats_score >= 0 AND ats_score <= 100),
    keyword_match_score INTEGER CHECK (keyword_match_score >= 0 AND keyword_match_score <= 100),
    
    -- Metadata
    language TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chatbot_cv_versions_session_id ON chatbot_cv_versions(session_id);
CREATE INDEX idx_chatbot_cv_versions_version_type ON chatbot_cv_versions(version_type);

-- Chatbot job opportunities table
-- Stores job opportunities analyzed in chatbot sessions
CREATE TABLE chatbot_job_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chatbot_sessions(id) ON DELETE CASCADE,
    
    -- Job opportunity data
    raw_text TEXT,
    structured_data JSONB NOT NULL DEFAULT '{}',
    company_name TEXT,
    company_website TEXT,
    company_linkedin TEXT,
    job_title TEXT,
    location TEXT,
    contract_type TEXT,
    
    -- Analysis
    requirements_obligatory JSONB DEFAULT '[]',
    requirements_preferred JSONB DEFAULT '[]',
    hard_skills JSONB DEFAULT '[]',
    soft_skills JSONB DEFAULT '[]',
    culture_keywords JSONB DEFAULT '[]',
    risk_assessment JSONB DEFAULT '{}',
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    
    -- Metadata
    language TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chatbot_job_opportunities_session_id ON chatbot_job_opportunities(session_id);
CREATE INDEX idx_chatbot_job_opportunities_company_name ON chatbot_job_opportunities(company_name) WHERE company_name IS NOT NULL;

-- Chatbot digital footprint analysis table
-- Stores analysis of candidate's digital footprint (LinkedIn, GitHub, etc.)
CREATE TABLE chatbot_digital_footprint (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chatbot_sessions(id) ON DELETE CASCADE,
    
    -- Links provided
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    other_links JSONB DEFAULT '[]',
    
    -- Analysis results
    linkedin_analysis JSONB DEFAULT '{}',
    github_analysis JSONB DEFAULT '{}',
    portfolio_analysis JSONB DEFAULT '{}',
    inconsistencies JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    
    -- Metadata
    analyzed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chatbot_digital_footprint_session_id ON chatbot_digital_footprint(session_id);

-- Chatbot interview preparation table
-- Stores interview preparation materials generated for the candidate
CREATE TABLE chatbot_interview_prep (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chatbot_sessions(id) ON DELETE CASCADE,
    
    -- Preparation content
    likely_questions JSONB DEFAULT '[]',
    suggested_answers JSONB DEFAULT '[]',
    key_stories JSONB DEFAULT '[]',
    preparation_summary TEXT,
    questions_to_ask JSONB DEFAULT '[]',
    
    -- Metadata
    language TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chatbot_interview_prep_session_id ON chatbot_interview_prep(session_id);

-- Chatbot employability score table
-- Stores employability scores and recommendations
CREATE TABLE chatbot_employability_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chatbot_sessions(id) ON DELETE CASCADE,
    
    -- Scores
    overall_score INTEGER NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    technical_skills_score INTEGER CHECK (technical_skills_score >= 0 AND technical_skills_score <= 100),
    experience_score INTEGER CHECK (experience_score >= 0 AND experience_score <= 100),
    communication_score INTEGER CHECK (communication_score >= 0 AND communication_score <= 100),
    
    -- Analysis
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    
    -- Metadata
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chatbot_employability_scores_session_id ON chatbot_employability_scores(session_id);
CREATE INDEX idx_chatbot_employability_scores_overall_score ON chatbot_employability_scores(overall_score DESC);

-- =============================================================================
-- RLS POLICIES
-- =============================================================================

-- Enable RLS on all chatbot tables
ALTER TABLE chatbot_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_cv_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_job_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_digital_footprint ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_interview_prep ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_employability_scores ENABLE ROW LEVEL SECURITY;

-- Admin can see all chatbot data
CREATE POLICY "Admin can view all chatbot sessions"
    ON chatbot_sessions FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view all chatbot messages"
    ON chatbot_messages FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view all chatbot CV versions"
    ON chatbot_cv_versions FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view all chatbot job opportunities"
    ON chatbot_job_opportunities FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view all chatbot digital footprint"
    ON chatbot_digital_footprint FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view all chatbot interview prep"
    ON chatbot_interview_prep FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admin can view all chatbot employability scores"
    ON chatbot_employability_scores FOR SELECT
    USING (auth.jwt() ->> 'role' = 'admin');

-- Public users can only access their own sessions (via service role key in backend)
-- The backend will handle access control, so we allow service role to manage all data
CREATE POLICY "Service role can manage all chatbot sessions"
    ON chatbot_sessions FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all chatbot messages"
    ON chatbot_messages FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all chatbot CV versions"
    ON chatbot_cv_versions FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all chatbot job opportunities"
    ON chatbot_job_opportunities FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all chatbot digital footprint"
    ON chatbot_digital_footprint FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all chatbot interview prep"
    ON chatbot_interview_prep FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all chatbot employability scores"
    ON chatbot_employability_scores FOR ALL
    USING (auth.role() = 'service_role');

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Update updated_at timestamp on chatbot_sessions
CREATE OR REPLACE FUNCTION update_chatbot_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_chatbot_sessions_updated_at
    BEFORE UPDATE ON chatbot_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_chatbot_sessions_updated_at();

-- Update updated_at timestamp on chatbot_cv_versions
CREATE OR REPLACE FUNCTION update_chatbot_cv_versions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_chatbot_cv_versions_updated_at
    BEFORE UPDATE ON chatbot_cv_versions
    FOR EACH ROW
    EXECUTE FUNCTION update_chatbot_cv_versions_updated_at();

-- Update updated_at timestamp on chatbot_job_opportunities
CREATE OR REPLACE FUNCTION update_chatbot_job_opportunities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_chatbot_job_opportunities_updated_at
    BEFORE UPDATE ON chatbot_job_opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_chatbot_job_opportunities_updated_at();

-- Update updated_at timestamp on chatbot_digital_footprint
CREATE OR REPLACE FUNCTION update_chatbot_digital_footprint_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_chatbot_digital_footprint_updated_at
    BEFORE UPDATE ON chatbot_digital_footprint
    FOR EACH ROW
    EXECUTE FUNCTION update_chatbot_digital_footprint_updated_at();

-- Update updated_at timestamp on chatbot_interview_prep
CREATE OR REPLACE FUNCTION update_chatbot_interview_prep_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_chatbot_interview_prep_updated_at
    BEFORE UPDATE ON chatbot_interview_prep
    FOR EACH ROW
    EXECUTE FUNCTION update_chatbot_interview_prep_updated_at();

