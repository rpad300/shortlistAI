# Documentação de QA e Acessibilidade

**Versão**: 1.0.0  
**Última atualização**: 2025-01-08

---

## 📚 Índice de Documentação

### 🎯 Contraste e Acessibilidade

1. **[Análise de Contraste CSS](./css-contrast-analysis.md)**
   - Análise completa dos arquivos CSS
   - Problemas identificados e correções aplicadas
   - Metodologia de análise

2. **[Guia de Testes Manuais de Contraste](./manual-contrast-testing-guide.md)**
   - Instruções passo a passo para testes manuais
   - Checklist por página e componente
   - Ferramentas recomendadas

3. **[Testes Automatizados de Contraste](./automated-contrast-testing.md)**
   - Opções de implementação
   - Scripts e configurações
   - Integração com CI/CD

4. **[Checklist de Contraste para Componentes](./component-contrast-checklist.md)**
   - Checklist completo para novos componentes
   - Verificações obrigatórias
   - Exemplos de boas práticas

5. **[Padrões de Contraste - Guia da Equipe](./contrast-patterns-guide.md)**
   - Padrões WCAG seguidos
   - Sistema de cores e variáveis CSS
   - Processo de revisão

---

## 🚀 Início Rápido

### Para Desenvolvedores

1. **Antes de criar um novo componente**:
   - Leia [Padrões de Contraste](./contrast-patterns-guide.md)
   - Use [Checklist de Componentes](./component-contrast-checklist.md)

2. **Durante desenvolvimento**:
   - Use variáveis CSS do tema
   - Verifique contraste com calculadora online
   - Teste em ambos os temas

3. **Antes de commit**:
   - Execute `npm run test:contrast`
   - Revise manualmente seguindo [Guia de Testes Manuais](./manual-contrast-testing-guide.md)

### Para QA/Testers

1. **Testes manuais**:
   - Siga [Guia de Testes Manuais](./manual-contrast-testing-guide.md)
   - Use extensão axe DevTools
   - Documente problemas encontrados

2. **Testes automatizados**:
   - Revise [Testes Automatizados](./automated-contrast-testing.md)
   - Configure ferramentas conforme necessário

---

## 📋 Padrões Seguidos

### WCAG 2.1 Level AA (Mínimo)

- **Texto Normal**: Contraste mínimo de **4.5:1**
- **Texto Grande**: Contraste mínimo de **3:1**
- **Elementos Não-Textuais**: Contraste mínimo de **3:1**

### WCAG 2.1 Level AAA (Aspiração)

- **Texto Normal**: Contraste recomendado de **7:1**
- **Texto Grande**: Contraste recomendado de **4.5:1**

---

## 🛠️ Ferramentas

### Calculadoras de Contraste
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Contrast Ratio Calculator](https://contrast-ratio.com/)

### Extensões do Browser
- [axe DevTools](https://chrome.google.com/webstore/detail/axe-devtools-web-accessibility/lhdoppojpmngadmnindnejefpokejbdd)
- [WAVE Evaluation Tool](https://wave.webaim.org/extension/)

### Scripts
- `npm run test:contrast` - Instruções para validação de contraste

---

## 📝 Processo de Revisão

1. **Desenvolvimento**: Seguir padrões e checklist
2. **Teste Local**: Executar testes manuais e automatizados
3. **Code Review**: Verificar contraste e acessibilidade
4. **QA**: Testes completos antes de merge
5. **Release**: Validação final

---

## 🔗 Links Úteis

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Sistema de Temas](../frontend/src/styles/theme.css)
- [Brand Rules](../../brandrules.md)

---

## 📅 Histórico de Atualizações

- **2025-01-08**: Criação inicial da documentação de contraste
  - Análise completa de CSS
  - Guias de teste
  - Padrões e checklists

---

**Mantido por**: Frontend & QA Team  
**Última atualização**: 2025-01-08

