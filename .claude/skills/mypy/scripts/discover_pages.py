#!/usr/bin/env python3
"""
Discover all documentation pages from mypy docs.
This script crawls the mypy documentation to find all pages that need to be scraped.
"""

import re
import sys
from urllib.parse import urljoin, urlparse
from collections import deque
import cloudscraper
from bs4 import BeautifulSoup

BASE_URL = "https://mypy.readthedocs.io/en/stable/"

def is_valid_doc_url(url, base_domain):
    """Check if URL is a valid documentation page"""
    parsed = urlparse(url)
    
    # Must be from the same domain
    if parsed.netloc and parsed.netloc != base_domain:
        return False
    
    # Skip anchors, external links, and special pages
    if any(skip in url for skip in ['#', 'javascript:', 'mailto:', '_static/', '_sources/', 'genindex.html', 'search.html', 'py-modindex.html']):
        return False
    
    # Must be HTML page
    if parsed.path and not (parsed.path.endswith('.html') or parsed.path.endswith('/')):
        return False
    
    return True

def get_all_links(html_content, base_url):
    """Extract all links from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Convert relative URLs to absolute
        absolute_url = urljoin(base_url, href)
        # Remove fragment
        absolute_url = absolute_url.split('#')[0]
        links.add(absolute_url)
    
    return links

def crawl_docs(start_url):
    """Crawl the documentation and discover all pages"""
    visited = set()
    to_visit = deque([start_url])
    all_pages = set()
    
    # Initialize scraper
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        },
        delay=1
    )
    
    base_domain = urlparse(start_url).netloc
    
    print(f"Starting crawl from: {start_url}", file=sys.stderr)
    print(f"Base domain: {base_domain}\n", file=sys.stderr)
    
    while to_visit:
        current_url = to_visit.popleft()
        
        if current_url in visited:
            continue
        
        # Normalize URL (remove trailing slash for comparison)
        normalized_url = current_url.rstrip('/')
        if normalized_url in visited:
            continue
        
        visited.add(current_url)
        visited.add(normalized_url)
        
        print(f"Crawling: {current_url}", file=sys.stderr)
        
        try:
            # Fetch the page
            response = scraper.get(current_url, timeout=10)
            
            if response.status_code != 200:
                print(f"  Warning: Status {response.status_code}", file=sys.stderr)
                continue
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                print(f"  Warning: Not HTML: {content_type}", file=sys.stderr)
                continue
            
            # Add to our list of pages
            all_pages.add(current_url)
            print(f"  Added to pages list (Total: {len(all_pages)})", file=sys.stderr)
            
            # Extract all links from the page
            links = get_all_links(response.text, current_url)
            
            # Filter and add new links to visit
            new_links = 0
            for link in links:
                if is_valid_doc_url(link, base_domain):
                    normalized_link = link.rstrip('/')
                    if normalized_link not in visited and link not in visited:
                        to_visit.append(link)
                        new_links += 1
            
            if new_links > 0:
                print(f"  Found {new_links} new links to explore", file=sys.stderr)
            
        except Exception as e:
            print(f"  Error: {str(e)}", file=sys.stderr)
            continue
    
    return sorted(all_pages)

def main():
    print("=" * 70, file=sys.stderr)
    print("MYPY DOCUMENTATION PAGE DISCOVERY", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print()
    
    pages = crawl_docs(BASE_URL)
    
    print("\n" + "=" * 70, file=sys.stderr)
    print(f"DISCOVERY COMPLETE: Found {len(pages)} pages", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print()
    
    # Output the list of pages
    for page in pages:
        print(page)
    
    # Also save to a file
    output_file = "mypy_doc_pages.txt"
    with open(output_file, 'w') as f:
        for page in pages:
            f.write(page + '\n')
    
    print(f"\nPage list saved to: {output_file}", file=sys.stderr)

if __name__ == "__main__":
    main()
