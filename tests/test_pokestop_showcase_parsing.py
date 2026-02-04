import asyncio
from pathlib import Path

from bs4 import BeautifulSoup

from pogo_scraper.parsers.events.pokestop_showcase_details import (
    parse_pokestop_showcase_details,
)


def test_pokestop_showcase_parsing():
    fixture_path = Path(__file__).parent / "fixtures" / "pokestop_showcase_event.html"
    html_content = fixture_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "lxml")

    event = {"name": "Showcase", "extraData": {"generic": {}}}

    asyncio.run(parse_pokestop_showcase_details(soup, event))

    showcase = event["extraData"].get("pokestopshowcase", {})
    pokemon = {entry.get("name") for entry in showcase.get("showcasePokemon", [])}

    assert {"Ludicolo", "Toucannon", "Quaquaval"}.issubset(pokemon)
