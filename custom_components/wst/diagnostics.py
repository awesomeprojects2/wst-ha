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
        "condition": data.situation.condition,
        "road_statuses": [
            {
                "id": rs.road.id,
                "name": rs.road.name,
                "direction": rs.road.direction,
                "road_condition": rs.road_condition,
                "deviations": [{"code": d.code, "name": d.name} for d in rs.deviations],
            }
            for rs in data.situation.road_statuses
        ],
        "active_incidents_count": len(data.active_incidents),
        "active_incidents": [
            {
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "phase": i.phase,
                "start_date": i.start_date,
                "end_date": i.end_date,
            }
            for i in data.active_incidents
        ],
        "scheduled_incidents_count": len(data.scheduled_incidents),
        "scheduled_incidents": [
            {
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "phase": i.phase,
                "start_date": i.start_date,
                "end_date": i.end_date,
            }
            for i in data.scheduled_incidents
        ],
    }