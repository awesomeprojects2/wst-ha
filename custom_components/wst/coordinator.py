"""DataUpdateCoordinator for the WST integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WSTApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .data import WSTData, WSTSituation, WSTIncident
from .exceptions import WSTApiAuthError, WSTApiError
from .models import from_api_incident, from_api_situation

_LOGGER = logging.getLogger(__name__)


class WSTDataUpdateCoordinator(DataUpdateCoordinator[WSTData]):
    """Coordinator for polling WST Status Board API data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: WSTApiClient,
    ) -> None:
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
            always_update=False,
        )
        self.api = api

    async def _async_update_data(self) -> WSTData:
        """Fetch data from all WST API endpoints in parallel."""
        try:
            async with asyncio.timeout(10):
                situation_raw, active_raw, scheduled_raw = await asyncio.gather(
                    self.api.async_get_situation(),
                    self.api.async_get_active_incidents(),
                    self.api.async_get_scheduled_incidents(),
                )

        except WSTApiAuthError as err:
            raise ConfigEntryAuthFailed from err
        except WSTApiError as err:
            raise UpdateFailed(f"Error fetching WST data: {err}") from err

        situation = from_api_situation(situation_raw)
        active_incidents = [from_api_incident(i) for i in (active_raw if isinstance(active_raw, list) else [])]
        scheduled_incidents = [from_api_incident(i) for i in (scheduled_raw if isinstance(scheduled_raw, list) else [])]

        return WSTData(
            situation=situation,
            active_incidents=active_incidents,
            scheduled_incidents=scheduled_incidents,
        )