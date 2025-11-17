# Database Tables Documentation

This file documents all tables in the CV Analysis Platform database following the per-table minimum documentation standard.

## Table: candidates

### Purpose
Stores core information about candidates who have used the platform (either through Candidate flow or via CV upload in Interviewer flow). Acts as the central entity for deduplication and headhunting database.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `email` (text, not null) – Candidate email, main deduplication key
- `name` (text, not null) – Candidate full name
- `phone` (text, nullable) – Contact phone number
- `country` (text, nullable) – Country of residence
- `consent_given` (boolean, not null, default false) – Whether candidate gave explicit consent
- `consent_timestamp` (timestamptz, nullable) – When consent was given
- `created_at` (timestamptz, not null, default now()) – Record creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Unique: email (for deduplication)

### Indexes
- `idx_candidates_email`: (email). Supports candidate lookup and deduplication.
- `idx_candidates_country`: (country). Supports filtering for headhunting.

### Relationships
- Candidates have many CVs through `cvs.candidate_id`
- Candidates have many analyses through `analyses.candidate_id`

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can see all records
  - Public users cannot query this table directly
- Notes: Contains personal data. RLS is mandatory.

### Typical usage
- Deduplicate candidate by email before creating new record
- Link new CV to existing candidate profile
- Search candidates for headhunting (Admin only)

### Business rules
- Email must be unique across all candidates
- Candidates cannot be hard deleted in prod; use soft delete or retention policy
- Consent must be recorded before storing candidate data

---

## Table: companies

### Purpose
Stores company information from interviewers using the platform. Used for organizing job postings and for future B2B features.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `name` (text, not null) – Company name
- `created_at` (timestamptz, not null, default now()) – Record creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id

### Indexes
- `idx_companies_name`: (name). Supports search and filtering.

### Relationships
- Companies have many interviewers through `interviewers.company_id`
- Companies have many job postings through `job_postings.company_id`

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can see all records
- Notes: Business data, not highly sensitive but still protected.

### Typical usage
- Associate interviewer with company
- Group job postings by company
- Future: company dashboards and analytics

### Business rules
- Company name is optional in interviewer flow (can be null initially)
- Admin can manually create or merge companies

---

## Table: interviewers

### Purpose
Stores contact information of people using the interviewer flow. Links to companies and job postings.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `company_id` (uuid, nullable) – Reference to companies table
- `name` (text, not null) – Interviewer full name
- `email` (text, not null) – Interviewer email
- `phone` (text, nullable) – Interviewer phone
- `country` (text, nullable) – Interviewer country
- `consent_given` (boolean, not null, default false) – Whether consent was given
- `consent_timestamp` (timestamptz, nullable) – When consent was given
- `created_at` (timestamptz, not null, default now()) – Record creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign keys:
  - company_id → companies.id (ON DELETE SET NULL)

### Indexes
- `idx_interviewers_email`: (email). Supports lookup.
- `idx_interviewers_company_id`: (company_id). Supports filtering by company.

### Relationships
- Interviewer belongs to one company (optional)
- Interviewer has many job postings through `job_postings.interviewer_id`

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can see all records
- Notes: Contains personal contact information.

### Typical usage
- Record interviewer details from identification form
- Link job postings to interviewer
- Contact interviewer for follow-up

### Business rules
- Email should be unique per interviewer (soft constraint, not enforced)
- Consent must be recorded

---

## Table: job_postings

