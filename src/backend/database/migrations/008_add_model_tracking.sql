-- ============================================================================
-- Migration 008: Add Model Tracking to Analyses
-- ============================================================================
-- Add model column to analyses table to track which specific AI model was used
-- This is important for accurate cost calculation as different models have different pricing
-- ============================================================================

-- Add model column to analyses table
ALTER TABLE analyses 
ADD COLUMN IF NOT EXISTS model TEXT;

-- Add index for model-based queries
CREATE INDEX IF NOT EXISTS idx_analyses_model ON analyses(model) WHERE model IS NOT NULL;

-- Add comment
COMMENT ON COLUMN analyses.model IS 'Specific AI model used for this analysis (e.g., gpt-4o-mini, gemini-2.0-flash-exp, claude-3-5-sonnet-20241022)';

