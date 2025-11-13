# Padrões de Contraste - Guia para a Equipe

**Versão**: 1.0.0  
**Última atualização**: 2025-01-08

---

## 1. Introdução

Este documento estabelece padrões e diretrizes de contraste para toda a equipe de desenvolvimento do ShortlistAI.

---

## 2. Padrões WCAG

### 2.1 Níveis de Conformidade

Seguimos **WCAG 2.1 Level AA** como mínimo:

- **Texto Normal** (< 18px ou < 14px bold): **4.5:1** mínimo
- **Texto Grande** (≥ 18px ou ≥ 14px bold): **3:1** mínimo
- **Elementos Não-Textuais**: **3:1** mínimo

### 2.2 Aspiração

Buscamos **WCAG 2.1 Level AAA** quando possível:

- **Texto Normal**: **7:1** recomendado
- **Texto Grande**: **4.5:1** recomendado

---

## 3. Sistema de Cores do Tema

### 3.1 Variáveis CSS Disponíveis

#### Backgrounds
```css
var(--bg)              /* Background principal */
var(--surface)         /* Background de superfície (cards, etc.) */
var(--bg-light)        /* Background light mode */
var(--bg-dark)         /* Background dark mode */
var(--surface-light)   /* Surface light mode */
var(--surface-dark)    /* Surface dark mode */
```

#### Textos
```css
var(--text-primary)    /* Texto principal */
var(--text-secondary)  /* Texto secundário */
var(--text-tertiary)   /* Texto terciário */
var(--text-primary-light)   /* Texto principal light */
var(--text-primary-dark)    /* Texto principal dark */
var(--text-secondary-light) /* Texto secundário light */
var(--text-secondary-dark)  /* Texto secundário dark */
```

#### Bordas
```css
var(--border)          /* Borda padrão */
var(--border-light)    /* Borda light mode */
var(--border-dark)     /* Borda dark mode */
```

#### Cores Semânticas
```css
var(--success)         /* Verde - sucesso */
var(--warning)         /* Laranja - aviso */
var(--error)           /* Vermelho - erro */
```

#### Cores de Marca
```css
var(--color-ai-blue)        /* Azul principal */
var(--color-neural-purple)  /* Roxo secundário */
```

### 3.2 Uso Correto

✅ **SEMPRE usar variáveis CSS**:
```css
.component {
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
}
```

❌ **NUNCA hardcodar cores**:
```css
.component {
  background: white;
  color: black;
  border: 1px solid #ccc;
}
```

---

## 4. Padrões por Tipo de Componente

### 4.1 Botões

#### Botão Primário
```css
.btn-primary {
  background: var(--color-ai-blue);
  color: white; /* OK: sobre background azul escuro */
}
```
- ✅ Contraste: ~4.5:1 (azul escuro + branco)
- ✅ Funciona em ambos os temas

#### Botão Secundário
```css
.btn-secondary {
  background: transparent;
  color: var(--color-ai-blue);
  border: 2px solid var(--color-ai-blue);
}
```
- ✅ Contraste: ~4.5:1 (azul sobre transparente)
- ✅ Funciona em ambos os temas

#### Botão Outline
```css
.btn-outline {
  background: transparent;
  color: var(--color-ai-blue);
  border: 2px solid var(--color-ai-blue);
}
```
- ✅ Contraste: ~4.5:1
- ✅ Funciona em ambos os temas

### 4.2 Inputs

```css
.input {
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.input::placeholder {
  color: var(--text-secondary);
  opacity: 0.6;
}

.input:focus {
  border-color: var(--color-ai-blue);
  outline: 2px solid var(--color-ai-blue);
  outline-offset: 2px;
}
```
- ✅ Contraste adequado em todos os estados
- ✅ Placeholder tem contraste menor mas legível
- ✅ Focus outline tem contraste adequado

### 4.3 Cards

```css
.card {
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.card-title {
  color: var(--text-primary);
}

.card-description {
  color: var(--text-secondary);
}
```
- ✅ Contraste adequado
- ✅ Hierarquia visual clara

### 4.4 Links

```css
.link {
  color: var(--color-ai-blue);
}

.link:hover {
  color: var(--color-neural-purple);
}

.link:focus {
  outline: 2px solid var(--color-ai-blue);
  outline-offset: 2px;
}
```
- ✅ Contraste mínimo de 4.5:1
- ✅ Hover mantém contraste
- ✅ Focus visível

### 4.5 Badges/Status

