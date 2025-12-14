#!/usr/bin/env python3
"""
Generate README.md with live statistics for the data branch.
This script analyzes all data files and creates a comprehensive statistics report.
"""

import json
import os
from datetime import datetime
from collections import Counter
from typing import Dict, List, Any


def load_json_file(filepath: str) -> List[Any]:
    """Load a JSON file and return its contents."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []


def analyze_events(events: List[Dict]) -> Dict[str, Any]:
    """Analyze events data and return statistics."""
    if not events:
        return {}

    event_types = Counter(event.get('eventType', 'unknown') for event in events)
    headings = Counter(event.get('heading', 'unknown') for event in events)

    # Count events with spawns and field research
    has_spawns = sum(1 for event in events
                     if event.get('extraData', {}).get('generic', {}).get('hasSpawns', False))
    has_research = sum(1 for event in events
                       if event.get('extraData', {}).get('generic', {}).get('hasFieldResearchTasks', False))

    return {
        'total': len(events),
        'by_type': dict(event_types.most_common()),
        'by_heading': dict(headings.most_common()),
        'with_spawns': has_spawns,
        'with_field_research': has_research
    }


def analyze_raids(raids: List[Dict]) -> Dict[str, Any]:
    """Analyze raids data and return statistics."""
    if not raids:
        return {}

    tiers = Counter(raid.get('tier', 'unknown') for raid in raids)
    shiny_available = sum(1 for raid in raids if raid.get('canBeShiny', False))

    # Count pokemon by type
    type_counter = Counter()
    for raid in raids:
        for poke_type in raid.get('types', []):
            type_counter[poke_type.get('name', 'unknown')] += 1

    return {
        'total': len(raids),
        'by_tier': dict(tiers.most_common()),
        'shiny_available': shiny_available,
        'top_types': dict(type_counter.most_common(10))
    }


def analyze_research(research_tasks: List[Dict]) -> Dict[str, Any]:
    """Analyze research tasks and return statistics."""
    if not research_tasks:
        return {}

    total_rewards = sum(len(task.get('rewards', [])) for task in research_tasks)
    shiny_rewards = sum(
        1 for task in research_tasks
        for reward in task.get('rewards', [])
        if reward.get('can_be_shiny', False)
    )

    return {
        'total': len(research_tasks),
        'total_possible_rewards': total_rewards,
        'shiny_possible_rewards': shiny_rewards
    }


def analyze_eggs(eggs: List[Dict]) -> Dict[str, Any]:
    """Analyze eggs data and return statistics."""
    if not eggs:
        return {}

    # Eggs might have different structure, adjust as needed
    egg_distances = Counter()
    shiny_available = 0

    for egg in eggs:
        # Try to extract distance info if available
        distance = egg.get('eggType', egg.get('distance', egg.get('eggDistance', 'unknown')))
        egg_distances[distance] += 1
        if egg.get('canBeShiny', False):
            shiny_available += 1

    return {
        'total': len(eggs),
        'by_distance': dict(egg_distances.most_common()),
        'shiny_available': shiny_available
    }


def analyze_rocket(rocket_lineups: List[Dict]) -> Dict[str, Any]:
    """Analyze Team GO Rocket lineups and return statistics."""
    if not rocket_lineups:
        return {}

    return {
        'total': len(rocket_lineups)
    }


def analyze_promo_codes(promo_codes: List[Dict]) -> Dict[str, Any]:
    """Analyze promo codes and return statistics."""
    if not promo_codes:
        return {}

    return {
        'total': len(promo_codes)
    }


def generate_readme(stats: Dict[str, Any]) -> str:
    """Generate README content with statistics."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    readme = f"""<div align="center">

# Pokemon GO Data Statistics

**Last Updated:** {timestamp}

This branch contains automatically scraped Pokemon GO data from LeekDuck.com, updated hourly.

## Overall Statistics

