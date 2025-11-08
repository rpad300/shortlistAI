# CV Analysis Platform – Functional README (Instructions for Cursor)

This document defines how the project must work from a functional point of view.

The goal is:
- A free web platform for CV analysis using AI.
- Two public flows: Interviewer and Candidate.
- One private backoffice for Admin to manage data, AI prompts, translations and quality.
- Multi language user interface: EN, PT, FR, ES.
- A growing headhunting database, visible only to Admin.

No technical stack is defined here. All framework, library and hosting decisions must follow these rules.

---

## 1. Product overview

### 1.1. Purpose

The platform must:

- Help interviewers compare many CVs against a specific job posting in a structured and consistent way.
- Help candidates understand how they fit a job and prepare for interviews.
- Store all CVs and analyses in a structured way for future headhunting.
- Ensure that only the Admin has access to all stored data.
- Allow the Admin to define and adjust all AI prompts used in every step.
- Offer a multi language experience with automatic translations.
- Include basic controls to monitor and improve AI quality over time.

### 1.2. Target users

There are three types of users:

1. Interviewer  
   Person who has a job opening and wants to evaluate candidates.

2. Candidate  
   Person who has a CV and a job posting and wants help to prepare.

3. Admin  
   Owner of the platform.  
   Only user with access to the full dataset, quality controls and configuration backoffice.

No one except the Admin may see the full database of CVs, candidates, companies or analyses.

---

## 2. Languages and internationalization

### 2.1. Supported languages

The platform must support these user interface languages:

- English (EN) – base language.
- Portuguese (PT).
- French (FR).
- Spanish (ES).

All platform texts must exist in these languages, including:

- UI labels, menus and buttons.
- Form labels and validation messages.
- Help texts and tooltips.
- Error messages.
- Emails sent to users.
- Terms and Conditions.
- Privacy Policy.
- Static explanatory content.
- System messages shown while AI is running.

### 2.2. Base language and automatic translation

Functional rules:

- English is the base language for content management.
- All source texts are defined in English first.
- Translations to PT, FR and ES are generated automatically using AI translation.
- Translations are stored and reused. The system does not regenerate them on every request, unless Admin asks to update.

Admin must be able to:

- Edit the English text.
- Trigger AI translation for PT, FR and ES per text or per group of texts.
- See which translations were generated automatically and which were edited manually.
- Decide when to regenerate translations.

### 2.3. Language selection for users

Functional behaviour:

- There is a visible language selector in the public interface.
- Default language:
  - If the browser language matches EN, PT, FR or ES, use that language.
  - Otherwise, use English by default.
- Users can change language at any time.
- After a change, all UI elements on the page must switch to the selected language.

The AI responses shown to users must use the same language as the selected UI language, unless Admin explicitly configures a different rule in the prompts.

### 2.4. Language of content provided by users

Job postings and CVs can be in any language.

Rules:

- The system accepts job postings and CVs in different languages without blocking.
- AI prompts must be designed so that:
  - The AI can understand the content.
  - The AI answers in the selected UI language or in English, based on prompt configuration.
- Internal translation steps are allowed, but they do not change the functional result.

### 2.5. Multi language emails

Emails sent to Interviewers and Candidates must:

- Use the same language that the user selected in the UI at the time of the request, when this is known.
- Use English if the language is unknown.

Admin may later decide to send bilingual emails, but this is not required in the first version.

### 2.6. Multi language legal content

Terms and Conditions and Privacy Policy:

- Must exist at least in English as the base legal text.
- AI translated versions must exist for PT, FR and ES.
- The UI must clearly show:
  - English is the base legal version.
  - PT, FR and ES versions are translations for convenience.

Admin must be able to:

- Edit the English legal texts.
- Trigger AI translation to update PT, FR and ES versions.

---

## 3. Access and authentication

### 3.1. Public area (no login)

- Interviewer flow and Candidate flow must be accessible without login.
- Users fill forms and upload content.
- Users do not have accounts, passwords or personal dashboards.

### 3.2. Admin area (login required)

- There is a private backoffice for Admin.
- Only Admin can:
  - Log in.
  - See lists of candidates, companies, job postings and analyses.
  - Manage AI prompts, AI providers and translations.
  - Review AI quality and golden test cases.
  - Export or review data for headhunting.
- Access is protected by Admin credentials.

Public users must never access Admin screens or APIs that return stored data.

---

## 4. Interviewer flow (public)

