"""Unit tests for pogo_mcp utility functions."""

from datetime import datetime, timedelta, timezone

import pytest

from pogo_mcp.types import EggInfo, EventInfo, PokemonInfo, RaidInfo, TypeInfo
from pogo_mcp.utils import (
    filter_eggs_by_distance,
    filter_raids_by_tier,
    filter_raids_by_type,
    filter_shiny_pokemon,
    is_event_active,
    is_event_upcoming,
    parse_datetime,
    search_pokemon_by_name,
)

# Test date used across multiple test fixtures
TEST_DATE_YEAR = 2026
TEST_DATE_MONTH = 1
TEST_DATE_DAY = 24


class TestDatetimeParsing:
    """Test datetime parsing utility."""

    def test_parse_valid_datetime_string(self):
        """Test parsing a valid datetime string."""
        result = parse_datetime("2026-01-24 12:00:00")
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == TEST_DATE_YEAR
        assert result.month == TEST_DATE_MONTH
        assert result.day == TEST_DATE_DAY

    def test_parse_none_input(self):
        """Test parsing None input."""
        result = parse_datetime(None)
        assert result is None

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = parse_datetime("")
        assert result is None

    def test_parse_invalid_string(self):
        """Test parsing invalid string."""
        result = parse_datetime("not-a-date")
        assert result is None


class TestEventStatusChecks:
    """Test event active/upcoming status checks."""

    @pytest.fixture
    def current_time(self):
        """Fixed current time for testing."""
        return datetime(
            TEST_DATE_YEAR,
            TEST_DATE_MONTH,
            TEST_DATE_DAY,
            12,
            0,
            0,
            tzinfo=timezone.utc,
        )

    @pytest.fixture
    def active_event(self, current_time):
        """Create an event that is currently active."""
        start = current_time - timedelta(hours=1)
        end = current_time + timedelta(hours=1)
        return EventInfo(
            event_id="active-1",
            name="Active Event",
            event_type="community",
            heading="Active Event Heading",
            link="https://example.com/active",
            image="active.png",
            start=start.isoformat(),
            end=end.isoformat(),
            extra_data={},
        )

    @pytest.fixture
    def upcoming_event(self, current_time):
        """Create an event that is upcoming."""
        start = current_time + timedelta(hours=2)
        end = current_time + timedelta(hours=5)
        return EventInfo(
            event_id="upcoming-1",
            name="Upcoming Event",
            event_type="event",
            heading="Upcoming Event",
            link="https://example.com/upcoming",
            start=start.isoformat(),
            end=end.isoformat(),
            image="upcoming.png",
            extra_data={},
        )

    @pytest.fixture
    def past_event(self, current_time):
        """Create an event that has ended."""
        start = current_time - timedelta(hours=5)
        end = current_time - timedelta(hours=1)
        return EventInfo(
            event_id="past-1",
            name="Past Event",
            event_type="event",
            heading="Past Event",
            link="https://example.com/past",
            start=start.isoformat(),
            end=end.isoformat(),
            image="past.png",
            extra_data={},
        )

    def test_is_event_active_true(self, active_event, current_time):
        """Test that active event returns True."""
        assert is_event_active(active_event, current_time) is True

    def test_is_event_active_false_upcoming(self, upcoming_event, current_time):
        """Test that upcoming event returns False for active check."""
        assert is_event_active(upcoming_event, current_time) is False

    def test_is_event_active_false_past(self, past_event, current_time):
        """Test that past event returns False for active check."""
        assert is_event_active(past_event, current_time) is False

    def test_is_event_upcoming_true(self, upcoming_event, current_time):
        """Test that upcoming event returns True."""
        assert is_event_upcoming(upcoming_event, current_time) is True

    def test_is_event_upcoming_false_active(self, active_event, current_time):
        """Test that active event returns False for upcoming check."""
        assert is_event_upcoming(active_event, current_time) is False

    def test_is_event_upcoming_false_past(self, past_event, current_time):
        """Test that past event returns False for upcoming check."""
        assert is_event_upcoming(past_event, current_time) is False

    def test_is_event_active_invalid_dates(self):
        """Test event with invalid date strings."""
        event = EventInfo(
            event_id="invalid-1",
            name="Invalid Event",
            event_type="event",
            heading="Invalid Event",
            link="https://example.com/invalid",
            start="not-a-date",
            end="not-a-date",
            image="invalid.png",
            extra_data={},
        )
        assert is_event_active(event) is False
        assert is_event_upcoming(event) is False


class TestPokemonFilters:
    """Test Pokemon filtering utilities."""

    @pytest.fixture
    def sample_pokemon(self):
        """Create sample Pokemon list."""
        return [
            PokemonInfo(
                name="Pikachu",
                image="pikachu.png",
                can_be_shiny=True,
            ),
            PokemonInfo(
                name="Charizard",
                image="charizard.png",
                can_be_shiny=True,
            ),
            PokemonInfo(
                name="Bulbasaur",
                image="bulbasaur.png",
                can_be_shiny=False,
            ),
            PokemonInfo(
                name="Raichu",
                image="raichu.png",
                can_be_shiny=True,
            ),
        ]

    def test_search_pokemon_by_name_exact_match(self, sample_pokemon):
        """Test exact name match."""
        result = search_pokemon_by_name("Pikachu", sample_pokemon)
        assert len(result) == 1
        assert result[0].name == "Pikachu"

    def test_search_pokemon_by_name_partial_match(self, sample_pokemon):
        """Test partial name match."""
        result = search_pokemon_by_name("chu", sample_pokemon)
        assert len(result) == 2  # noqa: PLR2004 - Pikachu and Raichu match
        names = [p.name for p in result]
        assert "Pikachu" in names
        assert "Raichu" in names

    def test_search_pokemon_by_name_case_insensitive(self, sample_pokemon):
        """Test case-insensitive search."""
        result = search_pokemon_by_name("CHAR", sample_pokemon)
        assert len(result) == 1
        assert result[0].name == "Charizard"

    def test_search_pokemon_no_match(self, sample_pokemon):
        """Test search with no matches."""
        result = search_pokemon_by_name("Mewtwo", sample_pokemon)
        assert len(result) == 0

    def test_filter_shiny_pokemon(self, sample_pokemon):
        """Test filtering for shiny-capable Pokemon."""
        result = filter_shiny_pokemon(sample_pokemon)
        assert len(result) == 3  # noqa: PLR2004 - Pikachu, Charizard, and Raichu are shiny-capable
        names = [p.name for p in result]
        assert "Pikachu" in names
        assert "Charizard" in names
        assert "Raichu" in names
        assert "Bulbasaur" not in names


