/**
 * SEO Head Component
 * 
 * Manages page-specific SEO metadata, Open Graph tags, and structured data (JSON-LD).
 * Should be used in every page for optimal SEO.
 */

import React from 'react';
import { Helmet } from 'react-helmet-async';

interface SEOHeadProps {
  title: string;
  description: string;
  keywords?: string;
  ogImage?: string;
  ogType?: string;
  canonicalUrl?: string;
  structuredData?: object;
  noindex?: boolean;
}

export const SEOHead: React.FC<SEOHeadProps> = ({
  title,
  description,
  keywords,
  ogImage = 'https://shortlistai.com/assets/social/og-default.png',
  ogType = 'website',
  canonicalUrl,
  structuredData,
  noindex = false
}) => {
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
      <link rel="alternate" hreflang="en" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=en`} />
      <link rel="alternate" hreflang="pt" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=pt`} />
      <link rel="alternate" hreflang="fr" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=fr`} />
      <link rel="alternate" hreflang="es" href={`${currentUrl}${currentUrl.includes('?') ? '&' : '?'}lang=es`} />
      <link rel="alternate" hreflang="x-default" href={currentUrl} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={currentUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:secure_url" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:image:alt" content={fullTitle} />
      <meta property="og:image:type" content="image/png" />
      <meta property="og:site_name" content="ShortlistAI" />
      <meta property="og:locale" content="en_US" />
      <meta property="og:locale:alternate" content="pt_PT" />
      <meta property="og:locale:alternate" content="fr_FR" />
      <meta property="og:locale:alternate" content="es_ES" />
      <meta property="og:updated_time" content={new Date().toISOString()} />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={currentUrl} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />
      <meta name="twitter:image:alt" content={fullTitle} />
      <meta name="twitter:site" content="@ShortlistAI" />
      <meta name="twitter:creator" content="@ShortlistAI" />
      <meta name="twitter:label1" content="Price" />
      <meta name="twitter:data1" content="Free Forever" />
      <meta name="twitter:label2" content="Languages" />
      <meta name="twitter:data2" content="EN, PT, FR, ES" />

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