The Interviewer flow is used by someone who has a vacancy and a set of CVs.

### 4.1. Steps for the Interviewer

Step 1 – Identification and consent

Form with fields:

- Name
- Email
- Phone
- Country
- Company name (optional)

Checkboxes:

- Accept Terms and Conditions.
- Accept Privacy Policy.
- Explicit consent to:
  - Store their personal data.
  - Store the CVs they upload.
  - Use the data for future headhunting and contact.

If consent is not given, the process stops.

Step 2 – Job posting

The interviewer provides the job posting by:

- Pasting the text, or
- Uploading a file (for example PDF or DOCX).

The system must store:

- Raw text of the job posting.
- Raw file if uploaded.

The job posting must be stored as a reusable object, so the interviewer or Admin can:

- Reuse the same posting later.
- Upload new CVs for the same posting in new batches.

Step 3 – Key points for the role

The interviewer fills a free text field describing:

- Most important skills.
- Must have requirements.
- Nice to have skills.
- Experience level.
- Languages.
- Tools and technologies.

The system stores this text and links it to the job posting.

Step 4 – Weighting and hard blockers

The interviewer can refine the evaluation rules:

- Define weights for main categories. Examples:
  - Technical skills weight 50 percent.
  - Languages weight 20 percent.
  - Culture fit weight 10 percent.
- Define simple hard blockers. Examples:
  - Must speak French.
  - Must live in a given country.
  - Must accept on site work.

The platform uses:

- AI scores per category (1 to 5).
- Weights to compute the final global score per candidate.
- Hard blockers to flag candidates that do not meet critical requirements.

Hard blockers must be visible in the results as clear warnings.

Step 5 – CV upload

The interviewer uploads one or more CVs for this job posting.

Behaviour:

- Each CV is stored:
  - Original file.
  - Extracted text.
- The system must try to detect if a CV belongs to an existing candidate based on:
  - Email address inside the CV, or
  - Email provided manually in future versions.
- If the same candidate appears again, the system:
  - Links the new CV version to the existing candidate profile.
  - Does not create a completely new candidate record, unless data is incomplete.

The platform must support multiple batches of CVs for the same posting:

- First batch of CVs.
- Later, new CVs can be added and analysed for the same job.

Step 6 – AI analysis (Interviewer mode)

The system will:

- Convert:
  - Job posting to a structured representation.
  - Key points text to a structured representation.
  - Each CV to a structured representation.
- Call the AI analysis for “Interviewer mode” with:
  - Job posting structure.
  - Key points structure.
  - List of CV structures.
  - Information about:
    - Selected UI language.
    - Weights and hard blockers.

The AI must:

- Derive up to 10 evaluation categories that make sense for that job.
- For each candidate:
  - Assign a score from 1 to 5 for each category.
  - Provide text that explains the score when useful.
  - Suggest strengths and risks.
  - Suggest custom interview questions focused on:
    - The most important skills for the job.
    - Gaps, doubts or inconsistencies in the CV.

The platform must then:

- Apply interviewer weights to compute a weighted global score per candidate.
- Flag hard blockers for each candidate.
- Store:
  - Categories and scores.
  - Global score.
  - Flags for hard blockers.
  - Strengths and risks.
  - Custom interview questions.
  - Provider used.
  - Prompt configuration version used.
  - Language used in AI responses.

Step 7 – Results for the Interviewer

The results page for the interviewer must show:

1. Ranking table of candidates:
   - One row per candidate.
   - Columns:
     - Candidate name or identifier.
     - Each evaluation category and score.
     - Weighted global score.
     - Indicators for hard blockers.

   The table must be sorted by global score, from highest to lowest. Candidates with hard blockers should be visually flagged.

2. Detailed view per candidate:
   - Candidate summary.
   - Scores per category.
   - Strengths and risks.
   - List of custom interview questions.
   - Clear indication of any hard blocker.

3. Transparency block:
   - Short explanation such as:
     - What data was used.
     - Which type of AI engine was used.
     - Reminder that the analysis is advisory and not a final hiring decision.

All UI elements and AI texts must respect the language selected by the user.

Step 8 – Email and reports for the Interviewer

The interviewer can request:

- An email summary.
- A downloadable report.

Email summary must contain:

- Ranking table (simplified).
- Short textual summary of the overall analysis.
- Basic transparent note that AI was used as support.

Downloadable report (first version can be simple):