class TestRaidFilters:
    """Test raid filtering utilities."""

    @pytest.fixture
    def sample_raids(self):
        """Create sample raid list."""
        return [
            RaidInfo(
                name="Mega Charizard X",
                tier="Mega",
                can_be_shiny=True,
                types=[TypeInfo(name="Fire", image="fire.png")],
                combat_power={},
                boosted_weather=[],
                image="mega-charizard.png",
            ),
            RaidInfo(
                name="Mewtwo",
                tier="5*",
                can_be_shiny=True,
                types=[TypeInfo(name="Psychic", image="psychic.png")],
                combat_power={},
                boosted_weather=[],
                image="mewtwo.png",
            ),
            RaidInfo(
                name="Tyranitar",
                tier="4*",
                can_be_shiny=False,
                types=[
                    TypeInfo(name="Rock", image="rock.png"),
                    TypeInfo(name="Dark", image="dark.png"),
                ],
                combat_power={},
                boosted_weather=[],
                image="tyranitar.png",
            ),
        ]

    def test_filter_raids_by_tier_mega(self, sample_raids):
        """Test filtering by Mega tier."""
        result = filter_raids_by_tier(sample_raids, "Mega")
        assert len(result) == 1
        assert result[0].name == "Mega Charizard X"

    def test_filter_raids_by_tier_case_insensitive(self, sample_raids):
        """Test tier filter is case-insensitive."""
        result = filter_raids_by_tier(sample_raids, "5*")
        assert len(result) == 1
        assert result[0].name == "Mewtwo"

    def test_filter_raids_by_tier_partial_match(self, sample_raids):
        """Test tier filter with partial match."""
        result = filter_raids_by_tier(sample_raids, "4")
        assert len(result) == 1
        assert result[0].name == "Tyranitar"

    def test_filter_raids_by_type_single(self, sample_raids):
        """Test filtering by single type."""
        result = filter_raids_by_type(sample_raids, "Psychic")
        assert len(result) == 1
        assert result[0].name == "Mewtwo"

    def test_filter_raids_by_type_dual_type(self, sample_raids):
        """Test filtering by one type of dual-type Pokemon."""
        result = filter_raids_by_type(sample_raids, "Rock")
        assert len(result) == 1
        assert result[0].name == "Tyranitar"

    def test_filter_raids_by_type_case_insensitive(self, sample_raids):
        """Test type filter is case-insensitive."""
        result = filter_raids_by_type(sample_raids, "fire")
        assert len(result) == 1
        assert result[0].name == "Mega Charizard X"


class TestEggFilters:
    """Test egg filtering utilities."""

    @pytest.fixture
    def sample_eggs(self):
        """Create sample egg list."""
        return [
            EggInfo(
                name="Pichu",
                egg_type="2 km",
                is_adventure_sync=False,
                image="2km.png",
                can_be_shiny=True,
                combat_power=540,
                is_regional=False,
                is_gift_exchange=False,
                is_route_gift=False,
                rarity=1,
            ),
            EggInfo(
                name="Bulbasaur",
                egg_type="5 km",
                is_adventure_sync=False,
                image="5km.png",
                can_be_shiny=False,
                combat_power=644,
                is_regional=False,
                is_gift_exchange=False,
                is_route_gift=False,
                rarity=1,
            ),
            EggInfo(
                name="Eevee",
                egg_type="10 km",
                is_adventure_sync=False,
                image="10km.png",
                can_be_shiny=False,
                combat_power=744,
                is_regional=False,
                is_gift_exchange=False,
                is_route_gift=False,
                rarity=1,
            ),
        ]

    def test_filter_eggs_by_distance_2km(self, sample_eggs):
        """Test filtering 2km eggs."""
        result = filter_eggs_by_distance(sample_eggs, "2 km")
        assert len(result) == 1
        assert result[0].egg_type == "2 km"

    def test_filter_eggs_by_distance_number_only(self, sample_eggs):
        """Test filtering with just the number."""
        result = filter_eggs_by_distance(sample_eggs, 5)
        assert len(result) == 1
        assert result[0].egg_type == "5 km"

    def test_filter_eggs_by_distance_string_number(self, sample_eggs):
        """Test filtering with string number."""
        result = filter_eggs_by_distance(sample_eggs, "10")
        assert len(result) == 1
        assert result[0].egg_type == "10 km"

    def test_filter_eggs_by_distance_case_insensitive(self, sample_eggs):
        """Test distance filter is case-insensitive."""
        result = filter_eggs_by_distance(sample_eggs, "5 KM")
        assert len(result) == 1
        assert result[0].egg_type == "5 km"
