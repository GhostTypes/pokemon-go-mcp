"""Shared fixtures for MCP server integration tests."""

import pytest
import asyncio
from pathlib import Path
from pogo_mcp.server import mcp
from pogo_mcp.api_client import api_client


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def mcp_server():
    """Fixture that provides the MCP server instance.

    This fixture ensures the MCP server is properly initialized
    with all tools registered before tests run.
    """
    # The server is already initialized when imported, just return it
    return mcp


@pytest.fixture(scope="session")
def api_client_instance():
    """Fixture that provides the API client instance."""
    return api_client


@pytest.fixture(scope="function")
def fresh_cache():
    """Fixture that clears the cache before each test to ensure fresh data."""
    api_client.clear_cache()
    yield
    # Cache is cleared again after test if needed


@pytest.fixture(scope="session")
def data_dir():
    """Fixture that provides the path to the data directory."""
    return Path(__file__).parent.parent.parent / "data"


@pytest.fixture(scope="session")
def ensure_test_data(data_dir):
    """Ensure test data files exist before running integration tests.

    This fixture verifies that all required data files are present.
    If they're missing, tests will be skipped with a clear message.
    """
    required_files = [
        "events.json",
        "raids.json",
        "research.json",
        "eggs.json",
        "rocket-lineups.json",
        "promo-codes.json"
    ]

    missing_files = []
    for file in required_files:
        file_path = data_dir / file
        if not file_path.exists():
            missing_files.append(file)

    if missing_files:
        pytest.skip(
            f"Required data files missing: {', '.join(missing_files)}. "
            "Please run the scraper first to generate test data."
        )

    return True


@pytest.fixture(scope="session")
def sample_event_id(ensure_test_data):
    """Get a sample event ID for testing event-specific functions."""
    # Load events synchronously for session-scoped fixture
    import json
    from pathlib import Path
    data_file = Path(__file__).parent.parent.parent / "data" / "events.json"
    with open(data_file) as f:
        events = json.load(f)
    if events:
        return events[0]["eventID"]
    pytest.skip("No events available in test data")


@pytest.fixture(scope="session")
def sample_pokemon_name(ensure_test_data):
    """Get a sample Pokemon name for testing search functions."""
    import json
    from pathlib import Path

    # Try raids first
    data_file = Path(__file__).parent.parent.parent / "data" / "raids.json"
    with open(data_file) as f:
        raids = json.load(f)
    if raids:
        return raids[0]["name"]

    # Try research
    data_file = Path(__file__).parent.parent.parent / "data" / "research.json"
    with open(data_file) as f:
        research = json.load(f)
    if research and research[0].get("rewards"):
        return research[0]["rewards"][0]["name"]

    pytest.skip("No Pokemon available in test data")


@pytest.fixture(scope="session")
def sample_raid_tier(ensure_test_data):
    """Get a sample raid tier for testing tier-specific functions."""
    import json
    from pathlib import Path
    data_file = Path(__file__).parent.parent.parent / "data" / "raids.json"
    with open(data_file) as f:
        raids = json.load(f)
    if raids:
        return raids[0]["tier"]
    pytest.skip("No raids available in test data")


@pytest.fixture(scope="session")
def sample_trainer_name(ensure_test_data):
    """Get a sample Team Rocket trainer name for testing."""
    import json
    from pathlib import Path
    data_file = Path(__file__).parent.parent.parent / "data" / "rocket-lineups.json"
    with open(data_file) as f:
        trainers = json.load(f)
    if trainers:
        return trainers[0]["name"]
    pytest.skip("No Team Rocket trainers available in test data")
