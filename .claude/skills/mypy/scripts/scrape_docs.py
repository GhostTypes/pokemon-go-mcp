#!/usr/bin/env python3
"""
Bulk scrape all mypy documentation pages and clean them.
Saves each page as clean markdown in an organized output directory.
"""

import os
import sys
import time
import re
from pathlib import Path
import cloudscraper
from markdownify import markdownify as md

# Configuration
INPUT_FILE = "mypy_stable_pages.txt"
OUTPUT_DIR = "mypy_docs_scraped"
DELAY_BETWEEN_REQUESTS = 1.0  # seconds

# Hop-by-hop headers that should be removed
HOP_BY_HOP_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade',
}

def clean_headers(headers):
    """Remove hop-by-hop headers"""
    cleaned = {}
    for name, value in headers.items():
        if name.lower() not in HOP_BY_HOP_HEADERS:
            cleaned[name] = value
    cleaned.pop('content-encoding', None)
    cleaned.pop('content-length', None)
    return cleaned

def get_headers():
    """Get default headers for requests"""
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }

def generate_origin_and_ref(url):
    """Generate origin and referrer from URL"""
    parts = url.split('/')
    protocol = parts[0]
    domain = parts[2]
    base_url = f"{protocol}//{domain}/"
    return base_url, base_url

def clean_html_to_markdown(html_content):
    """Convert HTML content to clean markdown format"""
    try:
        # Convert HTML to markdown with ATX-style headers
        markdown_content = md(html_content, heading_style="ATX")
        return markdown_content
    except Exception as e:
        print(f"Warning: Error converting HTML to markdown: {str(e)}", file=sys.stderr)
        return html_content

def clean_mypy_markdown(content):
    """
    Clean mypy documentation markdown content.
    
    Removes:
    - Navigation header (everything before first H1 heading)
    - Footer navigation (Next/Previous links)
    - Copyright notice
    - "On this page" table of contents
    - Permalink anchors (¶) in headings
    """
    lines = content.split('\n')
    
    # Find the start of actual content (first H1 heading)
    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('# ') and '[¶]' in line:
            start_idx = i
            break
    
    # Find the end of actual content
    # Look for ALL footer markers and use the earliest one
    footer_markers = []
    
    for i in range(len(lines) - 1, start_idx, -1):
        line = lines[i].strip()
        
        # Look for standalone navigation markers
        if line in ['[Next', '[Previous']:
            footer_markers.append(('nav', i))
        
        # Look for copyright
        if 'Copyright ©' in line:
            footer_markers.append(('copyright', i))
        
        # Look for "On this page" table of contents
        if line == 'On this page':
            footer_markers.append(('toc', i))
    
    # Use the earliest footer marker found
    if footer_markers:
        # Sort by line number and take the first (earliest)
        footer_markers.sort(key=lambda x: x[1])
        marker_type, end_idx = footer_markers[0]
        
        # Remove trailing blank lines before the footer marker
        while end_idx > start_idx and lines[end_idx - 1].strip() == '':
            end_idx -= 1
    else:
        end_idx = len(lines)
    
    # Extract the main content
    cleaned_lines = lines[start_idx:end_idx]
    
    # Remove permalink anchors from headings
    # Pattern: [¶](#some-anchor "Link to this heading")
    permalink_pattern = r'\[¶\]\(#[^)]+\s+"[^"]+"\)'
    
    cleaned_lines = [re.sub(permalink_pattern, '', line) for line in cleaned_lines]
    
    # Join back together
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Clean up excessive blank lines (more than 2 consecutive)
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
    
    # Strip leading/trailing whitespace
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content

def scrape_url(url, scraper):
    """
    Scrape a URL using cloudscraper to bypass Cloudflare protection.
    
    Args:
        url: The URL to scrape
        scraper: The cloudscraper instance to use
    
    Returns:
        String containing the page content
    """
    # Prepare headers
    headers = get_headers()
    origin, ref = generate_origin_and_ref(url)
    headers['Origin'] = origin
    headers['Referer'] = ref
    
    # Make the request
    response = scraper.get(url, headers=headers, stream=False)
    
    # Get content type
    content_type = response.headers.get('content-type', '')
    
    # Handle different content types
    if 'text' in content_type or 'html' in content_type:
        content = response.text
        # Clean HTML to markdown if it's HTML
        if 'html' in content_type:
            content = clean_html_to_markdown(content)
    else:
        # For binary content, try to decode as UTF-8
        try:
            content = response.content.decode('utf-8')
        except UnicodeDecodeError:
            return f"[Binary content - {len(response.content)} bytes - Content-Type: {content_type}]"
    
    return content

def url_to_filename(url):
    """Convert URL to a safe filename"""
    # Extract the page name from the URL
    # e.g., https://mypy.readthedocs.io/en/stable/getting_started.html -> getting_started.md
    parts = url.rstrip('/').split('/')
    
    if parts[-1] == 'stable':
        # Index page
        filename = 'index.md'
    elif parts[-1].endswith('.html'):
        # Regular page
        filename = parts[-1].replace('.html', '.md')
    else:
        # Fallback
        filename = parts[-1] + '.md'
    
    return filename

def main():
    print("=" * 70)
    print("MYPY DOCUMENTATION BULK SCRAPER")
    print("=" * 70)
    print()
    
    # Read the list of URLs
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found", file=sys.stderr)
        print("Please run discover_pages.py first to generate the URL list.", file=sys.stderr)
        sys.exit(1)
    
    with open(INPUT_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} pages to scrape")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize scraper
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        },
        delay=1,
        allow_brotli=True
    )
    
    # Process each URL
    success_count = 0
    error_count = 0
    
    for i, url in enumerate(urls, 1):
        filename = url_to_filename(url)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"[{i}/{len(urls)}] {filename:<30} ", end='', flush=True)
        
        try:
            # Scrape the page
            content = scrape_url(url, scraper)
            
            # Clean the markdown
            cleaned_content = clean_mypy_markdown(content)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"OK ({len(cleaned_content):,} chars)")
            success_count += 1
            
            # Delay between requests to be polite
            if i < len(urls):
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            error_count += 1
    
    print()
    print("=" * 70)
    print("SCRAPING COMPLETE")
    print("=" * 70)
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Output: {OUTPUT_DIR}/")
    print()

if __name__ == "__main__":
    main()
