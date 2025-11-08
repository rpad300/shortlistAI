# Project Plan – CV Analysis Platform

## Project Goal

Build a free, AI-powered CV analysis platform with two public flows (Interviewer and Candidate), one Admin backoffice, multi-language support (EN, PT, FR, ES), and a headhunting database.

## Technology Stack

- **Backend**: Python (FastAPI)
- **Database**: Supabase PostgreSQL
- **Frontend**: React + TypeScript (PWA)
- **AI Providers**: Gemini, OpenAI, Claude, Kimi, Minimax
- **Email**: Resend (Gmail integration)
- **Deployment**: TBD (following DevOps rules)

## Current Tasks

### Phase 1: Foundation and Infrastructure
- [ ] Initialize Git repository and GitHub remote
- [ ] Create project structure (src/, docs/, temp/, tests/, config/)
- [ ] Setup .gitignore and .env.example
- [ ] Initialize Supabase project (dev environment)
- [ ] Setup Python backend structure with FastAPI
- [ ] Setup React frontend structure with PWA support
- [ ] Configure multi-language i18n system

### Phase 2: Database Schema
- [ ] Design and document core database schema
  - Candidates table
  - Companies and interviewers table
  - Job postings table
  - CVs table (files and extracted text)
  - Analyses table (Interviewer and Candidate modes)
  - AI prompts configuration table
  - Translations table
- [ ] Create initial migrations
- [ ] Setup RLS policies for Admin access
- [ ] Document schema in docs/db/

### Phase 3: Admin Authentication
- [ ] Implement Admin authentication system
- [ ] Create Admin login screen
- [ ] Setup protected routes and API endpoints
- [ ] Add session management

### Phase 4: Public Flows - Interviewer
- [ ] Interviewer Step 1: Identification and consent form
- [ ] Interviewer Step 2: Job posting input (text/file)
- [ ] Interviewer Step 3: Key points definition
- [ ] Interviewer Step 4: Weighting and hard blockers
- [ ] Interviewer Step 5: CV upload (batch support)
- [ ] Interviewer Step 6: AI analysis integration
- [ ] Interviewer Step 7: Results display (ranking table + details)
- [ ] Interviewer Step 8: Email and report generation

### Phase 5: Public Flows - Candidate
- [ ] Candidate Step 1: Identification and consent form
- [ ] Candidate Step 2: Job posting input
- [ ] Candidate Step 3: CV upload
- [ ] Candidate Step 4: AI analysis
- [ ] Candidate Step 5: Results display
- [ ] Candidate Step 6: Email and report

### Phase 6: AI Integration
- [ ] Setup AI provider management system
- [ ] Implement prompt configuration and versioning
- [ ] Create AI service layer (abstraction for multiple providers)
- [ ] Implement job posting normalization
- [ ] Implement CV extraction and structuring
- [ ] Implement Interviewer analysis flow
- [ ] Implement Candidate analysis flow
- [ ] Implement AI-powered translation system

### Phase 7: Admin Backoffice - Data Management
- [ ] Candidates list and detail views
- [ ] Companies and interviewers views
- [ ] Job postings list and details
- [ ] Analyses review interface
- [ ] Data export functionality

### Phase 8: Admin Backoffice - AI Management
- [ ] Prompt management interface (CRUD)
- [ ] Prompt versioning system
- [ ] Prompt testing interface
- [ ] AI provider configuration
- [ ] Golden test cases management
- [ ] Quality review tools

### Phase 9: Admin Backoffice - Translation Management
- [ ] Translation keys management
- [ ] AI translation trigger interface
- [ ] Manual translation editor
- [ ] Translation status tracking

### Phase 10: Legal and Compliance
- [ ] Terms and Conditions (EN base)
- [ ] Privacy Policy (EN base)
- [ ] Consent texts and checkboxes
- [ ] AI-powered translation of legal texts to PT, FR, ES
- [ ] Legal content versioning

### Phase 11: Email System
- [ ] Resend integration setup
- [ ] Email templates (multi-language)
- [ ] Interviewer summary email
- [ ] Candidate preparation email
- [ ] Email tracking and logging

### Phase 12: Abuse Prevention and Security
- [ ] Rate limiting implementation
- [ ] File upload validation (type, size)
- [ ] IP-based abuse detection
- [ ] Admin controls for blocking/disabling flows
- [ ] Security headers and hardening

### Phase 13: PWA and Multi-Device
- [ ] PWA manifest.json
- [ ] Service worker for offline support
- [ ] Responsive layout (mobile, tablet, desktop, TV)
- [ ] Light and dark theme support
- [ ] Multi-input support (touch, mouse, keyboard, remote)

### Phase 14: Testing and Quality
- [ ] Unit tests for critical backend logic
- [ ] Integration tests for API endpoints
- [ ] E2E tests for main flows
- [ ] Cross-device testing
- [ ] AI quality evaluation framework

### Phase 15: Documentation
- [ ] docs/db/ database documentation
- [ ] docs/api/ API documentation
- [ ] docs/ai/ AI system documentation
- [ ] docs/i18n/ internationalization documentation
- [ ] docs/product/ product and flows documentation
- [ ] User guides and help content

### Phase 16: Deployment and DevOps
- [ ] Setup dev, staging, prod environments
- [ ] CI/CD pipeline configuration
- [ ] Monitoring and logging setup
- [ ] Backup and recovery procedures
- [ ] Performance optimization

## Completed Tasks

(Tasks will be marked with [x] and date when completed)

## Backlog

- Advanced candidate search for headhunting
- Rich analytics dashboards for Admin
- Additional language support beyond EN, PT, FR, ES
- Mobile app versions (iOS/Android)
- Integration with job boards
- Candidate notifications system

## Technical Decisions

### Backend
- FastAPI chosen for modern Python API development with automatic OpenAPI docs
- Async/await for better performance with AI API calls

### Database
- Supabase PostgreSQL as single source of truth for all relational data
- RLS policies for secure Admin-only access to sensitive data
- Migration-based schema management

### Frontend
- React + TypeScript for type safety and developer experience
- PWA-first approach for installability and offline support
- Design tokens for consistent theming (light/dark mode)

### AI
- Multi-provider support for flexibility and cost optimization
- Prompt versioning to track changes and enable rollback
- Centralized AI service layer to abstract provider details

### Internationalization
- English as base language for all content
- AI-powered translation for PT, FR, ES with manual review capability
- Translation keys stored in database for dynamic updates

### Security
- Admin-only authentication (public flows are anonymous)
- Input validation and sanitization for all uploads and text
- Rate limiting to prevent abuse
- No sensitive data in AI prompts or logs

## Notes

- All code comments in English (following code-comments-and-docs-style.md)
- Never hardcode configuration; always use environment variables
- Follow the priority hierarchy for conflict resolution (Security > Legal > Product > Data > Marketing > UX > Implementation)
- Database documentation must be updated with every schema change
- AI prompts must be manageable by Admin without code changes
- All public-facing content must exist in EN, PT, FR, ES
- PWA compliance is mandatory for all web interfaces
- Candidate deduplication based on email address

