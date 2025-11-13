# AI Bot Testing Guide

## Overview

This guide explains how to test and verify that AI bots can properly crawl and index ShortlistAI pages.

---

## 1. Testing GPTBot (OpenAI)

### Robots.txt Test

```bash
# Test robots.txt with GPTBot user agent
curl -A "GPTBot" https://shortlistai.com/robots.txt

# Expected: Should see "Allow: /" for GPTBot
```

### Direct Page Access Test

```bash
# Test if GPTBot can access homepage
curl -A "GPTBot" https://shortlistai.com/

# Expected: Should return HTML content
```

### Verify Configuration

Check `robots.txt` contains:
```
User-agent: GPTBot
Allow: /
Disallow: /admin/
Disallow: /interviewer/step2
...
```

### Monitor Server Logs

```bash
# Check for GPTBot requests in server logs
grep "GPTBot" /var/log/nginx/access.log

# Or for Apache
grep "GPTBot" /var/log/apache2/access.log
```

---

## 2. Testing Claude-Web (Anthropic)

### Robots.txt Test

```bash
# Test robots.txt with Claude-Web user agent
curl -A "Claude-Web" https://shortlistai.com/robots.txt

# Expected: Should see "Allow: /" for Claude-Web
```

### Direct Page Access Test

```bash
# Test if Claude-Web can access homepage
curl -A "Claude-Web" https://shortlistai.com/

# Expected: Should return HTML content
```

### Verify Configuration

Check `robots.txt` contains:
```
User-agent: Claude-Web
Allow: /
Disallow: /admin/
...
```

### Monitor Server Logs

```bash
# Check for Claude-Web requests
grep "Claude-Web" /var/log/nginx/access.log
```

---

## 3. Testing PerplexityBot

### Robots.txt Test

```bash
# Test robots.txt with PerplexityBot user agent
curl -A "PerplexityBot" https://shortlistai.com/robots.txt

# Expected: Should see "Allow: /" for PerplexityBot
```

### Direct Page Access Test

```bash
# Test if PerplexityBot can access homepage
curl -A "PerplexityBot" https://shortlistai.com/

# Expected: Should return HTML content
```

### Verify Configuration

Check `robots.txt` contains:
```
User-agent: PerplexityBot
Allow: /
Disallow: /admin/
...
```

---

## 4. Testing Google-Extended

### Robots.txt Test

```bash
# Test robots.txt with Google-Extended user agent
curl -A "Google-Extended" https://shortlistai.com/robots.txt

# Expected: Should see "Allow: /" for Google-Extended
```

### Direct Page Access Test

```bash
# Test if Google-Extended can access homepage
curl -A "Google-Extended" https://shortlistai.com/

# Expected: Should return HTML content
```

---

## 5. Testing CCBot (Common Crawl)

### Robots.txt Test

```bash
# Test robots.txt with CCBot user agent
curl -A "CCBot" https://shortlistai.com/robots.txt

# Expected: Should see "Allow: /" for CCBot
```

### Verify Configuration

Check `robots.txt` contains:
```
User-agent: CCBot
Allow: /
Disallow: /admin/
...
```

---

## 6. Testing ChatGPT-User

### Robots.txt Test

```bash
# Test robots.txt with ChatGPT-User user agent
curl -A "ChatGPT-User" https://shortlistai.com/robots.txt

# Expected: Should see "Allow: /" for ChatGPT-User
```

---

## 7. Testing Anthropic AI Bot

### Robots.txt Test

```bash
# Test robots.txt with anthropic-ai user agent
curl -A "anthropic-ai" https://shortlistai.com/robots.txt

# Expected: Should see "Allow: /" for anthropic-ai
```

---

## 8. Automated Testing Script

### Create Test Script

```bash
#!/bin/bash
# test-ai-bots.sh

BOTS=("GPTBot" "Claude-Web" "PerplexityBot" "Google-Extended" "CCBot" "ChatGPT-User" "anthropic-ai")
URL="https://shortlistai.com"

echo "Testing AI Bot Access"
echo "===================="

for bot in "${BOTS[@]}"; do
    echo ""
    echo "Testing $bot..."
    
    # Test robots.txt
    if curl -s -A "$bot" "$URL/robots.txt" | grep -q "Allow: /"; then
        echo "  ✓ robots.txt allows $bot"
    else
        echo "  ✗ robots.txt does NOT allow $bot"
    fi
    
    # Test homepage access
    status=$(curl -s -o /dev/null -w "%{http_code}" -A "$bot" "$URL/")
    if [ "$status" = "200" ]; then
        echo "  ✓ Homepage accessible by $bot (HTTP $status)"
    else
        echo "  ✗ Homepage NOT accessible by $bot (HTTP $status)"
    fi
done

echo ""
echo "Testing complete!"
```

