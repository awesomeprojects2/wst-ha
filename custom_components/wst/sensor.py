"""Sensor platform for the WST integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    ALL_ROAD_SEGMENTS,
    DOMAIN,
    SEGMENT_TO_DEVICE,
    STATE_CLOSED,
    STATE_NORMAL,
)
from .coordinator import WSTDataUpdateCoordinator
from .data import WSTConfigEntry, WSTData, WSTRoadSegment
from .entity import WSTEntity
from .models import _get_primary_state


@dataclass(kw_only=True)
class WSTRoadSegmentSensorEntityDescription(SensorEntityDescription):
    """Describes a road segment sensor entity."""

    road_key: str
    value_fn: Callable[[WSTRoadSegment], StateType]


@dataclass(kw_only=True)
class WSTOverallSensorEntityDescription(SensorEntityDescription):
    """Describes an overall/system sensor entity."""

    value_fn: Callable[[WSTData], StateType | datetime]


ROAD_SEGMENT_STATUS_SENSORS: tuple[WSTRoadSegmentSensorEntityDescription, ...] = tuple(
    WSTRoadSegmentSensorEntityDescription(
        key=f"{road_key}_status",
        road_key=road_key,
        icon="mdi:road-variant",
        translation_key="segment_status",
        translation_placeholders={"road_name": road_key.replace("-", " ").title()},
        value_fn=lambda segment: _get_primary_state(segment.states) if segment else STATE_NORMAL,
    )
    for road_key in ALL_ROAD_SEGMENTS
)

ROAD_SEGMENT_SEVERITY_SENSORS: tuple[WSTRoadSegmentSensorEntityDescription, ...] = tuple(
    WSTRoadSegmentSensorEntityDescription(
        key=f"{road_key}_severity",
        road_key=road_key,
        icon="mdi:alert-circle-outline",
        translation_key="segment_severity",
        translation_placeholders={"road_name": road_key.replace("-", " ").title()},
        value_fn=lambda segment: segment.severity if segment else "none",
    )
    for road_key in ALL_ROAD_SEGMENTS
)

OVERALL_SENSORS: tuple[WSTOverallSensorEntityDescription, ...] = (
    WSTOverallSensorEntityDescription(
        key="overall_severity",
        icon="mdi:alert",
        translation_key="overall_severity",
        value_fn=lambda data: data.situation.overall_severity,
    ),
    WSTOverallSensorEntityDescription(
        key="active_incidents",
        icon="mdi:alert-decagram",
        translation_key="active_incidents",
        value_fn=lambda data: len(data.active_incidents),
    ),
    WSTOverallSensorEntityDescription(
        key="scheduled_incidents",
        icon="mdi:calendar-clock",
        translation_key="scheduled_incidents",
        value_fn=lambda data: len(data.scheduled_incidents),
    ),
    WSTOverallSensorEntityDescription(
        key="last_updated",
        icon="mdi:clock-outline",
        device_class="timestamp",
        translation_key="last_updated",
        value_fn=lambda data: data.situation.publish_date,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WSTConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WST sensor entities from a config entry."""
    coordinator: WSTDataUpdateCoordinator = entry.runtime_data

    entities: list[WSTRoadSegmentSensor | WSTOverallSensor] = []

    for description in ROAD_SEGMENT_STATUS_SENSORS:
        entities.append(WSTRoadSegmentSensor(coordinator, description))

    for description in ROAD_SEGMENT_SEVERITY_SENSORS:
        entities.append(WSTRoadSegmentSensor(coordinator, description))

    for description in OVERALL_SENSORS:
        entities.append(WSTOverallSensor(coordinator, description))

    async_add_entities(entities)


class WSTRoadSegmentSensor(WSTEntity, SensorEntity):
    """Sensor for a road segment's status or severity."""

    entity_description: WSTRoadSegmentSensorEntityDescription

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        description: WSTRoadSegmentSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, road_key=description.road_key)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        segment = self._get_segment()
        if segment is None:
            return None
        return self.entity_description.value_fn(segment)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes for road segment sensors."""
        segment = self._get_segment()
        if segment is None:
            return {}

        attrs: dict[str, object] = {
            "direction": segment.direction,
        }

        if self.entity_description.key.endswith("_status"):
            attrs["severity"] = segment.severity
            attrs["states"] = segment.states
            attrs["additional_information"] = [
                {k: v for k, v in info.items() if k != "notify"}
                for info in segment.additional_information
            ]

        return attrs

    def _get_segment(self) -> WSTRoadSegment | None:
        """Get the road segment data for this sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.situation.segments.get(self.entity_description.road_key)


class WSTOverallSensor(WSTEntity, SensorEntity):
    """Sensor for overall/system-level WST data."""

    entity_description: WSTOverallSensorEntityDescription

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        description: WSTOverallSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, device_key="wst_status_board")
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> StateType | datetime:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes for overall sensors."""
        data = self.coordinator.data
        if data is None:
            return {}

        key = self.entity_description.key

        if key == "active_incidents":
            return {
                "incident_titles": [i.title for i in data.active_incidents],
                "incident_start_dates": [i.start_date for i in data.active_incidents if i.start_date],
            }

        if key == "scheduled_incidents":
            return {
                "incident_titles": [i.title for i in data.scheduled_incidents],
                "incident_start_dates": [i.start_date for i in data.scheduled_incidents if i.start_date],
            }

        return {}