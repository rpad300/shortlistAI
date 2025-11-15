-- Migration 003: Enrichment Cache Tables
-- Created: 2025-11-12
-- Purpose: Add tables to cache company and candidate enrichment data from Brave Search API

-- =============================================================================
-- COMPANY ENRICHMENTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS company_enrichments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to companies table (optional - can enrich companies not yet in system)
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Company identification
    company_name TEXT NOT NULL,
    
    -- Enriched data from Brave Search
    website TEXT,
    description TEXT,
    industry TEXT,
    company_size TEXT,
    location TEXT,
    
    -- Social media links (JSONB for flexibility)
    social_media JSONB DEFAULT '{}'::jsonb,
    -- Example: {"linkedin": "https://...", "twitter": "https://...", "facebook": "https://..."}
    
    -- Recent news (JSONB array)
    recent_news JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"title": "...", "url": "...", "description": "...", "age": "..."}]
    
    -- Raw search results for reference (JSONB array)
    raw_results JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    search_query TEXT, -- Query used for enrichment
    result_count INTEGER DEFAULT 0, -- Number of results found
    
    -- Timestamps
    enriched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Validity tracking
    is_valid BOOLEAN DEFAULT TRUE, -- Can be marked invalid if data becomes stale
    expires_at TIMESTAMP WITH TIME ZONE, -- Optional expiration for cache
    
    -- Indexes for performance
    CONSTRAINT unique_company_enrichment UNIQUE (company_name, enriched_at)
);

-- Indexes for company_enrichments
CREATE INDEX idx_company_enrichments_company_id ON company_enrichments(company_id);
CREATE INDEX idx_company_enrichments_company_name ON company_enrichments(company_name);
CREATE INDEX idx_company_enrichments_enriched_at ON company_enrichments(enriched_at DESC);
CREATE INDEX idx_company_enrichments_valid ON company_enrichments(is_valid) WHERE is_valid = TRUE;

-- =============================================================================
-- CANDIDATE ENRICHMENTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS candidate_enrichments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to candidates table
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    
    -- Candidate identification
    candidate_name TEXT NOT NULL,
    
    -- Enriched professional data
    professional_summary TEXT,
    linkedin_profile TEXT,
    github_profile TEXT,
    portfolio_url TEXT,
    
    -- Publications and achievements (JSONB arrays)
    publications JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"title": "...", "url": "...", "description": "..."}]
    
    awards JSONB DEFAULT '[]'::jsonb,
    -- Example: ["Award 1", "Award 2", ...]
    
    -- Raw search results for reference (JSONB array)
    raw_results JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    search_query TEXT, -- Query used for enrichment
    search_keywords TEXT[], -- Keywords used in search
    result_count INTEGER DEFAULT 0, -- Number of results found
    
    -- Timestamps
    enriched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Validity tracking
    is_valid BOOLEAN DEFAULT TRUE, -- Can be marked invalid if data becomes stale
    expires_at TIMESTAMP WITH TIME ZONE, -- Optional expiration for cache
    
    -- Indexes for performance
    CONSTRAINT unique_candidate_enrichment UNIQUE (candidate_id, enriched_at)
);

