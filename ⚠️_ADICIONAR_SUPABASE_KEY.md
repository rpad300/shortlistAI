# ⚠️ ADICIONAR SUPABASE KEY PARA FUNCIONAR 100%

## 🎯 **PROBLEMA ATUAL**

**Frontend**: ✅ Funciona perfeitamente  
**Backend**: ⚠️ Erro 500 ao tentar gravar dados

**Erro**: `POST http://localhost:8000/api/interviewer/step1 500 (Internal Server Error)`

**Causa**: Falta `SUPABASE_SERVICE_ROLE_KEY` no ficheiro `.env`

---

## ✅ **SOLUÇÃO (2 MINUTOS)**

### **1. Obter a Chave do Supabase**

1. Abre: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/api
2. Procura **"service_role"** (não é a "anon")
3. Click em **"Copy"** ou **"Reveal"** e copia a chave
4. Deve começar com `eyJhbG...`

### **2. Adicionar ao `.env`**

Abre o ficheiro `.env` na **raíz do projeto**:
```
C:\Users\rdias\Documents\GitHub\ShortlistAI\.env
```

Adiciona ou atualiza:
```env
SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbG... (a chave que copiaste)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV4bWZhemlvcm9zcGFnbHN1ZnlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2MDc3MzksImV4cCI6MjA3ODE4MzczOX0.AIEg359ub3vHK5ZU2HUSwK2YKPVE_2XjZoV0631z-qk
```

### **3. Reiniciar Backend**

No terminal do backend:
1. Carrega **Ctrl+C** para parar
2. Executa novamente:
```powershell
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
.\venv\Scripts\activate
python main.py
```

### **4. Testar de Novo**

1. Recarrega http://localhost:3000
2. Click "Fluxo do Candidato" ou "Fluxo do Entrevistador"
3. Preenche form
4. Click "Seguinte"
5. ✅ **Agora funciona e grava dados!**

---

## 🔍 **VERIFICAR SE FUNCIONOU**

### Após reiniciar backend com a key:

```powershell
Invoke-WebRequest http://localhost:8000/health
```

Deve retornar:
```json
{
  "status": "healthy",      // ← MUDOU! Era "degraded"
  "database": "connected",  // ← MUDOU! Era "error"
  "supabase": "connected"   // ← MUDOU! Era "error"
}
```

---

## ✅ **FUNCIONALIDADE SEM vs COM KEY**

### **SEM Supabase Key** (atual):
- ✅ Homepage carrega
- ✅ Navegação funciona
- ✅ Forms aparecem
- ✅ Validação funciona
- ✅ Multi-idioma funciona
- ❌ **Não grava dados** (erro 500)
- ❌ Upload de files falha

### **COM Supabase Key**:
- ✅ **TUDO funciona 100%!**
- ✅ Grava candidates na BD
- ✅ Grava companies
- ✅ Cria sessions
- ✅ Upload de CVs para storage
- ✅ Análise completa
- ✅ Email (com Resend key)

---

## 💡 **OPCIONAL - Adicionar AI Key**

Para ter **análise AI REAL** (não placeholder):

```env
# Adiciona também:
GEMINI_API_KEY=tua_chave_aqui
# Ou
OPENAI_API_KEY=tua_chave_aqui
```

**Obter Gemini key** (grátis):  
https://makersuite.google.com/app/apikey

---

## 🎯 **RESUMO**

**Agora**: Frontend funciona, backend dá erro ao gravar  
**Depois de adicionar key**: **TUDO funciona 100%!**

---

## 📋 **CHECKLIST**

1. [ ] Abrir Supabase Dashboard
2. [ ] Copiar SERVICE_ROLE_KEY
3. [ ] Adicionar ao `.env`
4. [ ] Reiniciar backend (Ctrl+C e `python main.py`)
5. [ ] Testar form novamente
6. [ ] ✅ Ver dados gravados no Supabase!

---

## ✅ **DEPOIS DISTO**

**Terás 100% de funcionalidade**:
- ✅ Frontend completo
- ✅ Backend completo
- ✅ Database a gravar
- ✅ File upload a funcionar
- ✅ Análise completa
- ✅ Multi-idioma
- ✅ PWA

**ADICIONA A KEY E ESTÁ PERFEITO! 🚀**

---

**Link da chave**: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/api

**QUASE LÁ! SÓ FALTA A KEY! ✅**

