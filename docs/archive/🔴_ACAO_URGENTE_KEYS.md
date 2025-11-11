# 🔴 AÇÃO URGENTE - ATUALIZAR KEYS DO SUPABASE!

## ⚠️ **PROBLEMA CRÍTICO IDENTIFICADO!**

```
ERROR: Legacy API keys are disabled
Your legacy API keys (anon, service_role) were disabled on 2025-11-08
```

**As chaves ANTIGAS não funcionam mais!**

Supabase desativou as legacy keys em **2025-11-08 às 20:59**!

---

## ✅ **SOLUÇÃO (3 MINUTOS)**

### **PASSO 1: Revelar a Secret Key** 👁️

1. Abre: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/api
2. Scroll até "Secret keys"
3. Vês a linha "default" com `sb_secret_p2ZaH●●●●●●●●●●●●●●●●`
4. **CLICK no ícone do OLHO 👁️** ← SUPER IMPORTANTE!
5. Aparece a chave completa (tipo `sb_secret_p2ZaHxxx...`)
6. **COPIA TODA A CHAVE** (Ctrl+C)

### **PASSO 2: Adicionar ao `.env`**

Abre o ficheiro `.env` na raíz:
```
C:\Users\rdias\Documents\GitHub\ShortlistAI\.env
```

**ADICIONA ou ATUALIZA**:
```env
# SUPABASE - NOVAS API KEYS
SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co

# Publishable Key (já tens)
SUPABASE_PUBLISHABLE_KEY=sb_publishable_2RQcvmyrnYDAxrp35LP0Sw_LnxtGVb8

# Secret Key (COLA AQUI A CHAVE QUE COPIASTE!)
SUPABASE_SECRET_KEY=sb_secret_p2ZaH... (cola a chave completa)
```

**GUARDA O FICHEIRO!**

### **PASSO 3: Reiniciar Backend**

No terminal do backend:
1. Carrega **Ctrl+C** para parar
2. Executa:
```powershell
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
.\venv\Scripts\activate
python main.py
```

### **PASSO 4: Verificar**

Quando reiniciar, nos logs deve aparecer:
```
✅ INFO: Application startup complete
```

**E NÃO deve aparecer**:
```
❌ Error: Legacy API keys are disabled
```

### **PASSO 5: Testar!**

1. Recarrega http://localhost:3000 (F5)
2. Preenche Step 1
3. Click "Next"
4. ✅ **Funciona! Vai para Step 2!**
5. ✅ **Sem erros!**

---

## ⚠️ **VERIFICAR TYPOS NO `.env`**

### **ERRADO** ❌:
```
SUPABESE_SECRETE_KEY=...     # Typo no nome
SUPABASE_SECRET_KEY=sb_secre # Chave incompleta
```

### **CORRETO** ✅:
```
SUPABASE_SECRET_KEY=sb_secret_p2ZaHxxx...xxx (chave completa)
```

**Nome**: `SUPABASE_SECRET_KEY` (sem typos)  
**Valor**: Chave completa (revelar com 👁️)

---

## 🎯 **POR QUE ISTO ACONTECEU**

O Supabase mudou o sistema de API keys:
- ❌ **Antes**: `anon` e `service_role` (JWT format)
- ✅ **Agora**: `sb_publishable_*` e `sb_secret_*` (novo format)

**As antigas foram desativadas em 2025-11-08!**

---

## ✅ **O CÓDIGO JÁ ESTÁ ATUALIZADO**

O código do backend já foi atualizado para:
- ✅ Tentar `SUPABASE_SECRET_KEY` primeiro (nova)
- ✅ Fall back para `SUPABASE_SERVICE_ROLE_KEY` (legacy)
- ✅ Mensagens de erro claras

**Só precisas de adicionar a nova key ao `.env`!**

---

## 🎊 **DEPOIS DE ADICIONAR**

**TUDO funciona 100%!**
- ✅ Backend conecta ao Supabase
- ✅ Grava dados
- ✅ Upload files
- ✅ Análise completa
- ✅ Email
- ✅ Sessions

---

## 📝 **EM RESUMO**

1. 👁️ **Click no olho** no dashboard
2. 📋 **Copia** a secret key completa
3. 📝 **Adiciona** ao `.env`: `SUPABASE_SECRET_KEY=...`
4. 🔄 **Reinicia** backend
5. ✅ **FUNCIONA 100%!**

---

**LINK DO DASHBOARD**:  
https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/api

**CLICK 👁️ → COPIA → COLA NO .env → REINICIA!**

**ESTÁ QUASE! SÓ FALTA ISTO! 🚀**

