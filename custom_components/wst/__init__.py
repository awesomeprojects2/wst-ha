"""Westerscheldetunnel (WST) Status Board integration for Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from .api import WSTApiClient
from .const import DOMAIN, PLATFORMS
from .coordinator import WSTDataUpdateCoordinator
from .data import WSTConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: WSTConfigEntry) -> bool:
    """Set up WST from a config entry."""
    api = WSTApiClient(hass)

    coordinator = WSTDataUpdateCoordinator(hass, entry, api)

    entry.runtime_data = coordinator

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: WSTConfigEntry) -> bool:
    """Unload a WST config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    coordinator: WSTDataUpdateCoordinator = entry.runtime_data
    await coordinator.api.async_close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: WSTConfigEntry) -> None:
    """Handle options update - reload the entry."""
    await hass.config_entries.async_reload(entry.entry_id)