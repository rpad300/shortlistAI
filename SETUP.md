# Setup Instructions - CV Analysis Platform

This document provides step-by-step instructions to complete the setup and start development.

## ✅ Completed

The following has been set up:

- ✅ Project structure (src/, docs/, tests/, config/, temp/)
- ✅ Python backend with FastAPI
- ✅ React frontend with TypeScript, Vite, and PWA support
- ✅ Multi-language i18n system (EN, PT, FR, ES)
- ✅ Comprehensive documentation (database, AI, product, i18n)
- ✅ Git repository initialized with initial commit
- ✅ .gitignore configured

## 📋 Next Steps

### 1. Create GitHub Repository

The project is named **ShortlistAI** and is already in a Git repository locally.

To push to GitHub:

1. Go to https://github.com/new
2. Create a new repository:
   - Name: `ShortlistAI`
   - Description: "AI-powered CV analysis platform for interviewers and candidates"
   - **Do NOT initialize with README, .gitignore, or license** (we already have these)
3. After creating, run these commands locally:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ShortlistAI.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create .env File

Copy the environment variables template:

**Note**: There is a `.env.example` file that should exist in the root. If it doesn't (it was blocked), create `.env` with these variables:

```env
# ========================================
# APPLICATION
# ========================================
APP_ENV=development
APP_PORT=8000
APP_DEBUG=True

# ========================================
# DATABASE SERVICE (Supabase)
# ========================================
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=

# ========================================
# AI / LLM SERVICES
# ========================================
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
KIMI_API_KEY=
MINIMAX_API_KEY=

# ========================================
# EMAIL SERVICE (Resend)
# ========================================
RESEND_API_KEY=
FROM_EMAIL=

# ========================================
# SECURITY
# ========================================
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD_HASH=

# ========================================
# FRONTEND
# ========================================
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# ========================================
# RATE LIMITING & ABUSE PREVENTION
# ========================================
RATE_LIMIT_PER_MINUTE=10
MAX_CV_FILE_SIZE_MB=10
MAX_JOB_POSTING_LENGTH=50000

# ========================================
# FEATURE FLAGS
# ========================================
ENABLE_AI_TRANSLATION=True
ENABLE_CANDIDATE_FLOW=True
ENABLE_INTERVIEWER_FLOW=True
```

Fill in real values for:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Supabase credentials (after creating project in step 3)
- AI API keys (as you obtain them)
- Email service credentials (when setting up Resend)

### 3. Initialize Supabase Project

You need to create a Supabase project for the development environment.

#### Option 1: Using Supabase MCP (if available in Cursor)

Use the Supabase MCP tools to:
1. List organizations
2. Create a new project with:
   - Name: `shortlistai-dev`
   - Region: Choose closest to you (e.g., `us-east-1` for US, `eu-west-1` for Europe)
   - Organization: Your organization

#### Option 2: Using Supabase Dashboard

1. Go to https://supabase.com/dashboard
2. Click "New project"
3. Fill in:
   - Name: `shortlistai-dev`
   - Database Password: Generate a strong password
   - Region: Choose closest to you
4. Wait for project to be created
5. Go to Project Settings → API
6. Copy:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_ANON_KEY`
   - service_role key → `SUPABASE_SERVICE_ROLE_KEY`
7. Go to Project Settings → Database
8. Copy connection string → `DATABASE_URL`

Update `.env` with these values.

### 4. Setup Backend

```bash
cd src/backend
python -m venv venv
```

Activate virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

Run backend:
```bash
python main.py
```

Backend will run at http://localhost:8000  
API docs at http://localhost:8000/api/docs

### 5. Setup Frontend

```bash
cd src/frontend
npm install
npm run dev
```

Frontend will run at http://localhost:3000

### 6. Create Database Schema

Once Supabase is set up, create the initial database schema:

1. Review the schema documentation in `docs/db/tables.md`
2. Create migration files in `src/backend/database/migrations/`
3. Apply migrations to Supabase

This will be done as the next phase of implementation.

## 🔐 Security Reminders

- **NEVER commit `.env` file** (already in .gitignore)
- **NEVER commit real API keys or secrets**
- **Rotate any secrets that are accidentally committed**
- Use strong, unique passwords for all services

## 📚 Documentation

- **Project Plan**: `projectplan.md` - Full roadmap and tasks
- **README**: `Readme.md` - Functional specification
- **Database**: `docs/db/` - Schema and design
- **AI System**: `docs/ai/overview.md` - AI architecture
- **Product**: `docs/product/overview.md` - Product vision and flows
- **i18n**: `docs/i18n/overview.md` - Multi-language system
- **Backend**: `src/backend/README.md` - Backend setup and structure
- **Frontend**: `src/frontend/README.md` - Frontend setup and structure

## 🎯 Development Workflow

1. Check `projectplan.md` for current tasks
2. Choose the next unchecked task
3. Read relevant documentation
4. Implement the feature
5. Test locally
6. Update `projectplan.md` (mark task complete with date)
7. Update `docs/PROGRESS.md` with summary
8. Commit with clear message (format: "action: what was done")
9. Push to GitHub

## 🤝 Contribution Guidelines

- Follow the rules in `docs/rules/`
- All code comments in English
- Use TypeScript for frontend, Python for backend
- Write tests for critical features
- Keep documentation in sync with code
- Never hardcode configuration (use `.env`)

## 📞 Support

For questions about the project structure or development approach, refer to:
- `docs/rules/00-multi-role-coordinator.md` - How roles work together
- `docs/rules/02-core-coder-role.md` - Core coding standards
- `projectplan.md` - Project status and next steps

## ✨ Ready to Start!

Once you complete steps 1-5 above, you'll have:
- ✅ Code in GitHub
- ✅ Supabase project created
- ✅ Backend running locally
- ✅ Frontend running locally
- ✅ Development environment ready

The next phase is to implement the database schema and start building the public flows (Interviewer and Candidate).

