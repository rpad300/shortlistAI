-- ============================================================================
-- Migration 005: Detailed Analysis Support
-- ============================================================================
-- Add detailed_analysis JSONB column to analyses table to store comprehensive
-- analysis data (SWOT, detailed skills, score breakdown, etc.)
-- ============================================================================

-- Add detailed_analysis column to analyses table
ALTER TABLE analyses 
ADD COLUMN IF NOT EXISTS detailed_analysis JSONB;

-- Create index for JSONB queries on detailed_analysis
CREATE INDEX IF NOT EXISTS idx_analyses_detailed_analysis 
ON analyses USING GIN (detailed_analysis);

-- Add comment
COMMENT ON COLUMN analyses.detailed_analysis IS 
'Comprehensive analysis data including SWOT, detailed technical/soft skills evaluation, score breakdown, professional experience analysis, education assessment, notable achievements, and culture fit assessment';

