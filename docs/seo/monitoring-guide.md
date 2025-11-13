# SEO Monitoring Guide

## Overview

This guide explains how to monitor and maintain SEO performance for ShortlistAI after the initial implementation.

---

## 1. Google Search Console

### Initial Setup

1. **Verify Ownership**
   - Go to [Google Search Console](https://search.google.com/search-console)
   - Add property: `https://shortlistai.com`
   - Choose verification method (HTML file, DNS, or meta tag)
   - Verify ownership

2. **Submit Sitemap**
   - Go to Sitemaps section
   - Submit: `https://shortlistai.com/sitemap.xml`
   - Wait for Google to crawl (can take a few days)

### Weekly Monitoring

1. **Performance Report**
   - Check clicks, impressions, CTR, average position
   - Identify top-performing pages
   - Identify pages with declining performance

2. **Coverage Report**
   - Check for indexing errors
   - Fix any 404 errors or crawl issues
   - Monitor for duplicate content warnings

3. **Enhancements**
   - Check for rich results errors
   - Validate structured data
   - Fix any schema markup issues

### Monthly Review

1. **Search Queries**
   - Identify top search queries
   - Optimize pages for high-value keywords
   - Create content for missing keywords

2. **Mobile Usability**
   - Check for mobile usability issues
   - Fix any responsive design problems

3. **Core Web Vitals**
   - Monitor LCP, FID, CLS scores
   - Optimize performance issues

---

## 2. Structured Data Validation

### Google Rich Results Test

1. **Test URLs**
   - Go to [Rich Results Test](https://search.google.com/test/rich-results)
   - Test homepage: `https://shortlistai.com`
   - Test feature pages: `/features`, `/pricing`, `/about`
   - Test interview/candidate flows: `/interviewer/step1`, `/candidate/step1`

2. **Check for Errors**
   - Fix any structured data errors
   - Ensure all required fields are present
   - Validate JSON-LD syntax

### Schema.org Validator

1. **Validate Schemas**
   - Go to [Schema.org Validator](https://validator.schema.org/)
   - Paste HTML or JSON-LD code
   - Validate all schema types:
     - Organization
     - WebSite
     - SoftwareApplication
     - WebPage
     - FAQPage

### Automated Validation

Use our validation script:
```bash
python scripts/validate_seo.py
```

---

## 3. AI Bot Indexing Tests

### Test GPTBot (OpenAI)

1. **Check robots.txt**
   - Verify GPTBot is allowed
   - Test: `curl -A "GPTBot" https://shortlistai.com/robots.txt`

2. **Monitor Logs**
   - Check server logs for GPTBot requests
   - Verify pages are being crawled

### Test Claude-Web (Anthropic)

1. **Check robots.txt**
   - Verify Claude-Web is allowed
   - Test: `curl -A "Claude-Web" https://shortlistai.com/robots.txt`

### Test PerplexityBot

1. **Check robots.txt**
   - Verify PerplexityBot is allowed
   - Test: `curl -A "PerplexityBot" https://shortlistai.com/robots.txt`

### Test Google-Extended

1. **Check robots.txt**
   - Verify Google-Extended is allowed
   - Test: `curl -A "Google-Extended" https://shortlistai.com/robots.txt`

### Monitoring AI Bot Access

```bash
# Check server logs for AI bot user agents
grep -E "(GPTBot|Claude-Web|PerplexityBot|Google-Extended|anthropic-ai|CCBot|ChatGPT-User)" /var/log/nginx/access.log
```

---

## 4. Sitemap Maintenance

### Update Dates Monthly

Run the sitemap date updater:
```bash
python scripts/update_sitemap_dates.py
```

Or specify a date:
```bash
python scripts/update_sitemap_dates.py --date 2025-02-01
```

### Validate Sitemap

1. **Submit to Google Search Console**
   - Check sitemap status
   - Verify all URLs are indexed
   - Fix any crawl errors

2. **Test Sitemap**
   - Use [XML Sitemap Validator](https://www.xml-sitemaps.com/validate-xml-sitemap.html)
   - Check for syntax errors
   - Verify all URLs are accessible

---

## 5. Keyword Monitoring

### Weekly Keyword Review

Use the keyword checklist in `docs/seo/keyword-checklist.md`:

1. **Review Top Keywords**
   - Check Google Search Console for top queries
   - Analyze CTR and position
   - Identify opportunities

2. **Monitor Competitors**
   - Check competitor rankings
   - Identify new keywords
   - Analyze competitor content

3. **Content Gap Analysis**
   - Identify missing keywords
   - Create content for high-value keywords
   - Optimize existing content

### Monthly Keyword Refresh

1. **Update Keyword List**
   - Review keyword performance
   - Remove underperforming keywords
   - Add new trending keywords

2. **Update Meta Tags**
   - Refresh meta descriptions
   - Update page titles
   - Optimize for new keywords

---

## 6. Performance Monitoring

### Core Web Vitals

1. **Google PageSpeed Insights**
   - Test: [PageSpeed Insights](https://pagespeed.web.dev/)
   - Monitor LCP, FID, CLS
   - Aim for scores > 90

2. **Lighthouse CI**
   - Set up automated Lighthouse tests
   - Monitor performance over time
   - Fix regressions

### Mobile Performance

1. **Mobile-Friendly Test**
   - Test: [Mobile-Friendly Test](https://search.google.com/test/mobile-friendly)
   - Ensure all pages are mobile-friendly
   - Fix any mobile usability issues

---

## 7. Monitoring Checklist

### Daily
- [ ] Check Google Search Console for critical errors
- [ ] Monitor server logs for AI bot access

### Weekly
- [ ] Review performance report in Search Console
- [ ] Check for new indexing errors
- [ ] Validate structured data on key pages
- [ ] Review keyword performance

### Monthly
- [ ] Update sitemap dates
- [ ] Review keyword list
- [ ] Analyze competitor rankings
- [ ] Test rich results on all pages
- [ ] Review and update meta tags
- [ ] Check Core Web Vitals scores
- [ ] Review AI bot indexing status

### Quarterly
- [ ] Comprehensive SEO audit
- [ ] Update keyword strategy
- [ ] Review and optimize structured data
- [ ] Analyze competitor content strategy
- [ ] Update robots.txt if needed
- [ ] Review and optimize sitemap structure

---

## 8. Tools and Resources

### Free Tools
- **Google Search Console**: [search.google.com/search-console](https://search.google.com/search-console)
- **Google Rich Results Test**: [search.google.com/test/rich-results](https://search.google.com/test/rich-results)
- **Schema.org Validator**: [validator.schema.org](https://validator.schema.org/)
- **PageSpeed Insights**: [pagespeed.web.dev](https://pagespeed.web.dev/)
- **Mobile-Friendly Test**: [search.google.com/test/mobile-friendly](https://search.google.com/test/mobile-friendly)

### Paid Tools (Optional)
- **Ahrefs**: Keyword research and competitor analysis
- **SEMrush**: SEO auditing and keyword tracking
- **Moz**: Domain authority and link building

### Internal Scripts
- **SEO Validator**: `scripts/validate_seo.py`
- **Sitemap Updater**: `scripts/update_sitemap_dates.py`

---

## 9. Troubleshooting

### Common Issues

1. **Pages Not Indexing**
   - Check robots.txt
   - Verify canonical URLs
   - Ensure sitemap is submitted
   - Check for noindex tags

2. **Structured Data Errors**
   - Run validation script
   - Check JSON-LD syntax
   - Verify required fields
   - Test with Rich Results Test

3. **AI Bots Not Crawling**
   - Verify robots.txt allows bot
   - Check server logs
   - Ensure pages are accessible
   - Verify sitemap is public

---

## 10. Best Practices

1. **Regular Updates**
   - Update sitemap dates monthly
   - Refresh content regularly
   - Monitor performance continuously

2. **Quality Over Quantity**
   - Focus on high-value keywords
   - Create quality content
   - Optimize for user experience

3. **Stay Compliant**
   - Follow Google guidelines
   - Respect robots.txt rules
   - Maintain privacy compliance

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0

