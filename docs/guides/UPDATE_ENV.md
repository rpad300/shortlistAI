# Atualização do Ficheiro .env

## ✅ Configurações Existentes

O teu `.env` já tem a estrutura base. Precisas apenas **preencher e adicionar** algumas variáveis específicas do Supabase.

---

## 🔧 Variáveis a PREENCHER (que já existem no teu .env)

### 1. GEMINI_API_KEY (Já existe)
```env
GEMINI_API_KEY=<TUA_CHAVE_AQUI>
```
**Obter em**: https://makersuite.google.com/app/apikey
- É gratuito para testar
- Opcional por agora (só necessário para análises IA)

### 2. OPENAI_API_KEY (Já existe)
```env
OPENAI_API_KEY=<TUA_CHAVE_AQUI>
```
**Obter em**: https://platform.openai.com/api-keys
- Opcional (alternativa ao Gemini)

### 3. ANTHROPIC_API_KEY (Já existe)
```env
ANTHROPIC_API_KEY=<TUA_CHAVE_AQUI>
```
**Obter em**: https://console.anthropic.com/
- Necessário para usar Claude

### 4. KIMI_API_KEY (Já existe)
```env
KIMI_API_KEY=<TUA_CHAVE_AQUI>
```
**Obter em**: https://kimi-k2.ai/
- Usa o mesmo formato do OpenAI (SDK oficial com `base_url=https://kimi-k2.ai/api/v1`)

### 5. MINIMAX_API_KEY (Já existe)
```env
MINIMAX_API_KEY=<TUA_CHAVE_AQUI>
MINIMAX_GROUP_ID=<TEU_GROUP_ID>
```
**Obter em**: https://platform.minimax.io/
- A API exige **identificador de grupo** no cabeçalho `X-Group-ID`
- Necessário para chamadas ao endpoint `https://api.minimax.chat/v1/text/chatcompletion`

### 6. EMAIL_USER e EMAIL_PASSWORD (Já existem)
```env
EMAIL_USER=teu.email@gmail.com
EMAIL_PASSWORD=<APP_SPECIFIC_PASSWORD>
```
**Nota**: Para usar Resend no futuro, vamos adicionar outra variável (ver abaixo)

---

## ➕ Variáveis a ADICIONAR ao teu .env

### Adiciona esta secção no teu .env:

```env
# ==========================================================
# SUPABASE PROJECT CONFIGURATION (ShortlistAI)
# ==========================================================
# Supabase project URL
SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co

# Supabase anon/public key (safe for frontend)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV4bWZhemlvcm9zcGFnbHN1ZnlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2MDc3MzksImV4cCI6MjA3ODE4MzczOX0.AIEg359ub3vHK5ZU2HUSwK2YKPVE_2XjZoV0631z-qk

# Supabase service role key (BACKEND ONLY - get from dashboard)
SUPABASE_SERVICE_ROLE_KEY=<OBTER_DO_DASHBOARD>

# Database connection URL
DATABASE_URL=postgresql://postgres:<PASSWORD>@db.uxmfaziorospaglsufyp.supabase.co:5432/postgres

# ==========================================================
# EMAIL SERVICE (RESEND) - Alternative to direct Gmail
# ==========================================================
# Resend API key for transactional emails
RESEND_API_KEY=
# From email address for automated emails
FROM_EMAIL=noreply@shortlistai.com

# ==========================================================
# APPLICATION CONFIGURATION
# ==========================================================
# Application environment
APP_ENV=development
# API port
APP_PORT=8000
# Debug mode
APP_DEBUG=True
# Secret key for sessions and JWT
SECRET_KEY=dev-secret-key-change-in-production

# ==========================================================
# FRONTEND CONFIGURATION (VITE)
# ==========================================================
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
# Supabase URL for frontend
VITE_SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co
# Supabase anon key for frontend
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV4bWZhemlvcm9zcGFnbHN1ZnlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2MDc3MzksImV4cCI6MjA3ODE4MzczOX0.AIEg359ub3vHK5ZU2HUSwK2YKPVE_2XjZoV0631z-qk

# ==========================================================
# RATE LIMITING & ABUSE PREVENTION
# ==========================================================
RATE_LIMIT_PER_MINUTE=10
MAX_CV_FILE_SIZE_MB=10
MAX_JOB_POSTING_LENGTH=50000

# ==========================================================
# FEATURE FLAGS
# ==========================================================
ENABLE_AI_TRANSLATION=True
ENABLE_CANDIDATE_FLOW=True
ENABLE_INTERVIEWER_FLOW=True
```

