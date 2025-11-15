# Project Scripts

This directory contains utility scripts for ShortlistAI, including SEO validation, image generation, and asset optimization.

## Available Scripts

### SEO Scripts

#### 1. `validate_seo.py`

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

#### 2. `update_sitemap_dates.py`

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

### Image Generation Scripts

#### 3. `generate_brand_images.py`

Generates brand images using Google Gemini API. Creates prompts and manages image generation workflow.

**Usage:**
```bash
python scripts/generate_brand_images.py
```

**Requirements:**
- GEMINI_API_KEY in .env
- google-genai package

---

#### 4. `generate_images_nanobanan.py` / `generate_images_nano_banana.py`

Generate brand images using Gemini Nano Banana (gemini-2.5-flash-image) model.

**Usage:**
```bash
python scripts/generate_images_nanobanan.py
```

**Requirements:**
- GEMINI_API_KEY in .env
- google-genai, Pillow packages

---

#### 5. `generate_images_with_imagen.py`

Generate brand images directly using Google Imagen models.

**Usage:**
```bash
python scripts/generate_images_with_imagen.py
```

---

#### 6. `generate_pwa_icons.py`

Generate additional PWA icon sizes from the base app-icon-512.png.

**Usage:**
```bash
python scripts/generate_pwa_icons.py
```

**Requirements:**
- Pillow package
- Source image: `public/assets/logos/app-icon-512.png`

---

#### 7. `optimize_images_to_webp.py`

Convert brand PNG images to WebP format for better performance (~25-35% better compression).

**Usage:**
```bash
python scripts/optimize_images_to_webp.py
```

**Requirements:**
- Pillow package

---

#### 8. `generate_og_images_by_page.py`

Generate Open Graph images for different pages (home, about, pricing, features) with translated text.

**Usage:**
```bash
python scripts/generate_og_images_by_page.py
```

---

#### 9. `generate_og_images_by_platform.py`

Generate platform-specific Open Graph images (Facebook, LinkedIn, Twitter).

**Usage:**
```bash
python scripts/generate_og_images_by_platform.py
```

---

#### 10. `generate_og_images_multilingual.py`

Generate multilingual Open Graph images for social sharing (EN, PT, FR, ES).

**Usage:**
```bash
python scripts/generate_og_images_multilingual.py
```

---

## Installation

### Requirements

- Python 3.7 or higher
- For SEO scripts: No external dependencies (uses only standard library)
- For image generation scripts: 
  - `google-genai` package (for Gemini-based scripts)
  - `Pillow` package (for image processing)
  - `python-dotenv` package (for environment variables)

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

