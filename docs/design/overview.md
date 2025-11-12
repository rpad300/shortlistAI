# ShortlistAI Design System Overview

**Version**: 1.0.0  
**Last Updated**: November 10, 2025

---

## Purpose

This document provides an overview of the ShortlistAI design system, visual language, and implementation guidelines.

For complete brand guidelines, see: [`/brandrules.md`](../../brandrules.md)

---

## 1. Design Philosophy

### Core Principles

1. **Professional First** - Trusted by both interviewers and candidates
2. **AI-Forward** - Modern, tech-inspired aesthetics that communicate intelligence
3. **Accessible Always** - Clear, readable, usable by everyone
4. **Responsive Everywhere** - Works perfectly from mobile to TV
5. **Performance Matters** - Fast, lightweight, optimized

### Visual Language

- **Clean & Minimal** - Remove clutter, focus on content
- **Geometric** - Use clean shapes, structured layouts
- **Gradient Accents** - AI Blue → Neural Purple for energy
- **Light & Dark** - Full support for both themes
- **Data Visualization** - Charts, scores, and analytics are first-class

---

## 2. Color System

### Primary Colors

```css
/* AI Blue - Primary brand color */
--ai-blue-light: #0066FF;
--ai-blue-dark: #3388FF;

/* Neural Purple - Secondary brand color */
--neural-purple-light: #7C3AED;
--neural-purple-dark: #9F7AEA;
```

### Semantic Colors

```css
/* Success */
--success-light: #10B981;
--success-dark: #34D399;

/* Warning */
--warning-light: #F59E0B;
--warning-dark: #FBBF24;

/* Error */
--error-light: #EF4444;
--error-dark: #F87171;
```

### Neutrals

```css
/* Backgrounds */
--bg-light: #FFFFFF;
--bg-dark: #0A0A0B;
--surface-light: #F8F9FA;
--surface-dark: #1A1A1C;

/* Borders */
--border-light: #E5E7EB;
--border-dark: #2D2D30;

/* Text */
--text-primary-light: #111827;
--text-primary-dark: #F9FAFB;
--text-secondary-light: #6B7280;
--text-secondary-dark: #9CA3AF;
```

### Gradients

```css
/* AI Gradient - Primary */
--gradient-ai: linear-gradient(135deg, #0066FF 0%, #7C3AED 100%);

/* Neural Gradient - Accent */
--gradient-neural: linear-gradient(135deg, #7C3AED 0%, #EC4899 100%);

/* Dark Gradient - Backgrounds */
--gradient-dark: linear-gradient(180deg, #0A0A0B 0%, #1A1A1C 100%);
```

---

## 3. Typography

### Font Families

**Primary**: Inter (Sans-serif)
- All UI text, headings, body content
- Weights: 400, 500, 600, 700

**Monospace**: JetBrains Mono
- Code, technical data, IDs
- Weights: 400, 500

### Type Scale

| Element | Size (Desktop) | Size (Mobile) | Weight | Line Height |
|---------|---------------|---------------|--------|-------------|
| Display | 48px / 3rem | 32px / 2rem | 700 | 1.1 |
| H1 | 36px / 2.25rem | 28px / 1.75rem | 700 | 1.2 |
| H2 | 28px / 1.75rem | 24px / 1.5rem | 600 | 1.3 |
| H3 | 20px / 1.25rem | 20px / 1.25rem | 600 | 1.4 |
| Body Large | 18px / 1.125rem | 18px / 1.125rem | 400 | 1.6 |
| Body | 16px / 1rem | 16px / 1rem | 400 | 1.5 |
| Body Small | 14px / 0.875rem | 14px / 0.875rem | 400 | 1.5 |
| Caption | 12px / 0.75rem | 12px / 0.75rem | 500 | 1.4 |

---

## 4. Spacing System

Based on 8px grid:

```css
--space-1: 4px;   /* 0.25rem - Micro */
--space-2: 8px;   /* 0.5rem - Tiny */
--space-3: 12px;  /* 0.75rem - Small */
--space-4: 16px;  /* 1rem - Base */
--space-6: 24px;  /* 1.5rem - Medium */
--space-8: 32px;  /* 2rem - Large */
--space-12: 48px; /* 3rem - XL */
--space-16: 64px; /* 4rem - XXL */
--space-24: 96px; /* 6rem - Hero */
```