---

## 📝 ACÇÕES NECESSÁRIAS

### 1. Obter SUPABASE_SERVICE_ROLE_KEY

1. Ir a: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/api
2. Na secção **"Project API keys"**
3. Copiar a chave **"service_role"** (é a secreta, não a "anon")
4. Colar no `.env` na variável `SUPABASE_SERVICE_ROLE_KEY`

**IMPORTANTE**: Esta chave é SECRETA! Nunca fazer commit dela!

### 2. Obter Password da Base de Dados

O `<PASSWORD>` no `DATABASE_URL` precisa ser preenchido:

1. Ir a: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/database
2. Ver a **"Connection string"**
3. Copiar apenas a password (entre `postgres:` e `@`)
4. Substituir `<PASSWORD>` no `DATABASE_URL`

**Exemplo**:
```env
# Se a password for "abc123xyz"
DATABASE_URL=postgresql://postgres:abc123xyz@db.uxmfaziorospaglsufyp.supabase.co:5432/postgres
```

---

## 🔄 MAPEAMENTO: Variáveis Antigas → Novas

O código do projeto usa estas variáveis (de `config.py`):

| Variável no Código | Variável no teu .env | Estado |
|-------------------|---------------------|---------|
| `SUPABASE_URL` | (adicionar) | ➕ Nova |
| `SUPABASE_ANON_KEY` | (adicionar) | ➕ Nova |
| `SUPABASE_SERVICE_ROLE_KEY` | (adicionar) | ➕ Nova |
| `DATABASE_URL` | (adicionar) | ➕ Nova |
| `GEMINI_API_KEY` | `GEMINI_API_KEY` | ✅ Já existe |
| `OPENAI_API_KEY` | `OPENAI_API_KEY` | ✅ Já existe |
| `ANTHROPIC_API_KEY` | `ANTHROPIC_API_KEY` | ✅ Já existe |
| `KIMI_API_KEY` | `KIMI_API_KEY` | ✅ Já existe |
| `MINIMAX_API_KEY` | `MINIMAX_API_KEY` | ✅ Já existe |
| `MINIMAX_GROUP_ID` | `MINIMAX_GROUP_ID` | ✅ Já existe |
| `RESEND_API_KEY` | (adicionar) | ➕ Nova |
| `FROM_EMAIL` | (adicionar) | ➕ Nova |

---

## ⚠️ IMPORTANTE: Não Remover Variáveis Existentes

**NÃO APAGUES** as tuas variáveis atuais:
- `GOOGLE_VISION_API_KEY`
- `GOOGLE_MAPS_API_KEY`
- `SUPABASE_DB_HOST`
- `TWILIO_*`
- etc.

Elas podem ser úteis no futuro ou para outros projetos. Apenas **ADICIONA** as novas.

---

## 🎯 Variáveis Mínimas para Começar

Para testar o projeto **AGORA**, só precisas de:

### Obrigatórias:
1. ✅ `SUPABASE_URL` (já preenchida acima)
2. ✅ `SUPABASE_ANON_KEY` (já preenchida acima)
3. ⚠️ `SUPABASE_SERVICE_ROLE_KEY` (obter do dashboard)
4. ⚠️ `DATABASE_URL` (preencher password)
5. ✅ `SECRET_KEY` (pode deixar o valor default por agora)

### Opcionais (podem ficar vazias):
- `GEMINI_API_KEY` (só para análises IA)
- `RESEND_API_KEY` (só para enviar emails)
- `OPENAI_API_KEY` (alternativa ao Gemini)

---

## ✅ Verificação Final

Depois de atualizar o `.env`, verifica se tem:

```bash
# No terminal:
cd src/backend
python -c "from config import settings; print('✅ Config OK!' if settings.supabase_url else '❌ Falta config')"
```

Se aparecer `✅ Config OK!`, está tudo pronto!

---

## 🚀 Próximo Passo

Depois de atualizar o `.env`:

```bash
# Testar backend
cd src/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Ir a http://localhost:8000/api/docs
```

---

**Ficheiro criado**: `UPDATE_ENV.md` ✅
**Próxima acção**: Copiar as variáveis adicionais para o teu `.env`