### Purpose
Stores job posting text, files, structured representation, and key points. Reusable across multiple candidate evaluation batches.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `company_id` (uuid, nullable) – Reference to companies table
- `interviewer_id` (uuid, nullable) – Reference to interviewers table (for interviewer flow)
- `candidate_id` (uuid, nullable) – Reference to candidates table (for candidate flow)
- `raw_text` (text, not null) – Raw job posting text
- `file_url` (text, nullable) – URL to uploaded file in Supabase storage
- `structured_data` (jsonb, nullable) – AI-extracted structured representation
- `key_points` (text, nullable) – Interviewer-provided key points
- `weights` (jsonb, nullable) – Category weights defined by interviewer
- `hard_blockers` (jsonb, nullable) – Hard blocker rules
- `language` (text, nullable) – Detected or specified language of posting
- `created_at` (timestamptz, not null, default now()) – Record creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign keys:
  - company_id → companies.id (ON DELETE SET NULL)
  - interviewer_id → interviewers.id (ON DELETE SET NULL)
  - candidate_id → candidates.id (ON DELETE SET NULL)

### Indexes
- `idx_job_postings_company_id`: (company_id). Supports filtering.
- `idx_job_postings_interviewer_id`: (interviewer_id). Supports filtering.
- `idx_job_postings_candidate_id`: (candidate_id). Supports filtering.

### Relationships
- Job posting belongs to one company (optional)
- Job posting belongs to one interviewer (interviewer flow) OR one candidate (candidate flow)
- Job posting has many analyses through `analyses.job_posting_id`

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can see all records
- Notes: Contains job description data, not highly sensitive.

### Typical usage
- Store job posting from interviewer or candidate
- Reuse same posting for multiple CV batches
- Extract structured data using AI

### Business rules
- A job posting can be linked to either an interviewer OR a candidate, not both
- Structured data is generated by AI and stored for performance
- Same posting can be analyzed multiple times with different CVs

---

## Table: cvs

### Purpose
Stores uploaded CV files, extracted text, and structured representation. Links to candidates with versioning support.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `candidate_id` (uuid, not null) – Reference to candidates table
- `file_url` (text, not null) – URL to CV file in Supabase storage
- `extracted_text` (text, nullable) – AI-extracted text from CV
- `structured_data` (jsonb, nullable) – AI-generated structured representation
- `language` (text, nullable) – Detected language of CV
- `version` (integer, not null, default 1) – Version number for this candidate
- `uploaded_by_flow` (text, not null) – 'interviewer' or 'candidate'
- `created_at` (timestamptz, not null, default now()) – Record creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign keys:
  - candidate_id → candidates.id (ON DELETE CASCADE)
- Check constraints:
  - uploaded_by_flow IN ('interviewer', 'candidate')

### Indexes
- `idx_cvs_candidate_id`: (candidate_id). Supports fetching all CVs for a candidate.
- `idx_cvs_candidate_version`: (candidate_id, version). Supports versioning.

### Relationships
- CV belongs to one candidate
- CV has many analyses through `analyses.cv_id`

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can see all records
- Notes: Contains sensitive personal career information.

### Typical usage
- Store CV file and extract text
- Link multiple CV versions to same candidate
- Analyze CV against job posting

### Business rules
- Version number auto-increments for each new CV per candidate
- Extracted text is generated by AI during upload
- CVs are never deleted, only archived or soft deleted

---

## Table: analyses

### Purpose
Stores AI analysis results for both Interviewer and Candidate modes. Links job postings, CVs, prompts, and providers.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `mode` (text, not null) – 'interviewer' or 'candidate'
- `job_posting_id` (uuid, not null) – Reference to job_postings table
- `cv_id` (uuid, not null) – Reference to cvs table
- `candidate_id` (uuid, not null) – Reference to candidates table
- `prompt_id` (uuid, not null) – Reference to ai_prompts table
- `provider` (text, not null) – AI provider used (gemini, openai, claude, kimi, minimax)
- `categories` (jsonb, not null) – Evaluation categories and scores
- `global_score` (numeric, nullable) – Weighted global score (interviewer mode only)
- `strengths` (jsonb, nullable) – Identified strengths
- `risks` (jsonb, nullable) – Identified risks or gaps
- `questions` (jsonb, nullable) – Generated interview questions or preparation questions
- `intro_pitch` (text, nullable) – Intro pitch for candidate mode
- `hard_blocker_flags` (jsonb, nullable) – Hard blocker violations (interviewer mode)
- `language` (text, not null) – Language of AI response
- `created_at` (timestamptz, not null, default now()) – Analysis timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign keys:
  - job_posting_id → job_postings.id (ON DELETE CASCADE)
  - cv_id → cvs.id (ON DELETE CASCADE)
  - candidate_id → candidates.id (ON DELETE CASCADE)
  - prompt_id → ai_prompts.id (ON DELETE RESTRICT)
