#!/usr/bin/env python3
"""
SEO Validation Script
Validates structured data (JSON-LD) and SEO metadata for ShortlistAI.

Usage:
    python scripts/validate_seo.py
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "src" / "frontend"
PUBLIC_DIR = FRONTEND_DIR / "public"
INDEX_HTML = FRONTEND_DIR / "index.html"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Print success message"""
    try:
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    except UnicodeEncodeError:
        print(f"[OK] {message}")


def print_error(message: str):
    """Print error message"""
    try:
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
    except UnicodeEncodeError:
        print(f"[ERROR] {message}")


def print_warning(message: str):
    """Print warning message"""
    try:
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
    except UnicodeEncodeError:
        print(f"[WARN] {message}")


def print_info(message: str):
    """Print info message"""
    try:
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")
    except UnicodeEncodeError:
        print(f"[INFO] {message}")


def validate_json_ld(html_content: str) -> Tuple[bool, List[str]]:
    """Validate JSON-LD structured data in HTML"""
    errors = []
    warnings = []
    
    # Find all JSON-LD scripts
    json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    matches = re.findall(json_ld_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        warnings.append("No JSON-LD structured data found")
        return True, warnings
    
    for i, match in enumerate(matches, 1):
        try:
            data = json.loads(match.strip())
            
            # Validate @context
            if "@context" in data:
                if data["@context"] != "https://schema.org":
                    errors.append(f"JSON-LD #{i}: @context should be 'https://schema.org', got '{data['@context']}'")
            
            # Validate @graph if present
            if "@graph" in data:
                if not isinstance(data["@graph"], list):
                    errors.append(f"JSON-LD #{i}: @graph should be an array")
                else:
                    for j, item in enumerate(data["@graph"]):
                        if "@type" not in item:
                            errors.append(f"JSON-LD #{i}, item #{j+1}: Missing @type")
                        if "@id" not in item:
                            warnings.append(f"JSON-LD #{i}, item #{j+1}: Missing @id (recommended)")
            
            # Validate single object
            elif "@type" not in data:
                errors.append(f"JSON-LD #{i}: Missing @type")
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON-LD #{i}: Invalid JSON - {str(e)}")
    
    return len(errors) == 0, errors + warnings


def validate_meta_tags(html_content: str) -> Tuple[bool, List[str]]:
    """Validate essential meta tags"""
    errors = []
    warnings = []
    
    required_tags = {
        "title": (r'<title>(.*?)</title>', "Title tag"),
        "description": (r'<meta\s+name=["\']description["\'][^>]*content=["\'](.*?)["\']', "Meta description"),
        "viewport": (r'<meta\s+name=["\']viewport["\'][^>]*content=["\'](.*?)["\']', "Viewport meta tag"),
        "charset": (r'<meta\s+charset=["\'](.*?)["\']', "Charset meta tag"),
    }
    
    for tag_name, (pattern, description) in required_tags.items():
        match = re.search(pattern, html_content, re.IGNORECASE)
        if not match:
            errors.append(f"Missing {description}")
        else:
            value = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if tag_name == "description" and len(value) < 50:
                warnings.append(f"Meta description is too short ({len(value)} chars, recommended: 50-160)")
            elif tag_name == "description" and len(value) > 160:
                warnings.append(f"Meta description is too long ({len(value)} chars, recommended: 50-160)")
    
    # Check for Open Graph tags
    og_tags = ["og:title", "og:description", "og:image", "og:url"]
    for tag in og_tags:
        pattern = rf'<meta\s+property=["\']{tag}["\'][^>]*content=["\'](.*?)["\']'
        if not re.search(pattern, html_content, re.IGNORECASE):
            warnings.append(f"Missing Open Graph tag: {tag}")
    
    # Check for Twitter Cards
    twitter_tags = ["twitter:card", "twitter:title", "twitter:description"]
    for tag in twitter_tags:
        pattern = rf'<meta\s+name=["\']{tag}["\'][^>]*content=["\'](.*?)["\']'
        if not re.search(pattern, html_content, re.IGNORECASE):
            warnings.append(f"Missing Twitter Card tag: {tag}")
    
    # Check for AI-friendly meta tags
    ai_tags = ["ai:description", "ai:category"]
    for tag in ai_tags:
        pattern = rf'<meta\s+name=["\']{tag}["\'][^>]*content=["\'](.*?)["\']'
        if not re.search(pattern, html_content, re.IGNORECASE):
            warnings.append(f"Missing AI-friendly tag: {tag}")
    
    return len(errors) == 0, errors + warnings


def validate_canonical(html_content: str) -> Tuple[bool, List[str]]:
    """Validate canonical URLs"""
    errors = []
    warnings = []
    
    canonical_pattern = r'<link\s+rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']'
    matches = re.findall(canonical_pattern, html_content, re.IGNORECASE)
    
    if not matches:
        warnings.append("No canonical URL found")
    else:
        for url in matches:
            if not url.startswith("https://"):
                errors.append(f"Canonical URL should use HTTPS: {url}")
            if url.endswith("/"):
                warnings.append(f"Canonical URL should not end with '/': {url}")
    
    return len(errors) == 0, errors + warnings


