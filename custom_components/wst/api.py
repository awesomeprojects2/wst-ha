"""API client for the WST Status Board API.

Uses aiohttp to call the WST REST API directly, avoiding dependency
on the generated wst_api_client package structure which may vary
between versions and generator configurations.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp

from .const import API_BASE_URL
from .exceptions import WSTApiAuthError, WSTApiCommunicationError, WSTApiError, WSTApiTimeoutError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

PATH_SITUATION = "/situation"
PATH_INCIDENT_ACTIVE = "/incident/active"
PATH_INCIDENT_SCHEDULED = "/incident/scheduled"


class WSTApiClient:
    """Async client for the WST Status Board API using aiohttp directly."""

    def __init__(self, hass: HomeAssistant, base_url: str = API_BASE_URL) -> None:
        self._hass = hass
        self._base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get the shared aiohttp session from HA."""
        if self._session is None or self._session.closed:
            from homeassistant.helpers.aiohttp_client import async_get_clientsession
            self._session = async_get_clientsession(self._hass)
        return self._session

    async def async_get_situation(self) -> dict:
        """Fetch the current tunnel situation from the API."""
        return await self._async_get(PATH_SITUATION)

    async def async_get_active_incidents(self) -> list:
        """Fetch active incidents from the API."""
        return await self._async_get(PATH_INCIDENT_ACTIVE)

    async def async_get_scheduled_incidents(self) -> list:
        """Fetch scheduled incidents from the API."""
        return await self._async_get(PATH_INCIDENT_SCHEDULED)

    async def _async_get(self, path: str) -> dict | list:
        """Make a GET request to the API and return the JSON response."""
        url = f"{self._base_url}{path}"
        _LOGGER.info("Requesting WST API: %s", url)

        try:
            session = self._get_session()
            _LOGGER.debug("Using session: %s", type(session).__name__)
            async with session.get(url, headers={"Accept": "application/json"}, timeout=aiohttp.ClientTimeout(total=10)) as response:
                _LOGGER.debug("Response status from %s: %s", path, response.status)
                if response.status == 401:
                    raise WSTApiAuthError(f"Authentication failed (HTTP {response.status})")
                if response.status == 403:
                    raise WSTApiAuthError(f"Access forbidden (HTTP {response.status})")
                if response.status >= 400:
                    text = await response.text()
                    raise WSTApiCommunicationError(
                        f"HTTP {response.status} from {url}: {text[:200]}"
                    )
                return await response.json(content_type=None)

        except WSTApiError:
            raise
        except aiohttp.ClientConnectorError as err:
            _LOGGER.error("Cannot connect to %s: %s", self._base_url, err)
            raise WSTApiCommunicationError(f"Cannot connect to {self._base_url}: {err}") from err
        except aiohttp.ServerTimeoutError as err:
            _LOGGER.error("Timeout connecting to %s: %s", url, err)
            raise WSTApiTimeoutError(f"Timeout connecting to {url}: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error requesting %s: %s", url, err)
            raise WSTApiCommunicationError(f"Request error: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error requesting %s", url)
            raise

    async def async_validate_connection(self) -> bool:
        """Test the API connection by fetching the situation endpoint."""
        try:
            await self.async_get_situation()
            _LOGGER.info("WST API connection validated successfully")
            return True
        except WSTApiError as err:
            _LOGGER.warning("WST API connection test failed: %s", err)
            return False

    async def async_close(self) -> None:
        """Release references. HA manages the shared session lifecycle."""
        self._session = None
