# Social Sharing Metadata Configuration

**Status**: ✅ Complete  
**Last Updated**: January 11, 2025

---

## Overview

Complete social sharing metadata configuration for ShortlistAI, supporting all major platforms:
- ✅ Facebook
- ✅ LinkedIn
- ✅ Twitter / X
- ✅ WhatsApp
- ✅ Telegram
- ✅ TikTok
- ✅ Google (via structured data)

---

## Image Configuration

### Open Graph Images (Multilingual)

**Base Image**: `public/assets/social/og-default.png`  
**Default URL**: `https://shortlistai.com/assets/social/og-default.png`

**Language-Specific Images**:
- **English (EN)**: `og-en.png` - "AI-Powered CV Analysis & Interview Preparation"
- **Portuguese (PT)**: `og-pt.png` - "Análise de CV com IA & Preparação para Entrevistas"
- **French (FR)**: `og-fr.png` - "Analyse de CV par IA & Préparation aux Entretiens"
- **Spanish (ES)**: `og-es.png` - "Análisis de CV con IA & Preparación para Entrevistas"

**Dimensions**: 1200x630px (optimal for all platforms)  
**Format**: PNG

**Auto-Detection**: Images are automatically selected based on the current language setting.

### Image Specifications

- **Minimum Size**: 600x315px (absolute minimum)
- **Recommended Size**: 1200x630px (optimal)
- **Maximum Size**: 1200x630px (recommended max)
- **Aspect Ratio**: 1.91:1 (for Facebook, LinkedIn, Twitter)
- **Format**: PNG or JPEG (WebP also supported)

---

## Platform-Specific Metadata

### 1. Open Graph (Facebook, LinkedIn, WhatsApp, Telegram)

All these platforms use Open Graph meta tags:

```html
<!-- Basic OG Tags -->
<meta property="og:type" content="website" />
<meta property="og:site_name" content="ShortlistAI" />
<meta property="og:url" content="https://shortlistai.com/" />
<meta property="og:title" content="ShortlistAI - AI-Powered CV Analysis Platform" />
<meta property="og:description" content="Free AI-powered CV analysis..." />

<!-- Image Tags -->
<meta property="og:image" content="https://shortlistai.com/assets/social/og-default.png" />
<meta property="og:image:secure_url" content="https://shortlistai.com/assets/social/og-default.png" />
<meta property="og:image:url" content="https://shortlistai.com/assets/social/og-default.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="ShortlistAI - AI-Powered CV Analysis Platform" />
<meta property="og:image:type" content="image/png" />

<!-- Locale Support -->
<meta property="og:locale" content="en_US" />
<meta property="og:locale:alternate" content="pt_PT" />
<meta property="og:locale:alternate" content="fr_FR" />
<meta property="og:locale:alternate" content="es_ES" />
```

**Platforms using OG tags:**
- ✅ Facebook
- ✅ LinkedIn
- ✅ WhatsApp
- ✅ Telegram
- ✅ Slack
- ✅ Discord

---

### 2. Twitter / X

Twitter uses its own meta tags but also supports OG tags as fallback:

```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@ShortlistAI" />
<meta name="twitter:creator" content="@ShortlistAI" />
<meta name="twitter:url" content="https://shortlistai.com/" />
<meta name="twitter:title" content="ShortlistAI - AI-Powered CV Analysis Platform" />
<meta name="twitter:description" content="Free AI-powered CV analysis..." />
<meta name="twitter:image" content="https://shortlistai.com/assets/social/og-default.png" />
<meta name="twitter:image:alt" content="ShortlistAI - AI-Powered CV Analysis Platform" />

<!-- Additional Twitter metadata -->
<meta name="twitter:label1" content="Price" />
<meta name="twitter:data1" content="Free Forever" />
<meta name="twitter:label2" content="Languages" />
<meta name="twitter:data2" content="EN, PT, FR, ES" />
```

**Card Types:**
- `summary_large_image` - Large image card (1200x630px) ✅ **Using this**

---

### 3. TikTok

TikTok uses Open Graph tags (same as Facebook/WhatsApp).

**No additional tags needed** - uses OG tags above.

---

### 4. Google

Google uses structured data (JSON-LD) instead of meta tags.

See structured data in `index.html` and `SEOHead.tsx` component.

---

## Implementation Files

### 1. Static HTML (`src/frontend/index.html`)

Homepage static meta tags for initial page load.

### 2. Dynamic Component (`src/frontend/src/components/SEOHead.tsx`)

React component for page-specific metadata:
- Supports dynamic titles and descriptions
- Automatically generates canonical URLs
- Supports structured data (JSON-LD)
- Multi-language support

---

## URL Requirements

### ✅ Absolute URLs Required

All image URLs must be **absolute** (include domain):

✅ **Correct:**
```
https://shortlistai.com/assets/social/og-default.png
```

❌ **Incorrect:**
```
/assets/social/og-default.png
./assets/social/og-default.png
```

**Why?** Social platforms fetch images from external servers, so relative URLs won't work.

---

## Testing Social Sharing

### Facebook Sharing Debugger
https://developers.facebook.com/tools/debug/

### Twitter Card Validator
https://cards-dev.twitter.com/validator

### LinkedIn Post Inspector
https://www.linkedin.com/post-inspector/

### WhatsApp
Share link directly in WhatsApp to test.

### Telegram
Share link directly in Telegram to test.

### TikTok
Share link directly in TikTok to test.

---

## Best Practices

### 1. Image Optimization

- ✅ Use PNG or JPEG format
- ✅ Optimize file size (< 1MB recommended)
- ✅ Use WebP for modern browsers (with PNG fallback)
- ✅ Ensure image loads quickly

### 2. Title & Description

