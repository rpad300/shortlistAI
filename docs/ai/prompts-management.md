# AI Prompts Management System

## Overview

The AI Prompts Management System allows administrators to manage all AI prompt templates through a user-friendly Admin interface. This eliminates the need to modify code when adjusting prompts and enables version control, testing, and rollback capabilities.

## Features

### ✅ Complete CRUD Operations
- Create new prompts
- View and edit existing prompts
- Deactivate prompts (soft delete)
- List and filter prompts

### ✅ Version Control
- Automatic version history on content changes
- View all previous versions
- Rollback to any previous version
- Track who made changes and when

### ✅ Multi-Language Support
- Store prompts in different languages (EN, PT, FR, ES)
- Language-specific prompt versions
- Fallback to default language

### ✅ Categorization
- Organize prompts by category
- Filter by category, language, status
- Search and manage large prompt libraries

### ✅ Usage Tracking
- Track how many times each prompt is used
- Last used timestamp
- Statistics dashboard

### ✅ Model Preferences
- Configure preferred AI models per prompt
- Set temperature, max_tokens, and other parameters
- Override default settings

## Database Schema

### Table: `ai_prompts`

Stores all AI prompt templates.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `prompt_key` | VARCHAR(100) | Unique identifier (e.g., "cv_extraction") |
| `name` | VARCHAR(255) | Human-readable name |
| `description` | TEXT | Purpose and usage notes |
| `content` | TEXT | The actual prompt template |
| `category` | VARCHAR(50) | Category (cv_extraction, job_analysis, etc.) |
| `variables` | JSONB | Array of variable names used in the prompt |
| `language` | VARCHAR(10) | Language code (en, pt, fr, es) |
| `model_preferences` | JSONB | Preferred AI model settings |
| `version` | INTEGER | Current version number |
| `is_active` | BOOLEAN | Whether this prompt is active |
| `is_default` | BOOLEAN | Default version for this prompt_key |
| `usage_count` | INTEGER | Number of times used |
| `last_used_at` | TIMESTAMPTZ | Last usage timestamp |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |
| `created_by` | VARCHAR(255) | Admin who created this |
| `updated_by` | VARCHAR(255) | Admin who last updated this |
| `admin_notes` | TEXT | Internal notes for admins |

### Table: `prompt_versions`

Keeps history of all prompt changes.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `prompt_id` | UUID | Reference to ai_prompts |
| `version` | INTEGER | Version number |
| `content` | TEXT | Prompt content at this version |
| `variables` | JSONB | Variables at this version |
| `model_preferences` | JSONB | Model preferences at this version |
| `change_description` | TEXT | Description of changes |
| `created_at` | TIMESTAMPTZ | When this version was created |
| `created_by` | VARCHAR(255) | Who created this version |

### Table: `prompt_test_results`

Stores test results for prompt quality evaluation.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `prompt_id` | UUID | Reference to ai_prompts |
| `test_input` | JSONB | Input data for the test |
| `expected_output` | TEXT | Expected result |
| `actual_output` | TEXT | Actual AI response |
| `status` | VARCHAR(20) | Test status (passed, failed, pending) |
| `quality_score` | NUMERIC | Quality score 0.00-5.00 |
| `evaluation_notes` | TEXT | Notes about the test |
| `provider_used` | VARCHAR(50) | AI provider used |
| `model_used` | VARCHAR(100) | Model used |
| `execution_time_ms` | INTEGER | Execution time |
| `tokens_used` | INTEGER | Tokens consumed |
| `cost_usd` | NUMERIC | Cost of the test |
| `created_at` | TIMESTAMPTZ | Test timestamp |
| `created_by` | VARCHAR(255) | Who ran the test |
| `test_name` | VARCHAR(255) | Name of the test case |
| `is_golden_test` | BOOLEAN | Important test that should always pass |

## API Endpoints

All endpoints require admin authentication.

### List Prompts
```
GET /api/admin/prompts/
Query Parameters:
  - category (optional): Filter by category
  - is_active (optional): Filter by active status
  - language (optional): Filter by language code

Response:
{
  "prompts": [...],
  "total": 8
}
```

