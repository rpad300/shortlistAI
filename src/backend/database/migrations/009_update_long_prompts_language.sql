-- Migration: Update long prompts with explicit language instructions
-- Description: Updates interviewer_analysis, candidate_analysis, and executive_recommendation prompts
-- Author: System
-- Date: 2025-01-15

-- Note: Due to the length of these prompts, we'll use a Python script to update them
-- This migration file documents the change but the actual update will be done via script

COMMENT ON TABLE ai_prompts IS 'AI prompts with explicit language instructions. All prompts now include "IMPORTANT: You must respond in {language}" at the beginning. The prompts interviewer_analysis, candidate_analysis, and executive_recommendation have been updated with version 4.';

