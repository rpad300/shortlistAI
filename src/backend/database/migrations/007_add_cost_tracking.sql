-- ============================================================================
-- Migration 007: Add Cost Tracking to Analyses
-- ============================================================================
-- Add input_cost, output_cost, and total_cost columns to analyses table
-- to persist calculated costs based on token usage
-- ============================================================================

-- Add cost tracking columns to analyses table
ALTER TABLE analyses 
ADD COLUMN IF NOT EXISTS input_cost NUMERIC(12, 8),
ADD COLUMN IF NOT EXISTS output_cost NUMERIC(12, 8),
ADD COLUMN IF NOT EXISTS total_cost NUMERIC(12, 8);

-- Add index for cost-based queries
CREATE INDEX IF NOT EXISTS idx_analyses_costs ON analyses(total_cost) WHERE total_cost IS NOT NULL;

-- Add comments
COMMENT ON COLUMN analyses.input_cost IS 'Cost in USD for input/prompt tokens used in this analysis';
COMMENT ON COLUMN analyses.output_cost IS 'Cost in USD for output/completion tokens generated in this analysis';
COMMENT ON COLUMN analyses.total_cost IS 'Total cost in USD for this analysis (input_cost + output_cost)';

