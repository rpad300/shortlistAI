# 📚 ShortlistAI - Índice de Documentação

**Guia completo de navegação para todos os documentos do projeto.**

---

## 🚀 COMEÇAR AGORA

| Ficheiro | Descrição | Quando Usar |
|----------|-----------|-------------|
| **[START_HERE.md](START_HERE.md)** | ⭐ **COMEÇA AQUI** | Agora! Quick start em 5 minutos |
| **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** | Sumário completo da implementação | Ver o que foi feito |
| **[UPDATE_ENV.md](UPDATE_ENV.md)** | Como atualizar o .env | Antes de executar |

---

## 📖 DOCUMENTAÇÃO PRINCIPAL

### Setup e Configuração
| Ficheiro | Conteúdo |
|----------|----------|
| [SETUP.md](SETUP.md) | Instruções completas de configuração |
| [UPDATE_ENV.md](UPDATE_ENV.md) | Variáveis de ambiente necessárias |
| [start_backend.bat](start_backend.bat) | Script para iniciar backend |
| [start_frontend.bat](start_frontend.bat) | Script para iniciar frontend |

### Planeamento e Roadmap
| Ficheiro | Conteúdo |
|----------|----------|
| [projectplan.md](projectplan.md) | Roadmap completo (16 fases) |
| [Readme.md](Readme.md) | Especificação funcional (950 linhas) |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Próximos passos de desenvolvimento |

### Status e Progresso
| Ficheiro | Conteúdo |
|----------|----------|
| [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) | Estado atual detalhado com métricas |
| [README_IMPLEMENTATION.md](README_IMPLEMENTATION.md) | Sumário do que foi implementado |
| [FINAL_SUMMARY.md](FINAL_SUMMARY.md) | ⭐ Sumário executivo completo |
| [docs/PROGRESS.md](docs/PROGRESS.md) | Log técnico de progresso |

---

## 🗄️ DOCUMENTAÇÃO TÉCNICA

### Base de Dados
| Ficheiro | Conteúdo |
|----------|----------|
| [docs/db/overview.md](docs/db/overview.md) | Arquitetura da base de dados |
| [docs/db/tables.md](docs/db/tables.md) | Documentação de todas as 12 tabelas |
| [docs/db/changelog.md](docs/db/changelog.md) | Histórico de mudanças |
| [src/backend/database/migrations/001_initial_schema.sql](src/backend/database/migrations/001_initial_schema.sql) | Migração inicial SQL |

### Sistema de IA
| Ficheiro | Conteúdo |
|----------|----------|
| [docs/ai/overview.md](docs/ai/overview.md) | Arquitetura do sistema de IA |

### Produto
| Ficheiro | Conteúdo |
|----------|----------|
| [docs/product/overview.md](docs/product/overview.md) | Visão de produto, fluxos, métricas |

### Internacionalização
| Ficheiro | Conteúdo |
|----------|----------|
| [docs/i18n/overview.md](docs/i18n/overview.md) | Sistema multi-idioma (EN, PT, FR, ES) |

---

## 💻 CÓDIGO FONTE

