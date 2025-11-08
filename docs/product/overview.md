# Product Overview – CV Analysis Platform

## Vision

Build a free, AI-powered platform that helps interviewers make better hiring decisions and candidates prepare more effectively for interviews, while creating a valuable headhunting database.

## Target Users

### 1. Interviewers (Primary)
- **Who**: HR professionals, hiring managers, recruiters
- **Problem**: Comparing many CVs consistently and objectively is time-consuming and subjective
- **Solution**: AI-powered batch analysis with structured scoring, custom questions, and rankings
- **Value**: Save time, reduce bias, focus on best candidates, get better interview questions

### 2. Candidates (Primary)
- **Who**: Job seekers applying for roles
- **Problem**: Hard to know how well they match a job or what questions to expect
- **Solution**: AI-powered fit analysis with preparation guidance and suggested answers
- **Value**: Better interview preparation, understand strengths/gaps, increase confidence

### 3. Admin (Platform Owner)
- **Who**: Platform operator
- **Problem**: Need to manage data, AI quality, translations, and build headhunting value
- **Solution**: Comprehensive backoffice for data, AI, and content management
- **Value**: Control quality, optimize AI, grow database, extract business value

## Core Value Propositions

### For Interviewers
✅ **Speed**: Analyze 10, 50, or 100 CVs in minutes, not hours  
✅ **Consistency**: All candidates evaluated using same criteria  
✅ **Objectivity**: Structured scoring reduces unconscious bias  
✅ **Insight**: Custom interview questions based on gaps and strengths  
✅ **Free**: No cost to use the platform  

### For Candidates
✅ **Preparation**: Know what questions to expect  
✅ **Self-awareness**: Understand fit and gaps clearly  
✅ **Confidence**: Practice answers with AI-suggested structures  
✅ **Free**: No cost to access preparation tools  

### For Admin / Platform
✅ **Data**: Growing database of CVs, skills, and companies  
✅ **Headhunting**: Match candidates to future opportunities  
✅ **Quality**: Tools to monitor and improve AI behavior  
✅ **Scalability**: Multi-language, multi-provider, multi-tenant ready  

## Main Flows

### Interviewer Flow (8 Steps)
1. **Identification & Consent**: Name, email, company, consent checkboxes
2. **Job Posting**: Paste or upload job description
3. **Key Points**: Define most important skills and requirements
4. **Weighting & Hard Blockers**: Set category weights and must-have criteria
5. **Upload CVs**: Batch upload (PDF, DOCX)
6. **AI Analysis**: System processes job + CVs, generates scores and questions
7. **Results**: Ranked table + detailed candidate views + transparency note
8. **Email & Report**: Send summary and download report

### Candidate Flow (6 Steps)
1. **Identification & Consent**: Name, email, consent checkboxes
2. **Job Posting**: Paste or upload job they applied for
3. **Upload CV**: Single CV upload
4. **AI Analysis**: System evaluates fit and generates preparation content
5. **Results**: Scores, strengths, gaps, questions, suggested answers, intro pitch
6. **Email & Report**: Receive preparation guide via email

## Key Features

### Multi-Language Support
- EN, PT, FR, ES out of the box
- UI adapts to user selection
- AI responds in selected language
- Legal content translated with disclaimer

### AI Provider Flexibility
- Support for Gemini, OpenAI, Claude, Kimi, Minimax
- Admin configures which provider for which task
- Transparent to end users

### Headhunting Database
- All CVs and analyses stored
- Deduplication by email
- Admin can search candidates by skills, location, role fit
- Future: proactive candidate matching

### Admin Backoffice
- Candidate, company, job posting management
- AI prompt and provider configuration
- Translation management (view, edit, regenerate)
- Quality review and golden test cases
- Data export for headhunting

### Privacy & Compliance
- Explicit consent before storing data
- Clear privacy policy and terms
- User rights (access, deletion)
- Transparent AI usage
- Secure data handling

## Success Metrics

### User Adoption
- Number of analyses per month (interviewer + candidate)
- Number of CVs uploaded
- Return users (same email using platform again)

### Quality
- Average Admin quality rating of analyses
- User feedback (if collected)
- Support requests or complaints

### Database Growth
- Total candidates in database
- Diversity of skills and roles
- Companies using the platform

### Technical Health
- API uptime
- Average analysis latency
- AI cost per analysis

## Competitive Advantage

🔹 **Free for users**: Lower barrier to entry  
🔹 **Dual flow**: Serve both sides of the hiring process  
🔹 **Multi-language**: Broader market reach  
🔹 **AI-powered quality**: Better than manual comparison  
🔹 **Headhunting value**: Platform gains value over time  

## Future Roadmap

### Phase 1 (MVP)
- Core interviewer and candidate flows
- Basic admin backoffice
- Multi-language UI and AI
- Email integration

### Phase 2
- Advanced candidate search for headhunting
- Candidate notification system
- Analytics dashboards for Admin
- A/B testing of prompts

### Phase 3
- Integration with job boards
- Company-specific custom prompts
- Mobile apps (iOS, Android)
- Advanced reporting and exports

### Phase 4
- White-label solution for enterprises
- API access for third-party integrations
- Premium features (faster AI, priority support)
- Multi-modal analysis (video interviews)

## Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| Low-quality AI outputs | Golden cases, quality review, prompt versioning |
| Data privacy concerns | Clear consent, GDPR compliance, transparency |
| Cost explosion (AI usage) | Rate limiting, cost tracking, quotas |
| Abuse (spam, scraping) | Rate limiting, CAPTCHA, IP blocking |
| Low user adoption | SEO, marketing, partnerships, free value prop |

## Alignment with Other Roles

- **Legal**: Privacy policy, terms, consent flows
- **Security**: Data protection, abuse prevention, secrets management
- **AI**: Prompt quality, provider selection, cost optimization
- **Analytics**: Event tracking, dashboards, metrics
- **Marketing**: SEO, landing pages, growth campaigns
- **Frontend**: PWA, multi-device, responsive design, theming
- **DevOps**: Uptime, monitoring, scaling, backup

## Next Steps

1. Complete MVP flows (interviewer and candidate)
2. Test with real users (friends, small companies)
3. Iterate based on feedback
4. Launch publicly with basic SEO and marketing
5. Monitor metrics and improve AI quality
6. Build headhunting features