---

## 5. Components

### Buttons

**Primary Button**
```css
background: var(--gradient-ai);
color: white;
padding: 12px 24px;
border-radius: 8px;
font-weight: 600;
transition: transform 150ms ease;
```

**Secondary Button**
```css
background: transparent;
border: 2px solid var(--ai-blue);
color: var(--ai-blue);
padding: 10px 22px; /* Adjust for border */
border-radius: 8px;
```

### Cards

```css
background: var(--surface);
border: 1px solid var(--border);
border-radius: 12px;
padding: 24px;
box-shadow: 0 1px 3px rgba(0,0,0,0.1);
```

### Input Fields

```css
border: 1px solid var(--border);
border-radius: 8px;
padding: 12px 16px;
font-size: 16px;
transition: border-color 150ms;

/* Focus state */
border: 2px solid var(--ai-blue);
box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1);
```

---

## 6. Icons

### Style
- **Type**: Outline (2px stroke)
- **Corners**: Rounded (2px radius)
- **Size**: 24x24px default
- **Color**: Inherit from context

### Usage
- Always use SVG for scalability
- Ensure 3:1 contrast ratio minimum
- Provide ARIA labels for interactive icons

### Available Icons

Located in `public/assets/icons/`:

- `feature-ai.svg` - AI/Brain symbol
- `feature-document.svg` - Document/CV
- `feature-analytics.svg` - Charts/Analysis
- `feature-email.svg` - Email/Communication
- `upload.svg` - Upload action
- `download.svg` - Download action
- `check-circle.svg` - Success/Confirmation
- `warning.svg` - Warning/Alert

---

## 7. Layout & Grid

### Breakpoints

```css
/* Mobile */
@media (max-width: 639px) { }

/* Tablet */
@media (min-width: 640px) and (max-width: 1023px) { }

/* Desktop */
@media (min-width: 1024px) and (max-width: 1919px) { }

/* Large Desktop */
@media (min-width: 1920px) { }

/* TV */
@media (min-width: 2560px) { }
```

### Container Widths

```css
--container-mobile: 100%;
--container-tablet: 640px;
--container-desktop: 1024px;
--container-wide: 1280px;
--container-max: 1920px;
```

---

## 8. Animation & Motion

### Timing

```css
--duration-fast: 150ms;    /* Micro interactions */
--duration-normal: 250ms;  /* Standard transitions */
--duration-slow: 400ms;    /* Complex animations */
```

### Easing

```css
--ease-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
--ease-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);
--ease-accelerate: cubic-bezier(0.4, 0.0, 1, 1);
```

### Principles

- **Purposeful** - Every animation serves a function
- **Subtle** - Don't distract from content
- **Responsive** - Immediate feedback to user actions
- **Respectful** - Honor `prefers-reduced-motion`

---

## 9. Accessibility

### Standards

- **WCAG 2.1 Level AA** compliance minimum
- **4.5:1** contrast for normal text
- **3:1** contrast for large text (18px+)
- **Keyboard navigation** for all interactive elements
- **Screen reader** support with proper ARIA

### Testing Checklist

- [ ] Test keyboard-only navigation
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Test color contrast (use WebAIM checker)
- [ ] Test with 200% zoom
- [ ] Test color blindness modes
- [ ] Verify focus states are visible
- [ ] Ensure no reliance on color alone for information

---

## 10. Dark Mode

### Implementation

```css
/* Automatic detection */
@media (prefers-color-scheme: dark) {
  :root {
    --bg: var(--bg-dark);
    --text: var(--text-primary-dark);
    /* ... */
  }
}
```

### Manual Toggle

Store user preference in `localStorage`:

```javascript
const theme = localStorage.getItem('theme') || 'auto';
document.documentElement.setAttribute('data-theme', theme);
```

---

## 11. Visual Assets

### Logo

Location: `public/assets/logos/`

- `shortlistai-full-color.svg` - Primary logo (full color)
- `shortlistai-icon-only.svg` - Icon/App icon
- `shortlistai-monochrome-black.svg` - Black version
- `shortlistai-monochrome-white.svg` - White version

### Hero Images

Location: `public/assets/heroes/`

- Light mode and dark mode versions
- Desktop (1920x1080) and mobile (800x1200) sizes
- WebP format for optimal performance

