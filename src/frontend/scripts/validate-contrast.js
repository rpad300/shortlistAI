/**
 * Quick contrast validation script
 * Provides instructions for manual contrast testing
 */

console.log(`
╔══════════════════════════════════════════════════════════════╗
║         VALIDAÇÃO DE CONTRASTE - INSTRUÇÕES                  ║
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

5. Teste em ambos os temas (light/dark):
   - Use o ThemeSwitcher no navbar
   - Ou altere preferência do sistema

Páginas para testar:
- / (Home)
- /about
- /pricing
- /features
- /candidate/step1
- /interviewer/step1
- /admin/* (se aplicável)

Ferramentas úteis:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Contrast Ratio Calculator: https://contrast-ratio.com/

Para mais detalhes, veja: docs/qa/manual-contrast-testing-guide.md
`);

