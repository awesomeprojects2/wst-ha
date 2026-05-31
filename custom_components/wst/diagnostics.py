"""Diagnostics support for the WST integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .data import WSTData, WSTConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: WSTConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    data: WSTData | None = coordinator.data

    if data is None:
        return {"status": "no_data", "last_update_success": coordinator.last_update_success}

    return {
        "last_update_success": coordinator.last_update_success,
        "last_update_time": str(coordinator.last_update) if coordinator.last_update else None,
        "overall_severity": data.situation.overall_severity,
        "publish_date": data.situation.publish_date,
        "active_incidents_count": len(data.active_incidents),
        "scheduled_incidents_count": len(data.scheduled_incidents),
        "segments": {
            key: {
                "name": seg.name,
                "direction": seg.direction,
                "severity": seg.severity,
                "states": seg.states,
            }
            for key, seg in data.situation.segments.items()
        },
    }