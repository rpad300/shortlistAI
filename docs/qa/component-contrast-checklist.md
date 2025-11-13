# Checklist de Contraste para Novos Componentes

**Versão**: 1.0.0  
**Última atualização**: 2025-01-08

---

## 1. Antes de Criar um Novo Componente

### 1.1 Planejamento
- [ ] Definir cores do componente baseadas no sistema de temas
- [ ] Identificar todos os estados do componente (normal, hover, focus, disabled)
- [ ] Identificar todos os tamanhos de texto usados
- [ ] Verificar se há sobreposições de elementos

---

## 2. Durante o Desenvolvimento

### 2.1 Uso de Variáveis CSS
- [ ] **Textos**: Usar `var(--text-primary)`, `var(--text-secondary)`, etc.
- [ ] **Backgrounds**: Usar `var(--bg)`, `var(--surface)`, etc.
- [ ] **Bordas**: Usar `var(--border)`
- [ ] **Cores semânticas**: Usar `var(--success)`, `var(--error)`, `var(--warning)`
- [ ] **Cores de marca**: Usar `var(--color-ai-blue)`, `var(--color-neural-purple)`

### 2.2 Evitar Hardcoding
- [ ] ❌ Não usar `color: white` diretamente
- [ ] ❌ Não usar `background: white` diretamente
- [ ] ❌ Não usar `#FFFFFF` ou `#000000` diretamente
- [ ] ✅ Usar variáveis CSS do tema
- [ ] ✅ Se necessário usar cor específica, garantir contraste adequado

---

## 3. Verificação de Contraste

### 3.1 Texto Normal (< 18px ou < 14px bold)
- [ ] **Mínimo WCAG AA**: 4.5:1
- [ ] **Recomendado WCAG AAA**: 7:1
- [ ] Verificar em tema light
- [ ] Verificar em tema dark

### 3.2 Texto Grande (≥ 18px ou ≥ 14px bold)
- [ ] **Mínimo WCAG AA**: 3:1
- [ ] **Recomendado WCAG AAA**: 4.5:1
- [ ] Verificar em tema light
- [ ] Verificar em tema dark

### 3.3 Elementos Não-Textuais
- [ ] **Bordas**: Contraste mínimo de 3:1 com background adjacente
- [ ] **Ícones**: Contraste mínimo de 3:1 com background
- [ ] **Focus outlines**: Contraste mínimo de 3:1 com background

---

## 4. Estados Interativos

### 4.1 Hover
- [ ] Contraste mantido ou melhorado
- [ ] Texto permanece legível
- [ ] Mudança de cor é perceptível
- [ ] Não reduz contraste abaixo do mínimo

### 4.2 Focus
- [ ] Outline visível (mínimo 2px)
- [ ] Contraste do outline mínimo de 3:1
- [ ] Outline não esconde conteúdo
- [ ] Funciona em ambos os temas

### 4.3 Active/Pressed
- [ ] Contraste mantido
- [ ] Feedback visual claro
- [ ] Texto permanece legível

### 4.4 Disabled
- [ ] Contraste mínimo de 3:1 mantido
- [ ] Texto ainda é legível
- [ ] Visual indica estado disabled
- [ ] Não confunde com estado normal

---

## 5. Contextos Especiais

### 5.1 Sobre Backgrounds Coloridos
- [ ] Se texto sobre gradient, garantir contraste em toda a área
- [ ] Se texto sobre imagem, usar overlay se necessário
- [ ] Se texto sobre cor sólida, verificar contraste direto

### 5.2 Sobre Backgrounds Transparentes
- [ ] Considerar pior caso (background mais claro/escuro possível)
- [ ] Garantir contraste mesmo com transparência máxima
- [ ] Testar com diferentes conteúdos por trás

### 5.3 Sobre Backgrounds com Blur
- [ ] Verificar contraste considerando blur
- [ ] Testar com diferentes conteúdos por trás
- [ ] Garantir legibilidade

---

## 6. Responsividade

### 6.1 Mobile
- [ ] Contraste adequado em telas pequenas
- [ ] Texto legível sem zoom
- [ ] Elementos não se sobrepõem

### 6.2 Tablet
- [ ] Contraste adequado
- [ ] Texto legível

### 6.3 Desktop
- [ ] Contraste adequado
- [ ] Texto legível

### 6.4 TV/Large Screens
- [ ] Contraste adequado
- [ ] Texto legível à distância

---

## 7. Testes Obrigatórios

### 7.1 Tema Light
- [ ] Componente renderizado corretamente
- [ ] Todos os textos legíveis
- [ ] Todos os estados funcionam
- [ ] Contraste adequado em todos os elementos

### 7.2 Tema Dark
- [ ] Componente renderizado corretamente
- [ ] Todos os textos legíveis
- [ ] Todos os estados funcionam
- [ ] Contraste adequado em todos os elementos

### 7.3 Estados Interativos
- [ ] Hover funciona e mantém contraste
- [ ] Focus funciona e é visível
- [ ] Active funciona e mantém contraste
- [ ] Disabled funciona e mantém contraste mínimo

### 7.4 Navegação por Teclado
- [ ] Focus visível
- [ ] Contraste do focus adequado
- [ ] Navegação funciona corretamente

---

## 8. Ferramentas de Verificação

### 8.1 Durante Desenvolvimento
- [ ] Usar calculadora de contraste online
- [ ] Usar DevTools para inspecionar cores
- [ ] Usar extensão axe DevTools

### 8.2 Antes de Commit
- [ ] Executar `npm run test:contrast`
- [ ] Revisar manualmente em ambos os temas
- [ ] Testar estados interativos

---

## 9. Exemplos de Boas Práticas

### 9.1 ✅ Bom: Usando Variáveis CSS

```css
.my-component {
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.my-component:hover {
  background: var(--bg);
  border-color: var(--color-ai-blue);
}
```

### 9.2 ❌ Ruim: Hardcoding Cores

```css
.my-component {
  background: white;
  color: black;
  border: 1px solid #ccc;
}

.my-component:hover {
  background: #f5f5f5;
}
```

### 9.3 ✅ Bom: Contraste Garantido

```css
.btn-primary {
  background: var(--color-ai-blue);
  color: white; /* OK: sobre background azul escuro */
}

.btn-secondary {
  background: transparent;
  color: var(--color-ai-blue);
  border: 2px solid var(--color-ai-blue);
}
```

### 9.4 ❌ Ruim: Contraste Insuficiente

```css
.btn-bad {
  background: #f0f0f0;
  color: #f5f5f5; /* Ruim: contraste muito baixo */
}
```

---

## 10. Checklist Rápido

Antes de considerar um componente completo:

- [ ] Usa variáveis CSS do tema
- [ ] Texto normal tem contraste mínimo de 4.5:1
- [ ] Texto grande tem contraste mínimo de 3:1
- [ ] Testado em tema light
- [ ] Testado em tema dark
- [ ] Hover mantém contraste
- [ ] Focus é visível e tem contraste adequado
- [ ] Disabled mantém contraste mínimo de 3:1
- [ ] Funciona em mobile, tablet e desktop
- [ ] Navegação por teclado funciona
- [ ] Documentado se necessário

---

## 11. Recursos

- **Sistema de Temas**: `src/frontend/src/styles/theme.css`
- **Guia de Testes Manuais**: `docs/qa/manual-contrast-testing-guide.md`
- **Análise de Contraste**: `docs/qa/css-contrast-analysis.md`
- **Calculadora de Contraste**: https://webaim.org/resources/contrastchecker/

---

**Última atualização**: 2025-01-08