- PDF or similar format with:
  - Job posting summary.
  - List of candidates and scores.
  - Key highlights and warnings.

Emails must be sent through an email service integrated with Gmail via Resend and must use the selected UI language when known.

---

## 5. Candidate flow (public)

The Candidate flow is used by a person who wants to prepare for a specific job.

### 5.1. Steps for the Candidate

Step 1 – Identification and consent

Form with fields:

- Name
- Email
- Phone
- Country

Checkboxes:

- Accept Terms and Conditions.
- Accept Privacy Policy.
- Explicit consent to:
  - Store their CV.
  - Store the job posting they provide.
  - Use the data for future headhunting and contact.

If consent is not given, the process stops.

Step 2 – Job posting

The candidate provides the job posting for which they applied:

- Paste the text, or
- Upload a file.

The system stores:

- Raw text.
- Raw file if uploaded.

Step 3 – CV upload

The candidate uploads their CV.

The system:

- Stores the original file.
- Extracts text.
- Looks for an existing candidate profile based on email.
- If found:
  - Links the new CV to the existing profile as a new CV version.
- If not:
  - Creates a new candidate record.

Step 4 – AI analysis (Candidate mode)

The system will:

- Convert:
  - Job posting to structured representation.
  - CV to structured representation.
- Call AI analysis for “Candidate mode” with:
  - Job posting structure.
  - CV structure.
  - Selected UI language.

The AI must:

- Classify the candidate against the job using categories and scores from 1 to 5.
- Identify:
  - Strengths.
  - Gaps and risk areas.
- Generate:
  - Likely interview questions for this role.
  - Suggested answers or answer structures.
  - A short intro pitch paragraph for the candidate to use at the start of the interview.

The AI response must be in the selected UI language.

The system must store:

- Categories and scores.
- Strengths and gaps.
- Questions and suggested answers.
- Intro pitch.
- Provider used.
- Prompt configuration version used.
- Language used.

Step 5 – Results for the Candidate

The results page for the candidate must show:

- Scores per category.
- Strengths and gaps.
- Questions to prepare for.
- Suggested answers or answer structures.
- Intro pitch text.

A transparency block must explain:

- That AI generated the analysis.
- Which information was used.
- That the result is guidance and not a guarantee of success.

Step 6 – Email and report for the Candidate

The candidate can request an email and optionally a downloadable report.

Email must include:

- Scores per category.
- Questions and suggested answers.
- Intro pitch.

The report may include:

- Summary of fit.
- Clear preparation checklist.

Email content must use the selected UI language and must be sent using the same email service integrated with Gmail via Resend.

---

## 6. Data, storage, deduplication and headhunting

### 6.1. Data stored

The system must store at least:

For each candidate:

- Name
- Email
- Phone
- Country
- All CV files uploaded.
- Extracted text from each CV.
- Structured representations of CVs.
- Analyses from:
  - Interviewer flow.
  - Candidate flow.

For each company and interviewer:

- Company name (where available).
- Interviewer contact details.
- Job postings and associated analyses.

For each job posting:

- Original raw text.
- Original file if uploaded.
- Structured representation.
- Structured key points.
- All candidate evaluations across batches.

For each AI analysis:

- Mode (Interviewer or Candidate).
- Categories and scores.
- Weighted global score where applicable.
- Strengths and risks.
- Custom questions and content.
- Intro pitch where relevant.
- Provider used.
- Prompt configuration version used.
- Language of the response.
- Timestamps for creation and updates.

### 6.2. Candidate identity and deduplication

Functional rules:

- The email address is the main key to identify a candidate.
- If a new CV is uploaded and matches an existing email:
  - Attach as a new CV version to the existing candidate.
- Admin must have tools in the backoffice to:
  - Merge duplicate candidates if needed.
  - See which CVs and analyses belong to the same person.

### 6.3. Access rules for stored data

- Public users:
  - Do not browse or search the database.
  - Only see results of the current session in the browser and the emails they receive.

- Admin:
  - Can search by candidate, company and job posting.
  - Can open details of candidates, companies, job postings and analyses.
  - Can export data when needed.

### 6.4. Headhunting objective

All CVs and analyses form a headhunting database.

The platform must support future features where Admin can:

- Search candidates by:
  - Skills.
  - Experience level.
  - Location.
  - Other criteria from structured data.
- See candidate fit history across different roles.
- Contact candidates about new opportunities.

The consent text must explain this in all languages.

### 6.5. Data rights and retention

