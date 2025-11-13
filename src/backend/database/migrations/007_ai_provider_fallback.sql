-- Migration: Update AI provider settings to support fallback chain
-- Description: Changes from single provider to ordered list of provider/model combinations
-- Author: System
-- Date: 2025-11-13

-- Update app_settings to store fallback chain as JSON
-- The setting_value will be a JSON array like:
-- [
--   {"provider": "gemini", "model": "gemini-2.5-flash-lite", "order": 1},
--   {"provider": "kimi", "model": "kimi-k2-0905", "order": 2},
--   {"provider": "openai", "model": "gpt-4o-mini", "order": 3}
-- ]

-- Update existing default_ai_provider to new format if it exists
DO $$
DECLARE
    current_provider TEXT;
BEGIN
    -- Get current provider
    SELECT setting_value INTO current_provider
    FROM app_settings
    WHERE setting_key = 'default_ai_provider';
    
    -- If exists and is not JSON, convert to new format
    IF current_provider IS NOT NULL AND current_provider NOT LIKE '[%' THEN
        UPDATE app_settings
        SET setting_value = json_build_array(
            json_build_object(
                'provider', current_provider,
                'model', NULL,
                'order', 1
            )
        )::text,
        description = 'AI provider fallback chain (ordered list of provider/model combinations)'
        WHERE setting_key = 'default_ai_provider';
    END IF;
END $$;

-- Update description
UPDATE app_settings
SET description = 'AI provider fallback chain (ordered list of provider/model combinations)'
WHERE setting_key = 'default_ai_provider';

COMMENT ON TABLE app_settings IS 'Application-wide settings and configuration. default_ai_provider stores JSON array of provider/model fallback chain.';

