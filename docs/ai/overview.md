# AI System Overview – CV Analysis Platform

## Purpose

The AI system is the core of the CV Analysis Platform. It powers:
- CV text extraction and structuring
- Job posting normalization
- Candidate evaluation (Interviewer mode)
- Candidate preparation (Candidate mode)
- Multi-language translation

## Supported AI Providers

The platform supports multiple AI providers for flexibility, cost optimization, and redundancy:

1. **Google Gemini** - Fast, cost-effective for most tasks
2. **OpenAI (GPT-4, GPT-3.5)** - High quality, good for complex analysis
3. **Anthropic Claude** - Excellent for long-form text and reasoning
4. **Kimi** - Alternative provider
5. **Minimax** - Alternative provider

### Provider Selection

- Admin configures which provider to use per prompt type
- Default provider can be set globally
- Switching providers does not change functional behavior
- Provider selection is stored with each analysis for traceability

## AI Responsibilities

### 1. Document Processing

**CV Extraction**
- Input: PDF or DOCX file
- Output: Structured representation (JSON) with:
  - Personal information
  - Work experience
  - Education
  - Skills
  - Languages
  - Certifications

**Job Posting Normalization**
- Input: Free text or uploaded file
- Output: Structured representation with:
  - Role title
  - Required skills
  - Experience level
  - Location
  - Key responsibilities

### 2. Analysis and Evaluation

**Interviewer Mode**
- Input: Job posting + multiple CVs + weights + hard blockers
- Output: For each candidate:
  - 1-5 scores across 10 dynamic categories
  - Weighted global score
  - Strengths and risks
  - Custom interview questions
  - Hard blocker flags

**Candidate Mode**
- Input: Job posting + single CV
- Output:
  - 1-5 scores across evaluation categories
  - Strengths and gaps
  - Likely interview questions
  - Suggested answer structures
  - Intro pitch paragraph

### 3. Translation

- Translate UI strings from English to PT, FR, ES
- Translate legal content (Terms, Privacy Policy)
- Translate email templates
- Maintain translation quality with manual review option

## Prompt Management

All AI prompts are:
- Stored in the database
- Versioned for traceability
- Configurable by Admin without code changes
- Linked to specific provider
- Language-aware (can output in user's selected language)

### Prompt Types

1. **cv_extraction** - Extract structured data from CV
2. **job_posting_normalization** - Normalize job posting
3. **interviewer_analysis** - Evaluate candidates for interviewer
4. **candidate_analysis** - Prepare candidate for interview
5. **email_summary_interviewer** - Generate email content for interviewer
6. **email_summary_candidate** - Generate email content for candidate
7. **translation** - Translate text to target language

Each prompt type has:
- Active version used in production
- Inactive/draft versions for testing
- Version history for rollback

## Quality and Safety

### Guardrails

- Input validation (length limits, format checks)
- Output structure validation (ensure JSON schema compliance)
- Toxicity and abuse detection (basic filters)
- Cost limits per request

### Evaluation

- **Golden test cases**: Curated examples to test prompt changes
- **Quality markers**: Admin can flag good/bad analyses
- **Metrics tracked**:
  - Latency per provider
  - Cost per request
  - Success rate
  - User feedback (where available)

### Transparency

All AI outputs are marked with:
- Provider used
- Prompt version
- Language
- Timestamp
- Warning that AI is advisory, not definitive

## Data Privacy

- No passwords, secrets, or highly sensitive data sent to AI
- Candidates and interviewers consent to data processing
- Privacy Policy lists all AI providers used
- Option for users to opt-out (future feature)
- AI usage logs redacted of sensitive information

## Performance and Cost

### Latency Targets

- CV extraction: < 10 seconds
- Job posting normalization: < 5 seconds
- Analysis (single candidate): < 15 seconds
- Translation: < 3 seconds per text

### Cost Management

- Track cost per analysis
- Cache repeated requests where possible
- Use cheaper providers for simpler tasks
- Admin dashboard shows cost metrics

### Fallbacks

- If AI call fails, retry with exponential backoff
- If provider is down, log error and notify Admin
- Graceful degradation (e.g., show partial results)

## Admin Controls

Admin can:
- View and edit all prompts
- Create new prompt versions
- Test prompts with sample data
- Switch active prompt version
- Review AI quality with golden cases
- See cost and performance metrics per provider
- Enable/disable specific providers

## Architecture

```
User Input
    ↓
Backend API
    ↓
AI Service Layer (abstraction)
    ↓
[Gemini | OpenAI | Claude | Kimi | Minimax]
    ↓
Structured Output
    ↓
Database Storage
    ↓
Display to User
```

The AI Service Layer:
- Abstracts provider-specific APIs
- Handles authentication and rate limiting
- Formats prompts and parses responses
- Logs usage and errors
- Implements retry logic

## Documentation

- `prompts.md` - Details of each prompt type and structure
- `providers.md` - Configuration and usage of each AI provider
- `evaluation.md` - How to evaluate and improve AI quality

## Future Enhancements

- Fine-tuned models for specific evaluation tasks
- RAG (Retrieval Augmented Generation) for company knowledge
- A/B testing of prompt versions
- User feedback loop for continuous improvement
- Multi-modal analysis (e.g., video interview analysis)

