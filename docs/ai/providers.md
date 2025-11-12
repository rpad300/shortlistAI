# AI Providers Configuration

This document consolidates the configuration required to use the official SDKs
for each AI provider supported by the platform.

## Google Gemini

- **SDK**: [`google-generativeai`](https://pypi.org/project/google-generativeai/)
- **Docs**: [Gemini API quickstart](https://ai.google.dev/gemini-api/docs?hl=pt-br#python)
- **Environment variables**:
  - `GEMINI_API_KEY`
- **Notes**:
  - We instantiate `google.generativeai.GenerativeModel` directly.
  - Token and cost tracking is estimated from request/response sizes.

## OpenAI

- **SDK**: [`openai`](https://pypi.org/project/openai/)
- **Docs**: [OpenAI quickstart](https://platform.openai.com/docs/quickstart)
- **Environment variables**:
  - `OPENAI_API_KEY`
- **Notes**:
  - Uses the async client (`AsyncOpenAI`) for non-blocking calls.
  - Responses are parsed for JSON payloads when prompts request structured data.

## Anthropic Claude

- **SDK**: [`anthropic`](https://pypi.org/project/anthropic/)
- **Docs**: [Claude get started](https://docs.claude.com/en/docs/get-started)
- **Environment variables**:
  - `ANTHROPIC_API_KEY`
- **Notes**:
  - Default model is `claude-3-sonnet-20240229` and can be overridden in the database configuration.
  - Token accounting is based on provider usage metadata.

## Kimi K2

- **SDK**: [`openai`](https://pypi.org/project/openai/) (OpenAI-compatible endpoint)
- **Docs**: [Kimi API documentation](https://kimi-k2.ai/api-docs)
- **Environment variables**:
  - `KIMI_API_KEY`
- **Notes**:
  - We keep the official OpenAI client but set `base_url=https://kimi-k2.ai/api/v1`.
  - Model defaults to `kimi-k2-0905`; override via database/provider configuration as needed.
  - Credit-based pricing is logged downstream; the SDK still exposes token counters.

## MiniMax

- **HTTP client**: [`httpx`](https://www.python-httpx.org/)
- **Docs**: [MiniMax model guide](https://platform.minimax.io/docs/guides/models-intro)
- **Environment variables**:
  - `MINIMAX_API_KEY`
  - `MINIMAX_GROUP_ID`
- **Notes**:
  - The official REST endpoint (`https://api.minimax.chat/v1/text/chatcompletion`) requires the `X-Group-ID` header.
  - Responses may return either `output_text` or `choices.*.messages`. The provider normalises both cases.
  - Token usage is read from the `usage` object when provided.

## Brave Search API

- **HTTP client**: [`httpx`](https://www.python-httpx.org/)
- **Docs**: [Brave Search API documentation](https://api-dashboard.search.brave.com/app/documentation/web-search/get-started)
- **Environment variables**:
  - `BRAVE_SEARCH_API_KEY`
- **Purpose**: Enrich company and candidate data with publicly available information
- **Notes**:
  - Used for **data enrichment**, not AI generation
  - Endpoint: `https://api.search.brave.com/res/v1/web/search`
  - Headers: `X-Subscription-Token` for authentication
  - **Privacy considerations**:
    - Only searches publicly available information
    - Does NOT send CV content or sensitive personal data
    - Only uses candidate/company names for search queries
    - Respects rate limits and privacy policies
  - **Use cases**:
    - Company enrichment: website, industry, recent news, social media
    - Candidate enrichment: LinkedIn, GitHub, portfolio, publications
    - Company news search: recent updates and press releases

### Brave Search Service Architecture

The Brave Search service (`src/backend/services/search/brave_search.py`) provides:

- `search_web()` - General web search with filtering
- `enrich_company()` - Extract company information from search results
- `enrich_candidate()` - Find public professional profiles
- `search_company_news()` - Get recent news about companies

### API Endpoints

Data enrichment endpoints are available at `/api/enrichment/`:

- `POST /api/enrichment/status` - Check if service is enabled
- `POST /api/enrichment/company` - Enrich company by name
- `POST /api/enrichment/company/from-job` - Enrich from job posting session
- `POST /api/enrichment/candidate` - Enrich candidate by name
- `POST /api/enrichment/candidate/from-cv` - Enrich from candidate CV
- `POST /api/enrichment/company/news` - Search recent company news

## Provider routing

`src/backend/services/ai/manager.py` initialises all AI providers whose API keys
are present in configuration. The first available provider becomes the default,
and requests can explicitly target another provider when needed. Whenever a
provider fails and fallback is enabled, the manager loops through all remaining
providers in registration order.

The Brave Search service is independent from AI providers and is initialized
separately when `BRAVE_SEARCH_API_KEY` is configured.

## Safety and compliance

- All API keys must be stored in environment variables (`.env` / secrets manager).
- Never hardcode keys or base URLs outside configuration modules.
- Only send the minimum data required by each provider, in line with the privacy policy.
- Provider usage is logged via `AIResponse` metadata to support cost monitoring.
- **Brave Search specific**:
  - Never send CV content, personal data, or sensitive information to search API
  - Only use public identifiers (names, company names) for enrichment
  - All search data is publicly available information
  - Respects GDPR and data protection regulations

