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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
            }
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
        logger.info("Scraping events data...")
        
        cache_file = self.output_dir / "events.json"
        if not self._should_fetch(cache_file):
            logger.info("Using cached events data")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        try:
            # First get events feed for dates
            events_feed_url = f"{self.base_url}/feeds/events.json"
            response = await self.session.get(events_feed_url)
            response.raise_for_status()
            events_feed = response.json()
            
            # Create date lookup
            event_dates = {}
            for event in events_feed:
                event_id = event.get('eventID')
                if event_id:
                    event_dates[event_id] = {
                        'start': event.get('start'),
                        'end': event.get('end')
                    }
            
            # Now scrape events page for detailed info
            events_url = f"{self.base_url}/events/"
            response = await self.session.get(events_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            all_events = []
            
            # Process both current and upcoming events
            for category in ['current', 'upcoming']:
                event_links = soup.select(f'div.events-list.{category}-events a.event-item-link')
                
                for link in event_links:
                    try:
                        event = self._parse_event_item(link, event_dates)
                        if event:
                            all_events.append(event)
                    except Exception as e:
                        logger.warning(f"Error parsing event: {e}")
                        continue
            
            self._save_data(all_events, "events.json")
            return all_events
            
        except Exception as e:
            logger.error(f"Error scraping events: {e}")
            return self._load_fallback_data("events.json", [])
    
    def _parse_event_item(self, link_element, event_dates: Dict) -> Optional[Dict]:
        """Parse individual event item from the events page"""
        try:
            wrapper = link_element.find('div', class_='event-item-wrapper')
            if not wrapper:
                return None
            
            # Extract basic info
            heading_elem = wrapper.find('p')
            heading = heading_elem.get_text(strip=True) if heading_elem else ""
            
            name_elem = wrapper.select_one('.event-text h2')
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            img_elem = wrapper.select_one('.event-img-wrapper img')
            image = img_elem.get('src', '') if img_elem else ""
            
            # Clean up image URL (remove cloudflare caching)
            if 'cdn-cgi' in image:
                image = image.split('/cdn-cgi')[0]
            
            # Get event ID from link
            href = link_element.get('href', '')
            event_id = href.rstrip('/').split('/')[-1] if href else ""
            
            # Get dates from feed data
            dates = event_dates.get(event_id, {})
            
            event = {
                'eventID': event_id,
                'name': name,
                'eventType': self._infer_event_type(name, heading),
                'heading': heading,
                'link': f"{self.base_url}{href}" if href else "",
                'image': image,
                'start': dates.get('start', ''),
                'end': dates.get('end', ''),
                'extraData': {'generic': {'hasSpawns': False, 'hasFieldResearchTasks': False}}
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error parsing event item: {e}")
            return None
    
    def _infer_event_type(self, name: str, heading: str) -> str:
        """Infer event type based on name and heading"""
        name_lower = name.lower()
        heading_lower = heading.lower()
        
        if 'raid day' in name_lower or 'raid day' in heading_lower:
            return 'raid-day'
        elif 'community day' in name_lower:
            return 'community-day'
        elif 'raid' in heading_lower and 'battle' in heading_lower:
            return 'raid-battles'
        elif 'showcase' in name_lower or 'showcase' in heading_lower:
            return 'pokestop-showcase'
        elif heading_lower == 'event':
            return 'event'
        else:
            return 'event'
    
    async def scrape_raids(self) -> List[Dict]:
        """Scrape raid bosses data from leekduck.com"""
        logger.info("Scraping raids data...")
        
        cache_file = self.output_dir / "raids.json"
        if not self._should_fetch(cache_file):
            logger.info("Using cached raids data")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        try:
            raids_url = f"{self.base_url}/boss/"
            response = await self.session.get(raids_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            bosses = []
            
            # Find raid bosses container
            raid_bosses = soup.find(class_='raid-bosses')
            if not raid_bosses:
                raise ValueError("Could not find raid-bosses container")
            
            # Process each tier
            tiers = raid_bosses.find_all(class_='tier')
            for tier_div in tiers:
                # Get tier name
                tier_header = tier_div.find('h2', class_='header')
                current_tier = tier_header.get_text(strip=True) if tier_header else "Unknown"
                
                # Process cards in this tier
                cards = tier_div.select('.grid .card')
                for card in cards:
                    try:
                        boss = self._parse_raid_boss(card, current_tier)
                        if boss:
                            bosses.append(boss)
                    except Exception as e:
                        logger.warning(f"Error parsing raid boss: {e}")
                        continue
            
            self._save_data(bosses, "raids.json")
            return bosses
            
        except Exception as e:
            logger.error(f"Error scraping raids: {e}")
            return self._load_fallback_data("raids.json", [])
    
    def _parse_raid_boss(self, card, current_tier: str) -> Optional[Dict]:
        """Parse individual raid boss card"""
        try:
            boss = {
                'name': '',
                'tier': current_tier,
                'canBeShiny': False,
                'types': [],
                'combatPower': {
                    'normal': {'min': -1, 'max': -1},
                    'boosted': {'min': -1, 'max': -1}
                },
                'boostedWeather': [],
                'image': ''
            }
            
            # Name
            name_elem = card.select_one('.identity .name')
            boss['name'] = name_elem.get_text(strip=True) if name_elem else ""
            
            # Image
            img_elem = card.select_one('.boss-img img')
            boss['image'] = img_elem.get('src', '') if img_elem else ""
            
            # Shiny
            boss['canBeShiny'] = bool(card.select_one('.boss-img .shiny-icon'))
            
            # Types
            type_imgs = card.select('.boss-type .type img')
            for img in type_imgs:
                type_name = img.get('title', '').lower()
                if type_name:
                    boss['types'].append({
                        'name': type_name,
                        'image': img.get('src', '')
                    })
            
            # Combat Power (normal)
            cp_elem = card.select_one('.cp-range')
            if cp_elem:
                cp_text = cp_elem.get_text().replace('CP', '').strip()
                cp_parts = cp_text.split('-')
                if len(cp_parts) == 2:
                    try:
                        boss['combatPower']['normal']['min'] = int(cp_parts[0].strip())
                        boss['combatPower']['normal']['max'] = int(cp_parts[1].strip())
                    except ValueError:
                        pass
            
            # Combat Power (boosted)
            boosted_elem = card.select_one('.boosted-cp-row .boosted-cp')
            if boosted_elem:
                boosted_text = boosted_elem.get_text().replace('CP', '').strip()
                boosted_parts = boosted_text.split('-')
                if len(boosted_parts) == 2:
                    try:
                        boss['combatPower']['boosted']['min'] = int(boosted_parts[0].strip())
                        boss['combatPower']['boosted']['max'] = int(boosted_parts[1].strip())
                    except ValueError:
                        pass
            
            # Boosted Weather
            weather_imgs = card.select('.weather-boosted .boss-weather .weather-pill img')
            for img in weather_imgs:
                weather_name = img.get('alt', '').lower()
                if weather_name:
                    boss['boostedWeather'].append({
                        'name': weather_name,
                        'image': img.get('src', '')
                    })
            
            return boss
            
        except Exception as e:
            logger.warning(f"Error parsing raid boss card: {e}")
            return None
    
    async def scrape_research(self) -> List[Dict]:
        """Scrape field research data from leekduck.com"""
        logger.info("Scraping research data...")
        
        cache_file = self.output_dir / "research.json"
        if not self._should_fetch(cache_file):
            logger.info("Using cached research data")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        try:
            research_url = f"{self.base_url}/research/"
            response = await self.session.get(research_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            research_tasks = []
            
            # Find research items (updated selector)
            research_items = soup.select('.task-item')
            for item in research_items:
                try:
                    task = self._parse_research_task(item)
                    if task:
                        research_tasks.append(task)
                except Exception as e:
                    logger.warning(f"Error parsing research task: {e}")
                    continue
            
            self._save_data(research_tasks, "research.json")
            return research_tasks
            
        except Exception as e:
            logger.error(f"Error scraping research: {e}")
            return self._load_fallback_data("research.json", [])
    
    def _parse_research_task(self, item) -> Optional[Dict]:
        """Parse individual research task"""
        try:
            task = {
                'text': '',
                'rewards': []
            }
            
            # Task text (updated selector)
            text_elem = item.select_one('.task-text')
            task['text'] = text_elem.get_text(strip=True) if text_elem else ""
            
            # Rewards (updated selector)
            reward_items = item.select('.reward')
            for reward_item in reward_items:
                reward = self._parse_research_reward(reward_item)
                if reward:
                    task['rewards'].append(reward)
            
            return task if task['text'] and task['rewards'] else None
            
        except Exception as e:
            logger.warning(f"Error parsing research task: {e}")
            return None
    
    def _parse_research_reward(self, reward_item) -> Optional[Dict]:
        """Parse individual research reward"""
        try:
            reward = {
                'name': '',
                'image': '',
                'can_be_shiny': False
            }
            
            # Name (updated selector)
            name_elem = reward_item.select_one('.reward-label span')
            reward['name'] = name_elem.get_text(strip=True) if name_elem else ""
            
            # Image (updated selector)
            img_elem = reward_item.select_one('.reward-image')
            reward['image'] = img_elem.get('src', '') if img_elem else ""
            
            # Shiny
            reward['can_be_shiny'] = bool(reward_item.select_one('.shiny-icon'))
            
            return reward if reward['name'] else None
            
        except Exception as e:
            logger.warning(f"Error parsing research reward: {e}")
            return None
    
    async def scrape_eggs(self) -> List[Dict]:
        """Scrape egg hatch data from leekduck.com"""
        logger.info("Scraping eggs data...")
        
        cache_file = self.output_dir / "eggs.json"
        if not self._should_fetch(cache_file):
            logger.info("Using cached eggs data")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        try:
            eggs_url = f"{self.base_url}/eggs/"
            response = await self.session.get(eggs_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            eggs = []
            
            # Process egg sections
            page_content = soup.select_one('.page-content')
            if not page_content:
                raise ValueError("Could not find page content")
            
            current_type = ""
            current_adventure_sync = False
            current_gift_exchange = False
            
            # Find all h2 headers and their following egg-grid containers
            headers = page_content.find_all('h2')
            for header in headers:
                egg_type_text = header.get_text(strip=True)
                
                # Parse egg type info
                current_adventure_sync = "(Adventure Sync Rewards)" in egg_type_text
                current_gift_exchange = "(From Route Gift)" in egg_type_text
                current_type = egg_type_text.split(" Eggs")[0]
                
                # Find the next egg-grid container after this header
                next_grid = header.find_next_sibling('ul', class_='egg-grid')
                if next_grid:
                    # Process pokemon cards in this grid
                    pokemon_cards = next_grid.select('li.pokemon-card')
                    for card in pokemon_cards:
                        try:
                            egg = self._parse_egg_item(card, current_type, current_adventure_sync, current_gift_exchange)
                            if egg:
                                eggs.append(egg)
                        except Exception as e:
                            logger.warning(f"Error parsing egg item: {e}")
                            continue
            
            self._save_data(eggs, "eggs.json")
            return eggs
            
        except Exception as e:
            logger.error(f"Error scraping eggs: {e}")
            return self._load_fallback_data("eggs.json", [])
    
    def _parse_egg_item(self, item, egg_type: str, is_adventure_sync: bool, is_gift_exchange: bool) -> Optional[Dict]:
        """Parse individual egg item"""
        try:
            pokemon = {
                'name': '',
                'eggType': egg_type,
                'isAdventureSync': is_adventure_sync,
                'image': '',
                'canBeShiny': False,
                'combatPower': {'min': -1, 'max': -1},
                'isRegional': False,
                'isGiftExchange': is_gift_exchange
            }
            
            # Name
            name_elem = item.select_one('span.name')
            pokemon['name'] = name_elem.get_text(strip=True) if name_elem else ""
            
            # Image
            img_elem = item.select_one('img')
            pokemon['image'] = img_elem.get('src', '') if img_elem else ""
            
            # Shiny
            pokemon['canBeShiny'] = bool(item.select_one('.shiny-icon'))
            
            # Regional
            pokemon['isRegional'] = bool(item.select_one('.regional-icon'))
            
            # Combat Power
            cp_elem = item.select_one('.font-size-smaller')
            if cp_elem:
                cp_text = cp_elem.get_text()
                # Extract CP range after removing span content
                cp_parts = cp_text.split('</span>')
                if len(cp_parts) > 1:
                    cp_range = cp_parts[1].strip()
                    if ' - ' in cp_range:
                        try:
                            cp_min, cp_max = cp_range.split(' - ')
                            pokemon['combatPower']['min'] = int(cp_min.strip())
                            pokemon['combatPower']['max'] = int(cp_max.strip())
                        except ValueError:
                            pass
            
            return pokemon if pokemon['name'] else None
            
        except Exception as e:
            logger.warning(f"Error parsing egg item: {e}")
            return None
    
    def _load_fallback_data(self, filename: str, default: Any) -> Any:
        """Load fallback data from cache or return default"""
        cache_file = self.output_dir / filename
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    logger.info(f"Using cached fallback data for {filename}")
                    return json.load(f)
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
            'eggs': self.scrape_eggs()
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
        scrape_targets = ['events', 'raids', 'research', 'eggs']
    else:
        scrape_targets = []
        if args.events: scrape_targets.append('events')
        if args.raids: scrape_targets.append('raids')
        if args.research: scrape_targets.append('research')
        if args.eggs: scrape_targets.append('eggs')
        
        # Default to all if nothing specified
        if not scrape_targets:
            scrape_targets = ['events', 'raids', 'research', 'eggs']
    
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