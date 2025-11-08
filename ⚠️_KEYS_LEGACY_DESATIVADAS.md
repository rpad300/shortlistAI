# ⚠️ LEGACY KEYS DESATIVADAS - USAR NOVAS KEYS!

## 🔴 **PROBLEMA IDENTIFICADO!**

```
ERROR: Legacy API keys are disabled
Legacy API keys (anon, service_role) were disabled on 2025-11-08
```

**As chaves antigas foram DESATIVADAS!**

Tens de usar as **NOVAS keys**: `sb_publishable_*` e `sb_secret_*`

---

## ✅ **SOLUÇÃO IMEDIATA**

### **No teu `.env`, ASSEGURA que tens**:

```env
# SUPABASE - NOVAS API KEYS (Obrigatório!)
SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co

# Nova Publishable Key (pública)
SUPABASE_PUBLISHABLE_KEY=sb_publishable_2RQcvmyrnYDAxrp35LP0Sw_LnxtGVb8

# Nova Secret Key (IMPORTANTE - revelar no dashboard!)
SUPABASE_SECRET_KEY=sb_secret_p2ZaH... (click olho 👁️ para ver completa)
```

---

## 👁️ **REVELAR SECRET KEY**

1. Vai ao dashboard: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/api
2. Na secção "Secret keys"
3. Linha "default"
4. **Click no ícone do olho 👁️** ← IMPORTANTE!
5. Aparece: `sb_secret_p2ZaH...` (chave completa)
6. **Copia TODA a chave**
7. Cola no `.env` em `SUPABASE_SECRET_KEY=`

---

## ⚠️ **CUIDADO COM TYPOS!**

Se tens isto no `.env`:
```
SUPABESE_SECRETE_KEY=...  ❌ ERRADO (typo)
```

Deve ser:
```
SUPABASE_SECRET_KEY=...  ✅ CORRETO
```

**Nota os typos**:
- `SUPABESE` → `SUPABASE` ✅
- `SECRETE` → `SECRET` ✅

---

## 🔄 **DEPOIS DE ADICIONAR**

### **1. Verifica `.env`**:
```env
SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co
SUPABASE_SECRET_KEY=sb_secret_p2ZaH... (chave completa)
```

### **2. Reinicia Backend**:
```powershell
# Para (Ctrl+C)
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
.\venv\Scripts\activate
python main.py
```

### **3. Verifica Logs**:
Quando reiniciar, **NÃO** deve aparecer:
```
❌ Error: Legacy API keys are disabled
```

Deve aparecer:
```
✅ INFO: Application startup complete
```

### **4. Testa de Novo**:
1. Recarrega http://localhost:3000
2. Preenche Step 1
3. ✅ **Agora grava sem erro!**

---

## 📋 **CHECKLIST**

- [ ] Click 👁️ no dashboard para revelar secret key
- [ ] Copiar chave completa (começa com `sb_secret_`)
- [ ] Verificar que **NÃO há typos** no `.env`
  - `SUPABASE_SECRET_KEY` ✅ (não `SUPABESE_SECRETE_KEY`)
- [ ] Adicionar chave ao `.env`
- [ ] Reiniciar backend
- [ ] Verificar logs (sem erro "Legacy keys")
- [ ] Testar
- [ ] ✅ **Funciona!**

---

## 🎯 **DEPOIS DISTO**

**TUDO funciona 100%!**
- ✅ Gravar dados na BD
- ✅ Upload de ficheiros
- ✅ Sessions persistentes
- ✅ Análise completa

---

## 🔑 **RESUMO**

**Problema**: Legacy keys desativadas  
**Solução**: Usar novas keys (sb_secret_*)  
**Ação**: Revelar secret key e adicionar ao `.env`  
**Depois**: ✅ Tudo funciona!

---

**CLICK 👁️ PARA REVELAR A SECRET KEY E ADICIONA AO .env!**

**ESTÁ QUASE! 🚀**

