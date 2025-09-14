#!/usr/bin/env python3
"""
Pokemon Go LeekDuck Data Scraper

A robust Python scraper for Pokemon Go data from leekduck.com
Replaces the broken ScrapedDuck scraper with improved reliability and error handling.

Features:
- Scrapes events, raids, research, and eggs data
- Caches data locally to avoid repeated requests
- CLI interface with individual data source selection
- Improved error handling and fallbacks
- Compatible with existing Pokemon Go MCP server
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import sys

import httpx
from bs4 import BeautifulSoup
import requests

# Import page-specific scrapers
try:
    from . import events, raids, research, eggs, rocket_lineups
except ImportError:
    # Fallback for when running as main script
    import events, raids, research, eggs, rocket_lineups

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


### <<< ADDED START: Debugging hook for HTTP responses >>> ###
async def log_response_hook(response):
    """Event hook to log details of each HTTP response."""
    await response.aread()  # Make sure the response body is available
    logger.info("--- HTTP Response Debug ---")
    logger.info(f"URL: {response.request.url}")
    logger.info(f"Status Code: {response.status_code}")
    # Log the first 500 characters to check for CAPTCHA or error pages
    logger.info(f"Response Text (first 500 chars):\n{response.text[:500]}")
    logger.info("---------------------------")
### <<< ADDED END >>> ###


class LeekDuckScraper:
    """Main scraper class for Pokemon Go data from leekduck.com"""
    
    def __init__(self, output_dir: str = "data", cache_duration: int = 300):
        self.output_dir = Path(output_dir)
        self.cache_duration = cache_duration  # seconds
        self.base_url = "https://leekduck.com"
        self.session = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            event_hooks={'response': [log_response_hook]}  ### <<< MODIFIED: Added event hook >>> ###
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    def _should_fetch(self, cache_file: Path) -> bool:
        """Check if we should fetch new data based on cache age"""
        if not cache_file.exists():
            return True
        
        cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
        return cache_age > self.cache_duration
    
    def _save_data(self, data: Any, filename: str) -> None:
        """Save data to JSON file"""
        output_file = self.output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Also create minified version
        min_filename = filename.replace('.json', '.min.json')
        min_output_file = self.output_dir / min_filename
        
        with open(min_output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
        
        logger.info(f"Saved {len(data) if isinstance(data, list) else 'data'} items to {output_file}")
    
    async def scrape_events(self) -> List[Dict]:
        """Scrape events data from leekduck.com"""
        return await events.scrape_events(self, self.base_url)
    
    
    async def scrape_raids(self) -> List[Dict]:
        """Scrape raid bosses data from leekduck.com"""
        return await raids.scrape_raids(self, self.base_url)
    
    
    async def scrape_research(self) -> List[Dict]:
        """Scrape field research data from leekduck.com"""
        return await research.scrape_research(self, self.base_url)
    
    
    async def scrape_eggs(self) -> List[Dict]:
        """Scrape egg hatch data from leekduck.com"""
        return await eggs.scrape_eggs(self, self.base_url)

    async def scrape_rocket_lineups(self) -> List[Dict]:
        """Scrape Team Rocket lineups data from leekduck.com"""
        return await rocket_lineups.scrape_rocket_lineups(self, self.base_url)


    def _load_fallback_data(self, filename: str, default: Any) -> Any:
        """Load fallback data from cache or return default"""
        cache_file = self.output_dir / filename
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    logger.info(f"Using cached fallback data for {filename}")
                    data = json.load(f)
                    # Ensure both .json and .min.json versions exist
                    self._save_data(data, filename)
                    return data
            except Exception as e:
                logger.warning(f"Could not load cached {filename}: {e}")

        logger.warning(f"No cached data available for {filename}, returning default")
        return default
    
    async def scrape_all(self) -> Dict[str, Any]:
        """Scrape all data sources"""
        logger.info("Starting comprehensive scrape of all Pokemon Go data...")
        
        results = {}
        
        # Run all scrapers concurrently
        tasks = {
            'events': self.scrape_events(),
            'raids': self.scrape_raids(),
            'research': self.scrape_research(),
            'eggs': self.scrape_eggs(),
            'rocket_lineups': self.scrape_rocket_lineups()
        }
        
        for name, task in tasks.items():
            try:
                results[name] = await task
                logger.info(f"Successfully scraped {name}: {len(results[name])} items")
            except Exception as e:
                logger.error(f"Failed to scrape {name}: {e}")
                results[name] = []
        
        # Save summary
        summary = {
            'scraped_at': datetime.now(timezone.utc).isoformat(),
            'counts': {name: len(data) for name, data in results.items()},
            'total_items': sum(len(data) for data in results.values())
        }
        
        summary_file = self.output_dir / "scrape_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Scraping completed! Total items: {summary['total_items']}")
        return results


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Pokemon Go LeekDuck Data Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scraper.py --all                    # Scrape all data sources
  python scraper.py --events --raids         # Scrape only events and raids
  python scraper.py --output-dir ./my_data   # Custom output directory
  python scraper.py --cache-duration 600     # Cache for 10 minutes
        """
    )
    
    # Data source selection
    parser.add_argument('--all', action='store_true', help='Scrape all data sources')
    parser.add_argument('--events', action='store_true', help='Scrape events data')
    parser.add_argument('--raids', action='store_true', help='Scrape raids data')
    parser.add_argument('--research', action='store_true', help='Scrape research data')
    parser.add_argument('--eggs', action='store_true', help='Scrape eggs data')
    parser.add_argument('--rocket-lineups', action='store_true', help='Scrape Team Rocket lineups data')

    # Configuration
    parser.add_argument('--output-dir', default='data', help='Output directory for scraped data')
    parser.add_argument('--cache-duration', type=int, default=300, help='Cache duration in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine what to scrape
    if args.all:
        scrape_targets = ['events', 'raids', 'research', 'eggs', 'rocket_lineups']
    else:
        scrape_targets = []
        if args.events: scrape_targets.append('events')
        if args.raids: scrape_targets.append('raids')
        if args.research: scrape_targets.append('research')
        if args.eggs: scrape_targets.append('eggs')
        if getattr(args, 'rocket_lineups', False): scrape_targets.append('rocket_lineups')

        # Default to all if nothing specified
        if not scrape_targets:
            scrape_targets = ['events', 'raids', 'research', 'eggs', 'rocket_lineups']
    
    logger.info(f"Starting Pokemon Go data scraper...")
    logger.info(f"Scraping: {', '.join(scrape_targets)}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Cache duration: {args.cache_duration} seconds")
    
    async with LeekDuckScraper(args.output_dir, args.cache_duration) as scraper:
        results = {}
        
        # Scrape selected data sources
        for target in scrape_targets:
            try:
                if target == 'events':
                    results[target] = await scraper.scrape_events()
                elif target == 'raids':
                    results[target] = await scraper.scrape_raids()
                elif target == 'research':
                    results[target] = await scraper.scrape_research()
                elif target == 'eggs':
                    results[target] = await scraper.scrape_eggs()
                elif target == 'rocket_lineups':
                    results[target] = await scraper.scrape_rocket_lineups()
                
                logger.info(f"✅ {target}: {len(results[target])} items")
                
            except Exception as e:
                logger.error(f"❌ Failed to scrape {target}: {e}")
                results[target] = []
        
        total_items = sum(len(data) for data in results.values())
        logger.info(f"🎉 Scraping completed! Total items: {total_items}")
        
        return results


if __name__ == "__main__":
    # Check required dependencies
    try:
        import httpx
        import bs4
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Install with: pip install httpx beautifulsoup4")
        sys.exit(1)
    
    # Run the scraper
    asyncio.run(main())