### Get Prompt Statistics
```
GET /api/admin/prompts/stats

Response:
{
  "total": 8,
  "active": 8,
  "inactive": 0,
  "by_category": {
    "cv_extraction": 2,
    "job_analysis": 2,
    ...
  },
  "most_used": [...]
}
```

### Get Single Prompt
```
GET /api/admin/prompts/{prompt_id}

Response: Prompt object
```

### Get Prompt by Key
```
GET /api/admin/prompts/key/{prompt_key}
Query Parameters:
  - language (default: "en")
  - version (optional): Specific version number

Response: Prompt object
```

### Create Prompt
```
POST /api/admin/prompts/

Body:
{
  "prompt_key": "my_new_prompt",
  "name": "My New Prompt",
  "content": "The prompt template with {variables}",
  "category": "general",
  "description": "What this prompt does",
  "variables": ["variable1", "variable2"],
  "language": "en",
  "model_preferences": {
    "temperature": 0.7,
    "max_tokens": 2000,
    "preferred_provider": "gemini"
  },
  "is_active": true,
  "is_default": true,
  "admin_notes": "Internal notes"
}

Response: Created prompt object
```

### Update Prompt
```
PUT /api/admin/prompts/{prompt_id}

Body:
{
  "content": "Updated prompt content",
  "name": "Updated name",
  "change_description": "What changed",
  "create_new_version": true
}

Response: Updated prompt object
```

### Delete Prompt (Soft Delete)
```
DELETE /api/admin/prompts/{prompt_id}

Response:
{
  "message": "Prompt deactivated successfully"
}
```

### Get Version History
```
GET /api/admin/prompts/{prompt_id}/versions

Response:
{
  "versions": [...],
  "total": 5
}
```

### Rollback to Version
```
POST /api/admin/prompts/{prompt_id}/rollback/{version}

Response:
{
  "message": "Rolled back to version 2",
  "prompt": {...}
}
```

### List Categories
```
GET /api/admin/prompts/categories/list

Response:
{
  "categories": ["cv_extraction", "job_analysis", ...],
  "total": 5
}
```

## Admin UI

### Accessing the Prompts Manager

1. Log in to the Admin panel
2. Navigate to **Dashboard** → **🤖 AI Prompts**
3. Or go directly to `/admin/prompts`

### UI Features

#### Left Panel - Prompts List
- View all prompts with filters
- Filter by category, status, language
- See usage statistics
- Click to select and view details

#### Right Panel - Details/Editor
- View full prompt details
- Edit prompt content and metadata
- Create new prompts
- Access version history
- Rollback to previous versions

#### Statistics Dashboard
- Total prompts count
- Active/inactive counts
- Categories overview
- Most used prompts

## Usage in Code

### Python (Async)

```python
from services.ai.prompts import get_prompt

# Get prompt from database
prompt_template = await get_prompt("cv_extraction", language="en")

# Use the prompt
formatted_prompt = prompt_template.format(cv_text=cv_content)
```

### Python (Sync - Fallback)

```python
from services.ai.prompts import get_prompt_sync

# Get prompt (uses defaults, not database)
prompt_template = get_prompt_sync("cv_extraction")

# Use the prompt
formatted_prompt = prompt_template.format(cv_text=cv_content)
```

### Database Service

```python
from services.database.prompt_service import get_prompt_service

service = get_prompt_service()

# Get by key
prompt = await service.get_prompt_by_key("cv_extraction", "en")

# Get by ID
prompt = await service.get_prompt_by_id(prompt_id)

# Create new
new_prompt = await service.create_prompt(
    prompt_key="my_prompt",
    name="My Prompt",
    content="Template",
    ...
)

# Update
updated = await service.update_prompt(
    prompt_id=prompt_id,
    content="New content",
    change_description="Fixed typo",
    create_new_version=True
)
```

## Setup and Migration

### 1. Run Database Migration

```bash
# Apply the migration
# Using Supabase MCP or your migration tool
```

The migration file is located at:
```
src/backend/database/migrations/004_ai_prompts.sql
```

### 2. Seed Default Prompts

```bash
# Run the seed script
cd src/backend
python -m scripts.seed_prompts
```

