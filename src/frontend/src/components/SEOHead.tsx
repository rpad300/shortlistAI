/**
 * SEO Head Component
 * 
 * Manages page-specific SEO metadata, Open Graph tags, and structured data (JSON-LD).
 * Should be used in every page for optimal SEO.
 */

import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useTranslation } from 'react-i18next';

interface SEOHeadProps {
  title: string;
  description: string;
  keywords?: string;
  ogImage?: string;
  ogVideo?: {
    url: string;
    secureUrl?: string;
    type?: string;
    width?: number;
    height?: number;
    alt?: string;
  };
  ogType?: string;
  canonicalUrl?: string;
  structuredData?: object;
  noindex?: boolean;
  pageType?: 'home' | 'about' | 'pricing' | 'features' | 'default';
  platformSpecific?: {
    facebook?: string;
    linkedin?: string;
    twitter?: string;
  };
}

/**
 * Get dynamic OG image URL based on page type and language.
 */
function getDynamicOGImage(pageType: string | undefined, lang: string): string {
  const baseUrl = 'https://shortlistai.com/assets/social';
  const supportedLanguages = ['en', 'pt', 'fr', 'es'];
  const languageSuffix = supportedLanguages.includes(lang) ? `-${lang}` : '';
  
  // Map page types to image names
  const pageImageMap: Record<string, string> = {
    'home': 'og',
    'about': 'og-about',
    'pricing': 'og-pricing',
    'features': 'og-features',
    'default': 'og'
  };
  
  const imageBase = pageImageMap[pageType || 'default'] || 'og';
  return `${baseUrl}/${imageBase}${languageSuffix}.png`;
}

/**
 * Get platform-specific OG image URL.
 */
function getPlatformImage(
  platform: 'facebook' | 'linkedin' | 'twitter' | 'default',
  baseImage: string,
  platformSpecific?: { facebook?: string; linkedin?: string; twitter?: string }
): string {
  // Use platform-specific image if provided
  if (platformSpecific) {
    if (platform === 'facebook' && platformSpecific.facebook) {
      return platformSpecific.facebook;
    }
    if (platform === 'linkedin' && platformSpecific.linkedin) {
      return platformSpecific.linkedin;
    }
    if (platform === 'twitter' && platformSpecific.twitter) {
      return platformSpecific.twitter;
    }
  }
  
  // Return base image for all platforms (they can use the same image)
  return baseImage;
}

