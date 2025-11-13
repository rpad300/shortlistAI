# Testes Automatizados de Contraste

**Versão**: 1.0.0  
**Última atualização**: 2025-01-08

---

## 1. Visão Geral

Este documento descreve como implementar e usar testes automatizados de contraste usando ferramentas como axe-core e outras soluções.

---

## 2. Opções de Implementação

### 2.1 Opção 1: axe-core via Browser Extension (Recomendado para Desenvolvimento)

**Vantagens**:
- Não requer configuração no código
- Funciona em qualquer página
- Interface visual clara
- Gratuito

**Como usar**:
1. Instalar extensão [axe DevTools](https://chrome.google.com/webstore/detail/axe-devtools-web-accessibility/lhdoppojpmngadmnindnejefpokejbdd)
2. Abrir página a testar
3. Clicar no ícone da extensão
4. Clicar em "Scan"
5. Revisar violações de contraste

**Limitações**:
- Requer ação manual
- Não integra com CI/CD

### 2.2 Opção 2: axe-core via Script de Teste

**Vantagens**:
- Pode ser automatizado
- Integra com CI/CD
- Testa múltiplas páginas

**Desvantagens**:
- Requer configuração
- Requer ambiente de teste

---

## 3. Implementação: Script de Teste com Puppeteer + axe-core

### 3.1 Instalação

```bash
cd src/frontend
npm install --save-dev @axe-core/cli puppeteer
```

### 3.2 Script de Teste

Criar arquivo `scripts/test-contrast.js`:

```javascript
/**
 * Automated contrast testing using axe-core
 * 
 * Usage: node scripts/test-contrast.js [url]
 */

const { spawn } = require('child_process');
const path = require('path');

const url = process.argv[2] || 'http://localhost:3000';

console.log(`Testing contrast on: ${url}`);
console.log('Using axe-core CLI...\n');

// Run axe-core CLI
const axe = spawn('npx', ['@axe-core/cli', url], {
  stdio: 'inherit',
  shell: true
});

axe.on('close', (code) => {
  if (code === 0) {
    console.log('\n✅ Contrast tests passed!');
  } else {
    console.log('\n❌ Contrast tests failed!');
    process.exit(1);
  }
});
```

### 3.3 Adicionar ao package.json

```json
{
  "scripts": {
    "test:contrast": "node scripts/test-contrast.js",
    "test:contrast:build": "npm run build && npm run preview & sleep 5 && npm run test:contrast http://localhost:4173"
  }
}
```

---

## 4. Implementação: Teste com Playwright + axe-core

### 4.1 Instalação

```bash
npm install --save-dev @playwright/test @axe-core/playwright
```

### 4.2 Configuração

Criar `playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### 4.3 Teste de Contraste

Criar `tests/contrast.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Contrast Tests', () => {
  const pages = [
    '/',
    '/about',
    '/pricing',
    '/features',
    '/candidate/step1',
    '/interviewer/step1',
  ];

  for (const page of pages) {
    test(`Light theme - ${page}`, async ({ page: p }) => {
      await p.goto(page);
      await injectAxe(p);
      
      // Set light theme
      await p.evaluate(() => {
        document.documentElement.setAttribute('data-theme', 'light');
      });
      
      await checkA11y(p, undefined, {
        detailedReport: true,
        detailedReportOptions: { html: true },
      }, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
    });

    test(`Dark theme - ${page}`, async ({ page: p }) => {
      await p.goto(page);
      await injectAxe(p);
      
      // Set dark theme
      await p.evaluate(() => {
        document.documentElement.setAttribute('data-theme', 'dark');
      });
      
      await checkA11y(p, undefined, {
        detailedReport: true,
        detailedReportOptions: { html: true },
      }, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
    });
  }
});
```

---

## 5. Implementação: Lighthouse CI

### 5.1 Instalação

```bash
npm install --save-dev @lhci/cli
```

### 5.2 Configuração

Criar `lighthouserc.js`:

```javascript
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000',
        'http://localhost:3000/about',
        'http://localhost:3000/pricing',
      ],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'color-contrast': ['error', { minScore: 0.9 }],
      },
    },
  },
};
```

### 5.3 Script

```json
{
  "scripts": {
    "test:lighthouse": "lhci autorun"
  }
}
```

---

## 6. Implementação Recomendada: Script Simples com axe DevTools

Para começar rapidamente, recomendamos usar a extensão do browser. Para automação, use o script abaixo:

### 6.1 Script de Validação Rápida

Criar `scripts/validate-contrast.js`:

```javascript
/**
 * Quick contrast validation script
 * Opens browser with axe DevTools instructions
 */

console.log(`
╔══════════════════════════════════════════════════════════════╗
║         CONTRASTE VALIDATION - INSTRUÇÕES                    ║
╚══════════════════════════════════════════════════════════════╝

1. Certifique-se de que o frontend está rodando:
   cd src/frontend && npm run dev

2. Abra o browser em: http://localhost:3000

3. Instale a extensão axe DevTools:
   https://chrome.google.com/webstore/detail/axe-devtools-web-accessibility/lhdoppojpmngadmnindnejefpokejbdd

4. Para cada página:
   a. Navegue para a página
   b. Clique no ícone da extensão axe
   c. Clique em "Scan"
   d. Revise violações de contraste
   e. Documente problemas encontrados

5. Teste em ambos os temas (light/dark)

Páginas para testar:
- / (Home)
- /about
- /pricing
- /features
- /candidate/step1
- /interviewer/step1
- /admin/* (se aplicável)

Para mais detalhes, veja: docs/qa/manual-contrast-testing-guide.md
`);
```

### 6.2 Adicionar ao package.json

```json
{
  "scripts": {
    "test:contrast": "node scripts/validate-contrast.js"
  }
}
```

---

## 7. Integração com CI/CD (Futuro)

Quando implementar CI/CD completo:

```yaml
# .github/workflows/contrast-test.yml
name: Contrast Tests

on: [push, pull_request]

jobs:
  test-contrast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run build
      - run: npm run preview &
      - run: sleep 5
      - run: npm run test:contrast
```

---

## 8. Recomendações

### 8.1 Para Desenvolvimento Diário
- Use extensão axe DevTools
- Teste manualmente após mudanças de CSS
- Use calculadora de contraste para novos componentes

### 8.2 Para Pull Requests
- Execute testes manuais completos
- Use script de validação
- Documente problemas encontrados

### 8.3 Para Releases
- Execute testes automatizados (quando implementados)
- Execute testes manuais completos
- Revise relatórios de acessibilidade

---

## 9. Próximos Passos

1. ✅ Documentação criada
2. ⏳ Implementar script de validação rápida
3. ⏳ Configurar testes com Playwright (opcional)
4. ⏳ Integrar com CI/CD (futuro)

---

**Última atualização**: 2025-01-08

