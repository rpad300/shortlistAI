# 🚀 COMO EXECUTAR O SHORTLISTAI

**Guia passo-a-passo simples**

---

## 📝 **PRÉ-REQUISITOS**

1. ✅ Python 3.13 instalado
2. ✅ Node.js instalado
3. ✅ Ficheiro `.env` na raíz com SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY

---

## 🎯 **EXECUTAR EM 2 TERMINAIS**

### **TERMINAL 1 - BACKEND** (FastAPI)

```powershell
# 1. Vai para pasta do backend:
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend

# 2. Ativa o virtual environment:
.\venv\Scripts\activate

# 3. (Opcional) Se deps não instaladas:
pip install fastapi uvicorn supabase python-multipart python-dotenv pydantic-settings openai anthropic google-generativeai resend PyPDF2 python-docx python-jose[cryptography] passlib[bcrypt] email-validator

# 4. Inicia o servidor:
python main.py
```

**Esperado**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **Backend a correr em**: http://localhost:8000  
📚 **API Docs em**: http://localhost:8000/api/docs

---

### **TERMINAL 2 - FRONTEND** (React + Vite)

```powershell
# 1. Vai para pasta do frontend:
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\frontend

# 2. (Opcional) Se deps não instaladas:
npm install

# 3. Inicia o dev server:
npm run dev
```

**Esperado**:
```
VITE ready in XXX ms

➜  Local:   http://localhost:3000
➜  Network: use --host to expose
```

✅ **Frontend a correr em**: http://localhost:3000

---

## 🌐 **ABRIR NO BROWSER**

```
http://localhost:3000
```

Deves ver:
- ✅ Homepage do ShortlistAI
- ✅ Botões de idiomas (EN, PT, FR, ES)
- ✅ 2 cards: "Interviewer Flow" e "Candidate Flow"

---

## 🧪 **TESTAR AGORA!**

### **Teste Rápido - Candidate Flow** (2 min)

1. Click **"Fluxo do Candidato"** (ou muda idioma primeiro)
2. Preenche:
   - Nome: João Silva
   - Email: joao@test.com
   - Marca **TODOS os 4 checkboxes** ← Importante!
3. Click "Seguinte"
4. **Step 2**: Paste um job description qualquer OU upload PDF
5. Click "Seguinte"
6. **Step 3**: Upload o teu CV (PDF ou DOCX)
7. Click "Analyze My Fit"
8. Aguarda 10-15 segundos
9. ✅ **VÊ RESULTADOS**: Scores, questions, intro pitch!

---

## ⚙️ **TROUBLESHOOTING**

### Backend não inicia?

```powershell
# Verifica se Python funciona:
python --version

# Verifica se estás no diretório correto:
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
dir main.py  # Deve existir

# Cria venv se não existe:
python -m venv venv

# Ativa:
.\venv\Scripts\activate

# Reinstala deps:
pip install fastapi uvicorn supabase python-multipart python-dotenv pydantic-settings email-validator

# Tenta novamente:
python main.py
```

### Frontend não inicia?

```powershell
# Verifica Node:
node --version
npm --version

# Verifica diretório:
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\frontend
dir package.json  # Deve existir

# Reinstala deps:
npm install

# Tenta novamente:
npm run dev
```

### Porta já em uso?

```powershell
# Backend (porta 8000):
netstat -ano | findstr :8000
# Mata o processo se necessário

# Frontend (porta 3000):
netstat -ano | findstr :3000
# Mata o processo se necessário
```

---

## 📍 **ONDE ESTÃO OS FICHEIROS**

```
C:\Users\rdias\Documents\GitHub\ShortlistAI\
├── src\
│   ├── backend\          ← TERMINAL 1 aqui
│   │   ├── main.py       ← Inicia com: python main.py
│   │   ├── venv\         ← Virtual environment
│   │   └── requirements.txt
│   │
│   └── frontend\         ← TERMINAL 2 aqui
│       ├── package.json  ← Tem aqui
│       ├── src\
│       └── node_modules\ ← Criado após npm install
│
└── .env                  ← Config na raíz
```

---

## ✅ **VERIFICAÇÃO RÁPIDA**

### Backend está a correr?
```
http://localhost:8000/health
```
Deve retornar JSON com status

### Frontend está a correr?
```
http://localhost:3000
```
Deve mostrar a homepage

---

## 🎯 **COMANDOS RÁPIDOS (COPIA E COLA)**

### Terminal 1 (Backend):
```powershell
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
.\venv\Scripts\activate
python main.py
```

### Terminal 2 (Frontend):
```powershell
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\frontend
npm run dev
```

### Browser:
```
http://localhost:3000
```

---

## 🎉 **ESTÁ PRONTO!**

**Depois de executar os 2 terminais**:
- ✅ Backend em http://localhost:8000
- ✅ Frontend em http://localhost:3000
- ✅ Podes testar os flows completos!

**DIVIRTE-TE A TESTAR! 🚀**