- Check constraints:
  - mode IN ('interviewer', 'candidate')

### Indexes
- `idx_analyses_mode`: (mode). Supports filtering by mode.
- `idx_analyses_job_posting_id`: (job_posting_id). Supports grouping by job.
- `idx_analyses_candidate_id`: (candidate_id). Supports candidate history.
- `idx_analyses_created_at`: (created_at DESC). Supports recent analyses queries.

### Relationships
- Analysis belongs to one job posting
- Analysis belongs to one CV
- Analysis belongs to one candidate
- Analysis references one AI prompt version

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can see all records
- Notes: Contains AI-generated evaluation data.

### Typical usage
- Store analysis results after AI processing
- Display results to interviewer or candidate
- Review quality and compare prompt versions (Admin)

### Business rules
- Each analysis is immutable after creation
- Prompt version is recorded for traceability
- Global score only exists for interviewer mode
- Language must match user-selected UI language

---

## Table: ai_prompts

### Purpose
Stores all AI prompt templates used throughout the platform. Allows admins to manage and version prompts through the Admin UI without code changes.

### Category
Configuration and metadata

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `prompt_key` (varchar(100), not null, unique) – Unique identifier used in code (e.g., "cv_extraction")
- `name` (varchar(255), not null) – Human-readable name
- `description` (text, nullable) – Purpose and usage notes
- `content` (text, not null) – The actual prompt template with {variable} placeholders
- `category` (varchar(50), not null, default 'general') – Prompt category
- `variables` (jsonb, default '[]') – Array of variable names expected in this prompt
- `language` (varchar(10), default 'en') – Language code (en, pt, fr, es)
- `model_preferences` (jsonb, default '{}') – Preferred AI model settings (temperature, max_tokens, etc.)
- `version` (integer, not null, default 1) – Current version number
- `is_active` (boolean, not null, default true) – Whether this prompt is active
- `is_default` (boolean, not null, default false) – Default version for this prompt_key
- `usage_count` (integer, default 0) – Number of times this prompt has been used
- `last_used_at` (timestamptz, nullable) – Last usage timestamp
- `created_at` (timestamptz, not null, default now()) – Creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp
- `created_by` (varchar(255), nullable) – Admin username who created this
- `updated_by` (varchar(255), nullable) – Admin username who last updated this
- `admin_notes` (text, nullable) – Internal notes for admins

### Keys and constraints
- Primary key: id
- Unique: prompt_key (ensures one prompt per key)
- Auto-update: updated_at via trigger

### Indexes
- `idx_ai_prompts_key`: (prompt_key). Main lookup index.
- `idx_ai_prompts_category`: (category). Supports filtering by category.
- `idx_ai_prompts_active`: (is_active) WHERE is_active = true. Supports active prompts lookup.
- `idx_ai_prompts_version`: (prompt_key, version). Supports version queries.
- `idx_ai_prompts_language`: (language). Supports language filtering.

### Relationships
- Prompts have many versions through `prompt_versions.prompt_id`
- Prompts have many test results through `prompt_test_results.prompt_id`
- Analyses reference prompts for traceability

### RLS and security
- RLS: Enabled
- Policies:
  - All operations allowed (will be refined with proper admin authentication)
- Notes: Admin-only table. Public flows use prompts indirectly through AI service.

### Typical usage
- AI service fetches active default prompt by key and language
- Admin UI displays all prompts with filtering
- Version history is tracked on updates
- Usage statistics help identify most-used prompts

