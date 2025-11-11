# ▶️ EXECUTAR TUDO COM 1 COMANDO!

## 🚀 **SCRIPT ÚNICO CRIADO!**

---

## ✅ **EXECUÇÃO SUPER SIMPLES**

### **Opção 1: Windows BAT (Mais Visual)**

```powershell
.\start.bat
```

**O que faz**:
- 🔄 Mata processos antigos
- 🐍 Abre janela do Backend
- ⚛️ Abre janela do Frontend
- ⏳ Aguarda inicialização
- ✅ Mostra URLs
- 🌐 Podes abrir http://localhost:3000

**Vantagem**: Vês os logs em janelas separadas

---

### **Opção 2: PowerShell (Mais Automático)**

```powershell
.\start.ps1
```

**O que faz**:
- 🔄 Mata processos antigos
- 🐍 Inicia Backend em background
- ⚛️ Inicia Frontend em background
- ⏳ Aguarda inicialização
- ✅ Mostra status
- ⚙️ Mantém-se a correr
- Ctrl+C para parar ambos

---

## 🎯 **RECOMENDAÇÃO: USA start.bat**

É mais fácil de ver o que está a acontecer!

```powershell
.\start.bat
```

Depois:
1. ✅ Vês 2 janelas aparecerem (Backend e Frontend)
2. ✅ Aguarda ~10 segundos
3. ✅ Abre http://localhost:3000
4. ✅ TESTA!

---

## 📋 **ALTERNATIVA: Manual (2 Terminais)**

Se os scripts não funcionarem:

**Terminal 1**:
```powershell
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
.\venv\Scripts\activate
python main.py
```

**Terminal 2**:
```powershell
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\frontend
npm run dev
```

---

## ✅ **DEPOIS DE EXECUTAR**

### **Verifica que está a correr**:

1. **Backend**: http://localhost:8000/health
   ```json
   {"status":"degraded",...}  // OK sem key
   ```

2. **Frontend**: http://localhost:3000
   ```
   Vês homepage ShortlistAI
   ```

3. **API Docs**: http://localhost:8000/api/docs
   ```
   Vês 21 endpoints documentados
   ```

---

## 🎉 **TUDO PRONTO!**

**Executa**:
```powershell
.\start.bat
```

**Aguarda**: ~10 segundos

**Abre**: http://localhost:3000

**Testa**: Os flows completos!

---

## ⚠️ **LEMBRA-TE**

Para **funcionalidade 100%**, adiciona ao `.env`:
```env
SUPABASE_SERVICE_ROLE_KEY=<tua_chave>
```

Ver: [⚠️_ADICIONAR_SUPABASE_KEY.md](⚠️_ADICIONAR_SUPABASE_KEY.md)

---

**EXECUTA .\start.bat E ESTÁ FEITO! 🚀**

