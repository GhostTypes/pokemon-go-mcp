"""
Handles parsing extra event information for timed reseach (with a code)
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict

logger = logging.getLogger(__name__)

async def parse_timed_research_code_details(soup: BeautifulSoup, event: Dict) -> None:
    """Parse Timed Research Code specific details"""
    try:
        timed_research_data = {
            'code': '',
            'code_expires': '',
            'research_expires': ''
        }

        # Look for the specific timed research code element
        # <h2 id="timed-research-code-gofestmax">Timed Research Code: GOFESTMAX</h2>
        code_header = soup.find('h2', id=lambda x: isinstance(x, str) and x.startswith('timed-research-code-'))
        
        if code_header:
            header_text = code_header.get_text(strip=True)
            # Extract code from header text (everything after the colon)
            if ':' in header_text:
                timed_research_data['code'] = header_text.split(":")[-1].strip()

        # Look for expiration information in list items
        list_items = soup.find_all('li')
        
        # Look for "Code expires" and "Research expires" information
        for li in list_items:
            text = li.get_text(strip=True)
            if "Code expires:" in text:
                timed_research_data['code_expires'] = text
            elif "Research expires:" in text:
                timed_research_data['research_expires'] = text

        # Only add timed research data if we found the code
        if timed_research_data['code']:
            event['extraData']['timedresearch'] = timed_research_data

    except Exception as e:
        logger.warning(f"Error parsing Timed Research details: {e}")