To support privacy and regulations:

- Users must be informed that they can:
  - Request access to their stored data.
  - Request deletion of their data, within legal and technical limits.

Functionally:

- There must be a clear way to request these actions, at least via a contact email in the legal pages.
- Admin must be able to:
  - Locate a candidate by email.
  - Export or delete their data on request.

Retention:

- The system must support a retention rule, for example:
  - Keep data for a given number of years unless deletion is requested earlier.
- Admin must be able to see and adjust the retention rule description in the legal texts. The technical enforcement can come later.

---

## 7. AI providers and behaviour

### 7.1. Providers supported

The platform must support several AI providers:

- Gemini
- OpenAI
- Claude
- Kimi
- Minimax

Functional requirements:

- There must be a way to set a default provider.
- Admin must be able to choose the provider per prompt configuration.
- Switching providers must not change the functional flow.

### 7.2. AI responsibilities

The AI layer is responsible for:

- Converting free text into structured representations.
- Generating evaluation categories and scores.
- Generating comparative analysis and interviewer questions.
- Generating preparation content, suggested answers and pitches for candidates.
- Translating texts for multi language support when requested.
- Respecting:
  - Prompt configuration.
  - Target language for each response.

Outputs must always be structured and easy to map to:

- Categories.
- Scores.
- Lists of questions.
- Short paragraphs.

---

## 8. AI quality control and golden cases

### 8.1. Quality review in backoffice

The Admin backoffice must provide tools to review AI behaviour.

Admin must be able to:

- See a list of recent analyses.
- Open a detail view for each analysis showing:
  - Inputs:
    - Job posting.
    - Key points.
    - CV text.
  - Outputs:
    - Categories and scores.
    - Strengths and risks.
    - Questions and pitches.
  - Provider and prompt version used.

Admin can:

- Mark an analysis as:
  - Acceptable.
  - Problematic.
- Add an internal comment or note explaining the issue.

These quality markers are stored and can be used to guide future improvements.

### 8.2. Golden test cases

Admin must be able to maintain a set of “golden cases”:

- Test samples that represent important or frequent situations.
- Each golden case includes:
  - Example job posting.
  - Example CV or CV set.
  - Expected behaviour notes (for human reference).

Admin must be able to:

- Run a golden case with:
  - A selected prompt version.
  - A selected provider.
- See the output and decide if it is acceptable.

Golden cases are used to check the impact of changes in prompts or providers before these changes affect real users.

---

## 9. Backoffice (Admin) – Prompt management

The Admin backoffice controls all AI prompts.

### 9.1. Goals of prompt management

Admin must be able to:

- See all prompt configurations, grouped by use case.
- Create, edit and version prompts without code changes.
- Select AI provider per prompt.
- Define language behaviour in prompts.
- Track which prompt version was used in each analysis.

### 9.2. Prompt types

At minimum, the system must support these prompt groups:

1. Job posting normalization.
2. Key points normalization.
3. CV extraction and structuring.
4. Interviewer analysis.
5. Candidate self analysis.
6. Email summary for Interviewer.
7. Email summary for Candidate.
8. Translation of platform texts and legal content.

### 9.3. Prompt configuration fields

For each prompt configuration, Admin defines:

- Name of the prompt.
- Description.
- Flow and step (for example “Interviewer / Analysis”).
- AI provider to use.
- Base prompt template content in English.
- Rules for response language:
  - Use user selected language.
  - Use English only.
  - Other rule if needed.
- Expected response structure.
- Status:
  - Active.
  - Inactive.
- Version identifier.

The system always uses the active version per prompt type.

### 9.4. Prompt versioning and tracking

Functional rules:

- Admin can:
  - Duplicate an existing prompt.
  - Edit it.
  - Save as a new version.
  - Activate the new version.

- For each AI analysis stored, the system must record:
  - Prompt configuration identifier.
  - Prompt version identifier.

This allows Admin to trace issues back to specific prompts.

### 9.5. Prompt testing interface

The Admin backoffice must provide a test interface where Admin can:

- Choose a prompt.
- Provide sample input.
- Call AI.
- See raw and structured output.

Test calls must not alter production data.

---

## 10. Backoffice (Admin) – Translation and content management

### 10.1. Base text management

Admin must manage base texts in English for:

- UI labels and messages.
- Email templates.
- Static pages.
- Legal texts (Terms and Privacy).

Each text entry must store:

