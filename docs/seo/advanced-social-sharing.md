# Advanced Social Sharing Features

**Status**: ✅ Complete  
**Last Updated**: January 11, 2025

---

## Overview

Advanced social sharing features for ShortlistAI:
1. ✅ Dynamic images by page content
2. ✅ Platform-specific images (Facebook, LinkedIn, Twitter)
3. ✅ Video support for TikTok/Instagram

---

## 1. Dynamic Images by Page Content

### How It Works

The `SEOHead` component automatically detects the page type and selects the appropriate OG image based on:
- **Page type** (home, about, pricing, features)
- **Current language** (EN, PT, FR, ES)

### Image Naming Convention

Images are named using the pattern: `og-{pageType}-{lang}.png`

**Examples**:
- Home page (EN): `og-en.png` or `og-default.png`
- About page (PT): `og-about-pt.png`
- Pricing page (FR): `og-pricing-fr.png`
- Features page (ES): `og-features-es.png`

### Generating Page-Specific Images

To generate images for all pages and languages:

```bash
python scripts/generate_og_images_by_page.py
```

This creates:
- `og-about-en.png`, `og-about-pt.png`, `og-about-fr.png`, `og-about-es.png`
- `og-pricing-en.png`, `og-pricing-pt.png`, `og-pricing-fr.png`, `og-pricing-es.png`
- `og-features-en.png`, `og-features-pt.png`, `og-features-fr.png`, `og-features-es.png`

### Usage in Components

```tsx
import { SEOHead } from '../components/SEOHead';

// Home page
<SEOHead 
  title="ShortlistAI - Home"
  description="..."
  pageType="home"  // Uses og-en.png (or current language)
/>

// About page
<SEOHead 
  title="About - ShortlistAI"
  description="..."
  pageType="about"  // Uses og-about-{lang}.png
/>

// Pricing page
<SEOHead 
  title="Pricing - ShortlistAI"
  description="..."
  pageType="pricing"  // Uses og-pricing-{lang}.png
/>

// Features page
<SEOHead 
  title="Features - ShortlistAI"
  description="..."
  pageType="features"  // Uses og-features-{lang}.png
/>
```

---

## 2. Platform-Specific Images

### Platform Dimensions

Different platforms have slightly different optimal dimensions:

| Platform | Dimensions | Aspect Ratio |
|----------|-----------|--------------|
| Facebook | 1200x630px | 1.91:1 |
| LinkedIn | 1200x627px | 1.91:1 (slightly different) |
| Twitter/X | 1200x600px | 2:1 |

### Generating Platform-Specific Images

To generate optimized images for each platform:

```bash
python scripts/generate_og_images_by_platform.py
```

This creates:
- `og-facebook.png` (1200x630px)
- `og-linkedin.png` (1200x627px)
- `og-twitter.png` (1200x600px)

### Usage in Components

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

**Note**: If `platformSpecific` is not provided, all platforms will use the same base image.

---

## 3. Video Support for TikTok/Instagram

### Video Requirements

For optimal video sharing:

- **Format**: MP4 (H.264 codec)
- **Recommended Size**: 1920x1080px (Full HD)
- **Duration**: 15-60 seconds (optimal for social)
- **File Size**: < 100MB (for better loading)
- **Aspect Ratio**: 
  - TikTok: 9:16 (vertical) or 16:9 (horizontal)
  - Instagram: 9:16 (vertical) or 1:1 (square)

### Video Metadata

The `ogVideo` prop accepts:

```tsx
{
  url: string;           // Video URL (required)
  secureUrl?: string;    // HTTPS version (optional)
  type?: string;         // MIME type (default: "video/mp4")
  width?: number;        // Video width in pixels
  height?: number;       // Video height in pixels
  alt?: string;          // Alt text for video
}
```

### Usage in Components

