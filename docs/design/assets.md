# ShortlistAI Visual Assets Guide

**Version**: 1.0.0  
**Last Updated**: November 10, 2025

---

## 1. Asset Organization

### Directory Structure

```
public/assets/
├── logos/                  # Logo variations
│   ├── shortlistai-full-color.svg
│   ├── shortlistai-icon-only.svg
│   ├── shortlistai-monochrome-black.svg
│   ├── shortlistai-monochrome-white.svg
│   └── app-icon-512.png  (to be generated)
├── icons/                  # UI icons
│   ├── feature-ai.svg
│   ├── feature-document.svg
│   ├── feature-analytics.svg
│   ├── feature-email.svg
│   ├── upload.svg
│   ├── download.svg
│   ├── check-circle.svg
│   └── warning.svg
├── heroes/                 # Hero images (to be generated)
│   ├── hero-home-light.webp
│   ├── hero-home-dark.webp
│   ├── hero-mobile-light.webp
│   └── hero-mobile-dark.webp
├── social/                 # Social media assets (to be generated)
│   └── og-default.png
├── backgrounds/            # Background patterns
│   └── pattern-neural.svg
└── illustrations/          # Feature illustrations (to be generated)
    ├── feature-interviewer.webp
    └── feature-candidate.webp
```

---

## 2. Logo Usage

### Primary Logo (Full Color)

**File**: `shortlistai-full-color.svg`

**When to use**:
- Primary usage in all marketing materials
- Website header
- Landing pages
- Email signatures
- Documents and presentations

**Minimum size**: 120px width

**Example**:
```html
<img src="/assets/logos/shortlistai-full-color.svg" 
     alt="ShortlistAI" 
     width="200" 
     height="50">
```

### Icon Only

**File**: `shortlistai-icon-only.svg`

**When to use**:
- App icons (PWA manifest)
- Favicons
- Small spaces (navigation, mobile headers)
- Social media profile pictures
- Loading screens

**Minimum size**: 32px

**Example**:
```html
<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/assets/logos/shortlistai-icon-only.svg">

<!-- PWA Manifest -->
{
  "icons": [
    {
      "src": "/assets/logos/app-icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### Monochrome Versions

**Files**: 
- `shortlistai-monochrome-black.svg` - For light backgrounds
- `shortlistai-monochrome-white.svg` - For dark backgrounds

**When to use**:
- Print materials (black & white)
- Watermarks
- Overlays on photos
- When color is not available

**Example**:
```html
<!-- Dynamic based on theme -->
<picture>
  <source srcset="/assets/logos/shortlistai-monochrome-white.svg" 
          media="(prefers-color-scheme: dark)">
  <img src="/assets/logos/shortlistai-monochrome-black.svg" 
       alt="ShortlistAI">
</picture>
```

### Logo DON'Ts

❌ Do not stretch or distort the logo  
❌ Do not change colors outside brand palette  
❌ Do not rotate or tilt  
❌ Do not add effects (shadows, strokes, glows)  
❌ Do not place on low-contrast backgrounds  
❌ Do not use old or unofficial logo versions

---

## 3. Icons

### UI Icons

All icons are **outline style** with **2px stroke** and **24x24px** default size.

**Color**: Icons inherit color from their parent element.

#### Available Icons

| Icon | File | Usage |
|------|------|-------|
| AI/Brain | `feature-ai.svg` | AI features, analysis, intelligence |
| Document | `feature-document.svg` | CVs, resumes, files, documents |
| Analytics | `feature-analytics.svg` | Charts, scores, results, data |
| Email | `feature-email.svg` | Email, communication, send |
| Upload | `upload.svg` | File upload actions |
| Download | `download.svg` | Download, export actions |
| Check | `check-circle.svg` | Success, confirmation, completed |
| Warning | `warning.svg` | Alerts, warnings, errors |

#### Usage Example

```html
<!-- Inline SVG (recommended for color control) -->
<svg class="icon icon-ai">
  <use href="/assets/icons/feature-ai.svg#icon"></use>
</svg>

<!-- Or as img -->
<img src="/assets/icons/feature-ai.svg" 
     alt="" 
     class="icon" 
     width="24" 
     height="24">
```

```css
.icon {
  width: 24px;
  height: 24px;
  color: var(--ai-blue); /* Icons inherit color */
}
```

#### Accessibility

Always provide appropriate `aria-label` or `alt` text:

```html
<!-- Decorative icon (empty alt) -->
<img src="/assets/icons/feature-ai.svg" alt="" aria-hidden="true">

<!-- Functional icon -->
<button aria-label="Upload CV">
  <img src="/assets/icons/upload.svg" alt="">
</button>