### Backend (Python + FastAPI)
| Ficheiro/Pasta | Descrição |
|----------------|-----------|
| [src/backend/main.py](src/backend/main.py) | Entry point da API |
| [src/backend/config.py](src/backend/config.py) | Configuração (Pydantic) |
| [src/backend/test_setup.py](src/backend/test_setup.py) | Script de teste |
| [src/backend/requirements.txt](src/backend/requirements.txt) | Dependências Python |
| [src/backend/README.md](src/backend/README.md) | Documentação backend |
| **routers/** | API endpoints |
| [src/backend/routers/interviewer.py](src/backend/routers/interviewer.py) | Interviewer flow (9 endpoints) |
| [src/backend/routers/candidate.py](src/backend/routers/candidate.py) | Candidate flow (7 endpoints) |
| **services/database/** | CRUD operations |
| [src/backend/services/database/candidate_service.py](src/backend/services/database/candidate_service.py) | Serviço de candidatos |
| [src/backend/services/database/company_service.py](src/backend/services/database/company_service.py) | Serviço de empresas |
| [src/backend/services/database/interviewer_service.py](src/backend/services/database/interviewer_service.py) | Serviço de interviewers |
| [src/backend/services/database/session_service.py](src/backend/services/database/session_service.py) | Gestão de sessões |
| **services/ai/** | Sistema de IA |
| [src/backend/services/ai/base.py](src/backend/services/ai/base.py) | Interface abstrata |
| [src/backend/services/ai/gemini_provider.py](src/backend/services/ai/gemini_provider.py) | Provider Gemini |
| [src/backend/services/ai/manager.py](src/backend/services/ai/manager.py) | Manager central |
| **services/storage/** | File storage |
| [src/backend/services/storage/supabase_storage.py](src/backend/services/storage/supabase_storage.py) | Supabase Storage |
| **services/email/** | Email sending |
| [src/backend/services/email/resend_service.py](src/backend/services/email/resend_service.py) | Resend integration |

### Frontend (React + TypeScript + Vite)
| Ficheiro/Pasta | Descrição |
|----------------|-----------|
| [src/frontend/src/main.tsx](src/frontend/src/main.tsx) | Entry point |
| [src/frontend/src/App.tsx](src/frontend/src/App.tsx) | App principal + routing |
| [src/frontend/src/index.css](src/frontend/src/index.css) | Design tokens (CSS) |
| [src/frontend/package.json](src/frontend/package.json) | Dependências Node |
| [src/frontend/vite.config.ts](src/frontend/vite.config.ts) | Config Vite + PWA |
| [src/frontend/index.html](src/frontend/index.html) | HTML base |
| [src/frontend/README.md](src/frontend/README.md) | Documentação frontend |
| **i18n/** | Multi-idioma |
| [src/frontend/src/i18n/config.ts](src/frontend/src/i18n/config.ts) | Config i18next |
| [src/frontend/src/i18n/locales/en.json](src/frontend/src/i18n/locales/en.json) | Traduções EN |
| [src/frontend/src/i18n/locales/pt.json](src/frontend/src/i18n/locales/pt.json) | Traduções PT |
| [src/frontend/src/i18n/locales/fr.json](src/frontend/src/i18n/locales/fr.json) | Traduções FR |
| [src/frontend/src/i18n/locales/es.json](src/frontend/src/i18n/locales/es.json) | Traduções ES |
| **components/** | UI components |
| [src/frontend/src/components/Input.tsx](src/frontend/src/components/Input.tsx) | Input com validação |
| [src/frontend/src/components/Checkbox.tsx](src/frontend/src/components/Checkbox.tsx) | Checkbox |
| [src/frontend/src/components/Button.tsx](src/frontend/src/components/Button.tsx) | Button |
| **pages/** | Páginas/rotas |
| [src/frontend/src/pages/InterviewerStep1.tsx](src/frontend/src/pages/InterviewerStep1.tsx) | Step 1 interviewer |
| [src/frontend/src/pages/CandidateStep1.tsx](src/frontend/src/pages/CandidateStep1.tsx) | Step 1 candidate |
| **services/** | Integração API |
| [src/frontend/src/services/api.ts](src/frontend/src/services/api.ts) | Cliente HTTP |

---

## 📋 REGRAS DE DESENVOLVIMENTO (20 ficheiros)

Todas as regras que DEVEM ser seguidas durante o desenvolvimento:

| Regra | Ficheiro | Responsabilidade |
|-------|----------|------------------|
| 00 | [docs/rules/00-multi-role-coordinator.md](docs/rules/00-multi-role-coordinator.md) | Coordenação entre roles |
| 01 | [docs/rules/01-technology-standard.md](docs/rules/01-technology-standard.md) | Python + Supabase + .env |
| 02 | [docs/rules/02-core-coder-role.md](docs/rules/02-core-coder-role.md) | Estrutura e qualidade |
| 03 | [docs/rules/03-code-comments-and-docs-style.md](docs/rules/03-code-comments-and-docs-style.md) | Comentários em inglês |
| 04 | [docs/rules/04-git-github-manager-role.md](docs/rules/04-git-github-manager-role.md) | Git e commits |
| 05 | [docs/rules/05-db-supabase-role.md](docs/rules/05-db-supabase-role.md) | Base de dados |
| 06 | [docs/rules/06-devops-role.md](docs/rules/06-devops-role.md) | DevOps e deploy |
| 07 | [docs/rules/07-security-privacy-role.md](docs/rules/07-security-privacy-role.md) | Segurança e privacidade |
| 08 | [docs/rules/08-legal-role.md](docs/rules/08-legal-role.md) | Legal e compliance |
| 09 | [docs/rules/09-product-role.md](docs/rules/09-product-role.md) | Produto e UX |
| 10 | [docs/rules/10-billing-role.md](docs/rules/10-billing-role.md) | Billing e monetização |
| 11 | [docs/rules/11-analytics-role.md](docs/rules/11-analytics-role.md) | Analytics e tracking |
| 12 | [docs/rules/12-seo-digital-marketing-role.md](docs/rules/12-seo-digital-marketing-role.md) | SEO e marketing |
| 13 | [docs/rules/13-marketing-ai-content-role.md](docs/rules/13-marketing-ai-content-role.md) | Marketing com IA |
| 14 | [docs/rules/14-l10n-i18n-role.md](docs/rules/14-l10n-i18n-role.md) | Localização (i18n) |
| 15 | [docs/rules/15-core-ai-ml-role.md](docs/rules/15-core-ai-ml-role.md) | IA e ML |
| 16 | [docs/rules/16-frontend-pwa-ux-role.md](docs/rules/16-frontend-pwa-ux-role.md) | Frontend e PWA |
| 17 | [docs/rules/17-graphic-design-role.md](docs/rules/17-graphic-design-role.md) | Design visual |
| 18 | [docs/rules/18-qa-testing-role.md](docs/rules/18-qa-testing-role.md) | QA e testes |
| 19 | [docs/rules/19-technical-writer-role.md](docs/rules/19-technical-writer-role.md) | Documentação |
| 20 | [docs/rules/20-customer-success-role.md](docs/rules/20-customer-success-role.md) | Customer success |

---

## 🔍 ENCONTRAR INFORMAÇÃO RÁPIDA

### "Como inicio o projeto?"
→ **[START_HERE.md](START_HERE.md)**

### "O que já está feito?"
→ **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** ou **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)**

### "Como configuro o .env?"
→ **[UPDATE_ENV.md](UPDATE_ENV.md)**

### "Qual é o próximo passo?"
→ **[NEXT_STEPS.md](NEXT_STEPS.md)** ou **[projectplan.md](projectplan.md)**

### "Como funciona a base de dados?"
→ **[docs/db/tables.md](docs/db/tables.md)**

### "Como funciona o sistema de IA?"
→ **[docs/ai/overview.md](docs/ai/overview.md)**

### "Como funciona o multi-idioma?"
→ **[docs/i18n/overview.md](docs/i18n/overview.md)**

### "Qual é a visão do produto?"
→ **[docs/product/overview.md](docs/product/overview.md)**

### "Quais são os requisitos funcionais?"
→ **[Readme.md](Readme.md)** (950 linhas)

### "O que mudou recentemente?"
→ **[docs/PROGRESS.md](docs/PROGRESS.md)**

---

## 📁 ESTRUTURA DE PASTAS

```
ShortlistAI/
├── 📄 Guias principais (10 ficheiros)
│   ├── START_HERE.md              ⭐ Começa aqui
│   ├── FINAL_SUMMARY.md           ⭐ Sumário completo
│   ├── UPDATE_ENV.md              Configuração .env
│   ├── SETUP.md                   Setup detalhado
│   ├── NEXT_STEPS.md              Próximos passos
│   ├── IMPLEMENTATION_STATUS.md   Status atual
│   ├── README_IMPLEMENTATION.md   O que foi feito
│   ├── projectplan.md             Roadmap (16 fases)
│   ├── Readme.md                  Spec funcional
│   └── INDEX.md                   Este ficheiro
│
├── 🐍 src/backend/                Python + FastAPI
│   ├── main.py                    Entry point
│   ├── config.py                  Configuração
│   ├── test_setup.py              Script de teste
│   ├── requirements.txt           Dependências
│   ├── routers/                   API endpoints
│   ├── services/                  Lógica de negócio
│   ├── models/                    Pydantic models
│   └── database/                  BD + migrations
│
├── ⚛️ src/frontend/               React + TypeScript
│   ├── src/
│   │   ├── main.tsx               Entry point
│   │   ├── App.tsx                Routing
│   │   ├── i18n/                  Multi-idioma
│   │   ├── components/            UI components
│   │   ├── pages/                 Páginas
│   │   └── services/              API client
│   ├── package.json               Dependências
│   └── vite.config.ts             Config + PWA
│
├── 📚 docs/                       Documentação
│   ├── PROGRESS.md                Log de progresso
│   ├── db/                        Base de dados
│   ├── ai/                        Sistema IA
│   ├── product/                   Produto
│   ├── i18n/                      i18n
│   └── rules/                     20 regras
│
├── 🧪 tests/                      Testes
│   ├── backend/
│   └── frontend/
│
├── ⚙️ config/                     Configuração
├── 📁 temp/                       Temporários
├── 🚀 start_backend.bat           Iniciar backend
└── 🚀 start_frontend.bat          Iniciar frontend
```

---

## 🎯 FLUXOS DE TRABALHO

### Para Começar a Desenvolver
1. Ler `START_HERE.md`
2. Configurar `.env` (ver `UPDATE_ENV.md`)
3. Executar `start_backend.bat` e `start_frontend.bat`
4. Testar Step 1
5. Começar implementação

### Para Implementar Nova Feature
1. Ler `projectplan.md` (escolher tarefa)
2. Ler regras relevantes em `docs/rules/`
3. Implementar
4. Documentar em `docs/PROGRESS.md`
5. Commit (formato: `action: description`)
6. Atualizar `projectplan.md`

### Para Debug
1. Ver logs no terminal (backend)
2. Ver console do browser (frontend)
3. Usar `/api/docs` para testar endpoints
4. Verificar dados no Supabase Dashboard

---

## 🔗 LINKS ÚTEIS

### Supabase
- **Dashboard**: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp
- **Editor BD**: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/editor
- **API Keys**: https://supabase.com/dashboard/project/uxmfaziorospaglsufyp/settings/api

### Local
- **API Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Frontend App**: http://localhost:3000

---

## 📞 RECURSOS EXTERNOS

- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Vite: https://vitejs.dev
- Supabase: https://supabase.com/docs
- i18next: https://www.i18next.com

---

## ✅ CHECKLIST PRÉ-DESENVOLVIMENTO

Antes de começar a codificar:

- [ ] .env configurado com SUPABASE_SERVICE_ROLE_KEY
- [ ] Backend a correr (http://localhost:8000/health retorna "healthy")
- [ ] Frontend a correr (http://localhost:3000 carrega)
- [ ] Step 1 testado e funcional
- [ ] Git configurado (remote, se aplicável)
- [ ] Regras lidas (docs/rules/)
- [ ] Próxima tarefa escolhida (projectplan.md)

---

**Criado em**: 2025-01-08  
**Última atualização**: 2025-01-08  
**Commits totais**: 12  
**Status**: ✅ Ready for development

---

**Boa codificação! 🚀**