```tsx
<SEOHead 
  title="ShortlistAI Demo Video"
  description="Watch how ShortlistAI analyzes CVs with AI..."
  ogVideo={{
    url: "https://shortlistai.com/assets/videos/demo.mp4",
    secureUrl: "https://shortlistai.com/assets/videos/demo.mp4",
    type: "video/mp4",
    width: 1920,
    height: 1080,
    alt: "ShortlistAI Platform Demo - AI CV Analysis"
  }}
/>
```

### Platform Support

**TikTok**: Uses `og:video` tags  
**Instagram**: Uses `og:video` and `og:video:instagram` tags  
**Twitter**: Uses `twitter:player` tags (if video provided)

### Video Fallback

If a video is provided, platforms will:
1. Show video player (if supported)
2. Fall back to image preview (if video fails to load)
3. Use image-only preview (if video not available)

---

## Complete Example

Combining all features:

```tsx
<SEOHead 
  title="ShortlistAI - AI-Powered CV Analysis"
  description="Free AI-powered CV analysis for interviewers and candidates..."
  keywords="CV analysis, AI recruitment..."
  pageType="home"  // Uses og-{lang}.png
  platformSpecific={{
    facebook: "https://shortlistai.com/assets/social/og-facebook.png",
    linkedin: "https://shortlistai.com/assets/social/og-linkedin.png",
    twitter: "https://shortlistai.com/assets/social/og-twitter.png"
  }}
  ogVideo={{
    url: "https://shortlistai.com/assets/videos/demo.mp4",
    type: "video/mp4",
    width: 1920,
    height: 1080,
    alt: "ShortlistAI Platform Demo"
  }}
  canonicalUrl="https://shortlistai.com/"
/>
```

---

## Image Generation Scripts

### 1. Multilingual Images

```bash
python scripts/generate_og_images_multilingual.py
```

Generates: `og-en.png`, `og-pt.png`, `og-fr.png`, `og-es.png`

### 2. Page-Specific Images

```bash
python scripts/generate_og_images_by_page.py
```

Generates: `og-{page}-{lang}.png` for all pages and languages

### 3. Platform-Specific Images

```bash
python scripts/generate_og_images_by_platform.py
```

Generates: `og-facebook.png`, `og-linkedin.png`, `og-twitter.png`

---

## Testing

### Facebook Sharing Debugger
https://developers.facebook.com/tools/debug/

### Twitter Card Validator
https://cards-dev.twitter.com/validator

### LinkedIn Post Inspector
https://www.linkedin.com/post-inspector/

### TikTok
Share link directly in TikTok to test video preview.

### Instagram
Share link directly in Instagram to test video preview.

---

## Best Practices

### 1. Image Selection Priority

The `SEOHead` component selects images in this order:
1. **Provided `ogImage`** (if explicitly set)
2. **Dynamic page-based image** (if `pageType` is set)
3. **Language-specific image** (based on current language)
4. **Default image** (`og-default.png`)

### 2. Platform-Specific Optimization

- Use platform-specific images for best results
- Different aspect ratios can improve engagement
- Test each platform separately

### 3. Video Recommendations

- Keep videos short (15-60 seconds)
- Use clear, descriptive titles
- Add captions for accessibility
- Optimize file size (< 100MB)
- Use HTTPS for secure URLs

### 4. Performance

- Optimize all images (compress PNGs)
- Use WebP format when possible (with PNG fallback)
- Lazy load video previews
- Use CDN for faster delivery

---

## Troubleshooting

### Images Not Showing

1. **Check URL is absolute** (must include `https://`)
2. **Verify image exists** on server
3. **Check platform cache** (clear in debugger)
4. **Verify image dimensions** are correct

### Video Not Playing

1. **Check video format** (MP4 recommended)
2. **Verify video URL** is accessible
3. **Check video size** (< 100MB recommended)
4. **Test video URL** directly in browser
5. **Use HTTPS** for secure URLs

### Platform-Specific Issues

- **Facebook**: May take time to update cache
- **Twitter**: Requires `twitter:player` tags for video
- **TikTok**: Uses Open Graph video tags
- **Instagram**: Uses Open Graph video tags

---

**Last Updated**: January 11, 2025  
**Maintained by**: ShortlistAI Development Team