### Business rules
- Each prompt_key should have exactly one default version per language
- Content changes should create new versions (tracked in prompt_versions)
- Inactive prompts fall back to default prompts in code
- Variables array should match placeholders in content
- Temperature in model_preferences should be 0.0-1.0

---

## Table: prompt_versions

### Purpose
Maintains complete version history of all prompt changes for auditing, rollback, and quality tracking.

### Category
Audit or log

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `prompt_id` (uuid, not null, references ai_prompts.id ON DELETE CASCADE) – Reference to current prompt
- `version` (integer, not null) – Version number
- `content` (text, not null) – Complete snapshot of prompt content at this version
- `variables` (jsonb, default '[]') – Variables array at this version
- `model_preferences` (jsonb, default '{}') – Model preferences at this version
- `change_description` (text, nullable) – Description of what changed in this version
- `created_at` (timestamptz, not null, default now()) – When this version was created
- `created_by` (varchar(255), nullable) – Admin who created this version

### Keys and constraints
- Primary key: id
- Foreign key: prompt_id → ai_prompts.id (ON DELETE CASCADE)
- Unique: (prompt_id, version) – Ensures no duplicate version numbers

### Indexes
- `idx_prompt_versions_prompt_id`: (prompt_id). Supports version history lookup.
- `idx_prompt_versions_created_at`: (created_at). Supports chronological queries.

### Relationships
- Each version belongs to one prompt (prompt_id → ai_prompts.id)

### RLS and security
- RLS: Enabled
- Policies:
  - All operations allowed (will be refined)
- Notes: Admin-only table for version history.

### Typical usage
- Automatically created when prompt content is updated
- Admin UI displays version history for a prompt
- Rollback operation retrieves old version content and creates new version
- Audit trail for prompt changes

### Business rules
- Version numbers are sequential integers (1, 2, 3, ...)
- Each content change creates a new version
- Versions are immutable (never updated or deleted)
- change_description should explain what changed
- Versions cascade delete when parent prompt is deleted

---

## Table: prompt_test_results

### Purpose
Stores test results and quality evaluation for prompts, enabling systematic testing and monitoring of prompt performance.

### Category
Audit or log

### Columns
- `id` (uuid, not null, default gen_random_uuid()) – Primary key
- `prompt_id` (uuid, not null, references ai_prompts.id ON DELETE CASCADE) – Reference to tested prompt
- `test_input` (jsonb, not null) – Input variables and values used for this test
- `expected_output` (text, nullable) – What we expect from this test (optional)
- `actual_output` (text, nullable) – What the AI actually returned
- `status` (varchar(20), not null, default 'pending') – Test status: pending, passed, failed, manual_review
- `quality_score` (numeric(3,2), nullable) – Score 0.00 to 5.00 (or null if not scored)
- `evaluation_notes` (text, nullable) – Human or automated evaluation notes
- `provider_used` (varchar(50), nullable) – AI provider used for this test
- `model_used` (varchar(100), nullable) – Model used for this test
- `execution_time_ms` (integer, nullable) – Execution time in milliseconds
- `tokens_used` (integer, nullable) – Tokens consumed by this test
- `cost_usd` (numeric(10,6), nullable) – Cost of this test in USD
- `created_at` (timestamptz, not null, default now()) – Test timestamp
- `created_by` (varchar(255), nullable) – Admin who ran the test
- `test_name` (varchar(255), nullable) – Optional name for this test case
- `is_golden_test` (boolean, default false) – Important test case that should always pass

### Keys and constraints
- Primary key: id
- Foreign key: prompt_id → ai_prompts.id (ON DELETE CASCADE)

### Indexes
- `idx_prompt_test_results_prompt_id`: (prompt_id). Supports test history lookup.
- `idx_prompt_test_results_status`: (status). Supports filtering by status.
- `idx_prompt_test_results_golden`: (is_golden_test) WHERE is_golden_test = true. Golden tests.
- `idx_prompt_test_results_created_at`: (created_at). Chronological queries.