- ✅ Keep titles under 60 characters
- ✅ Keep descriptions under 160 characters
- ✅ Make them engaging and descriptive
- ✅ Include key value propositions

### 3. Alt Text

- ✅ Always include `og:image:alt` and `twitter:image:alt`
- ✅ Describe what's in the image
- ✅ Make it accessible for screen readers

### 4. Security

- ✅ Use HTTPS for all image URLs (`og:image:secure_url`)
- ✅ Ensure images are publicly accessible
- ✅ Avoid sensitive information in images

---

## Multi-Language Support

### Locale Tags

```html
<meta property="og:locale" content="en_US" />
<meta property="og:locale:alternate" content="pt_PT" />
<meta property="og:locale:alternate" content="fr_FR" />
<meta property="og:locale:alternate" content="es_ES" />
```

### Language-Specific URLs

Each language has its own alternate URL:
- English: `https://shortlistai.com/?lang=en`
- Portuguese: `https://shortlistai.com/?lang=pt`
- French: `https://shortlistai.com/?lang=fr`
- Spanish: `https://shortlistai.com/?lang=es`

---

## Troubleshooting

### Image Not Showing

1. **Check URL is absolute** (must include `https://`)
2. **Verify image is publicly accessible** (not behind auth)
3. **Check image dimensions** (minimum 600x315px)
4. **Verify HTTPS** (use `og:image:secure_url`)
5. **Clear cache** in social platform debugger

### Wrong Title/Description

1. **Check meta tags** are in correct order
2. **Verify no duplicate tags** with conflicting values
3. **Use social platform debuggers** to refresh cache

### WhatsApp/Telegram Not Showing Preview

1. **Verify OG tags** are present
2. **Check image URL** is absolute and HTTPS
3. **Ensure image** is accessible without authentication
4. **Wait a few minutes** for cache to update

---

## Future Enhancements

- [x] ✅ Create separate images for different languages (EN, PT, FR, ES)
- [x] ✅ Create platform-specific images (Facebook, LinkedIn, Twitter)
- [x] ✅ Add dynamic OG images based on page content (home, about, pricing, features)
- [x] ✅ Add video support for TikTok/Instagram
- [ ] Implement OG image generator API (optional)

---

## References

- [Open Graph Protocol](https://ogp.me/)
- [Twitter Card Documentation](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
- [Facebook Sharing Best Practices](https://developers.facebook.com/docs/sharing/webmasters)
- [LinkedIn Sharing Best Practices](https://www.linkedin.com/help/linkedin/answer/46687)

---

## Status

✅ **Complete** - All major platforms supported:
- ✅ Facebook
- ✅ LinkedIn  
- ✅ Twitter/X
- ✅ WhatsApp
- ✅ Telegram
- ✅ TikTok
- ✅ Google (via structured data)

---

**Last Updated**: January 11, 2025  
**Maintained by**: ShortlistAI Development Team

---

## Advanced Features

### 1. Dynamic Images by Page Content

The `SEOHead` component automatically selects OG images based on the page type:

- **Home**: `og-{lang}.png` or `og-default.png`
- **About**: `og-about-{lang}.png` or `og-about-en.png`
- **Pricing**: `og-pricing-{lang}.png` or `og-pricing-en.png`
- **Features**: `og-features-{lang}.png` or `og-features-en.png`

**Usage**:
```tsx
<SEOHead 
  title="About - ShortlistAI"
  description="..."
  pageType="about"  // Automatically uses og-about-{lang}.png
/>
```

### 2. Platform-Specific Images

Optimized images for different platforms:

- **Facebook**: `og-facebook.png` (1200x630px)
- **LinkedIn**: `og-linkedin.png` (1200x627px)
- **Twitter**: `og-twitter.png` (1200x600px)

**Usage**:
```tsx
<SEOHead 
  title="ShortlistAI"
  description="..."
  platformSpecific={{
    facebook: "https://shortlistai.com/assets/social/og-facebook.png",
    linkedin: "https://shortlistai.com/assets/social/og-linkedin.png",
    twitter: "https://shortlistai.com/assets/social/og-twitter.png"
  }}
/>
```

### 3. Video Support for TikTok/Instagram

Support for video sharing on TikTok and Instagram:

**Usage**:
```tsx
<SEOHead 
  title="ShortlistAI Demo"
  description="..."
  ogVideo={{
    url: "https://shortlistai.com/assets/videos/demo.mp4",
    secureUrl: "https://shortlistai.com/assets/videos/demo.mp4",
    type: "video/mp4",
    width: 1920,
    height: 1080,
    alt: "ShortlistAI Platform Demo Video"
  }}
/>
```

---

## Multilingual OG Images

### Generating Language-Specific Images

To regenerate OG images with translated text for each language:

```bash
python scripts/generate_og_images_multilingual.py
```

This script will:
1. Load the base OG image (`og-default.png`)
2. Add translated text for each language (EN, PT, FR, ES)
3. Generate language-specific images (`og-en.png`, `og-pt.png`, `og-fr.png`, `og-es.png`)

### Automatic Language Detection

The `SEOHead` component automatically detects the current language from `i18n` and selects the appropriate OG image:

- **English**: `og-en.png`
- **Portuguese**: `og-pt.png`
- **French**: `og-fr.png`
- **Spanish**: `og-es.png`
- **Fallback**: `og-default.png` (for unsupported languages)

### Text Content

Each language-specific image includes:
- **Title**: "ShortlistAI"
- **Tagline**: Translated version of "AI-Powered CV Analysis & Interview Preparation"
- **Features**: Translated version of "Free • Multi-language • AI-Powered"

### Image Format

- **Format**: PNG
- **Dimensions**: 1200x630px
- **Text Style**: White text with shadow for readability
- **Layout**: Centered text with title, tagline, and features

