# 🔴 Problemas em Produção - Soluções

**Data**: 11 de Janeiro de 2025

---

## 📋 Problemas Identificados

### 1. **Erro 404: CSS não encontrado**
```
index-DBiVQeX1.css:1 Failed to load resource: the server responded with a status of 404 (Not Found)
```

### 2. **Erro 500: Falha ao criar job posting**
```
POST https://shortlistai.net/api/interviewer/step2 500 (Internal Server Error)
[API] Response error: 500 {detail: 'Failed to create job posting record'}
```

---

## 🔧 Soluções

### Problema 1: CSS 404 (Frontend Build/Cache)

**Causa**: O navegador está tentando carregar um arquivo CSS com hash antigo que não existe mais. Isso pode acontecer por:
- Cache do navegador com versão antiga
- Service Worker servindo versão antiga
- Build não atualizado corretamente

**Soluções**:

#### **A. Limpar Cache e Service Worker (Imediato)**
```javascript
// No console do navegador (F12)
// 1. Desregistrar service workers
navigator.serviceWorker.getRegistrations().then(function(registrations) {
  for(let registration of registrations) {
    registration.unregister();
  }
});

// 2. Limpar cache
caches.keys().then(function(names) {
  for (let name of names) caches.delete(name);
});

// 3. Hard reload
location.reload(true);
```

#### **B. Verificar Build do Frontend**
```bash
cd src/frontend
npm run build

# Verificar se os arquivos CSS foram gerados
ls -la dist/assets/*.css
```

#### **C. Atualizar Vite Config para Forçar Invalidação de Cache**
O `vite.config.ts` já está configurado corretamente, mas podemos adicionar:
- Versionamento manual dos assets
- Configuração de headers de cache no servidor

**Nota**: Este é principalmente um problema de deploy/cache. Após fazer o novo build e deploy, os usuários precisarão fazer hard refresh (Ctrl+Shift+R).

---

### Problema 2: Erro 500 - Failed to create job posting (Backend)

**Causa**: O `job_posting_service.create()` está retornando `None` ou falhando silenciosamente.

**Localização do Código**: `src/backend/routers/interviewer.py:317-329`

**Possíveis Causas**:
1. Erro no banco de dados (constraints, foreign keys)
2. Dados inválidos sendo passados
3. Erro no service de job posting

**Soluções**:

#### **A. Verificar Logs do Backend**
```bash
# Verificar logs do backend em produção
# Procurar por:
- "Error in step2_job_posting"
- "Failed to create job posting record"
- Erros de database/exceptions
```

#### **B. Verificar Service de Job Posting**
O service está em `src/backend/services/database/job_posting_service.py` (assumindo estrutura padrão).

**Verificar**:
1. Se `job_posting_service.create()` está retornando o registro criado
2. Se há erros de validação de dados
3. Se há problemas com foreign keys (company_id, interviewer_id)

#### **C. Adicionar Mais Logging (Temporário para Debug)**
No arquivo `src/backend/routers/interviewer.py`, linha ~317:

```python
# Antes de criar job posting
logger.info(f"Creating job posting with data: raw_text_length={len(final_text)}, company_id={session['data'].get('company_id')}, interviewer_id={session['data'].get('interviewer_id')}")

try:
    job_posting = await job_posting_service.create(
        raw_text=final_text,
        company_id=session["data"].get("company_id"),
        interviewer_id=session["data"].get("interviewer_id"),
        file_url=file_url,
        language=session_language
    )
    
    if not job_posting:
        logger.error(f"job_posting_service.create() returned None for session: {session_id}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create job posting record"
        )
except Exception as e:
    logger.error(f"Exception in job_posting_service.create(): {e}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail=f"Failed to create job posting record: {str(e)}"
    )
```

#### **D. Verificar Database Constraints**
Possíveis problemas:
- `company_id` ou `interviewer_id` não existem no banco
- Campos obrigatórios faltando
- Validações de tamanho/texto

---

## 🚀 Plano de Ação Imediato

### **Passo 1: Frontend (CSS 404)**
1. ✅ Fazer novo build do frontend
2. ✅ Deploy do novo build
3. ✅ Limpar cache do CDN/servidor (se aplicável)
4. ⚠️ Instruir usuários a fazer hard refresh (Ctrl+Shift+R)

### **Passo 2: Backend (500 Error)**
1. ✅ Verificar logs do backend
2. ✅ Verificar se o job_posting_service está funcionando
3. ✅ Adicionar logging adicional (se necessário)
4. ✅ Verificar constraints do banco de dados
5. ✅ Testar endpoint `/api/interviewer/step2` localmente

---

## 📝 Comandos Úteis

### Build Frontend
```bash
cd src/frontend
npm run build
```

### Verificar Build
```bash
cd src/frontend/dist
ls -la assets/*.css
ls -la assets/*.js
```

### Testar Backend Localmente
```bash
cd src/backend
# Testar step2 endpoint
curl -X POST http://localhost:8000/api/interviewer/step2 \
  -F "session_id=<session_id>" \
  -F "raw_text=<job_text>" \
  -F "language=en"
```

---

## ⚠️ Notas Importantes

1. **CSS 404**: É um problema de cache/deploy. Após novo build e deploy, deve resolver automaticamente (usuários podem precisar fazer hard refresh).

2. **500 Error**: É um problema crítico de backend que precisa ser investigado imediatamente. Pode estar relacionado a:
   - Dados inválidos
   - Problemas no banco de dados
   - Bugs no service de job posting

3. **Prioridade**: 
   - **Alta**: Erro 500 (bloqueia funcionalidade)
   - **Média**: Erro 404 CSS (afeta aparência, mas não funcionalidade)

---

## 🔍 Próximos Passos

1. Fazer build e deploy do frontend
2. Verificar logs do backend para entender o erro 500
3. Adicionar tratamento de erro mais detalhado no backend
4. Testar endpoint step2 em ambiente de staging antes de produção