<!-- Icon with text -->
<a href="/upload">
  <img src="/assets/icons/upload.svg" alt="">
  Upload CV
</a>
```

---

## 4. Hero Images

Hero images set the tone for each page and adapt to light/dark themes.

### Homepage Heroes

**Light Mode**: `hero-home-light.webp` (1920x1080)  
**Dark Mode**: `hero-home-dark.webp` (1920x1080)

**Usage**:
```html
<picture>
  <source srcset="/assets/heroes/hero-home-dark.webp" 
          media="(prefers-color-scheme: dark)">
  <img src="/assets/heroes/hero-home-light.webp" 
       alt="AI-powered CV analysis" 
       class="hero-image">
</picture>
```

```css
.hero-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  max-height: 600px;
}
```

### Mobile Heroes

**Light Mode**: `hero-mobile-light.webp` (800x1200)  
**Dark Mode**: `hero-mobile-dark.webp` (800x1200)

**Usage**:
```html
<picture>
  <!-- Dark mode -->
  <source srcset="/assets/heroes/hero-mobile-dark.webp" 
          media="(prefers-color-scheme: dark) and (max-width: 640px)">
  <source srcset="/assets/heroes/hero-home-dark.webp" 
          media="(prefers-color-scheme: dark)">
  
  <!-- Light mode -->
  <source srcset="/assets/heroes/hero-mobile-light.webp" 
          media="(max-width: 640px)">
  <img src="/assets/heroes/hero-home-light.webp" 
       alt="AI-powered CV analysis">
</picture>
```

---

## 5. Social Media / OG Images

### Default OG Image

**File**: `og-default.png` (1200x630)

**Usage**:
```html
<!-- In <head> -->
<meta property="og:image" content="https://shortlistai.com/assets/social/og-default.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ShortlistAI - AI-Powered CV Analysis">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://shortlistai.com/assets/social/og-default.png">
```

### Page-Specific OG Images

For key pages, create specific OG images:

```
og-interviewer.png  - Interviewer flow page
og-candidate.png    - Candidate flow page
og-about.png        - About page
```

**Naming convention**: `og-{page-slug}.png`

---

## 6. Background Patterns

### Neural Network Pattern

**File**: `pattern-neural.svg`

**Usage**:
```css
.section {
  background-image: url('/assets/backgrounds/pattern-neural.svg');
  background-size: 512px 512px; /* Tileable */
  background-repeat: repeat;
}

/* With overlay color */
.section-with-color {
  background: 
    linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)),
    url('/assets/backgrounds/pattern-neural.svg');
}
```

**Properties**:
- Tileable (512x512px seamless pattern)
- Subtle (10-15% opacity)
- Works on both light and dark backgrounds

---

## 7. Feature Illustrations

### Interviewer Feature

**File**: `feature-interviewer.webp` (400x400)

**Shows**: Multiple CVs being analyzed and ranked by AI

**Usage**: Feature cards, landing page, marketing materials

### Candidate Feature

**File**: `feature-candidate.webp` (400x400)

**Shows**: CV and job posting being matched with insights

**Usage**: Feature cards, landing page, marketing materials

**Example**:
```html
<div class="feature-card">
  <img src="/assets/illustrations/feature-interviewer.webp" 
       alt="AI analyzing multiple CVs" 
       width="400" 
       height="400"
       loading="lazy">
  <h3>Interviewer Mode</h3>
  <p>Compare and rank multiple candidates efficiently.</p>
