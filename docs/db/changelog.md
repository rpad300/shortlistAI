# Database Schema Changelog

This file tracks all schema changes in chronological order.

## Format
Each entry includes:
- Date
- Migration name or identifier
- Description
- Impacted tables

---

## 2025-01-08 - Initial Schema Design

**Migration**: initial_schema_design

**Description**: Designed core database schema for CV Analysis Platform

**Impacted tables**:
- candidates
- companies
- interviewers
- job_postings
- cvs
- analyses

**Notes**:
- Schema designed following Supabase and database role rules
- RLS policies to be implemented
- Migration files to be created in next step
- Additional configuration tables (ai_prompts, ai_providers, translations, legal_content) to be added

---

## 2025-01-08 - Chatbot CV Preparation Schema

**Migration**: 010_chatbot_schema / create_chatbot_schema

**Description**: Created database schema for Chatbot CV Preparation feature. All tables are separate from existing flows to avoid interference.

**Impacted tables**:
- chatbot_sessions
- chatbot_messages
- chatbot_cv_versions
- chatbot_job_opportunities
- chatbot_digital_footprint
- chatbot_interview_prep
- chatbot_employability_scores

**Notes**:
- All tables have RLS enabled
- Service role policies allow backend to manage all data
- Admin policies allow viewing all chatbot data
- Triggers automatically update `updated_at` timestamps
- Separate from existing candidate/interviewer flows

