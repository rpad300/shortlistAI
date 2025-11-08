-- Migration: 001_initial_schema
-- Description: Create initial database schema for CV Analysis Platform
-- Date: 2025-01-08

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- =============================================================================
-- CORE BUSINESS ENTITIES
-- =============================================================================

-- Candidates table
-- Stores candidate information, main entity for deduplication
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    phone TEXT,
    country TEXT,
    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
    consent_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for candidates
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_country ON candidates(country) WHERE country IS NOT NULL;
CREATE INDEX idx_candidates_created_at ON candidates(created_at DESC);

-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_companies_name ON companies(name);

-- Interviewers table
CREATE TABLE interviewers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    country TEXT,
    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
    consent_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interviewers_email ON interviewers(email);
CREATE INDEX idx_interviewers_company_id ON interviewers(company_id) WHERE company_id IS NOT NULL;

-- Job postings table
CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    interviewer_id UUID REFERENCES interviewers(id) ON DELETE SET NULL,
    candidate_id UUID REFERENCES candidates(id) ON DELETE SET NULL,
    raw_text TEXT NOT NULL,
    file_url TEXT,
    structured_data JSONB,
    key_points TEXT,
    weights JSONB,
    hard_blockers JSONB,
    language TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Ensure job posting belongs to either interviewer OR candidate, not both
    CONSTRAINT check_job_posting_owner CHECK (
        (interviewer_id IS NOT NULL AND candidate_id IS NULL) OR
        (interviewer_id IS NULL AND candidate_id IS NOT NULL)
    )
);

CREATE INDEX idx_job_postings_company_id ON job_postings(company_id) WHERE company_id IS NOT NULL;
CREATE INDEX idx_job_postings_interviewer_id ON job_postings(interviewer_id) WHERE interviewer_id IS NOT NULL;
CREATE INDEX idx_job_postings_candidate_id ON job_postings(candidate_id) WHERE candidate_id IS NOT NULL;
CREATE INDEX idx_job_postings_created_at ON job_postings(created_at DESC);

