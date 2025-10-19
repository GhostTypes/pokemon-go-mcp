"""
Standalone test script for raid day HTML parsing
Tests extraction of bonuses, research, shinies, and bosses from LeekDuck raid day pages
"""

import asyncio
import logging
from bs4 import BeautifulSoup
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import the cloudscraper scraper
try:
    from pogo_scraper.scraper import create_scraper
except ImportError:
    logger.warning("Could not import scraper, will try manual HTML fetch")
    create_scraper = None


async def fetch_raid_day_html(url: str) -> str:
    """Fetch HTML from raid day page"""
    if create_scraper:
        scraper = await create_scraper()
        try:
            response = await scraper.get(url)
            return response.text
        finally:
            await scraper.close()
    else:
        # Fallback: use requests
        import requests
        response = requests.get(url)
        response.raise_for_status()
        return response.text


def parse_bonuses_with_sections(soup: BeautifulSoup) -> tuple:
    """Parse bonuses and ticket bonuses separately"""
    free_bonuses = []
    ticket_bonuses = []

    # Find the bonuses section
    bonuses_section = soup.find('h2', id='bonuses')
    if not bonuses_section:
        logger.warning("No #bonuses section found")
        return free_bonuses, ticket_bonuses

    logger.info("Found #bonuses section")
    current_section = "free"

    # Iterate through siblings
    current = bonuses_section.find_next_sibling()

    while current:
        # Check if we've hit another major section (stop parsing bonuses)
        if current.name == 'h2':
            section_id = current.get('id', '')
            if section_id == 'event-ticket':
                logger.info("Found #event-ticket section, switching to ticket bonuses")
                current_section = "ticket"
            elif section_id not in ['bonuses', 'event-ticket']:
                # Hit a different section, stop
                logger.info(f"Hit section #{section_id}, stopping bonus parsing")
                break

        # Look for bonus lists
        if current.name == 'div' and 'bonus-list' in current.get('class', []):
            bonus_items = current.select('.bonus-item')
            logger.info(f"Found {len(bonus_items)} bonus items in {current_section} section")

            for bonus in bonus_items:
                text_elem = bonus.select_one('.bonus-text')
                img_elem = bonus.select_one('.item-circle img')

                if text_elem:
                    bonus_data = {
                        'text': text_elem.get_text(strip=True),
                        'image': img_elem.get('src', '') if img_elem else ''
                    }

                    if current_section == "free":
                        free_bonuses.append(bonus_data)
                    else:
                        ticket_bonuses.append(bonus_data)

        current = current.find_next_sibling()

    logger.info(f"Extracted {len(free_bonuses)} free bonuses, {len(ticket_bonuses)} ticket bonuses")
    return free_bonuses, ticket_bonuses


def parse_research(soup: BeautifulSoup) -> list:
    """Parse timed research tasks and rewards"""
    research_list = []

    research_items = soup.select('.special-research-list .step-item')
    logger.info(f"Found {len(research_items)} research steps")

    for item in research_items:
        research = {
            'name': '',
            'step': 0,
            'tasks': [],
            'rewards': []
        }

        # Step number
        step_num_elem = item.select_one('.step-number')
        if step_num_elem:
            try:
                research['step'] = int(step_num_elem.get_text(strip=True))
            except ValueError:
                logger.warning("Could not parse step number")

        # Step name
        step_name_elem = item.select_one('.step-name')
        if step_name_elem:
            research['name'] = step_name_elem.get_text(strip=True)

        # Tasks with rewards
        task_rewards = item.select('.task-reward')
        logger.info(f"  Step {research['step']}: Found {len(task_rewards)} tasks")

        for task_reward in task_rewards:
            task_text_elem = task_reward.select_one('.task-text')
            reward_label_elem = task_reward.select_one('.reward-label')
            reward_img_elem = task_reward.select_one('.reward-image')

            if task_text_elem:
                task = {
                    'text': task_text_elem.get_text(strip=True),
                    'reward': {
                        'text': reward_label_elem.get_text(strip=True) if reward_label_elem else '',
                        'image': reward_img_elem.get('src', '') if reward_img_elem else ''
                    }
                }
                research['tasks'].append(task)

        # Page-level rewards
        page_rewards = item.select('.page-reward')
        logger.info(f"  Step {research['step']}: Found {len(page_rewards)} page rewards")

        for reward in page_rewards:
            reward_label_elem = reward.select_one('.reward-label span')
            reward_img_elem = reward.select_one('.reward-image')

            if reward_img_elem:
                research['rewards'].append({
                    'text': reward_label_elem.get_text(strip=True) if reward_label_elem else '',
                    'image': reward_img_elem.get('src', '')
                })

        if research['name'] or research['tasks'] or research['rewards']:
            research_list.append(research)

    logger.info(f"Extracted {len(research_list)} research steps total")
    return research_list