export const SEOHead: React.FC<SEOHeadProps> = ({
  title,
  description,
  keywords,
  ogImage,
  ogVideo,
  ogType = 'website',
  canonicalUrl,
  structuredData,
  noindex = false,
  pageType = 'default',
  platformSpecific
}) => {
  // Get current language from i18n
  const { i18n } = useTranslation();
  const currentLang = i18n.language.split('-')[0] || 'en'; // Extract base language (en-US -> en)
  
  // Get OG image: use provided ogImage, or dynamic page-based image, or language-based image
  const ogImageUrl = ogImage || getDynamicOGImage(pageType, currentLang);
  
  // Get platform-specific images
  const facebookImage = getPlatformImage('facebook', ogImageUrl, platformSpecific);
  const linkedinImage = getPlatformImage('linkedin', ogImageUrl, platformSpecific);
  const twitterImage = getPlatformImage('twitter', ogImageUrl, platformSpecific);
  
  const fullTitle = title.includes('ShortlistAI') ? title : `${title} | ShortlistAI`;
  const currentUrl = canonicalUrl || (typeof window !== 'undefined' ? window.location.href : 'https://shortlistai.com');

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      {keywords && <meta name="keywords" content={keywords} />}
      <meta name="author" content="ShortlistAI" />
      <meta name="copyright" content="© 2025 ShortlistAI. All rights reserved." />
      <meta name="generator" content="ShortlistAI Platform v1.0.0" />
      <meta name="application-name" content="ShortlistAI" />
      <meta name="revisit-after" content="7 days" />
      <meta name="distribution" content="global" />
      <meta name="rating" content="general" />
      
      {/* Robots */}
      {noindex ? (
        <meta name="robots" content="noindex, nofollow" />
      ) : (
        <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
      )}

      {/* AI Search Engine Meta Tags */}
      <meta name="ai:description" content={description} />
      {keywords && <meta name="ai:tags" content={keywords} />}
      <meta name="ai:category" content="Recruitment Software, HR Technology, AI Tools, Job Interview Preparation, CV Analysis" />
      
      {/* Canonical */}
      <link rel="canonical" href={currentUrl} />
      
      {/* Alternate Language Links */}
      <link rel="alternate" hrefLang="en" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=en`} />
      <link rel="alternate" hrefLang="pt" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=pt`} />
      <link rel="alternate" hrefLang="fr" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=fr`} />
      <link rel="alternate" hrefLang="es" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=es`} />
      <link rel="alternate" hrefLang="x-default" href={currentUrl} />

      {/* Open Graph / Facebook / LinkedIn / WhatsApp / Telegram */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={currentUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      
      {/* OG Image - Facebook optimized (1200x630) */}
      <meta property="og:image" content={facebookImage} />
      <meta property="og:image:secure_url" content={facebookImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:image:alt" content={fullTitle} />
      <meta property="og:image:type" content="image/png" />
      
      {/* OG Video - TikTok/Instagram support */}
      {ogVideo && (
        <>
          <meta property="og:video" content={ogVideo.url} />
          <meta property="og:video:secure_url" content={ogVideo.secureUrl || ogVideo.url} />
          <meta property="og:video:type" content={ogVideo.type || 'video/mp4'} />
          {ogVideo.width && <meta property="og:video:width" content={ogVideo.width.toString()} />}
          {ogVideo.height && <meta property="og:video:height" content={ogVideo.height.toString()} />}
          {ogVideo.alt && <meta property="og:video:alt" content={ogVideo.alt} />}
        </>
      )}
      
      <meta property="og:site_name" content="ShortlistAI" />
      <meta property="og:locale" content={currentLang === 'en' ? 'en_US' : currentLang === 'pt' ? 'pt_PT' : currentLang === 'fr' ? 'fr_FR' : currentLang === 'es' ? 'es_ES' : 'en_US'} />
      <meta property="og:locale:alternate" content="en_US" />
      <meta property="og:locale:alternate" content="pt_PT" />
      <meta property="og:locale:alternate" content="fr_FR" />
      <meta property="og:locale:alternate" content="es_ES" />
      <meta property="og:updated_time" content={new Date().toISOString()} />
      
      {/* Platform-specific images */}
      {linkedinImage !== facebookImage && (
        <>
          {/* LinkedIn optimized (1200x627) - uses same image but could be different */}
          <meta property="og:image:linkedin" content={linkedinImage} />
        </>
      )}

      {/* Twitter / X - optimized (1200x600) */}
      <meta name="twitter:card" content={ogVideo ? "player" : "summary_large_image"} />
      <meta name="twitter:url" content={currentUrl} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={twitterImage} />
      <meta name="twitter:image:alt" content={fullTitle} />
      <meta name="twitter:site" content="@ShortlistAI" />
      <meta name="twitter:creator" content="@ShortlistAI" />
      {ogVideo && (
        <>
          <meta name="twitter:player" content={ogVideo.url} />
          {ogVideo.width && <meta name="twitter:player:width" content={ogVideo.width.toString()} />}
          {ogVideo.height && <meta name="twitter:player:height" content={ogVideo.height.toString()} />}
        </>
      )}
      <meta name="twitter:label1" content="Price" />
      <meta name="twitter:data1" content="Free Forever" />
      <meta name="twitter:label2" content="Languages" />
      <meta name="twitter:data2" content="EN, PT, FR, ES" />

      {/* WhatsApp / Telegram / TikTok - Use OG tags with absolute URL */}
      <meta property="og:image:url" content={ogImageUrl} />
      
      {/* TikTok specific - uses OG video if available */}
      {ogVideo && (
        <meta name="tiktok:video" content={ogVideo.url} />
      )}
      
      {/* Instagram specific - uses OG video and image */}
      {ogVideo && (
        <>
          <meta property="og:video:instagram" content={ogVideo.url} />
        </>
      )}

      {/* Additional social platforms */}
      <meta name="description" content={description} />
      
      {/* Article-specific (if applicable) */}
      {ogType === 'article' && (
        <>
          <meta property="article:author" content="ShortlistAI" />
          <meta property="article:publisher" content="https://shortlistai.com" />
        </>
      )}

      {/* Structured Data (JSON-LD) */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
};

// Pre-defined structured data templates
export const getOrganizationSchema = () => ({
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://shortlistai.com/#organization",
  "name": "ShortlistAI",
  "legalName": "ShortlistAI",
  "description": "AI-Powered CV Analysis Platform for interviewers and candidates. Free, multilingual, and powered by the latest AI technology.",
  "url": "https://shortlistai.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://shortlistai.com/assets/logos/app-icon-512.png",
    "width": 512,
    "height": 512
  },
  "email": "privacy@shortlistai.com",
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "privacy@shortlistai.com",
    "contactType": "Privacy",
    "availableLanguage": ["en", "pt", "fr", "es"]
  },
  "sameAs": [],
  "foundingDate": "2025",
  "copyrightYear": "2025",
  "copyrightHolder": {
    "@type": "Organization",
    "name": "ShortlistAI"
  }
});

export const getWebsiteSchema = () => ({
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://shortlistai.com/#website",
  "name": "ShortlistAI",
  "description": "AI-Powered CV Analysis and Interview Preparation Platform",
  "url": "https://shortlistai.com",
  "publisher": {
    "@id": "https://shortlistai.com/#organization"
  },
  "inLanguage": ["en", "pt", "fr", "es"],
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://shortlistai.com/?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
});

export const getSoftwareApplicationSchema = () => ({
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "ShortlistAI",
  "applicationCategory": "BusinessApplication",
  "applicationSubCategory": "HR Software, Recruitment Software",
  "operatingSystem": "Web, iOS, Android, Windows, macOS, Linux",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "priceValidUntil": "2026-01-01"
  },
  "description": "Free AI-powered CV analysis platform. Compare candidates or prepare for interviews with advanced AI technology. Supports English, Portuguese, French, and Spanish. Powered by Google Gemini, OpenAI GPT-4, Anthropic Claude, Kimi, and Minimax.",
  "screenshot": "https://shortlistai.com/assets/heroes/hero-home-light.png",
  "featureList": [
    "Batch CV Upload (10, 50, 100+ CVs)",
    "AI-Powered Analysis",
    "Custom Interview Questions",
    "PDF Report Generation",
    "Multilingual Support (EN, PT, FR, ES)",
    "Progressive Web App (PWA)",
    "Free Forever",
    "Multiple AI Providers (Gemini, OpenAI, Claude, Kimi, Minimax)"
  ],
  "softwareVersion": "1.0.0",
  "releaseNotes": "Initial release with full CV analysis features",
  "author": {
    "@id": "https://shortlistai.com/#organization"
  }
});

