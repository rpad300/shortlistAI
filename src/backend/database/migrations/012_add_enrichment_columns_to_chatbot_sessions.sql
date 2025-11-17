-- Migration: 012_add_enrichment_columns_to_chatbot_sessions
-- Description: Add candidate_enrichment and companies_enrichment columns to chatbot_sessions
-- Date: 2025-01-16
-- 
-- This migration adds JSONB columns to store enriched candidate and company data
-- from Brave Search API integration.

-- Add candidate enrichment column to store enriched candidate data
ALTER TABLE chatbot_sessions
ADD COLUMN IF NOT EXISTS candidate_enrichment JSONB DEFAULT '{}';

-- Add companies enrichment column to store enriched company data
ALTER TABLE chatbot_sessions
ADD COLUMN IF NOT EXISTS companies_enrichment JSONB DEFAULT '{}';

-- Add index on candidate_enrichment for faster queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_chatbot_sessions_candidate_enrichment 
ON chatbot_sessions USING GIN (candidate_enrichment);

-- Add index on companies_enrichment for faster queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_chatbot_sessions_companies_enrichment 
ON chatbot_sessions USING GIN (companies_enrichment);