- Key or identifier.
- English base value.
- PT, FR and ES translated values.
- A flag per translation indicating:
  - Generated automatically.
  - Edited manually.

### 10.2. Translation operations

Admin can:

- Trigger AI translation from EN to PT, FR and ES for one text.
- Trigger AI translation for a group of texts.
- Regenerate translations after editing the English base text.

If a translation was edited manually, the system should warn before overwriting.

---

## 11. Backoffice (Admin) – Data management

### 11.1. Candidates

Admin can:

- List candidates with filters:
  - Name.
  - Email.
  - Country.
- Open candidate details:
  - Personal data.
  - CV files and versions.
  - Analyses from both flows.
  - Data rights status if relevant (for example, “deletion requested”).

Admin can merge duplicate candidates when needed.

### 11.2. Companies and interviewers

Admin can:

- List companies.
- See interviewers per company.
- See job postings per company.
- See a summary of candidate analyses for each job posting.

### 11.3. Job postings and evaluations

Admin can:

- List all job postings.
- Open a job posting to see:
  - Original text and file.
  - Structured representation and key points.
  - Batches of CVs analysed.
  - Evaluation tables and detailed results.

### 11.4. Exports

The system must be prepared so that Admin can:

- Export candidate lists.
- Export job posting summaries.
- Export evaluation tables.

Exports are limited to Admin.

---

## 12. Abuse prevention and usage limits

Even without full technical detail, the platform must include basic functional rules to prevent abuse:

- Limit number of analyses per session or per IP within a time window, to reduce automated abuse.
- Validate file types and sizes for uploads.
- Allow Admin to:
  - Block abusive patterns.
  - Temporarily disable public flows in extreme cases.

Error messages shown to users in these cases must be clear and polite.

---

## 13. Terms, Conditions and Privacy

The platform must have:

- A Terms and Conditions page.
- A Privacy Policy page.
- Short consent texts near checkboxes in forms.

Functional requirements:

- English is the base legal version.
- PT, FR and ES AI translations are available.
- The UI must:
  - Show the correct language version based on the language selector.
  - Indicate that English is the main legal reference.

Legal content must explain:

- What data is stored.
- For which purposes:
  - Analysis and preparation.
  - Future headhunting and contact.
- That data may be processed by external AI providers:
  - Gemini, OpenAI, Claude, Kimi, Minimax and future providers.
- Which rights users have:
  - Access to data.
  - Correction.
  - Deletion, within legal limits.
- How users can exercise these rights (for example via contact email).

---

## 14. Rules for implementation and documentation (for Cursor)

These rules guide how work must be organized.

### 14.1. Project files

The project must include at least:

- `projectplan.md`  
  Main task list and roadmap. Must be read first before any change.

- `README.md`  
  High level project description and how to run it. It must reference this functional specification.

- `src/`  
  Only production application code.

- `docs/`  
  Documentation for:
  - Data structures.
  - API contracts.
  - Prompt definitions and their intent.
  - Translation model and flows.
  - Data rights and retention model.

- `temp/`  
  Temporary scripts and experiments. Not considered production code.

### 14.2. Behaviour rules for Cursor

1. Always read `projectplan.md` before starting to work.
2. Only implement behaviour that is aligned with:
   - This functional README.
   - `projectplan.md`.
3. If something important is not defined:
   - Choose the safest and simplest assumption.
   - Add a clear `TODO` comment describing the open point.
4. Keep the codebase clean:
   - No leftover debug code in production areas.
   - No business logic hidden in `temp/`.
5. All code comments must be in English with professional tone:
   - Describe purpose of modules and functions.
   - Describe inputs and outputs when relevant.
   - Explain non obvious business rules, especially around:
     - Scoring and weights.
     - Hard blockers.
     - AI prompts and translation.
     - Data privacy and retention.
6. Maintain documentation in `docs/`:
   - Update schema documentation when data structures change.
   - Document new prompts and translation flows.
   - Document new Admin features, such as quality review or golden cases.

---

## 15. Future evolution

The platform should support future extensions, such as:

- Advanced candidate search for Admin:
  - By skills.
  - By experience.
  - By location.
- Notifications for new opportunities sent to candidates.
- More UI languages beyond EN, PT, FR and ES.
- Rich dashboards and analytics for Admin:
  - Number of CVs analysed.
  - Most common roles and skills.
  - AI performance metrics.

This document is the reference for what the platform must do.  
All technical design and implementation choices must respect the behaviour described here.
