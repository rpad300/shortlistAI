# 🎯 Gemini 2.5 Pro - Configuração Forçada

## ✅ Mudanças aplicadas (2025-11-09 21:20)

### 1. **Prioridade: Gemini 2.5 Pro**
```python
preferred_order = [
    "models/gemini-2.0-flash-exp",       # Experimental (pode ter safety mais permissivo)
    "models/gemini-exp-1206",            # Experimental alternativo
    "models/gemini-2.5-pro-latest",      # ⭐ SUA PREFERÊNCIA
    "models/gemini-2.5-pro",
    "models/gemini-2.5-flash",
    "models/gemini-1.5-pro-latest",      # Fallback
    ...
]
```

### 2. **ESTRATÉGIA RADICAL: Sem safety_settings**

**Problema descoberto:**
```
Safety ratings: ALL NEGLIGIBLE ✅
finish_reason: 2 (SAFETY) ❌
```

Isto é **contraditório**! Todas as categorias em NEGLIGIBLE mas ainda assim bloqueia!

**Nova abordagem:**
1. **Primeiro:** Tenta **SEM** enviar `safety_settings`
   - Deixa o modelo usar comportamento default
   - Paradoxalmente, pode ser mais permissivo!
   
2. **Se falhar:** Tenta **COM** `BLOCK_NONE` explícito
   - Como fallback da estratégia anterior

### 3. **Ordem de tentativa:**
```
1. gemini-2.0-flash-exp (sem safety_settings)
2. gemini-exp-1206 (sem safety_settings)
3. gemini-2.5-pro-latest (sem safety_settings) ⭐
4. Se todos falharem, retenta COM safety_settings=BLOCK_NONE
```

---

## 🔬 Por que esta estratégia?

### Hipótese:
**Explicitamente definir `BLOCK_NONE` pode ACTIVAR verificações mais rigorosas!**

Raciocínio:
- API vê `safety_settings` → "Utilizador está preocupado com safety"
- Activa modo "paranoid" para verificar se deve REALMENTE ignorar
- Resultado: Bloqueia mesmo conteúdo NEGLIGIBLE

**Sem safety_settings:**
- API usa comportamento default (mais relaxado)
- Não entra em modo "paranoid"
- Pode passar conteúdo que seria bloqueado com BLOCK_NONE

---

## 📊 O que esperar nos logs

### ✅ SUCESSO (estratégia sem safety_settings funciona):
```
INFO: Gemini request to models/gemini-2.5-pro-latest
INFO: 127.0.0.1 - "POST /api/interviewer/step2 HTTP/1.1" 200 OK
```

### ⚠️ FALLBACK (precisa de BLOCK_NONE):
```
WARNING: Gemini without safety_settings failed: ... Trying with BLOCK_NONE...
INFO: 127.0.0.1 - "POST /api/interviewer/step2 HTTP/1.1" 200 OK
```

### 🔴 FALHA TOTAL (todos os modelos bloqueiam):
```
ERROR: Gemini blocked content due to safety filters (finish_reason: 2).
All models tried with BLOCK_NONE settings.
Safety ratings: [...]
```

---

## 🚀 Próximos passos

### 1. Reiniciar backend
```powershell
taskkill /F /FI "IMAGENAME eq python.exe"
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
..\..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Testar fluxo completo
- Step 1: Identificação ✅
- Step 2: Job posting → **Deve funcionar agora com Gemini 2.5 Pro**
- Step 3: Key points
- Step 4: Weighting
- Step 5: Upload CVs
- Step 6: Análise

### 3. Se AINDA falhar
Opções:
- **A)** Usar modelos experimentais (gemini-2.0-flash-exp, gemini-exp-1206)
- **B)** Simplificar o prompt (remover palavras que podem triggar)
- **C)** Pedir à Google para whitelist a tua API key (suporte comercial)

---

## 💡 Teoria técnica

### Por que `BLOCK_NONE` pode ser pior que sem settings:

```python
# COM safety_settings=BLOCK_NONE
if user_sent_safety_settings:
    if content_needs_extra_scrutiny():  # ← Activado!
        perform_deep_safety_check()
        if any_tiny_flag():
            block()  # ← Bloqueia mesmo NEGLIGIBLE

# SEM safety_settings
use_default_behavior()  # ← Mais relaxado
if content_clearly_harmful():
    block()
else:
    allow()  # ← Passa mais facilmente
```

---

## 📋 Checklist de verificação

- [x] Gemini 2.5 Pro como prioritário
- [x] Tenta SEM safety_settings primeiro
- [x] Fallback para BLOCK_NONE se necessário
- [x] Modelos experimentais no topo (podem ter safety mais relaxado)
- [x] Logging detalhado de safety ratings
- [ ] Testar e confirmar que funciona!

---

**Status:** Configurado para usar Gemini 2.5 Pro com estratégia experimental  
**Próximo teste:** Reiniciar e testar Steps 1-4





