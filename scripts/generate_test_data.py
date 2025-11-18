#!/usr/bin/env python3
"""Generate JSON test data from HTML fixtures.

This script parses HTML fixtures from tests/fixtures/ and generates
JSON data files in the data/ directory for testing the MCP server.
"""

import json
import os
from pathlib import Path
from bs4 import BeautifulSoup

# Import the parsers
from pogo_scraper.events import parse_event_item
from pogo_scraper.raids import parse_raid_boss
from pogo_scraper.research import parse_research_task
from pogo_scraper.eggs import parse_egg_item
from pogo_scraper.rocket_lineups import parse_rocket_trainer
from pogo_scraper.promo_codes import parse_promo_card


def main():
    """Generate all JSON test data from HTML fixtures."""
    fixtures_dir = Path('tests/fixtures')
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    base_url = "https://leekduck.com"

    print("🎮 Generating Pokemon Go MCP test data...\n")

    # Parse Events
    print("📅 Parsing events...")
    with open(fixtures_dir / 'current_events.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    event_items = soup.select('a.event-item-link')
    events = []
    for event_item in event_items:
        event = parse_event_item(event_item, {}, base_url)
        if event:
            events.append(event)

    with open(data_dir / 'events.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2)
    print(f"  ✓ Generated {len(events)} events")

    # Parse Raids
    print("⚔️  Parsing raids...")
    with open(fixtures_dir / 'current_raids.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    raids = []

    # Find raid bosses container
    raid_bosses = soup.find(class_='raid-bosses')
    if raid_bosses:
        # Process each tier in regular raids
        tiers = raid_bosses.find_all(class_='tier')
        for tier_div in tiers:
            # Get tier name
            tier_header = tier_div.find('h2', class_='header')
            current_tier = tier_header.get_text(strip=True) if tier_header else "Unknown"

            # Process cards in this tier
            cards = tier_div.select('.grid .card')
            for card in cards:
                try:
                    boss = parse_raid_boss(card, current_tier, base_url)
                    if boss:
                        raids.append(boss)
                except Exception as e:
                    print(f"    Warning: Error parsing raid boss: {e}")
                    continue

    # Find shadow raid bosses container
    shadow_raid_bosses = soup.find(class_='shadow-raid-bosses')
    if shadow_raid_bosses:
        # Process each tier in shadow raids
        shadow_tiers = shadow_raid_bosses.find_all(class_='tier')
        for tier_div in shadow_tiers:
            # Get tier name
            tier_header = tier_div.find('h2', class_='header')
            current_tier = tier_header.get_text(strip=True) if tier_header else "Unknown"

            # Process cards in this tier
            cards = tier_div.select('.grid .card')
            for card in cards:
                try:
                    boss = parse_raid_boss(card, current_tier, base_url)
                    if boss:
                        raids.append(boss)
                except Exception as e:
                    print(f"    Warning: Error parsing shadow raid boss: {e}")
                    continue

    with open(data_dir / 'raids.json', 'w', encoding='utf-8') as f:
        json.dump(raids, f, indent=2)
    print(f"  ✓ Generated {len(raids)} raids")

    # Parse Research
    print("🔬 Parsing research...")
    with open(fixtures_dir / 'current_research.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    research_items = soup.select('.task-item')
    research = []
    for research_item in research_items:
        try:
            task = parse_research_task(research_item)
            if task:
                research.append(task)
        except Exception as e:
            print(f"    Warning: Error parsing research task: {e}")
            continue

    with open(data_dir / 'research.json', 'w', encoding='utf-8') as f:
        json.dump(research, f, indent=2)
    print(f"  ✓ Generated {len(research)} research tasks")

    # Parse Eggs
    print("🥚 Parsing eggs...")
    with open(fixtures_dir / 'current_eggs.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    eggs = []
    page_content = soup.select_one('.page-content')
    if page_content:
        # Find all h2 headers and their following egg-grid containers
        headers = page_content.find_all('h2')
        for header in headers:
            egg_type_text = header.get_text(strip=True)

            # Parse egg type info
            current_adventure_sync = "(Adventure Sync Rewards)" in egg_type_text
            current_gift_exchange = "(From Gift)" in egg_type_text
            current_route_gift = "(From Route Gift)" in egg_type_text
            current_type = egg_type_text.split(" Eggs")[0]
            if "(From" in current_type:
                current_type = current_type.split(" (From")[0]

            # Find the next egg-grid container after this header
            next_grid = header.find_next_sibling('ul', class_='egg-grid')
            if next_grid:
                # Process pokemon cards in this grid
                pokemon_cards = next_grid.select('li.pokemon-card')
                for card in pokemon_cards:
                    try:
                        egg = parse_egg_item(card, current_type, current_adventure_sync, current_gift_exchange, current_route_gift)
                        if egg:
                            eggs.append(egg)
                    except Exception as e:
                        print(f"    Warning: Error parsing egg item: {e}")
                        continue

    with open(data_dir / 'eggs.json', 'w', encoding='utf-8') as f:
        json.dump(eggs, f, indent=2)
    print(f"  ✓ Generated {len(eggs)} eggs")

    # Parse Rocket Lineups
    print("🚀 Parsing rocket lineups...")
    with open(fixtures_dir / 'current_rocket_lineups.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    rocket_profiles = soup.select('.rocket-profile')
    lineups = []
    for profile in rocket_profiles:
        try:
            lineup = parse_rocket_trainer(profile, base_url)
            if lineup:
                lineups.append(lineup)
        except Exception as e:
            print(f"    Warning: Error parsing rocket trainer: {e}")
            continue

    with open(data_dir / 'rocket-lineups.json', 'w', encoding='utf-8') as f:
        json.dump(lineups, f, indent=2)
    print(f"  ✓ Generated {len(lineups)} rocket lineups")

    # Parse Promo Codes
    print("🎁 Parsing promo codes...")
    with open(fixtures_dir / 'current_promos.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    promo_cards = soup.select('.promo-card:not(.expired):not(.-expired)')
    promos = []
    for card in promo_cards:
        try:
            promo = parse_promo_card(card, base_url)
            if promo:
                promos.append(promo)
        except Exception as e:
            print(f"    Warning: Error parsing promo code: {e}")
            continue

    with open(data_dir / 'promo-codes.json', 'w', encoding='utf-8') as f:
        json.dump(promos, f, indent=2)
    print(f"  ✓ Generated {len(promos)} promo codes")

    print("\n✅ All test data generated successfully!\n")
    print("📦 Generated files:")
    for json_file in sorted(data_dir.glob('*.json')):
        size = json_file.stat().st_size
        print(f"  • {json_file.name}: {size:,} bytes")


if __name__ == "__main__":
    main()
