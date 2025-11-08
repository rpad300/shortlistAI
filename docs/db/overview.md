# Database Overview – CV Analysis Platform

## Purpose

This document describes the main entities, relationships, and design principles for the CV Analysis Platform database hosted on Supabase PostgreSQL.

## Main Entities

### Core Business Entities

1. **Candidates**
   - Stores candidate personal information
   - Links to multiple CV versions
   - Deduplication key: email address

2. **Companies**
   - Stores company information from interviewer flows
   - Links to interviewers and job postings

3. **Interviewers**
   - Contact details of people using the interviewer flow
   - Links to companies and job postings

4. **Job Postings**
   - Stores job posting text and files
   - Links to structured representation
   - Reusable across multiple analysis batches

5. **CVs**
   - Stores CV files and extracted text
   - Links to candidates
   - Versioning support (multiple CVs per candidate)

6. **Analyses**
   - Stores AI analysis results
   - Two modes: Interviewer and Candidate
   - Links to job postings, CVs, and prompts used

### Configuration and Content

7. **AI Prompts**
   - Prompt templates for different AI tasks
   - Versioning support
   - Provider configuration per prompt

8. **AI Providers**
   - Configuration for AI services (Gemini, OpenAI, Claude, etc.)
   - API key management (encrypted)
   - Active/inactive status

9. **Translations**
   - Multi-language content storage
   - Keys for EN, PT, FR, ES
   - Manual vs AI-generated flags

10. **Legal Content**
    - Terms and Conditions
    - Privacy Policy
    - Consent texts
    - Versioning and multi-language support

### Audit and Logs

11. **Audit Logs**
    - User actions and system events
    - Security and compliance tracking

12. **AI Usage Logs**
    - Track AI API calls
    - Cost and performance monitoring

## Access Model

- **Public flows (Interviewer and Candidate)**: No authentication, anonymous access
- **Admin backoffice**: Protected by authentication
- **RLS policies**: Ensure only Admin can access full database
- **Data isolation**: Public users never see stored data except their current session

## Security Principles

1. **Row Level Security (RLS)**: Enabled on all sensitive tables
2. **Admin-only access**: Full database access requires admin authentication
3. **No sensitive data in logs**: Passwords, API keys, and personal data redacted
4. **Encrypted secrets**: AI provider API keys stored encrypted

## Multi-Language Strategy

- English is the base language for all content
- Translations stored in dedicated table
- AI-powered translation with manual review option
- All UI strings, emails, and legal content support EN, PT, FR, ES

## Candidate Deduplication

- Email address is the primary deduplication key
- Multiple CVs link to same candidate when email matches
- Admin can manually merge duplicates when needed

## Data Retention

- Retention policy defined in legal documents
- Admin can export or delete candidate data on request
- Soft delete pattern for important records

## Schema Documentation

Detailed table documentation is maintained in [tables.md](./tables.md).

Schema change history is tracked in [changelog.md](./changelog.md).

## Next Steps

1. Create detailed table definitions in tables.md
2. Design and implement initial migrations
3. Setup RLS policies
4. Document typical queries and usage patterns

