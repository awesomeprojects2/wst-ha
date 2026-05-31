"""API client wrapper for the WST Status Board API.

Wraps the generated wst_api_client package with async methods
suitable for use within Home Assistant's event loop.
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


class WSTApiClient:
    """Async wrapper around the wst_api_client for Home Assistant.

    The generated openapi-client is synchronous (urllib3-based),
    so all calls are dispatched via hass.async_add_executor_job.
    """

    def __init__(self, hass: HomeAssistant, base_url: str = API_BASE_URL) -> None:
        self._hass = hass
        self._base_url = base_url
        self._api_client = None
        self._api_instance = None

    def _ensure_client(self) -> None:
        """ lazily initialize the generated API client and instance."""
        if self._api_client is not None:
            return

        try:
            from wst_api_client import ApiClient, Configuration
            from wst_api_client.api.default_api import DefaultApi
        except ImportError as err:
            raise WSTApiError(
                "wst_api_client package is not installed. "
                "Install it with: pip install wst_api_client"
            ) from err

        configuration = Configuration(host=self._base_url)
        self._api_client = ApiClient(configuration=configuration)
        self._api_instance = DefaultApi(self._api_client)

    async def async_get_situation(self) -> dict:
        """Fetch the current tunnel situation from the API."""
        return await self._async_call_api("get_situation")

    async def async_get_active_incidents(self) -> list:
        """Fetch active incidents from the API."""
        return await self._async_call_api("get_incident_active")

    async def async_get_scheduled_incidents(self) -> list:
        """Fetch scheduled incidents from the API."""
        return await self._async_call_api("get_incident_scheduled")

    async def _async_call_api(self, method_name: str) -> object:
        """Call a synchronous API method via executor job and return raw response data."""
        self._ensure_client()

        method = getattr(self._api_instance, method_name, None)
        if method is None:
            raise WSTApiError(f"API method '{method_name}' not found in wst_api_client")

        try:
            result = await self._hass.async_add_executor_job(method)
        except aiohttp.ClientError as err:
            raise WSTApiCommunicationError(
                f"Communication error calling {method_name}: {err}"
            ) from err
        except TimeoutError as err:
            raise WSTApiTimeoutError(
                f"Timeout calling {method_name}: {err}"
            ) from err
        except Exception as err:
            error_msg = str(err).lower()
            if "unauthorized" in error_msg or "forbidden" in error_msg or "401" in error_msg or "403" in error_msg:
                raise WSTApiAuthError(f"Auth error calling {method_name}: {err}") from err
            raise WSTApiError(f"Error calling {method_name}: {err}") from err

        if result is None:
            raise WSTApiCommunicationError(f"API returned None for {method_name}")

        # Convert generated model to dict for stable processing
        if hasattr(result, "to_dict"):
            return result.to_dict()
        if isinstance(result, list):
            return [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        return result

    async def async_validate_connection(self) -> bool:
        """Test the API connection by fetching the situation endpoint."""
        try:
            await self.async_get_situation()
            return True
        except WSTApiError:
            return False

    async def async_close(self) -> None:
        """Close the API client and release resources."""
        if self._api_client is not None:
            try:
                await self._hass.async_add_executor_job(self._api_client.close)
            except Exception:
                _LOGGER.debug("Error closing API client", exc_info=True)
            self._api_client = None
            self._api_instance = None