export const getFAQSchema = (faqs: Array<{question: string; answer: string}>) => ({
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": faqs.map(faq => ({
    "@type": "Question",
    "name": faq.question,
    "acceptedAnswer": {
      "@type": "Answer",
      "text": faq.answer
    }
  }))
});

export const getBreadcrumbSchema = (items: Array<{name: string; url: string}>) => ({
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": items.map((item, index) => ({
    "@type": "ListItem",
    "position": index + 1,
    "name": item.name,
    "item": item.url
  }))
});

export const getWebPageSchema = (url: string, title: string, description: string, dateModified?: string) => ({
  "@context": "https://schema.org",
  "@type": "WebPage",
  "@id": `${url}#webpage`,
  "url": url,
  "name": title,
  "description": description,
  "isPartOf": {
    "@id": "https://shortlistai.com/#website"
  },
  "about": {
    "@id": "https://shortlistai.com/#organization"
  },
  "datePublished": "2025-01-08T00:00:00+00:00",
  "dateModified": dateModified || "2025-01-10T00:00:00+00:00",
  "inLanguage": "en",
  "primaryImageOfPage": {
    "@type": "ImageObject",
    "url": "https://shortlistai.com/assets/social/og-default.png",
    "width": 1200,
    "height": 630
  }
});

export const getArticleSchema = (url: string, title: string, description: string, datePublished: string, dateModified: string, author?: string) => ({
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": title,
  "description": description,
  "url": url,
  "datePublished": datePublished,
  "dateModified": dateModified,
  "author": {
    "@type": "Organization",
    "name": author || "ShortlistAI",
    "@id": "https://shortlistai.com/#organization"
  },
  "publisher": {
    "@id": "https://shortlistai.com/#organization"
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": url
  },
  "inLanguage": "en"
});

export default SEOHead;


