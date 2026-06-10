"""Test fixtures for the WST integration (new API format)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from custom_components.wst.const import DEFAULT_SCAN_INTERVAL, DOMAIN, ENTRY_UNIQUE_ID
from custom_components.wst.coordinator import WSTDataUpdateCoordinator
from custom_components.wst.data import WSTData
from custom_components.wst.api import WSTApiClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict:
    """Load a JSON fixture file."""
    with open(FIXTURES_DIR / filename) as f:
        return json.load(f)


@pytest.fixture
def situation_response():
    """Return a mock situation API response dict."""
    return load_fixture("situation_response.json")


@pytest.fixture
def active_incidents_response():
    """Return a mock active incidents API response."""
    return load_fixture("active_incidents_response.json")


@pytest.fixture
def scheduled_incidents_response():
    """Return a mock scheduled incidents API response."""
    return load_fixture("scheduled_incidents_response.json")


@pytest.fixture
def mock_api(situation_response, active_incidents_response, scheduled_incidents_response):
    """Return a mock WSTApiClient with pre-configured responses."""
    api = MagicMock(spec=WSTApiClient)
    api.async_get_situation = AsyncMock(return_value=situation_response)
    api.async_get_active_incidents = AsyncMock(return_value=active_incidents_response)
    api.async_get_scheduled_incidents = AsyncMock(return_value=scheduled_incidents_response)
    api.async_validate_connection = AsyncMock(return_value=True)
    api.async_close = AsyncMock()
    return api


@pytest.fixture
def wst_data(situation_response, active_incidents_response, scheduled_incidents_response):
    """Return a parsed WSTData object from fixtures."""
    from custom_components.wst.models import to_wst_data

    return to_wst_data(situation_response, active_incidents_response, scheduled_incidents_response)


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_api):
    """Set up the WST integration with mock data."""
    with patch("custom_components.wst.api.WSTApiClient", return_value=mock_api):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
        )

    if result.get("type") != "create_entry":
        await hass.async_block_till_done()

    entries = hass.config_entries.async_entries(DOMAIN)
    if entries:
        await hass.config_entries.async_setup(entries[0].entry_id)
        await hass.async_block_till_done()

    return entries[0] if entries else None


@pytest.fixture
def mock_config_entry(hass: HomeAssistant):
    """Create a mock ConfigEntry for WST."""
    from homeassistant import config_entries

    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=ENTRY_UNIQUE_ID,
        data={},
        options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
    )
    entry.add_to_hass(hass)
    return entry


class MockConfigEntry:
    """Minimal mock ConfigEntry for testing."""

    def __init__(self, domain, unique_id, data=None, options=None, entry_id="test_entry_id"):
        self.domain = domain
        self.unique_id = unique_id
        self.entry_id = entry_id
        self.data = data or {}
        self.options = options or {}
        self.runtime_data = None

    def add_to_hass(self, hass):
        """Add entry to hass config entries."""
        hass.config_entries._entries[self.entry_id] = self