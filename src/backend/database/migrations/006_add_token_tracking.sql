-- ============================================================================
-- Migration 006: Add Token Tracking to Analyses
-- ============================================================================
-- Add input_tokens and output_tokens columns to analyses table
-- to track actual token usage for accurate cost calculation
-- ============================================================================

-- Add token tracking columns to analyses table
ALTER TABLE analyses 
ADD COLUMN IF NOT EXISTS input_tokens INTEGER,
ADD COLUMN IF NOT EXISTS output_tokens INTEGER;

-- Add index for token-based queries
CREATE INDEX IF NOT EXISTS idx_analyses_tokens ON analyses(input_tokens, output_tokens) WHERE input_tokens IS NOT NULL;

-- Add comments
COMMENT ON COLUMN analyses.input_tokens IS 'Number of input/prompt tokens used in this analysis';
COMMENT ON COLUMN analyses.output_tokens IS 'Number of output/completion tokens generated in this analysis';

