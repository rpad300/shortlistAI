# SEO Scripts

This directory contains scripts for maintaining and monitoring SEO for ShortlistAI.

## Available Scripts

### 1. `validate_seo.py`

Validates structured data (JSON-LD) and SEO metadata for ShortlistAI.

**Usage:**
```bash
# Windows
python scripts/validate_seo.py

# Linux/Mac
python3 scripts/validate_seo.py
```

**What it checks:**
- JSON-LD structured data validity
- Essential meta tags (title, description, viewport, charset)
- Open Graph tags
- Twitter Card tags
- AI-friendly meta tags
- Canonical URLs
- Hreflang alternate language links
- sitemap.xml structure
- robots.txt configuration

**Output:**
- ✓ Success messages (green)
- ✗ Error messages (red)
- ⚠ Warning messages (yellow)
- ℹ Info messages (blue)

---

### 2. `update_sitemap_dates.py`

Updates lastmod dates in sitemap.xml to current date or specified date.

**Usage:**
```bash
# Update all dates to today
python scripts/update_sitemap_dates.py

# Update all dates to specific date
python scripts/update_sitemap_dates.py --date 2025-02-01
```

**What it does:**
- Reads sitemap.xml
- Finds all `<lastmod>` tags
- Updates them to specified date (or today)
- Writes updated sitemap back

**Example:**
```bash
python scripts/update_sitemap_dates.py --date 2025-01-15
# ✓ Updated 9 lastmod date(s) to 2025-01-15 in sitemap.xml
```

---

## Installation

### Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

### Setup

1. **Clone repository** (if not already done)
2. **Navigate to project root**
3. **Run scripts directly**

No installation required!

---

## Windows Usage

On Windows, you can run the scripts directly with Python:

```cmd
python scripts\validate_seo.py
python scripts\update_sitemap_dates.py
```

Or create batch files:

**validate_seo.bat:**
```batch
@echo off
python scripts\validate_seo.py
pause
```

**update_sitemap_dates.bat:**
```batch
@echo off
python scripts\update_sitemap_dates.py %*
pause
```

---

## Linux/Mac Usage

On Linux/Mac, you can run the scripts directly:

```bash
python3 scripts/validate_seo.py
python3 scripts/update_sitemap_dates.py
```

Make scripts executable (optional):
```bash
chmod +x scripts/validate_seo.py
chmod +x scripts/update_sitemap_dates.py
./scripts/validate_seo.py
./scripts/update_sitemap_dates.py
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: SEO Validation

on:
  pull_request:
    paths:
      - 'src/frontend/index.html'
      - 'src/frontend/src/components/SEOHead.tsx'
      - 'src/frontend/public/sitemap.xml'
      - 'src/frontend/public/robots.txt'

jobs:
  validate-seo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Validate SEO
        run: python3 scripts/validate_seo.py
```

---

## Scheduled Tasks

### Monthly Sitemap Update

Create a cron job (Linux/Mac) or scheduled task (Windows) to update sitemap dates monthly:

**Linux/Mac (Cron):**
```bash
# Run on 1st of every month at 2 AM
0 2 1 * * cd /path/to/project && python3 scripts/update_sitemap_dates.py
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Monthly, 1st day
4. Set action: Start a program
5. Program: `python`
6. Arguments: `scripts\update_sitemap_dates.py`
7. Start in: `C:\path\to\project`

---

## Troubleshooting

### Common Issues

**Issue: "python: command not found"**
- Solution: Use `python3` instead of `python`
- Or install Python and add to PATH

**Issue: "File not found"**
- Solution: Run script from project root directory
- Check file paths are correct

**Issue: "Permission denied" (Linux/Mac)**
- Solution: Make script executable: `chmod +x scripts/validate_seo.py`
- Or run with: `python3 scripts/validate_seo.py`

**Issue: "Module not found"**
- Solution: All scripts use only standard library
- No installation needed
- Check Python version (3.7+)

---

## Testing

### Test Validation Script

```bash
# Run validation
python scripts/validate_seo.py

# Expected: Should show validation results
```

### Test Sitemap Updater

```bash
# Update dates
python scripts/update_sitemap_dates.py --date 2025-01-15

# Verify dates were updated
cat src/frontend/public/sitemap.xml | grep lastmod
```

---

## Related Documentation

- **Monitoring Guide**: `docs/seo/monitoring-guide.md`
- **Keyword Checklist**: `docs/seo/keyword-checklist.md`
- **AI Bot Testing**: `docs/seo/ai-bot-testing.md`
- **SEO Review**: `docs/seo/SEO_METADATA_REVIEW_2025-01-10.md`

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0

