#!/usr/bin/env python3
"""
Sitemap Date Updater
Updates lastmod dates in sitemap.xml to current date.

Usage:
    python scripts/update_sitemap_dates.py
    python scripts/update_sitemap_dates.py --date 2025-01-15
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
SITEMAP_PATH = PROJECT_ROOT / "src" / "frontend" / "public" / "sitemap.xml"


def update_sitemap_dates(date_str: str = None):
    """Update lastmod dates in sitemap.xml"""
    
    if date_str:
        try:
            new_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD")
            return False
    else:
        new_date = datetime.now().strftime("%Y-%m-%d")
    
    if not SITEMAP_PATH.exists():
        print(f"Error: sitemap.xml not found at {SITEMAP_PATH}")
        return False
    
    # Read sitemap
    with open(SITEMAP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all lastmod dates
    pattern = r'<lastmod>(.*?)</lastmod>'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("Warning: No lastmod dates found in sitemap.xml")
        return False
    
    # Replace all lastmod dates
    updated_content = re.sub(pattern, f'<lastmod>{new_date}</lastmod>', content)
    
    # Count replacements
    count = len(matches)
    
    # Write back
    with open(SITEMAP_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    try:
        print(f"✓ Updated {count} lastmod date(s) to {new_date} in sitemap.xml")
    except UnicodeEncodeError:
        print(f"[OK] Updated {count} lastmod date(s) to {new_date} in sitemap.xml")
    return True


def main():
    parser = argparse.ArgumentParser(description='Update lastmod dates in sitemap.xml')
    parser.add_argument('--date', type=str, help='Date to use (YYYY-MM-DD). Defaults to today.')
    args = parser.parse_args()
    
    print("Sitemap Date Updater")
    print("=" * 50)
    
    if args.date:
        print(f"Updating all dates to: {args.date}")
    else:
        print("Updating all dates to: today")
    
    success = update_sitemap_dates(args.date)
    
    if success:
        try:
            print("\n✓ Done!")
        except UnicodeEncodeError:
            print("\n[SUCCESS] Done!")
    else:
        try:
            print("\n✗ Failed!")
        except UnicodeEncodeError:
            print("\n[ERROR] Failed!")
        exit(1)


if __name__ == "__main__":
    main()