```css
.badge-success {
  background: var(--success);
  color: white; /* OK: sobre verde escuro */
}

.badge-error {
  background: var(--error);
  color: white; /* OK: sobre vermelho escuro */
}

.badge-warning {
  background: var(--warning);
  color: white; /* OK: sobre laranja escuro */
}
```
- ✅ Contraste adequado em todos os badges
- ✅ Cores semânticas claras

---

## 5. Quando Usar `color: white`

### 5.1 ✅ Contextos Apropriados

- Sobre backgrounds coloridos escuros (azul, verde, vermelho, etc.)
- Sobre gradients escuros
- Em botões com background colorido
- Em badges com background colorido
- Em headers com background colorido

### 5.2 ❌ Contextos Inapropriados

- Sobre backgrounds brancos/claros
- Sobre backgrounds transparentes sobre fundo claro
- Em texto normal sobre fundo claro
- Sem verificar contraste adequado

---

## 6. Estados Interativos

### 6.1 Hover

**Regra**: Manter ou melhorar contraste

```css
.button:hover {
  background: var(--color-neural-purple); /* Mais escuro = melhor contraste */
  /* OU */
  opacity: 0.9; /* Mantém contraste */
}
```

### 6.2 Focus

**Regra**: Outline visível com contraste mínimo de 3:1

```css
.button:focus-visible {
  outline: 2px solid var(--color-ai-blue);
  outline-offset: 2px;
}
```

### 6.3 Disabled

**Regra**: Contraste mínimo de 3:1 mantido

```css
.button:disabled {
  opacity: 0.5;
  /* Ainda mantém contraste mínimo de 3:1 */
}
```

---

## 7. Exceções e Casos Especiais

### 7.1 Texto sobre Gradients

Se texto sobre gradient, garantir contraste em toda a área:

```css
.cta-section {
  background: linear-gradient(135deg, #0066FF 0%, #7C3AED 100%);
  color: white; /* OK: ambos os lados do gradient são escuros */
}
```

### 7.2 Texto sobre Imagens

Se necessário, usar overlay:

```css
.hero {
  position: relative;
}

.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5); /* Overlay escuro */
}

.hero-text {
  position: relative;
  color: white; /* OK: sobre overlay escuro */
  z-index: 1;
}
```

### 7.3 Glassmorphism

Garantir contraste mesmo com blur:

```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  color: var(--text-primary-light); /* Texto escuro sobre fundo claro */
}
```

---

## 8. Processo de Revisão

### 8.1 Antes de Criar Componente
1. Revisar este guia
2. Verificar variáveis CSS disponíveis
3. Planejar estados interativos

### 8.2 Durante Desenvolvimento
1. Usar variáveis CSS
2. Verificar contraste com calculadora
3. Testar em ambos os temas

### 8.3 Antes de Commit
1. Executar `npm run test:contrast`
2. Revisar manualmente
3. Testar estados interativos

### 8.4 Em Code Review
1. Verificar uso de variáveis CSS
2. Verificar contraste adequado
3. Verificar estados interativos
4. Verificar ambos os temas

---

## 9. Ferramentas e Recursos

### 9.1 Calculadoras
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Contrast Ratio Calculator](https://contrast-ratio.com/)

### 9.2 Extensões
- [axe DevTools](https://chrome.google.com/webstore/detail/axe-devtools-web-accessibility/lhdoppojpmngadmnindnejefpokejbdd)
- [WAVE Evaluation Tool](https://wave.webaim.org/extension/)

### 9.3 Documentação
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Análise de Contraste](docs/qa/css-contrast-analysis.md)
- [Guia de Testes Manuais](docs/qa/manual-contrast-testing-guide.md)

---

## 10. Perguntas Frequentes

### Q: Posso usar `color: white`?
**A**: Sim, mas apenas sobre backgrounds escuros/coloridos. Sempre verificar contraste.

### Q: E se precisar de uma cor específica?
**A**: Adicionar à variável CSS do tema se for reutilizável, ou garantir contraste adequado se for específica.

### Q: Como testar contraste rapidamente?
**A**: Use a extensão axe DevTools ou calculadora online. Execute `npm run test:contrast` para instruções.

### Q: E se o contraste estiver no limite?
**A**: Preferir aumentar contraste quando possível. Se não for possível, documentar a decisão.

---

## 11. Checklist Rápido

Antes de considerar código pronto:

- [ ] Usa variáveis CSS do tema
- [ ] Contraste mínimo WCAG AA atendido
- [ ] Testado em tema light
- [ ] Testado em tema dark
- [ ] Estados interativos testados
- [ ] Navegação por teclado funciona
- [ ] Documentado se necessário

---

**Última atualização**: 2025-01-08  
**Mantido por**: Frontend & QA Team