### Relationships
- Each test result belongs to one prompt (prompt_id → ai_prompts.id)

### RLS and security
- RLS: Enabled
- Policies:
  - All operations allowed (will be refined)
- Notes: Admin-only table for testing.

### Typical usage
- Admin runs a test with specific input
- System records actual output, performance metrics, and cost
- Admin reviews and scores the result
- Golden tests are flagged for regression testing
- Performance trends tracked over time

### Business rules
- test_input must be valid JSON with all required variables
- quality_score must be between 0.00 and 5.00
- Golden tests should be run before deploying prompt changes
- Cost tracking helps monitor testing expenses
- Failed golden tests should block deployment

---

## Table: chatbot_sessions

### Purpose
Stores conversation sessions for the Chatbot CV Preparation feature. Each session represents a complete conversational flow where a candidate is guided through CV optimization for a specific job opportunity.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default uuid_generate_v4()) – Primary key
- `candidate_id` (uuid, nullable, references candidates.id ON DELETE CASCADE) – Associated candidate if known
- `current_step` (text, not null, default 'welcome') – Current step in the conversation flow
- `status` (text, not null, default 'active') – Session status: active, completed, abandoned
- `language` (text, not null, default 'en') – Language for conversation
- `profile_data` (jsonb, default '{}') – Collected profile information
- `cv_data` (jsonb, default '{}') – CV information and extracted data
- `job_opportunity_data` (jsonb, default '{}') – Job opportunity information
- `digital_footprint_data` (jsonb, default '{}') – Digital footprint analysis data
- `additional_questions_data` (jsonb, default '{}') – Answers to adaptive questions
- `generated_cv_data` (jsonb, default '{}') – Generated CV versions data
- `interview_prep_data` (jsonb, default '{}') – Interview preparation materials
- `consent_given` (boolean, not null, default false) – Whether consent was given
- `consent_timestamp` (timestamptz, nullable) – When consent was given
- `started_at` (timestamptz, not null, default now()) – Session start timestamp
- `completed_at` (timestamptz, nullable) – Session completion timestamp
- `created_at` (timestamptz, not null, default now()) – Record creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign key: candidate_id → candidates.id (ON DELETE CASCADE)

### Indexes
- `idx_chatbot_sessions_candidate_id`: (candidate_id). Links sessions to candidates.
- `idx_chatbot_sessions_status`: (status). Filters by session status.
- `idx_chatbot_sessions_current_step`: (current_step). Filters by conversation step.
- `idx_chatbot_sessions_created_at`: (created_at DESC). Chronological queries.

### Relationships
- Each session may belong to one candidate (candidate_id → candidates.id)
- Sessions have many messages through `chatbot_messages.session_id`
- Sessions have many CV versions through `chatbot_cv_versions.session_id`
- Sessions have one job opportunity through `chatbot_job_opportunities.session_id`
- Sessions have one digital footprint through `chatbot_digital_footprint.session_id`
- Sessions have one interview prep through `chatbot_interview_prep.session_id`
- Sessions have one employability score through `chatbot_employability_scores.session_id`

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can view all sessions
  - Service role can manage all sessions (backend operations)
- Notes: Contains personal data. RLS is mandatory. Backend handles access control.

### Typical usage
- Create new session when user starts chatbot flow
- Update current_step as conversation progresses
- Store collected data in JSONB fields
- Mark as completed when flow finishes

### Business rules
- All consents must be given before session is created
- current_step must be one of: welcome, profile_collection, cv_upload, job_opportunity, digital_footprint, adaptive_questions, cv_generation, interview_prep, score_and_recommendations, completed
- status must be: active, completed, or abandoned
- Sessions are automatically cleaned up when candidate is deleted (CASCADE)

---

