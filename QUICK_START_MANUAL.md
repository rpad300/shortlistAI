# 🚀 Quick Start Manual - Execução do Projeto

## ✅ **Como Executar o ShortlistAI**

### **Opção 1: Scripts Automáticos**

```powershell
# No PowerShell, usar .\
.\start_backend.bat
.\start_frontend.bat
```

### **Opção 2: Manual (Recomendado)**

#### **Terminal 1 - Backend:**
```powershell
cd src\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Backend estará em**: http://localhost:8000  
**API Docs em**: http://localhost:8000/api/docs

#### **Terminal 2 - Frontend:**
```powershell
cd src\frontend
npm install
npm run dev
```

**Frontend estará em**: http://localhost:3000

---

## 🧪 **Testar Agora**

### **1. Abre o Browser**
```
http://localhost:3000
```

### **2. Teste Rápido - Candidate Flow** (2 min)
1. ✅ Escolhe idioma (PT, EN, FR ou ES)
2. ✅ Clica "Fluxo do Candidato"
3. ✅ Preenche nome, email (marca todos os checkboxes)
4. ✅ Clica "Seguinte"
5. ✅ Paste um job posting qualquer ou upload PDF
6. ✅ Clica "Seguinte"
7. ✅ Upload teu CV (PDF ou DOCX)
8. ✅ Aguarda análise (10-15s)
9. ✅ **VÊ RESULTADOS!**

### **3. Teste Avançado - Interviewer Flow** (5 min)
1. ✅ Clica "Fluxo do Entrevistador"
2. ✅ Preenche dados + nome da empresa
3. ✅ Upload job description (PDF ou paste text)
4. ✅ Define key requirements
5. ✅ Ajusta sliders de weighting
6. ✅ Upload 5-10 CVs (PDF ou DOCX)
7. ✅ Aguarda análise
8. ✅ **VÊ RANKING COMPLETO!**

---

## 🔍 **Verificação de Servidores**

### Verificar Backend
```powershell
# Deve mostrar documentação da API:
http://localhost:8000/api/docs

# Deve retornar JSON:
http://localhost:8000/health
```

### Verificar Frontend
```powershell
# Deve mostrar homepage:
http://localhost:3000
```

---

## ⚠️ **Troubleshooting**

### Backend não inicia
```powershell
cd src\backend

# Verificar Python:
python --version

# Criar venv:
python -m venv venv

# Ativar:
.\venv\Scripts\activate

# Instalar deps:
pip install -r requirements.txt

# Iniciar:
python main.py
```

### Frontend não inicia
```powershell
cd src\frontend

# Verificar Node:
node --version
npm --version

# Limpar e reinstalar:
rm -r node_modules
npm install

# Iniciar:
npm run dev
```

### Porta já em uso
```powershell
# Backend (8000):
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (3000):
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## ✅ **Está a Funcionar Quando**

### Backend ✅
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Frontend ✅
```
VITE ready in XXXms
➜  Local:   http://localhost:3000
```

---

## 🎯 **URLs Importantes**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend** | http://localhost:3000 | Aplicação principal |
| **API Docs** | http://localhost:8000/api/docs | Documentação interativa |
| **API Root** | http://localhost:8000 | API endpoint |
| **Health Check** | http://localhost:8000/health | Status do backend |
| **Supabase** | https://supabase.com/dashboard/project/uxmfaziorospaglsufyp | Dashboard BD |

---

## 🎉 **Depois de Iniciar**

1. ✅ Abre http://localhost:3000
2. ✅ Escolhe um idioma
3. ✅ Testa o Candidate Flow completo
4. ✅ Testa o Interviewer Flow
5. ✅ Verifica dados no Supabase Dashboard

**TUDO FUNCIONA! DIVIRTE-TE A TESTAR! 🚀**