-- CVs table
CREATE TABLE cvs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    extracted_text TEXT,
    structured_data JSONB,
    language TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    uploaded_by_flow TEXT NOT NULL CHECK (uploaded_by_flow IN ('interviewer', 'candidate')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cvs_candidate_id ON cvs(candidate_id);
CREATE INDEX idx_cvs_candidate_version ON cvs(candidate_id, version DESC);
CREATE INDEX idx_cvs_created_at ON cvs(created_at DESC);

-- Analyses table
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mode TEXT NOT NULL CHECK (mode IN ('interviewer', 'candidate')),
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    cv_id UUID NOT NULL REFERENCES cvs(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    prompt_id UUID, -- Will be FK once ai_prompts table is created
    provider TEXT NOT NULL,
    categories JSONB NOT NULL,
    global_score NUMERIC(3, 2),
    strengths JSONB,
    risks JSONB,
    questions JSONB,
    intro_pitch TEXT,
    hard_blocker_flags JSONB,
    language TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analyses_mode ON analyses(mode);
CREATE INDEX idx_analyses_job_posting_id ON analyses(job_posting_id);
CREATE INDEX idx_analyses_candidate_id ON analyses(candidate_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX idx_analyses_provider ON analyses(provider);

-- =============================================================================
-- CONFIGURATION TABLES
-- =============================================================================

-- AI Providers table
CREATE TABLE ai_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE, -- gemini, openai, claude, kimi, minimax
    api_key_encrypted TEXT, -- Encrypted API key
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    config JSONB, -- Provider-specific configuration
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_providers_name ON ai_providers(name);
CREATE INDEX idx_ai_providers_active ON ai_providers(is_active) WHERE is_active = TRUE;

-- AI Prompts table
CREATE TABLE ai_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    prompt_type TEXT NOT NULL, -- cv_extraction, job_posting_normalization, interviewer_analysis, etc.
    provider_name TEXT NOT NULL,
    template_content TEXT NOT NULL,
    response_language_rule TEXT, -- use_ui_language, always_english, etc.
    expected_response_structure JSONB,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(prompt_type, version)
);

CREATE INDEX idx_ai_prompts_type ON ai_prompts(prompt_type);
CREATE INDEX idx_ai_prompts_active ON ai_prompts(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_ai_prompts_type_active ON ai_prompts(prompt_type, is_active) WHERE is_active = TRUE;

-- Add FK constraint to analyses now that ai_prompts exists
ALTER TABLE analyses
    ADD CONSTRAINT fk_analyses_prompt 
    FOREIGN KEY (prompt_id) 
    REFERENCES ai_prompts(id) 
    ON DELETE RESTRICT;

-- Translations table
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key TEXT NOT NULL UNIQUE,
    en TEXT NOT NULL, -- Base language
    pt TEXT,
    fr TEXT,
    es TEXT,
    category TEXT NOT NULL, -- ui, email, legal, help
    auto_translated JSONB DEFAULT '{"pt": false, "fr": false, "es": false}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_translations_key ON translations(key);
CREATE INDEX idx_translations_category ON translations(category);

-- Legal Content table
CREATE TABLE legal_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type TEXT NOT NULL UNIQUE, -- terms, privacy, cookie_policy
    en TEXT NOT NULL,
    pt TEXT,
    fr TEXT,
    es TEXT,
    version TEXT NOT NULL,
    auto_translated JSONB DEFAULT '{"pt": false, "fr": false, "es": false}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_legal_content_type ON legal_content(content_type);

-- =============================================================================
-- AUDIT AND LOGS
-- =============================================================================

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_type TEXT NOT NULL, -- admin, interviewer, candidate, system
    user_id UUID,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_type ON audit_logs(user_type);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id) WHERE entity_type IS NOT NULL;

-- AI Usage logs table
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider TEXT NOT NULL,
    prompt_type TEXT NOT NULL,
    model_name TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd NUMERIC(10, 6),
    latency_ms INTEGER,
    status TEXT NOT NULL, -- success, error, timeout
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_usage_logs_provider ON ai_usage_logs(provider);
CREATE INDEX idx_ai_usage_logs_prompt_type ON ai_usage_logs(prompt_type);
CREATE INDEX idx_ai_usage_logs_created_at ON ai_usage_logs(created_at DESC);
CREATE INDEX idx_ai_usage_logs_status ON ai_usage_logs(status);

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update_updated_at trigger to all tables with updated_at column
CREATE TRIGGER update_candidates_updated_at BEFORE UPDATE ON candidates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviewers_updated_at BEFORE UPDATE ON interviewers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_postings_updated_at BEFORE UPDATE ON job_postings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cvs_updated_at BEFORE UPDATE ON cvs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_providers_updated_at BEFORE UPDATE ON ai_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_prompts_updated_at BEFORE UPDATE ON ai_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_translations_updated_at BEFORE UPDATE ON translations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_legal_content_updated_at BEFORE UPDATE ON legal_content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all sensitive tables
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviewers ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;
ALTER TABLE cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE translations ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_usage_logs ENABLE ROW LEVEL SECURITY;

-- Create policies for Admin access (using service role)
-- Note: In production, you would have a proper auth system
-- For now, service role key will be used for Admin operations

-- Public read access for translations and legal content
CREATE POLICY "Public can read translations" ON translations
    FOR SELECT USING (TRUE);

CREATE POLICY "Public can read legal content" ON legal_content
    FOR SELECT USING (TRUE);

-- All other tables: Admin only (service role)
-- Public flows will use backend API with service role key for specific operations
-- No direct database access from public users

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE candidates IS 'Stores candidate information for deduplication and headhunting database';
COMMENT ON TABLE companies IS 'Stores company information from interviewer flows';
COMMENT ON TABLE interviewers IS 'Stores interviewer contact details';
COMMENT ON TABLE job_postings IS 'Stores job posting text, files, and structured data';
COMMENT ON TABLE cvs IS 'Stores CV files, extracted text, and structured data';
COMMENT ON TABLE analyses IS 'Stores AI analysis results for both interviewer and candidate modes';
COMMENT ON TABLE ai_providers IS 'Configuration for AI service providers';
COMMENT ON TABLE ai_prompts IS 'Versioned AI prompt templates';
COMMENT ON TABLE translations IS 'Multi-language UI and content translations';
COMMENT ON TABLE legal_content IS 'Legal documents in multiple languages';
COMMENT ON TABLE audit_logs IS 'Audit trail for all user actions';
COMMENT ON TABLE ai_usage_logs IS 'Tracking for AI API usage, cost, and performance';

