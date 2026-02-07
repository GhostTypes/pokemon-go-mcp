"""Integration tests for API client fallback logic."""

from datetime import datetime, timezone

import pytest

from pogo_mcp.pogo_types import EventInfo


class TestRaidFallbackLogic:
    """Test raid extraction from events as fallback."""

    @pytest.fixture
    def sample_events_with_raids(self) -> list[EventInfo]:
        """Create sample events with raid battle data."""
        now = datetime.now(timezone.utc)
        return [
            EventInfo(
                event_id="mega-rayquaza-raid-day",
                name="Mega Rayquaza Raid Day",
                event_type="raid",
                heading="Mega Rayquaza Raid Day",
                link="https://example.com/mega-rayquaza",
                start=now.isoformat(),
                end=now.isoformat(),
                image="mega-rayquaza.png",
                extra_data={
                    "raidbattles": {
                        "bosses": [
                            {
                                "name": "Mega Rayquaza",
                                "canBeShiny": True,
                                "image": "mega-rayquaza.png",
                            },
                            {
                                "name": "Mega Gyarados",
                                "canBeShiny": False,
                                "image": "mega-gyarados.png",
                            },
                        ]
                    }
                },
            ),
            EventInfo(
                event_id="legendary-raid-hour",
                name="Legendary Raid Hour",
                event_type="raid",
                heading="Legendary Raid Hour",
                link="https://example.com/legendary-hour",
                start=now.isoformat(),
                end=now.isoformat(),
                image="legendary-hour.png",
                extra_data={
                    "raidbattles": {
                        "bosses": [
                            {
                                "name": "Palkia",
                                "canBeShiny": True,
                                "image": "palkia.png",
                            },
                        ]
                    }
                },
            ),
            EventInfo(
                event_id="community-day",
                name="Community Day",
                event_type="community",
                heading="Community Day",
                link="https://example.com/community-day",
                start=now.isoformat(),
                end=now.isoformat(),
                image="community-day.png",
                extra_data={
                    "other": "data",
                },
            ),
        ]

    def test_extract_raids_from_events(
        self, api_client_instance, sample_events_with_raids
    ):
        """Test extraction of raid bosses from event data."""
        extracted = api_client_instance.extract_raids_from_events(
            sample_events_with_raids
        )

        # Should extract 3 raids (2 from first event, 1 from second, 0 from third)
        assert len(extracted) == 3  # noqa: PLR2004 - Expected number of raids extracted from events

        # Check first raid (Mega Rayquaza)
        assert extracted[0].name == "Mega Rayquaza"
        assert extracted[0].tier == "Mega"
        assert extracted[0].can_be_shiny is True
        assert extracted[0].extra_data["source"] == "events_fallback"
        assert extracted[0].extra_data["event_name"] == "Mega Rayquaza Raid Day"

        # Check second raid (Mega Gyarados)
        assert extracted[1].name == "Mega Gyarados"
        assert extracted[1].tier == "Mega"
        assert extracted[1].can_be_shiny is False

        # Check third raid (Palkia - legendary)
        assert extracted[2].name == "Palkia"
        assert extracted[2].tier == "5*"
        assert extracted[2].can_be_shiny is True

    def test_extract_raids_empty_events(self, api_client_instance):
        """Test extraction with empty event list."""
        extracted = api_client_instance.extract_raids_from_events([])
        assert len(extracted) == 0

    def test_extract_raids_no_raid_data(self, api_client_instance):
        """Test extraction with events that have no raid data."""
        now = datetime.now(timezone.utc)
        events = [
            EventInfo(
                event_id="regular-event",
                name="Regular Event",
                event_type="event",
                heading="Regular Event",
                link="https://example.com/regular",
                start=now.isoformat(),
                end=now.isoformat(),
                image="event.png",
                extra_data={},
            ),
        ]
        extracted = api_client_instance.extract_raids_from_events(events)
        assert len(extracted) == 0

    def test_extract_raids_tier_inference(self, api_client_instance):
        """Test tier inference for different boss types."""
        now = datetime.now(timezone.utc)

        # Test Mega tier
        mega_event = EventInfo(
            event_id="mega-event",
            name="Mega Event",
            event_type="raid",
            heading="Mega Event",
            link="https://example.com/mega",
            start=now.isoformat(),
            end=now.isoformat(),
            image="mega.png",
            extra_data={
                "raidbattles": {
                    "bosses": [{"name": "Mega Charizard", "canBeShiny": True}]
                }
            },
        )
        raids = api_client_instance.extract_raids_from_events([mega_event])
        assert raids[0].tier == "Mega"

        # Test Legendary tier
        legendary_events = [
            EventInfo(
                event_id=f"{legendary.lower()}-raid",
                name=f"{legendary} Raid",
                event_type="raid",
                heading=f"{legendary} Raid",
                link=f"https://example.com/{legendary.lower()}",
                start=now.isoformat(),
                end=now.isoformat(),
                image="legendary.png",
                extra_data={
                    "raidbattles": {
                        "bosses": [{"name": legendary, "canBeShiny": False}]
                    }
                },
            )
            for legendary in ["Dialga", "Giratina", "Lugia", "Ho-Oh", "Mewtwo"]
        ]

        for event in legendary_events:
            raids = api_client_instance.extract_raids_from_events([event])
            assert raids[0].tier == "5*"

        # Test Unknown tier
        unknown_event = EventInfo(
            event_id="unknown-raid",
            name="Unknown Raid",
            event_type="raid",
            heading="Unknown Raid",
            link="https://example.com/unknown",
            start=now.isoformat(),
            end=now.isoformat(),
            image="unknown.png",
            extra_data={
                "raidbattles": {"bosses": [{"name": "Snorlax", "canBeShiny": True}]}
            },
        )
        raids = api_client_instance.extract_raids_from_events([unknown_event])
        assert raids[0].tier == "Unknown"

    def test_extract_raids_preserves_event_metadata(self, api_client_instance):
        """Test that event metadata is preserved in extracted raids."""
        now = datetime.now(timezone.utc)
        event_end = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        event = EventInfo(
            event_id="test-raid-event",
            name="Test Raid Event",
            event_type="raid",
            heading="Test Raid Event",
            link="https://example.com/test",
            start=now.isoformat(),
            end=event_end.isoformat(),
            image="test.png",
            extra_data={
                "raidbattles": {"bosses": [{"name": "Test Boss", "canBeShiny": False}]}
            },
        )

        raids = api_client_instance.extract_raids_from_events([event])
        assert len(raids) == 1
        assert raids[0].extra_data["event_name"] == "Test Raid Event"
        assert raids[0].extra_data["event_end"] == event_end.isoformat()
        assert raids[0].extra_data["source"] == "events_fallback"
