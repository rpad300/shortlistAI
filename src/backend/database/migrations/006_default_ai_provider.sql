-- Migration: Add default AI provider configuration
-- Description: Stores the default AI provider preference in the database
-- Author: System
-- Date: 2025-11-13

-- Create table for application settings
CREATE TABLE IF NOT EXISTS app_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_app_settings_key ON app_settings(setting_key);

-- Insert default AI provider setting (if not exists)
INSERT INTO app_settings (setting_key, setting_value, description)
VALUES ('default_ai_provider', 'gemini', 'Default AI provider to use for analysis (gemini, openai, claude, kimi, minimax)')
ON CONFLICT (setting_key) DO NOTHING;

-- Add trigger to update updated_at
CREATE TRIGGER update_app_settings_updated_at
    BEFORE UPDATE ON app_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE app_settings ENABLE ROW LEVEL SECURITY;

-- Policy: Only authenticated admins can read/write settings
CREATE POLICY app_settings_admin_policy ON app_settings
    FOR ALL
    USING (auth.role() = 'authenticated');

COMMENT ON TABLE app_settings IS 'Application-wide settings and configuration';

