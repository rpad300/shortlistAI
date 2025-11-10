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
      
      {/* Robots */}
      {noindex ? (
        <meta name="robots" content="noindex, nofollow" />
      ) : (
        <meta name="robots" content="index, follow" />
      )}

      {/* Canonical */}
      <link rel="canonical" href={currentUrl} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={currentUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1344" />
      <meta property="og:image:height" content="768" />
      <meta property="og:image:alt" content={fullTitle} />
      <meta property="og:site_name" content="ShortlistAI" />
      <meta property="og:locale" content="en_US" />
      <meta property="og:locale:alternate" content="pt_PT" />
      <meta property="og:locale:alternate" content="fr_FR" />
      <meta property="og:locale:alternate" content="es_ES" />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={currentUrl} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />
      <meta name="twitter:image:alt" content={fullTitle} />
      <meta name="twitter:site" content="@ShortlistAI" />

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
  "name": "ShortlistAI",
  "description": "AI-Powered CV Analysis Platform for interviewers and candidates",
  "url": "https://shortlistai.com",
  "logo": "https://shortlistai.com/assets/logos/app-icon-512.png",
  "email": "privacy@shortlistai.com",
  "sameAs": []
});

export const getWebsiteSchema = () => ({
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "ShortlistAI",
  "description": "AI-Powered CV Analysis and Interview Preparation Platform",
  "url": "https://shortlistai.com",
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
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "operatingSystem": "Web, iOS, Android, Windows, macOS, Linux",
  "description": "Free AI-powered CV analysis platform. Compare candidates or prepare for interviews with advanced AI technology. Supports EN, PT, FR, ES.",
  "screenshot": "https://shortlistai.com/assets/heroes/hero-home-light.png",
  "featureList": [
    "Batch CV Upload (10, 50, 100+ CVs)",
    "AI-Powered Analysis",
    "Custom Interview Questions",
    "PDF Report Generation",
    "Multilingual Support (EN, PT, FR, ES)",
    "Progressive Web App (PWA)"
  ]
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

export default SEOHead;

