# 🔴 GEMINI SAFETY BLOCK - Troubleshooting

## Status: ⚠️ Gemini continua a bloquear mesmo com BLOCK_NONE

### O que descobrimos:

Nos logs vês:
```
Gemini API error: finish_reason is 2 (SAFETY)
AI returned no normalized data
```

**Isto significa:**
- Gemini está a bloquear o conteúdo POR RAZÕES DE SEGURANÇA
- Mesmo com `safety_settings = BLOCK_NONE` em TODAS as categorias
- A API Gemini pode ter **limites hard-coded** que não podem ser desabilitados

---

## 🔍 Debugging melhorado

Agora quando o bloqueio ocorre, o sistema vai mostrar:
```
🔴 Gemini SAFETY BLOCK despite BLOCK_NONE settings!
Model: models/gemini-2.5-pro-latest
Safety ratings: [categoria que bloqueou]
```

Isto ajuda-nos a entender:
1. **Qual modelo** está a bloquear
2. **Qual categoria de segurança** está a causar o bloqueio
3. Se é um problema de conteúdo ou de configuração

---

## 🎯 Soluções possíveis

### Solução 1: Testar com job posting diferente
**Problema:** O conteúdo atual pode ter palavras/frases que triggam o filtro

**Teste:**
```
Job Posting SIMPLES para testar:
"Senior Python Developer needed. 5+ years experience. Remote work."
```

Se isto funcionar mas o job posting real não, o problema é no **conteúdo específico**.

### Solução 2: Usar Gemini 1.5 Pro em vez de 2.5
**Problema:** Modelos mais recentes podem ter filtros mais agressivos

**Mudança no código:**
```python
# em gemini_provider.py, preferred_order:
preferred_order = [
    "models/gemini-1.5-pro-latest",  # Mover para topo
    "models/gemini-2.5-pro-latest",
    ...
]
```

### Solução 3: Reformular o prompt
**Problema:** O prompt pode ter instruções que o Gemini interpreta como perigosas

**Exemplo de problema:**
```
"Extract dangerous content from job posting"  ❌
"Parse job requirements from posting"  ✅
```

### Solução 4: Usar Claude ou OpenAI temporariamente
**Problema:** Gemini pode ter restrições que não conseguimos contornar

**No .env:**
```bash
# Comentar Gemini temporariamente
# GEMINI_API_KEY=...

# Usar Claude como default
ANTHROPIC_API_KEY=sk-ant-...
```

Mas isto **contradiz** o requisito de "Gemini tem de funcionar" ⚠️

---

## 📋 Próximos passos de debug

### 1. Ver os logs detalhados
Quando testares novamente, procura por:
```
Gemini request to models/gemini-X with safety_settings: ALL categories set to BLOCK_NONE
```

E depois:
```
🔴 Gemini SAFETY BLOCK despite BLOCK_NONE settings!
Safety ratings: [...]
```

**Copia os safety ratings** e partilha comigo.

### 2. Testar com conteúdo minimalista
```
POST /api/interviewer/step2
{
  "raw_text": "Need Python developer",
  "session_id": "...",
  "language": "en"
}
```

Se isto funcionar, o problema é no **tamanho ou conteúdo** do job posting real.

### 3. Verificar versão da biblioteca
```bash
pip show google-generativeai
```

Se for muito antiga, atualizar:
```bash
pip install --upgrade google-generativeai
```

---

## 🔬 Teoria sobre o problema

**Hipótese 1: Gemini API tem "super safety" para certos tópicos**
- Recrutamento pode incluir termos sensíveis (salário, localização, requisitos físicos)
- Gemini pode ter lista negra de contextos que **nunca** aceita
- `BLOCK_NONE` só funciona para conteúdo "moderadamente seguro"

**Hipótese 2: Job posting contém trigger words**
- Palavras como "discrimination", "physical requirements", "background check"
- Mesmo em contexto profissional, podem triggar filtros
- Solução: Sanitizar o texto antes de enviar para Gemini

**Hipótese 3: Incompatibilidade de versão API**
- Biblioteca `google-generativeai` pode estar desatualizada
- Safety settings podem ter mudado de formato
- Solução: Atualizar para latest version

---

## ✅ O que ESTÁ a funcionar

Apesar do bloqueio:
1. ✅ Sistema não tenta OpenAI como fallback (corrigido)
2. ✅ Gemini tenta modelos diferentes internamente
3. ✅ Erro é explícito e detalhado
4. ✅ Step 1 funciona (sem IA)
5. ✅ Step 3 funciona (suggestions carregam do Step 2)

---

## 📞 Próxima ação

**Testa novamente** e partilha:
1. Os **safety ratings** completos do log
2. O **job posting** que estás a usar (primeiras linhas)
3. Qual **modelo Gemini** está a ser tentado

Com esta info posso ajustar a estratégia!

---

**Atualizado:** 2025-11-09 21:10  
**Status:** Debugging em progresso, aguardando mais info dos logs