def validate_hreflang(html_content: str) -> Tuple[bool, List[str]]:
    """Validate hreflang alternate language links"""
    errors = []
    warnings = []
    
    hreflang_pattern = r'<link\s+rel=["\']alternate["\'][^>]*hreflang=["\'](.*?)["\'][^>]*href=["\'](.*?)["\']'
    matches = re.findall(hreflang_pattern, html_content, re.IGNORECASE)
    
    expected_langs = ["en", "pt", "fr", "es", "x-default"]
    found_langs = [lang for lang, _ in matches]
    
    for lang in expected_langs:
        if lang not in found_langs:
            warnings.append(f"Missing hreflang for language: {lang}")
    
    return len(errors) == 0, errors + warnings


def validate_sitemap() -> Tuple[bool, List[str]]:
    """Validate sitemap.xml"""
    errors = []
    warnings = []
    
    sitemap_path = PUBLIC_DIR / "sitemap.xml"
    if not sitemap_path.exists():
        errors.append("sitemap.xml not found")
        return False, errors
    
    try:
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required namespaces
        if 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"' not in content:
            errors.append("sitemap.xml: Missing required namespace")
        
        # Check for URLs
        url_count = len(re.findall(r'<url>', content))
        if url_count == 0:
            errors.append("sitemap.xml: No URLs found")
        else:
            print_info(f"sitemap.xml: Found {url_count} URLs")
        
        # Check for lastmod dates (should be recent)
        lastmod_pattern = r'<lastmod>(.*?)</lastmod>'
        lastmods = re.findall(lastmod_pattern, content)
        if not lastmods:
            warnings.append("sitemap.xml: No lastmod dates found")
        else:
            # Check if dates are recent (within last 30 days)
            from datetime import datetime
            for lastmod in lastmods:
                try:
                    date = datetime.strptime(lastmod, "%Y-%m-%d")
                    days_old = (datetime.now() - date).days
                    if days_old > 90:
                        warnings.append(f"sitemap.xml: Some lastmod dates are old ({days_old} days)")
                except ValueError:
                    pass
        
    except Exception as e:
        errors.append(f"Error reading sitemap.xml: {str(e)}")
    
    return len(errors) == 0, errors + warnings


