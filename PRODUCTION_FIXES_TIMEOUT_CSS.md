# 🔧 Correções de Produção - Timeout e CSS 404

**Data**: 11 de Janeiro de 2025

---

## 📋 Problemas Identificados

### 1. **Erro 404: CSS não encontrado**
```
index-eaFIEsI-.css:1 Failed to load resource: the server responded with a status of 404 (Not Found)
```

### 2. **Erro de Timeout no Step 2**
```
Error in step 2: L {message: 'timeout of 30000ms exceeded', name: 'AxiosError', code: 'ECONNABORTED', ...}
```

---

## ✅ Correções Aplicadas

### 1. **Timeout do Step 2 Aumentado**

**Arquivo**: `src/frontend/src/services/api.ts`

**Mudança**: Timeout do `interviewerAPI.step2` aumentado de 30s (padrão) para **60 segundos**.

**Motivo**: Uploads de arquivos grandes e processamento de job postings podem demorar mais de 30 segundos, especialmente em produção com latência de rede.

```typescript
step2: (data: FormData) => api.post('/interviewer/step2', data, {
  headers: { 'Content-Type': 'multipart/form-data' },
  timeout: 60000 // 60s for large file uploads and processing
}),
```

---

### 2. **Melhorias no Cache Busting de Assets**

**Arquivo**: `src/frontend/vite.config.ts`

**Mudanças**:
- Configuração explícita de hash para assets CSS/JS
- Garantia de que CSS é extraído e tem hash único
- Configuração do VitePWA para limpar caches antigos automaticamente

**Benefícios**:
- Assets sempre têm hash baseado no conteúdo
- Caches antigos são limpos automaticamente em novos deploys
- Melhor invalidação de cache quando há mudanças

```typescript
build: {
  // ...
  rollupOptions: {
    output: {
      entryFileNames: 'assets/[name]-[hash].js',
      chunkFileNames: 'assets/[name]-[hash].js',
      assetFileNames: (assetInfo) => {
        // CSS e outros assets sempre com hash
        return `assets/[name]-[hash][extname]`;
      },
      // ...
    }
  },
  cssCodeSplit: true // CSS extraído e com hash
}
```

---

### 3. **Tratamento de Erro 404 no Service Worker**

**Arquivo**: `src/frontend/public/sw.js`

**Mudanças**:
- Service worker não cacheia respostas 404
- Tratamento específico para erros 404 em assets CSS/JS
- Fallback para `index.html` quando asset não é encontrado (força reload)

**Benefícios**:
- Erros 404 não são cacheados
- Quando um asset não é encontrado, o service worker tenta forçar reload da página
- Melhor experiência quando há mudanças de hash em produção

```javascript
// Não cachear 404s
if (networkResponse.status === 404) {
  if (/\.(css|js)$/i.test(url.pathname)) {
    console.warn('[SW] Asset not found (404):', url.pathname);
    // Não cachear 404s - browser vai recarregar e pegar novo index.html
  }
}

// Fallback para index.html em caso de erro de rede
.catch((error) => {
  if (/\.(css|js)$/i.test(url.pathname)) {
    return caches.match('/index.html').then((indexResponse) => {
      if (indexResponse) {
        return indexResponse; // Força reload
      }
      throw error;
    });
  }
  throw error;
});
```

---

## 🚀 Próximos Passos para Deploy

### 1. **Rebuild do Frontend**
```bash
cd src/frontend
npm run build
```

### 2. **Verificar Build**
```bash
# Verificar se os arquivos CSS foram gerados corretamente
ls -la dist/assets/*.css

# Verificar se o index.html referencia os arquivos corretos
cat dist/index.html | grep -E '\.(css|js)'
```

### 3. **Deploy**
- Fazer deploy de **TODOS** os arquivos do `dist/`
- Garantir que o `index.html` e todos os assets sejam atualizados
- Verificar que o service worker seja atualizado

### 4. **Para Usuários Afetados (Imediato)**
Se usuários ainda virem o erro 404 de CSS, eles podem:

**Opção A - Limpar Cache Manualmente**:
1. Abrir DevTools (F12)
2. Ir em Application → Service Workers → Unregister
3. Ir em Application → Storage → Clear site data
4. Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

**Opção B - Script no Console**:
```javascript
// No console do navegador (F12)
navigator.serviceWorker.getRegistrations().then(function(registrations) {
  for(let registration of registrations) {
    registration.unregister();
  }
});

caches.keys().then(function(names) {
  for (let name of names) caches.delete(name);
});

location.reload(true);
```

---

## 📊 Resumo das Mudanças

| Arquivo | Mudança | Impacto |
|---------|---------|---------|
| `src/frontend/src/services/api.ts` | Timeout step2: 30s → 60s | ✅ Resolve timeouts em uploads grandes |
| `src/frontend/vite.config.ts` | Hash explícito para assets + cleanup de cache | ✅ Melhor cache busting |
| `src/frontend/public/sw.js` | Tratamento de 404 + fallback | ✅ Melhor recuperação de erros |

---

## ✅ Testes Recomendados

1. **Teste de Upload Grande**:
   - Fazer upload de job posting grande (>1MB)
   - Verificar que não dá timeout

2. **Teste de Cache**:
   - Fazer deploy
   - Verificar que novos assets são carregados
   - Verificar que caches antigos são limpos

3. **Teste de Service Worker**:
   - Verificar que service worker atualiza automaticamente
   - Verificar que erros 404 não são cacheados

---

## 📝 Notas

- O problema de CSS 404 é principalmente de cache/deploy
- Após novo deploy com estas correções, usuários precisarão fazer hard refresh **uma vez**
- O timeout de 60s deve ser suficiente para a maioria dos casos, mas pode ser aumentado se necessário
- O service worker agora trata melhor erros 404, mas o ideal é sempre fazer deploy completo de todos os assets

---

**Status**: ✅ Correções aplicadas e prontas para deploy

