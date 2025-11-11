# 🔑 NOVA INTEGRAÇÃO SUPABASE - API KEYS ATUALIZADAS!

## ✅ **CÓDIGO ATUALIZADO PARA NOVAS KEYS!**

O Supabase tem **novas API keys** e o código foi atualizado!

---

## 📝 **ADICIONA AO `.env`**

```env
# SUPABASE - Nova Integração
SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co

# Nova Publishable Key
SUPABASE_PUBLISHABLE_KEY=sb_publishable_2RQcvmyrnYDAxrp35LP0Sw_LnxtGVb8

# Nova Secret Key (IMPORTANTE - Esta é a chave secreta!)
SUPABASE_SECRET_KEY=sb_secret_p2ZaH... (clica no olho 👁️ para ver completa)

# Frontend
VITE_SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_2RQcvmyrnYDAxrp35LP0Sw_LnxtGVb8
```

---

## 🔍 **ONDE OBTER AS CHAVES**

Na imagem que mostraste:

### **Publishable Key** (Pública - OK para frontend):
```
sb_publishable_2RQcvmyrnYDAxrp35LP0Sw_LnxtGVb8
```
✅ Já vi na tua imagem!

### **Secret Key** (Secreta - Backend only):
```
sb_secret_p2ZaH●●●●●●●●●●●●●●●●
```
⚠️ **Click no ícone do olho (👁️) para revelar a chave completa!**

---

## ⚙️ **CÓDIGO JÁ ATUALIZADO**

O código do backend já foi atualizado para:
1. ✅ Tentar usar `SUPABASE_SECRET_KEY` primeiro (nova)
2. ✅ Se não existir, usar `SUPABASE_SERVICE_ROLE_KEY` (legacy)
3. ✅ Compatível com ambos os sistemas!

---

## 🎯 **PRÓXIMOS PASSOS**

### **1. Revelar Secret Key**
- No dashboard do Supabase
- Na linha "default" em "Secret keys"
- Click no ícone do **olho 👁️**
- Copia a chave completa que aparece

### **2. Atualizar `.env`**

Abre `.env` e adiciona/atualiza:
```env
SUPABASE_URL=https://uxmfaziorospaglsufyp.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_2RQcvmyrnYDAxrp35LP0Sw_LnxtGVb8
SUPABASE_SECRET_KEY=sb_secret_... (cola a chave completa aqui)
```

### **3. Reiniciar Backend**

```powershell
# Para o backend (Ctrl+C)

# Reinicia:
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
.\venv\Scripts\activate
python main.py
```

### **4. Testar**

1. Recarrega http://localhost:3000
2. Testa qualquer flow
3. ✅ **Agora grava dados!**

---

## ✅ **VERIFICAR SE FUNCIONOU**

Depois de reiniciar com as novas keys:

```powershell
Invoke-WebRequest http://localhost:8000/health
```

Deve retornar:
```json
{
  "status": "healthy",      // ✅ MUDOU!
  "database": "connected",  // ✅ MUDOU!
  "supabase": "connected"   // ✅ MUDOU!
}
```

---

## 🎊 **DEPOIS DISSO**

**TUDO funciona 100%!**
- ✅ Gravar dados na BD
- ✅ Upload de ficheiros
- ✅ Análise completa
- ✅ Email
- ✅ Sessions persistentes

---

## 📋 **CHECKLIST**

1. [ ] Click olho 👁️ para revelar secret key
2. [ ] Copiar chave completa
3. [ ] Adicionar ao `.env`
4. [ ] Reiniciar backend
5. [ ] Testar
6. [ ] ✅ **Ver status "healthy"!**

---

## 🔑 **RESUMO DAS KEYS**

| Key | Valor | Usar em |
|-----|-------|---------|
| SUPABASE_URL | https://uxmfaziorospaglsufyp.supabase.co | Backend e Frontend |
| SUPABASE_PUBLISHABLE_KEY | sb_publishable_2RQcvmyrnYDAxrp35LP0Sw_LnxtGVb8 | Frontend |
| SUPABASE_SECRET_KEY | sb_secret_p2ZaH... (revelar) | **Backend** |

---

**CLICK NO OLHO 👁️ PARA REVELAR A SECRET KEY!**

**DEPOIS ADICIONA AO .env E REINICIA!**

**ESTÁ QUASE! 🚀**

