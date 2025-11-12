-- Migration: AI Prompts Management System
-- Description: Creates tables for managing AI prompts through the Admin interface
-- Author: System
-- Date: 2025-11-12

-- ============================================================================
-- Table: ai_prompts
-- Purpose: Stores all AI prompt templates used throughout the platform
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_prompts (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Prompt identification
    prompt_key VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Prompt content
    content TEXT NOT NULL,
    
    -- Categorization
    category VARCHAR(50) NOT NULL DEFAULT 'general',
    -- Categories: cv_extraction, job_analysis, candidate_evaluation, translation, reporting, enrichment, other
    
    -- Version control
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_default BOOLEAN NOT NULL DEFAULT false,
    
    -- Variables/placeholders used in this prompt
    -- Stored as JSONB array: ["variable1", "variable2"]
    variables JSONB DEFAULT '[]'::jsonb,
    
    -- Usage metadata
    language VARCHAR(10) DEFAULT 'en',
    -- Language code: en, pt, fr, es (for language-specific prompts)
    
    model_preferences JSONB DEFAULT '{}'::jsonb,
    -- JSON with preferred model settings: {"temperature": 0.7, "max_tokens": 2000, "preferred_provider": "gemini"}
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    -- Performance tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    -- Notes for admins
    admin_notes TEXT
);

-- Create indexes for performance
CREATE INDEX idx_ai_prompts_key ON ai_prompts(prompt_key);
CREATE INDEX idx_ai_prompts_category ON ai_prompts(category);
CREATE INDEX idx_ai_prompts_active ON ai_prompts(is_active) WHERE is_active = true;
CREATE INDEX idx_ai_prompts_version ON ai_prompts(prompt_key, version);
CREATE INDEX idx_ai_prompts_language ON ai_prompts(language);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_ai_prompts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ai_prompts_updated_at
    BEFORE UPDATE ON ai_prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_prompts_updated_at();

-- ============================================================================
-- Table: prompt_versions
-- Purpose: Keeps history of all prompt changes for rollback and auditing
-- ============================================================================

CREATE TABLE IF NOT EXISTS prompt_versions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference to current prompt
    prompt_id UUID NOT NULL REFERENCES ai_prompts(id) ON DELETE CASCADE,
    
    -- Version info
    version INTEGER NOT NULL,
    
    -- Complete snapshot of the prompt at this version
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    model_preferences JSONB DEFAULT '{}'::jsonb,
    
    -- Change tracking
    change_description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    
    -- Make sure we don't have duplicate versions
    UNIQUE(prompt_id, version)
);

-- Create indexes
CREATE INDEX idx_prompt_versions_prompt_id ON prompt_versions(prompt_id);
CREATE INDEX idx_prompt_versions_created_at ON prompt_versions(created_at);

-- ============================================================================
-- Table: prompt_test_results
-- Purpose: Stores test results for prompt quality evaluation
-- ============================================================================

CREATE TABLE IF NOT EXISTS prompt_test_results (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    prompt_id UUID NOT NULL REFERENCES ai_prompts(id) ON DELETE CASCADE,
    
    -- Test info
    test_input JSONB NOT NULL,
    -- Input variables and values used for this test
    
    expected_output TEXT,
    -- What we expect/want from this test (optional)
    
    actual_output TEXT,
    -- What the AI actually returned
    
    -- Evaluation
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- Status: pending, passed, failed, manual_review
    
    quality_score NUMERIC(3, 2),
    -- Score 0.00 to 5.00 (or null if not scored)
    
    evaluation_notes TEXT,
    -- Human or automated evaluation notes
    
    -- Execution details
    provider_used VARCHAR(50),
    model_used VARCHAR(100),
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd NUMERIC(10, 6),
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    
    test_name VARCHAR(255),
    -- Optional name for this test case
    
    is_golden_test BOOLEAN DEFAULT false
    -- Mark important test cases that should always pass
);

-- Create indexes
CREATE INDEX idx_prompt_test_results_prompt_id ON prompt_test_results(prompt_id);
CREATE INDEX idx_prompt_test_results_status ON prompt_test_results(status);
CREATE INDEX idx_prompt_test_results_golden ON prompt_test_results(is_golden_test) WHERE is_golden_test = true;
CREATE INDEX idx_prompt_test_results_created_at ON prompt_test_results(created_at);

-- ============================================================================
-- Add comments for documentation
-- ============================================================================

COMMENT ON TABLE ai_prompts IS 'AI prompt templates managed through Admin interface';
COMMENT ON TABLE prompt_versions IS 'Version history of all prompt changes';
COMMENT ON TABLE prompt_test_results IS 'Test results and quality evaluation for prompts';

COMMENT ON COLUMN ai_prompts.prompt_key IS 'Unique identifier used in code to reference this prompt';
COMMENT ON COLUMN ai_prompts.content IS 'The actual prompt template with {variable} placeholders';
COMMENT ON COLUMN ai_prompts.variables IS 'Array of variable names expected in this prompt';
COMMENT ON COLUMN ai_prompts.model_preferences IS 'Preferred AI model settings for this prompt';
COMMENT ON COLUMN ai_prompts.is_active IS 'Only active prompts are used by the system';
COMMENT ON COLUMN ai_prompts.is_default IS 'Default prompt for this prompt_key (when multiple versions exist)';

-- ============================================================================
-- Row Level Security (RLS)
-- Purpose: Only admins can manage prompts
-- ============================================================================

-- Enable RLS
ALTER TABLE ai_prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_test_results ENABLE ROW LEVEL SECURITY;

-- Policies: For now, we'll add basic policies
-- In production, these should be tied to proper admin authentication

-- Allow all operations for authenticated users (will be refined with admin roles)
CREATE POLICY ai_prompts_all_policy ON ai_prompts
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY prompt_versions_all_policy ON prompt_versions
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY prompt_test_results_all_policy ON prompt_test_results
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Note: In production, replace these policies with proper admin-only access
-- based on auth.jwt() claims or admin_users table

-- ============================================================================
-- End of migration
-- ============================================================================