### Social/OG Images

Location: `public/assets/social/`

- `og-default.png` - Default Open Graph image (1200x630)
- Page-specific OG images as needed

### Backgrounds

Location: `public/assets/backgrounds/`

- `pattern-neural.svg` - Tileable neural network pattern
- Subtle, non-distracting textures

---

## 12. Performance

### Image Optimization

- **Use WebP** for photos and complex graphics
- **Use SVG** for icons and simple graphics
- **Use PNG** only when transparency needed (OG images)
- **Compress** all images before deployment
- **Generate multiple sizes** for responsive images

### Loading Strategy

- **Critical images**: Preload, high priority
- **Above the fold**: Standard priority
- **Below the fold**: Lazy load with IntersectionObserver
- **Background patterns**: Low priority, lazy load

---

## 13. Implementation

### CSS Variables

Define all design tokens as CSS custom properties in `:root`:

```css
:root {
  /* Colors */
  --ai-blue: #0066FF;
  --neural-purple: #7C3AED;
  
  /* Spacing */
  --space-4: 1rem;
  
  /* Typography */
  --font-primary: 'Inter', -apple-system, sans-serif;
  
  /* ... */
}
```

### Component Library

Build reusable React components:

- `Button` (primary, secondary, ghost variants)
- `Card`
- `Input`, `Textarea`, `Select`
- `Modal`, `Dialog`
- `LoadingSpinner`
- `Alert` (success, warning, error)

### Theming

Use CSS custom properties to enable easy theming:

```css
button.primary {
  background: var(--button-primary-bg);
  color: var(--button-primary-color);
}
```

---

## 14. Documentation Structure

```
docs/design/
├── overview.md              # This file
├── components.md            # Component library documentation
├── assets.md                # Asset usage guidelines
├── image-generation-prompts.md  # AI image generation prompts
└── changelog.md             # Design system version history
```

---

## 15. Tools & Resources

### Design Tools
- **Figma** - UI design and prototyping
- **Adobe Illustrator** - Logo and vector work
- **AI Image Tools** - Gemini, DALL-E, Midjourney

### Development Tools
- **CSS Custom Properties** - Theming
- **PostCSS** - CSS processing
- **Vite** - Build tool with asset optimization

### Testing Tools
- **WebAIM Contrast Checker** - Color contrast
- **WAVE** - Accessibility evaluation
- **Lighthouse** - Performance and accessibility
- **axe DevTools** - Automated accessibility testing

---

## 16. Design Checklist

For every new page/component:

- [ ] Follows color system (AI Blue, Neural Purple, brand colors)
- [ ] Uses typography scale correctly
- [ ] Respects 8px spacing grid
- [ ] Works in both light and dark mode
- [ ] Responsive across all breakpoints (mobile to TV)
- [ ] Meets WCAG 2.1 AA accessibility standards
- [ ] Uses appropriate icons from design system
- [ ] Optimized images (correct format, compressed)
- [ ] Smooth, purposeful animations
- [ ] Keyboard navigable
- [ ] Screen reader friendly

---

## 17. Getting Started

### For Designers

1. Read `brandrules.md` for complete brand guidelines
2. Review color system and typography
3. Use design tokens (spacing, colors) consistently
4. Design for both light and dark modes
5. Consider mobile-first, then scale up
6. Test accessibility early and often

### For Developers

1. Use CSS custom properties from design system
2. Build components that accept theme variants
3. Implement responsive breakpoints
4. Ensure accessibility (ARIA, keyboard navigation)
5. Optimize images and assets
6. Test across devices and browsers

---

## 18. Updates & Versioning

### Version History

- **v1.0.0** (2025-11-10) - Initial design system
  - Brand colors defined
  - Typography scale established
  - Component library started
  - Logo and core assets created

### Future Roadmap

- [ ] Expanded component library
- [ ] Motion design guidelines
- [ ] Micro-interactions library
- [ ] 3D elements for hero sections
- [ ] Storybook component documentation

---

## 19. Questions & Support

**Design Questions**: legal@shortlistai.com  
**Technical Implementation**: See `docs/` for specific role guides  
**Brand Guidelines**: See `/brandrules.md`

---

## 20. References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Inter Font](https://rsms.me/inter/)
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- [MDN Web Docs - CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)

---

**This design system is a living document. Update as the product evolves.**