## Table: chatbot_messages

### Purpose
Stores all messages in chatbot conversations, including both user messages and bot responses. Enables conversation history and context maintenance.

### Category
Audit or log

### Columns
- `id` (uuid, not null, default uuid_generate_v4()) – Primary key
- `session_id` (uuid, not null, references chatbot_sessions.id ON DELETE CASCADE) – Parent session
- `role` (text, not null) – Message role: user, bot, or system
- `content` (text, not null) – Message content
- `message_type` (text, not null, default 'text') – Type: text, file_upload, confirmation, summary, cv_preview, recommendation
- `metadata` (jsonb, default '{}') – Additional metadata
- `created_at` (timestamptz, not null, default now()) – Message timestamp

### Keys and constraints
- Primary key: id
- Foreign key: session_id → chatbot_sessions.id (ON DELETE CASCADE)
- Check: role IN ('user', 'bot', 'system')
- Check: message_type IN ('text', 'file_upload', 'confirmation', 'summary', 'cv_preview', 'recommendation')

### Indexes
- `idx_chatbot_messages_session_id`: (session_id). Retrieves all messages for a session.
- `idx_chatbot_messages_created_at`: (created_at). Chronological ordering.
- `idx_chatbot_messages_role`: (role). Filters by message role.

### Relationships
- Each message belongs to one session (session_id → chatbot_sessions.id)

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can view all messages
  - Service role can manage all messages
- Notes: Contains conversation content. RLS is mandatory.

### Typical usage
- Store user input messages
- Store bot responses
- Store system messages (status updates, errors)
- Retrieve conversation history for context

### Business rules
- Messages cannot be updated or deleted (immutable for audit trail)
- Messages cascade delete when session is deleted
- role must be one of: user, bot, system

---

## Table: chatbot_cv_versions

### Purpose
Stores generated CV versions optimized for specific job opportunities. Supports both ATS-friendly and human-friendly versions.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default uuid_generate_v4()) – Primary key
- `session_id` (uuid, not null, references chatbot_sessions.id ON DELETE CASCADE) – Parent session
- `version_type` (text, not null) – Type: ats_friendly, human_friendly, original
- `cv_content` (text, not null) – Full CV content
- `structured_data` (jsonb, nullable) – Structured CV data
- `ats_score` (integer, nullable, check >= 0 AND <= 100) – ATS compatibility score
- `keyword_match_score` (integer, nullable, check >= 0 AND <= 100) – Keyword matching score
- `language` (text, not null, default 'en') – CV language
- `created_at` (timestamptz, not null, default now()) – Creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign key: session_id → chatbot_sessions.id (ON DELETE CASCADE)
- Check: version_type IN ('ats_friendly', 'human_friendly', 'original')
- Check: ats_score >= 0 AND ats_score <= 100
- Check: keyword_match_score >= 0 AND keyword_match_score <= 100

### Indexes
- `idx_chatbot_cv_versions_session_id`: (session_id). Retrieves all CV versions for a session.
- `idx_chatbot_cv_versions_version_type`: (version_type). Filters by version type.

### Relationships
- Each CV version belongs to one session (session_id → chatbot_sessions.id)

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can view all CV versions
  - Service role can manage all CV versions
- Notes: Contains candidate data. RLS is mandatory.

### Typical usage
- Store ATS-friendly CV version
- Store human-friendly CV version
- Store original CV for comparison
- Retrieve best version for candidate

### Business rules
- version_type must be one of: ats_friendly, human_friendly, original
- Scores must be between 0 and 100
- Multiple versions can exist for same session (one per type)

---

## Table: chatbot_job_opportunities

