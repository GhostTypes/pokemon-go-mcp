import pytest

from pogo_scraper.parsers.events.base_event import infer_event_type


@pytest.mark.parametrize(
    ("name", "heading", "expected"),
    [
        ("GO Battle League: Max Out", "GO Battle League", "go-battle-league"),
        ("PokéStop Showcase", "PokéStop Showcase", "pokestop-showcase"),
        ("Raid Hour: Kyogre", "Raid Hour", "raid-hour"),
        ("Max Monday: Something", "Max Mondays", "max-mondays"),
        ("Max Battle Weekend", "Max Battles", "max-battles"),
        ("Pokémon GO Tour: Unova", "Pokémon GO Tour", "pokemon-go-tour"),
        ("GO Pass: April", "GO Pass", "go-pass"),
        ("Season of Might", "Season", "season"),
        ("Research Day: Skrelp", "Research Day", "research-day"),
    ],
)
def test_infer_event_type_variants(name, heading, expected):
    assert infer_event_type(name, heading) == expected
