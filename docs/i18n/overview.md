# Internationalization (i18n) Overview

## Supported Languages

The CV Analysis Platform supports 4 languages:

1. **English (EN)** - Base language
2. **Portuguese (PT)**
3. **French (FR)**
4. **Spanish (ES)**

## Language Selection

### User Experience

- Language selector visible in UI (header or settings)
- Default language determined by:
  1. User's saved preference (localStorage)
  2. Browser language detection
  3. Fallback to English

- When user changes language:
  - All UI elements switch immediately
  - Preference saved to localStorage
  - AI responses use selected language (where configured)

### Technical Implementation

Frontend uses **i18next** with react-i18next.

Configuration in `src/frontend/src/i18n/config.ts`:
```typescript
i18n.use(initReactI18next).init({
  resources: { en, pt, fr, es },
  lng: detectLanguage(),
  fallbackLng: 'en'
});
```

## Translation Files

### Location
```
src/frontend/src/i18n/locales/
  ├── en.json  (Base language)
  ├── pt.json  (Portuguese)
  ├── fr.json  (French)
  └── es.json  (Spanish)
```

### Structure

Translations organized by feature/domain:

```json
{
  "common": { "loading": "Loading...", ... },
  "interviewer": { "title": "Interviewer Flow", ... },
  "candidate": { "title": "Candidate Flow", ... },
  "admin": { ... },
  "forms": { ... },
  "legal": { ... }
}
```

### Adding New Translations

1. Add key in `en.json` (base language)
2. Run AI translation or manually add to pt.json, fr.json, es.json
3. Use in code: `const { t } = useTranslation(); ... {t('common.loading')}`

## Database-Stored Translations

Some content is stored in the database for Admin control:

- UI labels (dynamic content)
- Email templates
- Legal texts (Terms, Privacy Policy)
- Help content
- System messages

### Translation Table Schema

```sql
CREATE TABLE translations (
  id UUID PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  en TEXT NOT NULL,      -- Base language
  pt TEXT,               -- Portuguese
  fr TEXT,               -- French
  es TEXT,               -- Spanish
  category TEXT,         -- ui, email, legal, help
  auto_translated JSONB, -- {pt: true, fr: true, es: false}
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

### Admin Translation Workflow

1. Admin edits English base text
2. Admin triggers AI translation to PT, FR, ES
3. Translations marked as `auto_translated: true`
4. Admin can manually edit any translation (marks as `auto_translated: false`)
5. Regenerating translations warns if manual edits will be overwritten

## Content Language (Job Postings and CVs)

Job postings and CVs can be in **any language**.

AI prompts are designed to:
- Understand content in common languages
- Output responses in user's selected UI language
- Handle mixed-language inputs gracefully

No forced translation of user-provided content.

## AI Response Language

AI outputs (scores, questions, pitches) are generated in the user's selected UI language.

Prompts include instructions like:
```
Respond in {language}. The user selected {language} as their UI language.
```

Admin can override this per prompt if needed.

## Email Language

Emails sent to users use:
- The language the user selected in the UI at the time of request
- Fallback to English if language unknown

Email templates exist in all 4 languages.

## Legal Content Language

**Terms and Conditions** and **Privacy Policy**:
- English is the official legal version
- PT, FR, ES are AI-translated for convenience
- UI clearly indicates: "English is the official version. Other languages are translations for convenience."

Admin can:
- Edit English legal text
- Trigger AI translation
- Review and manually adjust translations

## Localization Best Practices

### For Developers

✅ **Never hardcode user-facing strings**  
- Bad: `<button>Submit</button>`
- Good: `<button>{t('common.submit')}</button>`

✅ **Use descriptive translation keys**  
- Bad: `{t('btn1')}`
- Good: `{t('forms.submit_button')}`

✅ **Design for longer strings**  
- German and Portuguese can be 30-40% longer than English
- Use flexible layouts, avoid fixed widths

✅ **Format dates and numbers correctly**  
- Use locale-aware formatting libraries
- Don't hardcode formats like "MM/DD/YYYY"

✅ **Handle pluralization**  
- i18next supports plural forms per language
- Example: `{t('items', { count: 5 })}` → "5 items" or "5 itens"

### For Translators

✅ **Maintain tone and context**  
- Platform tone: Professional, clear, tech-oriented
- Legal tone: Formal, precise

✅ **Use gender-neutral language where possible**

✅ **Keep translations consistent**  
- Use same term for same concept across all screens

✅ **Test translations in UI**  
- Ensure text fits in buttons, labels, modals

## Testing i18n

### Manual Testing

- Switch languages and check all main screens
- Verify emails in all languages
- Check legal pages

### Automated Testing

- Unit tests for translation keys (ensure all keys exist in all languages)
- Visual regression tests for layout with long strings

## Performance

- Translation files loaded async per language (code splitting)
- Only active language bundle loaded
- Translations cached in memory
- Database translations cached with TTL

## Analytics and Monitoring

Track:
- Language distribution (% of users per language)
- Language switch events
- Missing translation keys (errors logged)

## Future Enhancements

- Add more languages (DE, IT, NL, etc.)
- Region-specific content (e.g., legal differences per country)
- Community-contributed translations
- Translation memory (TM) for consistency
- Professional human review for critical content