### Purpose
Stores job opportunities analyzed in chatbot sessions. Includes structured extraction of requirements, skills, and risk assessment.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default uuid_generate_v4()) – Primary key
- `session_id` (uuid, not null, references chatbot_sessions.id ON DELETE CASCADE) – Parent session
- `raw_text` (text, nullable) – Original job posting text
- `structured_data` (jsonb, not null, default '{}') – Extracted structured data
- `company_name` (text, nullable) – Company name
- `company_website` (text, nullable) – Company website
- `company_linkedin` (text, nullable) – Company LinkedIn URL
- `job_title` (text, nullable) – Job title
- `location` (text, nullable) – Job location
- `contract_type` (text, nullable) – Contract type (full-time, part-time, etc.)
- `requirements_obligatory` (jsonb, default '[]') – Obligatory requirements list
- `requirements_preferred` (jsonb, default '[]') – Preferred requirements list
- `hard_skills` (jsonb, default '[]') – Required hard skills
- `soft_skills` (jsonb, default '[]') – Required soft skills
- `culture_keywords` (jsonb, default '[]') – Culture and values keywords
- `risk_assessment` (jsonb, default '{}') – Risk assessment analysis
- `quality_score` (integer, nullable, check >= 0 AND <= 100) – Job quality score
- `language` (text, not null, default 'en') – Job posting language
- `created_at` (timestamptz, not null, default now()) – Creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign key: session_id → chatbot_sessions.id (ON DELETE CASCADE)
- Check: quality_score >= 0 AND quality_score <= 100

### Indexes
- `idx_chatbot_job_opportunities_session_id`: (session_id). One opportunity per session.
- `idx_chatbot_job_opportunities_company_name`: (company_name) WHERE company_name IS NOT NULL. Company search.

### Relationships
- Each job opportunity belongs to one session (session_id → chatbot_sessions.id)

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can view all job opportunities
  - Service role can manage all job opportunities
- Notes: Contains business information. RLS enabled.

### Typical usage
- Store job posting after extraction
- Analyze requirements for CV optimization
- Assess job quality and risks
- Extract company information

### Business rules
- One job opportunity per session
- quality_score must be between 0 and 100
- structured_data must always be an object (default '{}')

---

## Table: chatbot_digital_footprint

### Purpose
Stores analysis of candidate's digital footprint from LinkedIn, GitHub, portfolio, and other professional profiles. Identifies inconsistencies and provides recommendations.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default uuid_generate_v4()) – Primary key
- `session_id` (uuid, not null, references chatbot_sessions.id ON DELETE CASCADE) – Parent session
- `linkedin_url` (text, nullable) – LinkedIn profile URL
- `github_url` (text, nullable) – GitHub profile URL
- `portfolio_url` (text, nullable) – Portfolio website URL
- `other_links` (jsonb, default '[]') – Other professional links
- `linkedin_analysis` (jsonb, default '{}') – LinkedIn profile analysis
- `github_analysis` (jsonb, default '{}') – GitHub profile analysis
- `portfolio_analysis` (jsonb, default '{}') – Portfolio analysis
- `inconsistencies` (jsonb, default '[]') – Identified inconsistencies with CV
- `recommendations` (jsonb, default '[]') – Recommendations for improvement
- `analyzed_at` (timestamptz, nullable) – When analysis was performed
- `created_at` (timestamptz, not null, default now()) – Creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign key: session_id → chatbot_sessions.id (ON DELETE CASCADE)

### Indexes
- `idx_chatbot_digital_footprint_session_id`: (session_id). One footprint per session.

### Relationships
- Each digital footprint belongs to one session (session_id → chatbot_sessions.id)

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can view all digital footprints
  - Service role can manage all digital footprints
- Notes: Contains personal data from public profiles. RLS is mandatory.

### Typical usage
- Store links provided by candidate
- Analyze public profiles (LinkedIn, GitHub, portfolio)
- Compare with CV to find inconsistencies
- Generate recommendations

### Business rules
- Only analyzes publicly available information
- Requires explicit consent from candidate
- Inconsistencies are suggestions, not facts

---

## Table: chatbot_interview_prep