-- Indexes for candidate_enrichments
CREATE INDEX idx_candidate_enrichments_candidate_id ON candidate_enrichments(candidate_id);
CREATE INDEX idx_candidate_enrichments_candidate_name ON candidate_enrichments(candidate_name);
CREATE INDEX idx_candidate_enrichments_enriched_at ON candidate_enrichments(enriched_at DESC);
CREATE INDEX idx_candidate_enrichments_valid ON candidate_enrichments(is_valid) WHERE is_valid = TRUE;

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Function to get latest valid company enrichment
CREATE OR REPLACE FUNCTION get_latest_company_enrichment(p_company_name TEXT)
RETURNS TABLE (
    id UUID,
    company_id UUID,
    company_name TEXT,
    website TEXT,
    description TEXT,
    industry TEXT,
    company_size TEXT,
    location TEXT,
    social_media JSONB,
    recent_news JSONB,
    enriched_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.company_id,
        ce.company_name,
        ce.website,
        ce.description,
        ce.industry,
        ce.company_size,
        ce.location,
        ce.social_media,
        ce.recent_news,
        ce.enriched_at
    FROM company_enrichments ce
    WHERE 
        ce.company_name ILIKE p_company_name
        AND ce.is_valid = TRUE
        AND (ce.expires_at IS NULL OR ce.expires_at > NOW())
    ORDER BY ce.enriched_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest valid candidate enrichment
CREATE OR REPLACE FUNCTION get_latest_candidate_enrichment(p_candidate_id UUID)
RETURNS TABLE (
    id UUID,
    candidate_id UUID,
    candidate_name TEXT,
    professional_summary TEXT,
    linkedin_profile TEXT,
    github_profile TEXT,
    portfolio_url TEXT,
    publications JSONB,
    awards JSONB,
    enriched_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id,
        ce.candidate_id,
        ce.candidate_name,
        ce.professional_summary,
        ce.linkedin_profile,
        ce.github_profile,
        ce.portfolio_url,
        ce.publications,
        ce.awards,
        ce.enriched_at
    FROM candidate_enrichments ce
    WHERE 
        ce.candidate_id = p_candidate_id
        AND ce.is_valid = TRUE
        AND (ce.expires_at IS NULL OR ce.expires_at > NOW())
    ORDER BY ce.enriched_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to invalidate old enrichments
CREATE OR REPLACE FUNCTION invalidate_old_enrichments()
RETURNS void AS $$
BEGIN
    -- Invalidate company enrichments older than 30 days
    UPDATE company_enrichments
    SET is_valid = FALSE
    WHERE enriched_at < NOW() - INTERVAL '30 days'
    AND is_valid = TRUE;
    
    -- Invalidate candidate enrichments older than 90 days
    UPDATE candidate_enrichments
    SET is_valid = FALSE
    WHERE enriched_at < NOW() - INTERVAL '90 days'
    AND is_valid = TRUE;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on both tables
ALTER TABLE company_enrichments ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidate_enrichments ENABLE ROW LEVEL SECURITY;

-- Policy: Admin users can do everything
CREATE POLICY admin_all_company_enrichments ON company_enrichments
    FOR ALL
    USING (auth.role() = 'authenticated');

CREATE POLICY admin_all_candidate_enrichments ON candidate_enrichments
    FOR ALL
    USING (auth.role() = 'authenticated');

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_enrichment_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_company_enrichments_updated_at
    BEFORE UPDATE ON company_enrichments
    FOR EACH ROW
    EXECUTE FUNCTION update_enrichment_updated_at();

CREATE TRIGGER update_candidate_enrichments_updated_at
    BEFORE UPDATE ON candidate_enrichments
    FOR EACH ROW
    EXECUTE FUNCTION update_enrichment_updated_at();

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE company_enrichments IS 'Cache of enriched company data from Brave Search API';
COMMENT ON TABLE candidate_enrichments IS 'Cache of enriched candidate data from Brave Search API';

COMMENT ON COLUMN company_enrichments.social_media IS 'JSONB object with social media URLs (linkedin, twitter, facebook, etc.)';
COMMENT ON COLUMN company_enrichments.recent_news IS 'JSONB array of recent news articles about the company';
COMMENT ON COLUMN company_enrichments.expires_at IS 'Optional expiration date for cache invalidation';

COMMENT ON COLUMN candidate_enrichments.publications IS 'JSONB array of publications, papers, and articles';
COMMENT ON COLUMN candidate_enrichments.awards IS 'JSONB array of awards and achievements';
COMMENT ON COLUMN candidate_enrichments.search_keywords IS 'Array of keywords used in the search query';

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify tables were created
DO $$
BEGIN
    RAISE NOTICE 'Migration 003 completed successfully!';
    RAISE NOTICE 'Created tables: company_enrichments, candidate_enrichments';
    RAISE NOTICE 'Created helper functions: get_latest_company_enrichment, get_latest_candidate_enrichment, invalidate_old_enrichments';
END $$;