"""

    # Overall counts
    total_items = sum(
        stats.get(key, {}).get('total', 0)
        for key in ['events', 'raids', 'research', 'eggs', 'rocket', 'promo_codes']
    )

    readme += f"**Total Items:** {total_items}\n\n"
    readme += "| Data Type | Count |\n"
    readme += "|:---------:|:-----:|\n"

    if stats.get('events'):
        readme += f"| Events | {stats['events']['total']} |\n"
    if stats.get('raids'):
        readme += f"| Raids | {stats['raids']['total']} |\n"
    if stats.get('research'):
        readme += f"| Research Tasks | {stats['research']['total']} |\n"
    if stats.get('eggs'):
        readme += f"| Eggs | {stats['eggs']['total']} |\n"
    if stats.get('rocket'):
        readme += f"| Team GO Rocket Lineups | {stats['rocket']['total']} |\n"
    if stats.get('promo_codes'):
        readme += f"| Promo Codes | {stats['promo_codes']['total']} |\n"

    # Events breakdown
    if stats.get('events'):
        readme += "\n## Events Breakdown\n\n"

        if stats['events'].get('by_type'):
            readme += "### By Event Type\n\n"
            readme += "| Event Type | Count |\n"
            readme += "|:-----------|------:|\n"
            for event_type, count in sorted(stats['events']['by_type'].items(), key=lambda x: x[1], reverse=True):
                readme += f"| {event_type} | {count} |\n"
            readme += "\n"

        if stats['events'].get('by_heading'):
            readme += "### By Category\n\n"
            readme += "| Category | Count |\n"
            readme += "|:---------|------:|\n"
            for heading, count in sorted(stats['events']['by_heading'].items(), key=lambda x: x[1], reverse=True):
                readme += f"| {heading} | {count} |\n"
            readme += "\n"

        readme += "### Event Features\n\n"
        readme += "| Feature | Count |\n"
        readme += "|:--------|------:|\n"
        readme += f"| Events with spawns | {stats['events'].get('with_spawns', 0)} |\n"
        readme += f"| Events with field research | {stats['events'].get('with_field_research', 0)} |\n"

    # Raids breakdown
    if stats.get('raids'):
        readme += "\n## Raids Breakdown\n\n"

        if stats['raids'].get('by_tier'):
            readme += "### By Tier\n\n"
            readme += "| Tier | Count |\n"
            readme += "|:-----|------:|\n"
            tier_order = ['Tier 1', 'Tier 3', 'Tier 5', 'Mega', 'Mega Legendary', 'Elite']
            for tier in tier_order:
                if tier in stats['raids']['by_tier']:
                    readme += f"| {tier} | {stats['raids']['by_tier'][tier]} |\n"
            # Add any other tiers not in the predefined order
            for tier, count in stats['raids']['by_tier'].items():
                if tier not in tier_order:
                    readme += f"| {tier} | {count} |\n"
            readme += "\n"

        readme += f"**Raids with Shiny Available:** {stats['raids'].get('shiny_available', 0)}\n\n"

        if stats['raids'].get('top_types'):
            readme += "### Top Pokemon Types in Raids\n\n"
            readme += "| Type | Count |\n"
            readme += "|:-----|------:|\n"
            for poke_type, count in list(stats['raids']['top_types'].items())[:10]:
                readme += f"| {poke_type.title()} | {count} |\n"

    # Research breakdown
    if stats.get('research'):
        readme += "\n## Research Tasks Breakdown\n\n"
        readme += "| Metric | Count |\n"
        readme += "|:-------|------:|\n"
        readme += f"| Total Tasks | {stats['research']['total']} |\n"
        readme += f"| Total Possible Rewards | {stats['research'].get('total_possible_rewards', 0)} |\n"
        readme += f"| Rewards with Shiny Available | {stats['research'].get('shiny_possible_rewards', 0)} |\n"

    # Eggs breakdown
    if stats.get('eggs'):
        readme += "\n## Eggs Breakdown\n\n"

        if stats['eggs'].get('by_distance'):
            readme += "### By Distance\n\n"
            readme += "| Distance | Count |\n"
            readme += "|:---------|------:|\n"
            # Sort by extracting the numeric value from distance strings like "2 km"
            sorted_distances = sorted(stats['eggs']['by_distance'].items(),
                                     key=lambda x: int(x[0].split()[0]) if x[0].split()[0].isdigit() else 999)
            for distance, count in sorted_distances:
                readme += f"| {distance} | {count} |\n"
            readme += "\n"

        readme += f"**Eggs with Shiny Available:** {stats['eggs'].get('shiny_available', 0)}\n"

    # Rocket lineups
    if stats.get('rocket'):
        readme += f"\n## Team GO Rocket\n\n"
        readme += "| Metric | Count |\n"
        readme += "|:-------|------:|\n"
        readme += f"| Total Lineups | {stats['rocket']['total']} |\n"

    # Promo codes
    if stats.get('promo_codes'):
        readme += f"\n## Promo Codes\n\n"
        readme += "| Metric | Count |\n"
        readme += "|:-------|------:|\n"
        readme += f"| Available Codes | {stats['promo_codes']['total']} |\n"

    # Data files info
    readme += "\n## Data Files\n\n"
    readme += "| File | Description |\n"
    readme += "|:-----|:------------|\n"
    readme += "| `events.json` | Current and upcoming events |\n"
    readme += "| `raids.json` | Active raid bosses |\n"
    readme += "| `research.json` | Field research tasks and rewards |\n"
    readme += "| `eggs.json` | Egg hatching pool |\n"
    readme += "| `rocket-lineups.json` | Team GO Rocket lineups |\n"
    readme += "| `promo-codes.json` | Active promotional codes |\n"

    readme += "\n## Update Schedule\n\n"
    readme += "This data is automatically updated every hour via GitHub Actions.\n"

    readme += "\n## Data Source\n\n"
    readme += "All data is scraped from [LeekDuck.com](https://leekduck.com), a community resource for Pokemon GO information.\n"

    readme += "\n---\n\n"
    readme += "*This README is automatically generated. Do not edit manually.*\n"
    readme += "\n</div>\n"

    return readme


def main():
    """Main function to generate README with statistics."""
    print("Generating data statistics README...")

    # Load all data files
    events = load_json_file('events.json')
    raids = load_json_file('raids.json')
    research = load_json_file('research.json')
    eggs = load_json_file('eggs.json')
    rocket_lineups = load_json_file('rocket-lineups.json')
    promo_codes = load_json_file('promo-codes.json')

    # Analyze each data type
    stats = {
        'events': analyze_events(events),
        'raids': analyze_raids(raids),
        'research': analyze_research(research),
        'eggs': analyze_eggs(eggs),
        'rocket': analyze_rocket(rocket_lineups),
        'promo_codes': analyze_promo_codes(promo_codes)
    }

    # Generate README
    readme_content = generate_readme(stats)

    # Write README
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("README.md generated successfully!")
    print(f"Total items analyzed: {sum(s.get('total', 0) for s in stats.values())}")


if __name__ == '__main__':
    main()