</div>
```

---

## 8. PWA Icons

### App Icon Sizes

Generate from `app-icon-512.png`:

- 512x512 - PWA splash screen, high-res
- 192x192 - PWA standard icon
- 128x128 - Medium resolution
- 64x64 - Small screens
- 32x32 - Favicon
- 16x16 - Favicon small

**Manifest.json**:
```json
{
  "icons": [
    {
      "src": "/assets/logos/app-icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/assets/logos/app-icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

---

## 9. Performance Optimization

### Image Formats

| Use Case | Format | Why |
|----------|--------|-----|
| Logos, icons | SVG | Scalable, small file size |
| Hero images | WebP | Best compression for photos |
| OG images | PNG | Wide compatibility, transparency |
| App icons | PNG | Required by PWA spec |
| Patterns | SVG | Tileable, scalable |

### Compression

**Before deploying**:

```bash
# Optimize WebP
cwebp -q 80 hero-home-light.png -o hero-home-light.webp

# Optimize PNG
pngquant --quality=80-90 og-default.png

# Optimize SVG
svgo -i icon.svg -o icon-optimized.svg
```

### Lazy Loading

```html
<!-- Lazy load below-the-fold images -->
<img src="feature.webp" loading="lazy" alt="Feature illustration">

<!-- Eager load critical images -->
<img src="hero.webp" loading="eager" alt="Hero">

<!-- Preload critical images -->
<link rel="preload" as="image" href="hero.webp">
```

---

## 10. Responsive Images

### Using `srcset` for DPI

```html
<img srcset="/assets/logos/logo-1x.png 1x,
             /assets/logos/logo-2x.png 2x,
             /assets/logos/logo-3x.png 3x"
     src="/assets/logos/logo-1x.png"
     alt="ShortlistAI">
```

### Using `<picture>` for Art Direction

```html
<picture>
  <!-- Mobile: Vertical composition -->
  <source media="(max-width: 640px)" 
          srcset="/assets/heroes/hero-mobile-light.webp">
  
  <!-- Desktop: Horizontal composition -->
  <source media="(min-width: 641px)" 
          srcset="/assets/heroes/hero-home-light.webp">
  
  <!-- Fallback -->
  <img src="/assets/heroes/hero-home-light.webp" alt="Hero">
</picture>
```

---

## 11. Accessibility Guidelines

### Alt Text

**Decorative images** (no information, just visual):
```html
<img src="pattern.svg" alt="" aria-hidden="true">
```

**Informative images**:
```html
<img src="feature-ai.svg" alt="AI analyzing CV content">
```

**Functional images** (buttons, links):
```html
<button>
  <img src="upload.svg" alt="">
  <span>Upload CV</span> <!-- Text provides context -->
</button>
```

### Contrast

Ensure images with text overlays meet **4.5:1 contrast ratio**:

```css
.hero-text {
  /* Add text shadow or background for contrast */
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
  /* Or background */
  background: rgba(0,0,0,0.5);
  padding: 1rem;
}
```

---

## 12. File Naming Conventions

### Rules

- **Lowercase** with hyphens (kebab-case)
- **Descriptive** names
- **Include variant** (light/dark, mobile/desktop)
- **Version numbers** if needed (v2, v3)

### Examples

✅ Good:
- `hero-home-light.webp`
- `og-interviewer-flow.png`
- `icon-ai-analysis.svg`

❌ Bad:
- `Hero_Image_1.png`
- `OGimage.jpg`
- `icon2.svg`

---

## 13. Asset Checklist

Before adding a new asset:

- [ ] File name follows conventions (lowercase, descriptive, hyphens)
- [ ] Correct format for use case (SVG, WebP, PNG)
- [ ] Optimized/compressed
- [ ] Correct dimensions
- [ ] Alt text prepared (if needed)
- [ ] Light and dark variants (if applicable)
- [ ] Responsive versions (mobile/desktop)
- [ ] Added to this documentation

---

## 14. Generating New Assets

### For Hero Images and Illustrations

See: [`docs/design/image-generation-prompts.md`](./image-generation-prompts.md)

1. Use AI tools (Gemini, DALL-E, Midjourney)
2. Follow brand colors and style
3. Export at correct dimensions
4. Optimize before deployment

### For Icons

1. Use consistent 24x24 grid
2. 2px stroke weight
3. Export as SVG
4. Remove unnecessary code (optimize with SVGO)

---

## 15. Third-Party Assets

### Using Stock Photos/Illustrations

If using stock assets:

- ✅ Ensure proper licensing (commercial use allowed)
- ✅ Modify to match brand colors
- ✅ Maintain attribution if required
- ❌ Do not use copyrighted material without permission

### AI-Generated Assets

- ✅ Clearly label AI-generated content if required
- ✅ Review for brand consistency
- ✅ Check for unintended elements or bias
- ✅ Ensure no copyrighted elements

---

## 16. Version Control

### Git

Commit assets with descriptive messages:

```bash
git add public/assets/logos/shortlistai-full-color.svg
git commit -m "design: add primary full-color logo SVG"
```

### Large Files

For very large assets (videos, high-res PSDs):

- Consider Git LFS (Large File Storage)
- Or store in cloud (S3, Google Drive) and link in docs

---

## 17. Questions & Updates

**Asset Questions**: legal@shortlistai.com  
**Request New Assets**: Create issue or contact design team  
**Report Issues**: If an asset is broken or incorrect, open an issue

---

## 18. Resources

- **Brand Guidelines**: `/brandrules.md`
- **Design System**: `docs/design/overview.md`
- **Image Generation Prompts**: `docs/design/image-generation-prompts.md`
- **Optimization Tools**:
  - [SVGO](https://github.com/svg/svgo) - SVG optimization
  - [cwebp](https://developers.google.com/speed/webp/docs/cwebp) - WebP encoder
  - [TinyPNG](https://tinypng.com/) - PNG/JPEG compression

---

**Keep this document updated as new assets are added.**





