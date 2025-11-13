# Guia de Testes Manuais de Contraste

**Versão**: 1.0.0  
**Última atualização**: 2025-01-08

---

## 1. Objetivo

Este guia fornece instruções passo a passo para testar manualmente o contraste de cores em ambos os temas (light e dark) do ShortlistAI.

---

## 2. Pré-requisitos

### 2.1 Ferramentas Recomendadas

1. **Browser DevTools** (Chrome, Firefox, Edge)
   - Inspecionar elementos
   - Verificar CSS computado
   - Simular preferências de cor

2. **Ferramentas de Contraste Online**
   - [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
   - [Contrast Ratio Calculator](https://contrast-ratio.com/)

3. **Extensões do Browser**
   - [axe DevTools](https://chrome.google.com/webstore/detail/axe-devtools-web-accessibility/lhdoppojpmngadmnindnejefpokejbdd)
   - [WAVE Evaluation Tool](https://wave.webaim.org/extension/)

### 2.2 Configuração do Ambiente

1. Iniciar o frontend em modo desenvolvimento:
   ```bash
   cd src/frontend
   npm run dev
   ```

2. Abrir o browser em: `http://localhost:3000`

---

## 3. Checklist de Testes por Página

### 3.1 Home Page (`/`)

#### Tema Light
- [ ] **Hero Section**
  - [ ] Título principal tem contraste adequado sobre background
  - [ ] Botões primários (gradient) têm texto branco legível
  - [ ] Botões secundários têm contraste adequado
  - [ ] Links têm contraste adequado

- [ ] **Features Section**
  - [ ] Títulos de features têm contraste adequado
  - [ ] Texto descritivo tem contraste adequado
  - [ ] Cards têm bordas visíveis

- [ ] **CTA Section**
  - [ ] Texto branco sobre gradient background é legível
  - [ ] Botão branco com texto azul tem contraste adequado
  - [ ] Botão outline branco tem contraste adequado

- [ ] **Footer**
  - [ ] Links têm contraste adequado
  - [ ] Texto secundário é legível

#### Tema Dark
- [ ] Repetir todos os itens acima
- [ ] Verificar que cores se adaptam corretamente
- [ ] Verificar que não há texto branco sobre fundo branco

### 3.2 Páginas de Steps (Interviewer/Candidate)

#### Tema Light
- [ ] **Header/Navbar**
  - [ ] Logo é visível
  - [ ] Links de navegação têm contraste adequado
  - [ ] Botões têm contraste adequado

- [ ] **Formulários**
  - [ ] Labels têm contraste adequado
  - [ ] Inputs têm bordas visíveis
  - [ ] Placeholders têm contraste adequado (mas não muito forte)
  - [ ] Mensagens de erro têm contraste adequado
  - [ ] Botões têm contraste adequado

- [ ] **Cards/Containers**
  - [ ] Backgrounds têm contraste com texto
  - [ ] Bordas são visíveis
  - [ ] Sombras não escondem conteúdo

#### Tema Dark
- [ ] Repetir todos os itens acima
- [ ] Verificar que inputs mantêm contraste
- [ ] Verificar que placeholders são legíveis mas não confundem com texto preenchido

### 3.3 Páginas Admin

#### Tema Light
- [ ] **Dashboard**
  - [ ] Cards de estatísticas têm contraste adequado
  - [ ] Gráficos são legíveis
  - [ ] Tabelas têm contraste adequado

- [ ] **Formulários Admin**
  - [ ] Todos os campos têm contraste adequado
  - [ ] Botões de ação têm contraste adequado
  - [ ] Badges e status têm contraste adequado

#### Tema Dark
- [ ] Repetir todos os itens acima
- [ ] Verificar que cores semânticas (success, error, warning) são adequadas

---

## 4. Testes de Estados Interativos

### 4.1 Hover States
- [ ] **Links**
  - [ ] Mantêm contraste adequado no hover
  - [ ] Mudança de cor é perceptível mas não perde contraste

- [ ] **Botões**
  - [ ] Hover mantém contraste adequado
  - [ ] Texto permanece legível

- [ ] **Cards**
  - [ ] Hover não reduz contraste do texto
  - [ ] Sombras não escondem conteúdo

### 4.2 Focus States
- [ ] **Inputs**
  - [ ] Focus outline é visível
  - [ ] Contraste do outline é adequado
  - [ ] Texto dentro do input mantém contraste

- [ ] **Botões**
  - [ ] Focus outline é visível
  - [ ] Contraste do outline é adequado

- [ ] **Links**
  - [ ] Focus outline é visível
  - [ ] Contraste do outline é adequado

### 4.3 Disabled States
- [ ] **Botões Disabled**
  - [ ] Texto ainda é legível (pode ter opacidade reduzida)
  - [ ] Contraste mínimo de 3:1 mantido

- [ ] **Inputs Disabled**
  - [ ] Texto ainda é legível
  - [ ] Background indica estado disabled mas mantém contraste

---

## 5. Testes Específicos de Contraste

### 5.1 Verificação de Ratios WCAG

Para cada combinação texto/background, verificar:

#### Texto Normal (< 18px ou < 14px bold)
- [ ] **Mínimo**: 4.5:1 (WCAG AA)
- [ ] **Recomendado**: 7:1 (WCAG AAA)

#### Texto Grande (≥ 18px ou ≥ 14px bold)
- [ ] **Mínimo**: 3:1 (WCAG AA)
- [ ] **Recomendado**: 4.5:1 (WCAG AAA)

### 5.2 Como Verificar Ratios

1. **Usando DevTools**:
   - Inspecionar elemento
   - Ver CSS computado
   - Copiar valores de `color` e `background-color`
   - Usar calculadora online

2. **Usando Extensão axe DevTools**:
   - Abrir extensão
   - Clicar em "Scan"
   - Verificar violações de contraste
   - Corrigir problemas identificados

3. **Usando WAVE**:
   - Abrir extensão
   - Verificar erros de contraste
   - Verificar alertas de contraste

---

## 6. Testes de Acessibilidade Visual

### 6.1 Simulação de Deficiências Visuais

#### Daltonismo
- [ ] Usar [Sim Daltonismo](https://www.toptal.com/designers/colorfilter) ou similar
- [ ] Verificar que informações não dependem apenas de cor
- [ ] Verificar que ícones/textos complementam cores

#### Baixa Visão
- [ ] Zoom de 200% mantém contraste adequado
- [ ] Texto permanece legível em tamanhos maiores
- [ ] Elementos não se sobrepõem

### 6.2 Testes de Brilho

#### Tela Muito Brilhante
- [ ] Contraste ainda é adequado
- [ ] Texto não "desaparece" no fundo

#### Tela Escura (Dark Mode)
- [ ] Contraste adequado sem ser muito brilhante
- [ ] Texto não "queima" os olhos

---

## 7. Checklist Rápido por Componente

### 7.1 Botões
- [ ] Texto tem contraste mínimo de 4.5:1
- [ ] Hover mantém contraste
- [ ] Focus outline é visível
- [ ] Disabled ainda é legível (3:1 mínimo)

### 7.2 Inputs
- [ ] Labels têm contraste adequado
- [ ] Placeholders têm contraste adequado (mas menor que texto)
- [ ] Texto digitado tem contraste adequado
- [ ] Bordas são visíveis
- [ ] Focus outline é visível

### 7.3 Links
- [ ] Contraste mínimo de 4.5:1
- [ ] Hover mantém contraste
- [ ] Focus outline é visível
- [ ] Links visitados são distinguíveis

### 7.4 Cards
- [ ] Texto tem contraste adequado sobre background
- [ ] Bordas são visíveis
- [ ] Sombras não escondem conteúdo
- [ ] Hover não reduz contraste

### 7.5 Badges/Status
- [ ] Texto tem contraste adequado
- [ ] Background tem contraste adequado
- [ ] Cores semânticas são distinguíveis

---

## 8. Processo de Teste Recomendado

### 8.1 Antes de Começar
1. Limpar cache do browser
2. Garantir que frontend está rodando
3. Abrir DevTools
4. Preparar ferramentas de contraste

### 8.2 Para Cada Página
1. **Tema Light**
   - Navegar para página
   - Verificar todos os elementos visíveis
   - Testar estados interativos
   - Documentar problemas encontrados

2. **Tema Dark**
   - Alternar para dark mode
   - Repetir verificações
   - Comparar com tema light
   - Documentar problemas encontrados

3. **Estados Interativos**
   - Testar hover em todos os elementos interativos
   - Testar focus (navegação por teclado)
   - Testar disabled states
   - Documentar problemas encontrados

### 8.3 Após Testes
1. Compilar lista de problemas
2. Priorizar por severidade
3. Criar issues/tasks para correção
4. Documentar soluções aplicadas

---

## 9. Ferramentas e Recursos

### 9.1 Calculadoras de Contraste
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Contrast Ratio Calculator](https://contrast-ratio.com/)
- [Colour Contrast Analyser](https://www.tpgi.com/color-contrast-checker/)

### 9.2 Extensões do Browser
- [axe DevTools](https://chrome.google.com/webstore/detail/axe-devtools-web-accessibility/lhdoppojpmngadmnindnejefpokejbdd)
- [WAVE Evaluation Tool](https://wave.webaim.org/extension/)
- [Lighthouse](https://developer.chrome.com/docs/lighthouse/accessibility/)

### 9.3 Simuladores
- [Sim Daltonismo](https://www.toptal.com/designers/colorfilter)
- [NoCoffee](https://chrome.google.com/webstore/detail/nocoffee/jjeeggmbnhckmgdhmgdckeigabpjdfft) (simula baixa visão)

---

## 10. Documentação de Problemas

### 10.1 Template de Relatório

```markdown
## Problema de Contraste

**Página**: [Nome da página]
**Componente**: [Nome do componente]
**Tema**: [Light/Dark/Both]
**Elemento**: [Descrição do elemento]

**Problema**:
- Texto: [cor]
- Background: [cor]
- Ratio atual: [X:1]
- Ratio necessário: [4.5:1 ou 3:1]

**Screenshot**: [link ou anexo]

**Solução proposta**: [descrição]
```

---

## 11. Checklist Final

Antes de considerar testes completos:

- [ ] Todas as páginas principais testadas em light mode
- [ ] Todas as páginas principais testadas em dark mode
- [ ] Todos os estados interativos testados
- [ ] Todos os componentes reutilizáveis testados
- [ ] Problemas documentados e priorizados
- [ ] Correções aplicadas e re-testadas
- [ ] Documentação atualizada

---

**Última atualização**: 2025-01-08  
**Próxima revisão**: Após cada release major

