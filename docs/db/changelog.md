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