def parse_shinies(soup: BeautifulSoup) -> list:
    """Parse shiny Pokemon from dedicated #shiny section"""
    shinies = []

    shiny_section = soup.find('h2', id='shiny')
    if not shiny_section:
        logger.warning("No #shiny section found")
        return shinies

    logger.info("Found #shiny section")

    # Find the next .pkmn-list-flex after the shiny header
    pkmn_list = shiny_section.find_next_sibling('ul', class_='pkmn-list-flex')

    if pkmn_list:
        shiny_items = pkmn_list.select('.pkmn-list-item')
        logger.info(f"Found {len(shiny_items)} shiny Pokemon")

        for shiny in shiny_items:
            name_elem = shiny.select_one('.pkmn-name')
            img_elem = shiny.select_one('.pkmn-list-img img')

            if name_elem and img_elem:
                shiny_data = {
                    'name': name_elem.get_text(strip=True),
                    'image': img_elem.get('src', '')
                }
                shinies.append(shiny_data)

    logger.info(f"Extracted {len(shinies)} shiny Pokemon")
    return shinies


def parse_raid_bosses(soup: BeautifulSoup) -> list:
    """Parse raid bosses from #raids section"""
    bosses = []

    raids_section = soup.find('h2', id='raids')
    if not raids_section:
        logger.warning("No #raids section found")
        return bosses

    logger.info("Found #raids section")

    # Find featured Pokemon after raids section
    current = raids_section.find_next_sibling()

    while current:
        if current.name == 'h2':
            # Check if we've hit another major section
            if current.get('id') not in ['featured-pokémon', 'featured-pokemon', '']:
                logger.info(f"Hit section, stopping raid boss parsing")
                break

        if current.name == 'ul' and 'pkmn-list-flex' in current.get('class', []):
            boss_items = current.select('.pkmn-list-item')
            logger.info(f"Found {len(boss_items)} raid bosses")

            for boss in boss_items:
                name_elem = boss.select_one('.pkmn-name')
                img_elem = boss.select_one('.pkmn-list-img img')
                shiny_icon = boss.select_one('.shiny-icon')

                if name_elem and img_elem:
                    boss_data = {
                        'name': name_elem.get_text(strip=True),
                        'image': img_elem.get('src', ''),
                        'canBeShiny': shiny_icon is not None
                    }
                    bosses.append(boss_data)

        current = current.find_next_sibling()

    logger.info(f"Extracted {len(bosses)} raid bosses")
    return bosses


async def test_raid_day_parsing(url: str):
    """Main test function"""
    logger.info(f"Fetching raid day page: {url}")

    try:
        html = await fetch_raid_day_html(url)
        logger.info(f"Fetched HTML ({len(html)} bytes)")
    except Exception as e:
        logger.error(f"Failed to fetch HTML: {e}")
        return

    soup = BeautifulSoup(html, 'html.parser')

    # Extract all data
    logger.info("\n" + "="*60)
    logger.info("PARSING BONUSES")
    logger.info("="*60)
    free_bonuses, ticket_bonuses = parse_bonuses_with_sections(soup)

    logger.info("\n" + "="*60)
    logger.info("PARSING RESEARCH")
    logger.info("="*60)
    research = parse_research(soup)

    logger.info("\n" + "="*60)
    logger.info("PARSING SHINIES")
    logger.info("="*60)
    shinies = parse_shinies(soup)

    logger.info("\n" + "="*60)
    logger.info("PARSING RAID BOSSES")
    logger.info("="*60)
    bosses = parse_raid_bosses(soup)

    # Compile results
    raidday_data = {
        'bosses': bosses,
        'bonuses': free_bonuses,
        'ticketBonuses': ticket_bonuses,
        'research': research,
        'shinies': shinies
    }

    # Print results
    logger.info("\n" + "="*60)
    logger.info("FINAL RESULTS")
    logger.info("="*60)
    print(json.dumps(raidday_data, indent=2))

    # Summary
    logger.info("\n" + "="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info(f"Bosses: {len(bosses)}")
    logger.info(f"Free Bonuses: {len(free_bonuses)}")
    logger.info(f"Ticket Bonuses: {len(ticket_bonuses)}")
    logger.info(f"Research Steps: {len(research)}")
    logger.info(f"Shinies: {len(shinies)}")

    # Validation
    if not bosses:
        logger.warning("⚠️  No bosses extracted - check #raids section")
    if not free_bonuses:
        logger.warning("⚠️  No free bonuses extracted - check #bonuses section")
    if not research:
        logger.warning("⚠️  No research extracted - check .special-research-list")
    if not shinies:
        logger.warning("⚠️  No shinies extracted - check #shiny section")

    if bosses and (free_bonuses or ticket_bonuses) and research and shinies:
        logger.info("✅ ALL DATA EXTRACTED SUCCESSFULLY!")

    return raidday_data


if __name__ == "__main__":
    # Test with the Mega Rayquaza raid day
    test_url = "https://leekduck.com/events/mega-rayquaza-raid-day-november-2025/"

    asyncio.run(test_raid_day_parsing(test_url))
