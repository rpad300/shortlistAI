# ⚠️ Problemas de AI Provider e Soluções

## ✅ CORREÇÃO CRÍTICA APLICADA (2025-11-09 21:00)

### **NO CROSS-PROVIDER FALLBACK**

**O sistema agora NÃO tenta outros providers se Gemini falhar!**

#### Comportamento anterior (INCORRETO):
```
Gemini falha → Tenta OpenAI → Tenta Claude → Erro
```

#### Comportamento novo (CORRETO):
```
Gemini falha → ERRO IMEDIATO (sem tentar outros providers)
```

#### Fallback que AINDA funciona (dentro do mesmo provider):
```
Gemini: gemini-2.5-pro → gemini-2.5-flash → gemini-1.5-pro → gemini-pro
OpenAI: gpt-4.1-mini → gpt-4o-mini → gpt-4-turbo → gpt-3.5-turbo
```

---

## 🔴 Status atual (2025-11-09 21:00)

### Problema 1: Gemini bloqueia conteúdo (finish_reason: 2 - SAFETY)
**✅ CORRIGIDO** - Safety settings ajustadas para aceitar conteúdo de recrutamento

**Ficheiro:** `src/backend/services/ai/gemini_provider.py`

**Mudança:**
```python
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
```

### Problema 2: Sistema tentava OpenAI quando Gemini falhava
**✅ CORRIGIDO** - Cross-provider fallback desativado em `AIManager`

**Ficheiro:** `src/backend/services/ai/manager.py`

**Mudança:**
```python
async def execute(..., enable_fallback: bool = False):  # Era True, agora False
    # NO CROSS-PROVIDER FALLBACK
    # If the primary provider fails, we return the error directly
```

---

## 🎯 O que isto significa

1. **Gemini É OBRIGATÓRIO** - Se não funcionar, o sistema para
2. **OpenAI/Claude/outros NÃO são usados automaticamente**
3. **Qualidade consistente** - Não há mistura de estilos de providers diferentes
4. **Erros explícitos** - Utilizador vê claramente quando Gemini falha

---

## 🔧 Próximas ações

### 1. Reiniciar o backend
O backend precisa recarregar com as novas mudanças:

```powershell
# Matar processos
taskkill /F /FI "IMAGENAME eq python.exe"

# Reiniciar
cd C:\Users\rdias\Documents\GitHub\ShortlistAI\src\backend
..\..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Testar com Gemini apenas
- [ ] Step 1: Identificação
- [ ] Step 2: Job posting (deve usar Gemini com safety settings fix)
- [ ] Step 3: Key points
- [ ] Step 4: Weighting suggestions (deve usar Gemini)
- [ ] Step 5: Upload CVs
- [ ] Step 6: Análise com AI (deve usar Gemini)

### 3. Se Gemini continuar a falhar
**Logs esperados (BOM):**
```
INFO: Gemini provider initialized with model: models/gemini-2.5-pro-latest
INFO: 127.0.0.1 - "POST /api/interviewer/step2 HTTP/1.1" 200 OK
```

**Logs de erro (ESPERADO se Gemini falhar):**
```
ERROR: AI failed to generate weighting suggestions. Cannot proceed without AI.
INFO: 127.0.0.1 - "GET /api/interviewer/step4/suggestions/... HTTP/1.1" 500 Internal Server Error
```

**Logs que NÃO devem aparecer:**
```
Provider gemini failed, trying fallback  ❌ ISTO NÃO DEVE MAIS ACONTECER
```

---

## 📊 Configuração recomendada do .env

**Mínimo (só Gemini):**
```bash
GEMINI_API_KEY=AIza...
```

**Opcional (outros providers, mas NÃO usados como fallback):**
```bash
# Comentar ou remover se não quiser que sejam inicializados
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

---

**Última atualização:** 2025-11-09 21:00  
**Status:** ✅ Correções aplicadas, aguardando reinício do backend para teste