def validate_robots() -> Tuple[bool, List[str]]:
    """Validate robots.txt"""
    errors = []
    warnings = []
    
    robots_path = PUBLIC_DIR / "robots.txt"
    if not robots_path.exists():
        errors.append("robots.txt not found")
        return False, errors
    
    try:
        with open(robots_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for sitemap reference
        if "Sitemap:" not in content:
            warnings.append("robots.txt: No sitemap reference found")
        
        # Check for AI bots
        ai_bots = ["GPTBot", "ChatGPT-User", "CCBot", "anthropic-ai", "Claude-Web", "PerplexityBot"]
        for bot in ai_bots:
            if bot not in content:
                warnings.append(f"robots.txt: No configuration for {bot}")
        
        # Check for admin disallow
        if "/admin/" not in content or "Disallow" not in content:
            warnings.append("robots.txt: Admin routes might not be blocked")
        
    except Exception as e:
        errors.append(f"Error reading robots.txt: {str(e)}")
    
    return len(errors) == 0, errors + warnings


def main():
    """Main validation function"""
    print(f"{Colors.BOLD}{Colors.BLUE}SEO Validation for ShortlistAI{Colors.RESET}\n")
    
    all_passed = True
    total_errors = 0
    total_warnings = 0
    
    # Validate index.html
    if not INDEX_HTML.exists():
        print_error(f"index.html not found at {INDEX_HTML}")
        sys.exit(1)
    
    print_info(f"Reading {INDEX_HTML}")
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"\n{Colors.BOLD}Validating index.html...{Colors.RESET}\n")
    
    # Validate JSON-LD
    print("Validating JSON-LD structured data...")
    passed, issues = validate_json_ld(html_content)
    for issue in issues:
        if "JSON-LD" in issue and "Missing" in issue:
            print_warning(issue)
            total_warnings += 1
        elif "error" in issue.lower() or "invalid" in issue.lower():
            print_error(issue)
            total_errors += 1
            all_passed = False
        else:
            print_warning(issue)
            total_warnings += 1
    if passed and not issues:
        print_success("JSON-LD structured data is valid")
    
    # Validate meta tags
    print("\nValidating meta tags...")
    passed, issues = validate_meta_tags(html_content)
    for issue in issues:
        if "Missing" in issue or "too" in issue.lower():
            if "Missing" in issue and "Open Graph" not in issue and "Twitter" not in issue and "AI-friendly" not in issue:
                print_error(issue)
                total_errors += 1
                all_passed = False
            else:
                print_warning(issue)
                total_warnings += 1
        else:
            print_warning(issue)
            total_warnings += 1
    if passed and not issues:
        print_success("All essential meta tags are present")
    
    # Validate canonical URLs
    print("\nValidating canonical URLs...")
    passed, issues = validate_canonical(html_content)
    for issue in issues:
        if "should use HTTPS" in issue or "No canonical" in issue:
            if "No canonical" in issue:
                print_warning(issue)
                total_warnings += 1
            else:
                print_error(issue)
                total_errors += 1
                all_passed = False
        else:
            print_warning(issue)
            total_warnings += 1
    if passed and not issues:
        print_success("Canonical URLs are valid")
    
    # Validate hreflang
    print("\nValidating hreflang links...")
    passed, issues = validate_hreflang(html_content)
    for issue in issues:
        print_warning(issue)
        total_warnings += 1
    if passed and not issues:
        print_success("All hreflang links are present")
    
    # Validate sitemap.xml
    print(f"\n{Colors.BOLD}Validating sitemap.xml...{Colors.RESET}\n")
    passed, issues = validate_sitemap()
    for issue in issues:
        if "not found" in issue.lower() or "Missing required" in issue:
            print_error(issue)
            total_errors += 1
            all_passed = False
        else:
            print_warning(issue)
            total_warnings += 1
    if passed and not issues:
        print_success("sitemap.xml is valid")
    
    # Validate robots.txt
    print(f"\n{Colors.BOLD}Validating robots.txt...{Colors.RESET}\n")
    passed, issues = validate_robots()
    for issue in issues:
        if "not found" in issue.lower():
            print_error(issue)
            total_errors += 1
            all_passed = False
        else:
            print_warning(issue)
            total_warnings += 1
    if passed and not issues:
        print_success("robots.txt is valid")
    
    # Summary
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Errors: {total_errors}")
    print(f"  Warnings: {total_warnings}")
    
    if all_passed:
        try:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All validations passed!{Colors.RESET}")
        except UnicodeEncodeError:
            print("\n[SUCCESS] All validations passed!")
        sys.exit(0)
    else:
        try:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ Some validations failed{Colors.RESET}")
        except UnicodeEncodeError:
            print("\n[ERROR] Some validations failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

