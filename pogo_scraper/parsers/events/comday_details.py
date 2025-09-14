"""
Handles parsing extra event information for community days
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict

logger = logging.getLogger(__name__)


async def parse_community_day_details(soup: BeautifulSoup, event: Dict) -> None:
    """Parse Community Day specific details"""
    try:
        commday_data = {
            'spawns': [],
            'bonuses': [],
            'bonusDisclaimers': [],
            'shinies': [],
            'specialresearch': []
        }

        page_content = soup.select_one('.page-content')
        if not page_content:
            return

        last_header = ""

        # Process page content sections using ScrapedDuck's approach
        all_nodes = page_content.contents

        for element in all_nodes:
            # Get element classes and id (works for both tag elements and navigable strings)
            element_classes = []
            element_id = ''

            # Only try to get class and id attributes from actual HTML elements, not text nodes
            if hasattr(element, 'name') and element.name:
                element_classes = element.get('class', [])
                element_id = element.get('id', '')

            # Check if this is a section header
            if element_classes and 'event-section-header' in element_classes:
                last_header = element_id
                # Uncomment for debugging:
                # print(f"Found section header: {element_id}")

            # Parse spawns and shinies sections - check if 'pkmn-list-flex' is in classes like ScrapedDuck
            # (Changed from exact match to inclusion check to be more robust)
            elif element_classes and 'pkmn-list-flex' in element_classes:
                # Uncomment for debugging:
                # print(f"Found pkmn-list-flex, last_header: {last_header}")
                if last_header == "spawns":
                    spawns = element.select(':scope > .pkmn-list-item')
                    for spawn in spawns:
                        name_elem = spawn.select_one(':scope > .pkmn-name')
                        img_elem = spawn.select_one(':scope > .pkmn-list-img > img')
                        if name_elem and img_elem:
                            spawn_data = {
                                'name': name_elem.get_text(strip=True),
                                'image': img_elem.get('src', '')
                            }
                            commday_data['spawns'].append(spawn_data)

                elif last_header == "shiny":
                    shinies = element.select(':scope > .pkmn-list-item')
                    for shiny in shinies:
                        name_elem = shiny.select_one(':scope > .pkmn-name')
                        img_elem = shiny.select_one(':scope > .pkmn-list-img > img')
                        if name_elem and img_elem:
                            shiny_data = {
                                'name': name_elem.get_text(strip=True),
                                'image': img_elem.get('src', '')
                            }
                            commday_data['shinies'].append(shiny_data)

        # Parse bonuses
        bonuses = soup.select('.bonus-item')
        bonus_has_disclaimer = False

        for bonus in bonuses:
            text_elem = bonus.select_one('.bonus-text')
            img_elem = bonus.select_one('.item-circle img')
            if text_elem and img_elem:
                bonus_text = text_elem.get_text(strip=True)
                commday_data['bonuses'].append({
                    'text': bonus_text,
                    'image': img_elem.get('src', '')
                })

                if '*' in bonus_text:
                    bonus_has_disclaimer = True

        # Parse bonus disclaimers if present
        if bonus_has_disclaimer:
            bonus_list = soup.select_one('.bonus-list')
            if bonus_list and bonus_list.next_sibling:
                next_elem = bonus_list.next_sibling
                while next_elem and getattr(next_elem, 'name', '') != 'h2':
                    if getattr(next_elem, 'name', '') == 'p':
                        disclaimer_text = next_elem.get_text(strip=True)
                        if disclaimer_text:
                            # Split on <br> tags if present
                            if '<br>' in str(next_elem):
                                disclaimers = str(next_elem).split('<br>')
                                for disclaimer in disclaimers:
                                    clean_disclaimer = BeautifulSoup(disclaimer, 'html.parser').get_text(strip=True)
                                    if clean_disclaimer:
                                        commday_data['bonusDisclaimers'].append(clean_disclaimer)
                            else:
                                commday_data['bonusDisclaimers'].append(disclaimer_text)
                    next_elem = next_elem.next_sibling

        # Parse special research
        research_items = soup.select('.special-research-list .step-item')
        for item in research_items:
            research = {
                'name': '',
                'step': 0,
                'tasks': [],
                'rewards': []
            }

            # Step number and name
            step_num_elem = item.select_one('.step-number')
            step_name_elem = item.select_one('.step-name')

            if step_num_elem:
                try:
                    research['step'] = int(step_num_elem.get_text(strip=True))
                except ValueError:
                    pass

            if step_name_elem:
                research['name'] = step_name_elem.get_text(strip=True)

            # Tasks and their rewards
            task_rewards = item.select('.task-reward')
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

            # Page rewards
            page_rewards = item.select('.page-reward')
            for reward in page_rewards:
                reward_label_elem = reward.select_one('.reward-label span')
                reward_img_elem = reward.select_one('.reward-image')

                if reward_label_elem and reward_img_elem:
                    research['rewards'].append({
                        'text': reward_label_elem.get_text(strip=True),
                        'image': reward_img_elem.get('src', '')
                    })

            if research['name'] or research['tasks'] or research['rewards']:
                commday_data['specialresearch'].append(research)

        # Only add communityday data if we found meaningful content
        if (commday_data['spawns'] or commday_data['bonuses'] or
            commday_data['shinies'] or commday_data['specialresearch']):
            event['extraData']['communityday'] = commday_data

    except Exception as e:
        logger.warning(f"Error parsing Community Day details: {e}")