### Purpose
Stores interview preparation materials generated for candidates, including likely questions, suggested answers, key stories, and preparation summary.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default uuid_generate_v4()) – Primary key
- `session_id` (uuid, not null, references chatbot_sessions.id ON DELETE CASCADE) – Parent session
- `likely_questions` (jsonb, default '[]') – Predicted interview questions
- `suggested_answers` (jsonb, default '[]') – Suggested answer templates
- `key_stories` (jsonb, default '[]') – Key stories to prepare (STAR format)
- `preparation_summary` (text, nullable) – Summary of preparation materials
- `questions_to_ask` (jsonb, default '[]') – Questions candidate should ask
- `language` (text, not null, default 'en') – Preparation language
- `created_at` (timestamptz, not null, default now()) – Creation timestamp
- `updated_at` (timestamptz, not null, default now()) – Last update timestamp

### Keys and constraints
- Primary key: id
- Foreign key: session_id → chatbot_sessions.id (ON DELETE CASCADE)

### Indexes
- `idx_chatbot_interview_prep_session_id`: (session_id). One prep per session.

### Relationships
- Each interview prep belongs to one session (session_id → chatbot_sessions.id)

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can view all interview prep
  - Service role can manage all interview prep
- Notes: Contains personal preparation data. RLS is mandatory.

### Typical usage
- Generate interview questions based on job and CV
- Provide answer templates using candidate's experience
- Identify key stories from candidate's background
- Create preparation summary

### Business rules
- One interview prep per session
- Questions and answers are suggestions, not guarantees
- Based on job requirements and candidate's CV

---

## Table: chatbot_employability_scores

### Purpose
Stores employability scores and analysis for candidates based on job opportunity fit. Includes breakdown by technical skills, experience, and communication.

### Category
Core business entity

### Columns
- `id` (uuid, not null, default uuid_generate_v4()) – Primary key
- `session_id` (uuid, not null, references chatbot_sessions.id ON DELETE CASCADE) – Parent session
- `overall_score` (integer, not null, check >= 0 AND <= 100) – Overall fit score
- `technical_skills_score` (integer, nullable, check >= 0 AND <= 100) – Technical skills match
- `experience_score` (integer, nullable, check >= 0 AND <= 100) – Experience match
- `communication_score` (integer, nullable, check >= 0 AND <= 100) – Communication/clarity score
- `strengths` (jsonb, default '[]') – List of strengths
- `weaknesses` (jsonb, default '[]') – List of weaknesses
- `recommendations` (jsonb, default '[]') – Recommendations to improve score
- `calculated_at` (timestamptz, not null, default now()) – When score was calculated
- `created_at` (timestamptz, not null, default now()) – Creation timestamp

### Keys and constraints
- Primary key: id
- Foreign key: session_id → chatbot_sessions.id (ON DELETE CASCADE)
- Check: overall_score >= 0 AND overall_score <= 100
- Check: technical_skills_score >= 0 AND technical_skills_score <= 100
- Check: experience_score >= 0 AND experience_score <= 100
- Check: communication_score >= 0 AND communication_score <= 100

### Indexes
- `idx_chatbot_employability_scores_session_id`: (session_id). One score per session.
- `idx_chatbot_employability_scores_overall_score`: (overall_score DESC). Ranking queries.

### Relationships
- Each employability score belongs to one session (session_id → chatbot_sessions.id)

### RLS and security
- RLS: Enabled
- Policies:
  - Admin can view all employability scores
  - Service role can manage all employability scores
- Notes: Contains personal assessment data. RLS is mandatory.

### Typical usage
- Calculate fit score based on CV and job requirements
- Provide breakdown by dimension
- Identify areas for improvement
- Track score over time (future)

### Business rules
- All scores must be between 0 and 100
- overall_score is required
- Other scores are optional but recommended
- One score per session (can be updated)

---

(Additional tables will be documented as they are implemented: ai_providers, translations, legal_content, audit_logs, ai_usage_logs)

