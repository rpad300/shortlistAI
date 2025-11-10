-- ============================================================================
-- Migration 002: Analysis Reports
-- ============================================================================
-- Create table to persist complete interviewer analysis reports
-- Allows continuing reports and adding more candidates over time
-- ============================================================================

-- Analysis Reports table
CREATE TABLE IF NOT EXISTS analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Report identifier (user-friendly, unique)
    report_code VARCHAR(50) UNIQUE NOT NULL,
    
    -- References
    interviewer_id UUID NOT NULL REFERENCES interviewers(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    
    -- Report metadata
    title VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    language VARCHAR(10) DEFAULT 'en',
    
    -- Evaluation criteria (from Step 4)
    weights JSONB NOT NULL,  -- {"technical_skills": 50, "experience": 30, ...}
    hard_blockers JSONB,     -- ["Must have X", "Must have Y"]
    nice_to_have JSONB,      -- ["Preferred Z"]
    
    -- Job context (from Steps 2 & 3)
    key_points TEXT,         -- User-edited key requirements
    structured_job_posting JSONB,  -- AI-extracted job posting structure
    
    -- AI-generated insights
    executive_recommendation JSONB,  -- AI executive summary
    
    -- Statistics
    total_candidates INTEGER DEFAULT 0,
    analyzed_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for fast lookup by code
CREATE INDEX IF NOT EXISTS idx_analysis_reports_code ON analysis_reports(report_code);

-- Create index for interviewer lookup
CREATE INDEX IF NOT EXISTS idx_analysis_reports_interviewer ON analysis_reports(interviewer_id);

-- Create index for company lookup
CREATE INDEX IF NOT EXISTS idx_analysis_reports_company ON analysis_reports(company_id);

-- Create index for job posting lookup
CREATE INDEX IF NOT EXISTS idx_analysis_reports_job_posting ON analysis_reports(job_posting_id);


-- ============================================================================
-- Add report_id to analyses table (link analysis to report)
-- ============================================================================

ALTER TABLE analyses 
ADD COLUMN IF NOT EXISTS report_id UUID REFERENCES analysis_reports(id) ON DELETE CASCADE;

-- Create index for report lookup
CREATE INDEX IF NOT EXISTS idx_analyses_report ON analyses(report_id);


-- ============================================================================
-- Trigger to update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_analysis_reports_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_analysis_reports_updated_at
    BEFORE UPDATE ON analysis_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_analysis_reports_updated_at();


-- ============================================================================
-- RLS Policies for analysis_reports
-- ============================================================================

-- Enable RLS
ALTER TABLE analysis_reports ENABLE ROW LEVEL SECURITY;

-- Policy: Interviewers can read their own reports
CREATE POLICY "Interviewers can view own reports"
    ON analysis_reports
    FOR SELECT
    USING (auth.uid() = interviewer_id);

-- Policy: Interviewers can create reports
CREATE POLICY "Interviewers can create reports"
    ON analysis_reports
    FOR INSERT
    WITH CHECK (auth.uid() = interviewer_id);

-- Policy: Interviewers can update their own reports
CREATE POLICY "Interviewers can update own reports"
    ON analysis_reports
    FOR UPDATE
    USING (auth.uid() = interviewer_id);

-- Policy: Service role has full access (for backend operations)
CREATE POLICY "Service role has full access to reports"
    ON analysis_reports
    FOR ALL
    USING (auth.role() = 'service_role');


-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE analysis_reports IS 'Persistent analysis reports that group multiple candidate analyses';
COMMENT ON COLUMN analysis_reports.report_code IS 'User-friendly unique code for the report (e.g., REP-20250109-ABC123)';
COMMENT ON COLUMN analysis_reports.weights IS 'Category weights used for scoring (e.g., {"technical_skills": 50})';
COMMENT ON COLUMN analysis_reports.hard_blockers IS 'Mandatory requirements that candidates must meet';
COMMENT ON COLUMN analysis_reports.executive_recommendation IS 'AI-generated executive summary and recommendation';
COMMENT ON COLUMN analysis_reports.total_candidates IS 'Number of candidates analyzed in this report';

