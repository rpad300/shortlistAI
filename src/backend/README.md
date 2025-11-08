# Backend - CV Analysis Platform

Python FastAPI backend for the CV Analysis Platform.

## Structure

```
src/backend/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration and environment variables
├── requirements.txt     # Python dependencies
├── routers/            # API route handlers
│   ├── interviewer.py  # Public interviewer flow endpoints
│   ├── candidate.py    # Public candidate flow endpoints
│   ├── admin_auth.py   # Admin authentication
│   ├── admin_data.py   # Admin data management
│   └── admin_ai.py     # Admin AI management
├── services/           # Business logic layer
│   ├── ai/            # AI integration services
│   ├── storage/       # File storage services
│   ├── email/         # Email sending services
│   └── translation/   # Translation services
├── models/            # Pydantic models and schemas
├── database/          # Database models and migrations
└── utils/             # Utility functions
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in real values

5. Run the development server:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

## API Documentation

When the server is running, API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Environment Variables

See `.env.example` in the project root for all required environment variables.

All configuration is loaded through the `config.py` module using Pydantic settings.

## Development Guidelines

- All code comments in English
- Follow FastAPI best practices
- Use async/await for all I/O operations
- Validate inputs using Pydantic models
- Never log sensitive data (passwords, API keys, personal data)
- Handle errors gracefully with appropriate HTTP status codes
- Write unit tests for business logic
- Document all public functions and endpoints

## Testing

Run tests with pytest:
```bash
pytest tests/backend/
```

## Security

- All API keys and secrets must be in environment variables
- Use password hashing for any stored credentials
- Implement rate limiting on public endpoints
- Validate and sanitize all file uploads
- Apply input length limits
- Never trust user input

