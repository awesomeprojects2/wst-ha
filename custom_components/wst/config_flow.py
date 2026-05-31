"""Config flow for the WST integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, ENTRY_UNIQUE_ID, MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL
from .api import WSTApiClient


class WSTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WST Status Board."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            scan_interval = max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, scan_interval))

            try:
                api = WSTApiClient(self.hass)
                valid = await api.async_validate_connection()
                if not valid:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(ENTRY_UNIQUE_ID)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="Westerscheldetunnel",
                        data={},
                        options={CONF_SCAN_INTERVAL: scan_interval},
                    )
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    step=30,
                    unit_of_measurement="s",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> WSTOptionsFlow:
        """Return the options flow handler."""
        return WSTOptionsFlow()


class WSTOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for WST (changing scan interval)."""

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            scan_interval = max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)))
            return self.async_create_entry(title="", data={CONF_SCAN_INTERVAL: scan_interval})

        current_interval = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        data_schema = vol.Schema({
            vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    step=30,
                    unit_of_measurement="s",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)