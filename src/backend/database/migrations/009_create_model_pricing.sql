-- ============================================================================
-- Migration 009: Create Model Pricing Table
-- ============================================================================
-- Create table to store pricing information for AI models from providers
-- This allows dynamic pricing updates from provider APIs
-- ============================================================================

-- Model Pricing table
CREATE TABLE IF NOT EXISTS ai_model_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Provider and model identification
    provider TEXT NOT NULL,  -- 'openai', 'claude', 'gemini', 'kimi', 'minimax'
    model_name TEXT NOT NULL,  -- Full model name (e.g., 'gpt-4o-mini', 'claude-3-5-sonnet-20241022')
    model_display_name TEXT,  -- Human-readable name (e.g., 'GPT-4o Mini')
    
    -- Pricing per 1M tokens (in USD)
    input_price_per_1m NUMERIC(12, 8) NOT NULL,  -- Price per 1M input tokens
    output_price_per_1m NUMERIC(12, 8) NOT NULL,  -- Price per 1M output tokens
    
    -- Pricing type
    pricing_type TEXT NOT NULL DEFAULT 'per_token',  -- 'per_token', 'per_request', 'credit_based'
    per_request_price NUMERIC(12, 8),  -- For credit-based or per-request pricing
    
    -- Model metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    context_window INTEGER,  -- Max context window in tokens
    max_output_tokens INTEGER,  -- Max output tokens
    
    -- Source and update tracking
    source TEXT NOT NULL DEFAULT 'api',  -- 'api', 'manual', 'estimated'
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by TEXT,  -- 'system', 'admin', etc.
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(provider, model_name)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_model_pricing_provider ON ai_model_pricing(provider);
CREATE INDEX IF NOT EXISTS idx_model_pricing_active ON ai_model_pricing(provider, model_name) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_model_pricing_updated ON ai_model_pricing(last_updated_at DESC);

-- Comments
COMMENT ON TABLE ai_model_pricing IS 'Stores pricing information for AI models, fetched from provider APIs or manually configured';
COMMENT ON COLUMN ai_model_pricing.provider IS 'AI provider name: openai, claude, gemini, kimi, minimax';
COMMENT ON COLUMN ai_model_pricing.model_name IS 'Full model identifier as used by the provider API';
COMMENT ON COLUMN ai_model_pricing.input_price_per_1m IS 'Price in USD per 1 million input tokens';
COMMENT ON COLUMN ai_model_pricing.output_price_per_1m IS 'Price in USD per 1 million output tokens';
COMMENT ON COLUMN ai_model_pricing.pricing_type IS 'Type of pricing: per_token (standard), per_request, credit_based';
COMMENT ON COLUMN ai_model_pricing.source IS 'Source of pricing data: api (from provider API), manual (admin configured), estimated';