This will populate the database with all default prompts:
- cv_extraction
- job_posting_normalization
- weighting_recommendation
- cv_summary
- interviewer_analysis
- candidate_analysis
- translation
- executive_recommendation

### 3. Verify in Admin UI

1. Log in to Admin
2. Go to **AI Prompts**
3. Check that all default prompts are listed
4. Verify they are all active

## Prompt Categories

### cv_extraction
Prompts that extract and structure data from CVs.

### job_analysis
Prompts that analyze and normalize job posting data.

### candidate_evaluation
Prompts that evaluate and score candidates.

### translation
Prompts for multi-language translation.

### reporting
Prompts that generate summaries and reports.

### general
General-purpose prompts.

## Best Practices

### ✅ DO

- **Test prompts before activating**: Use the test interface to verify outputs
- **Use descriptive names**: Make it easy to identify prompts
- **Document changes**: Always provide a change description when updating
- **Use variables**: Make prompts reusable with `{variable}` placeholders
- **Set appropriate temperatures**: Lower for structured output, higher for creative
- **Version important changes**: Create new versions for significant updates
- **Add admin notes**: Document special requirements or gotchas

### ❌ DON'T

- **Don't hardcode values**: Use variables instead
- **Don't skip change descriptions**: Always document what changed
- **Don't delete prompts**: Deactivate instead (soft delete)
- **Don't forget to test**: Test in staging before production
- **Don't use high temperatures for JSON**: Keep it low (0.3-0.5) for structured output

## Prompt Variables

Variables are placeholders in prompts that get replaced with actual values.

### Format
```
{variable_name}
```

### Common Variables

| Variable | Description | Used In |
|----------|-------------|---------|
| `cv_text` | CV content | CV extraction, analysis |
| `job_posting` | Job posting text | Job analysis, candidate evaluation |
| `key_points` | Interviewer's key requirements | Weighting, analysis |
| `language` | Target language | Translation, localized prompts |
| `weights` | Category weights | Candidate evaluation |
| `hard_blockers` | Must-have requirements | Candidate evaluation |
| `nice_to_have` | Preferred requirements | Candidate evaluation |
| `enrichment_context` | External data context | Enhanced analysis |

### Example

Prompt template:
```
Analyze this CV for the following job:

Job: {job_posting}

CV: {cv_text}

Focus on: {key_points}
```

Python usage:
```python
formatted = prompt_template.format(
    job_posting=job_text,
    cv_text=cv_content,
    key_points=interviewer_notes
)
```

## Model Preferences

Each prompt can have preferred AI model settings.

### Available Settings

```json
{
  "temperature": 0.7,
  "max_tokens": 2000,
  "preferred_provider": "gemini",
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

### Temperature Guide

- **0.0 - 0.3**: Highly deterministic, consistent (JSON extraction, data normalization)
- **0.4 - 0.6**: Balanced (summaries, standard analysis)
- **0.7 - 0.9**: Creative, varied (reports, recommendations)
- **1.0+**: Very creative, unpredictable (not recommended for production)

## Troubleshooting

### Prompt not loading
**Problem**: Code is not using the database prompt

**Solution**:
1. Check that migration was applied
2. Verify prompt exists in database
3. Check prompt is active (`is_active = true`)
4. Check prompt is default (`is_default = true`)
5. Look at logs for errors

### Version not updating
**Problem**: Changes not creating new version

**Solution**:
1. Ensure `create_new_version` is `true`
2. Check that content actually changed
3. Verify user has permissions

### Test failed
**Problem**: Prompt test failed

**Solution**:
1. Check test input data
2. Review expected vs actual output
3. Adjust temperature if needed
4. Review model preferences
5. Test with different provider

## Support

For issues, questions, or feature requests:
1. Check this documentation
2. Review the code in `src/backend/services/database/prompt_service.py`
3. Check API documentation at `/api/docs`
4. Contact the development team

## Future Enhancements

Planned features:
- [ ] A/B testing framework
- [ ] Prompt performance analytics
- [ ] Auto-optimization suggestions
- [ ] Prompt templates library
- [ ] Collaborative editing
- [ ] Approval workflows
- [ ] Integration with monitoring tools