### Run Test Script

```bash
chmod +x test-ai-bots.sh
./test-ai-bots.sh
```

---

## 9. Testing Blocked Routes

### Test Admin Route

```bash
# Should be blocked
curl -A "GPTBot" https://shortlistai.com/admin/

# Expected: Should see "Disallow: /admin/" in robots.txt
```

### Test Internal Flows

```bash
# Should be blocked
curl -A "GPTBot" https://shortlistai.com/interviewer/step2
curl -A "GPTBot" https://shortlistai.com/interviewer/step3

# Expected: Should see "Disallow: /interviewer/step2" etc. in robots.txt
```

---

## 10. Monitoring AI Bot Access

### Server Log Monitoring

```bash
# Monitor all AI bots in real-time
tail -f /var/log/nginx/access.log | grep -E "(GPTBot|Claude-Web|PerplexityBot|Google-Extended|CCBot|ChatGPT-User|anthropic-ai|Applebot-Extended)"
```

### Log Analysis

```bash
# Count requests by AI bot
grep "GPTBot" /var/log/nginx/access.log | wc -l
grep "Claude-Web" /var/log/nginx/access.log | wc -l
grep "PerplexityBot" /var/log/nginx/access.log | wc -l
```

### Extract Bot Activity

```bash
# Get unique pages accessed by AI bots
grep -E "(GPTBot|Claude-Web|PerplexityBot)" /var/log/nginx/access.log | awk '{print $7}' | sort | uniq -c | sort -rn
```

---

## 11. Verification Checklist

### Weekly Checks
- [ ] Verify robots.txt allows all AI bots
- [ ] Check server logs for AI bot activity
- [ ] Test homepage accessibility with AI bot user agents
- [ ] Verify blocked routes are properly disallowed

### Monthly Checks
- [ ] Review AI bot access patterns
- [ ] Update robots.txt if needed
- [ ] Check for new AI bot user agents
- [ ] Test all major pages with AI bot user agents

---

## 12. Common Issues & Solutions

### Issue: AI Bot Getting 403 Forbidden
**Solution**: Check robots.txt allows the bot, verify server configuration

### Issue: AI Bot Not Appearing in Logs
**Solution**: Bot may not have crawled yet, wait and monitor, or manually test with curl

### Issue: Pages Not Being Indexed
**Solution**: Verify robots.txt allows access, check for noindex tags, ensure sitemap is public

### Issue: Slow Crawling
**Solution**: Check crawl-delay in robots.txt, ensure server is responsive

---

## 13. User Agent Strings

### Known AI Bot User Agents
- **GPTBot**: `GPTBot` or `ChatGPT-User`
- **Claude-Web**: `anthropic-ai` or `Claude-Web`
- **PerplexityBot**: `PerplexityBot`
- **Google-Extended**: `Google-Extended`
- **CCBot**: `CCBot`
- **Applebot-Extended**: `Applebot-Extended`

### Test User Agent Strings

```bash
# Test with full user agent strings
curl -A "GPTBot/1.0" https://shortlistai.com/
curl -A "Claude-Web/1.0" https://shortlistai.com/
curl -A "PerplexityBot/1.0" https://shortlistai.com/
```

---

## 14. Best Practices

### Do
- ✅ Allow AI bots to crawl public pages
- ✅ Block admin and internal routes
- ✅ Monitor AI bot access regularly
- ✅ Keep robots.txt updated
- ✅ Test with actual user agents

### Don't
- ❌ Block all AI bots (unless required)
- ❌ Allow AI bots to access admin areas
- ❌ Ignore AI bot activity
- ❌ Use outdated user agent strings
- ❌ Forget to test after changes

---

## 15. Resources

### Documentation
- [OpenAI GPTBot](https://openai.com/gptbot)
- [Anthropic Claude-Web](https://anthropic.com)
- [Google-Extended](https://developers.google.com/search/docs/crawling-indexing/control-what-indexes/google-extended)
- [PerplexityBot](https://www.perplexity.ai)

### Tools
- **curl**: Command-line tool for testing
- **Server Logs**: Monitor bot activity
- **robots.txt Tester**: Test robots.txt rules

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0

