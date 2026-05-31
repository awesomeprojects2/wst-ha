"""Binary sensor platform for the WST integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ALL_ROAD_SEGMENTS, DOMAIN, STATE_CLOSED
from .coordinator import WSTDataUpdateCoordinator
from .data import WSTConfigEntry, WSTRoadSegment
from .entity import WSTEntity


@dataclass(kw_only=True)
class WSTRoadSegmentBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a road segment binary sensor."""

    road_key: str
    is_on_fn: callable


ROAD_SEGMENT_CLOSED_SENSORS: tuple[WSTRoadSegmentBinarySensorEntityDescription, ...] = tuple(
    WSTRoadSegmentBinarySensorEntityDescription(
        key=f"{road_key}_closed",
        road_key=road_key,
        device_class="safety",
        translation_key="segment_closed",
        translation_placeholders={"road_name": road_key.replace("-", " ").title()},
        is_on_fn=lambda segment: STATE_CLOSED in segment.states if segment else False,
    )
    for road_key in ALL_ROAD_SEGMENTS
)

ACTIVE_INCIDENT_BINARY_SENSOR = WSTRoadSegmentBinarySensorEntityDescription(
    key="active_incident",
    road_key=None,
    device_class="safety",
    icon="mdi:alert-decagram",
    translation_key="active_incident",
    is_on_fn=None,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WSTConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WST binary sensor entities from a config entry."""
    coordinator: WSTDataUpdateCoordinator = entry.runtime_data

    entities: list[WSTRoadSegmentBinarySensor | WSTActiveIncidentBinarySensor] = []

    for description in ROAD_SEGMENT_CLOSED_SENSORS:
        entities.append(WSTRoadSegmentBinarySensor(coordinator, description))

    entities.append(WSTActiveIncidentBinarySensor(coordinator, ACTIVE_INCIDENT_BINARY_SENSOR))

    async_add_entities(entities)


class WSTRoadSegmentBinarySensor(WSTEntity, BinarySensorEntity):
    """Binary sensor for road segment closed state."""

    entity_description: WSTRoadSegmentBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        description: WSTRoadSegmentBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, road_key=description.road_key)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return True if the road segment is closed."""
        segment = self._get_segment()
        if segment is None:
            return False
        return self.entity_description.is_on_fn(segment)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        segment = self._get_segment()
        if segment is None:
            return {}
        return {"states": segment.states}

    def _get_segment(self) -> WSTRoadSegment | None:
        """Get the road segment data for this binary sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.situation.segments.get(self.entity_description.road_key)


class WSTActiveIncidentBinarySensor(WSTEntity, BinarySensorEntity):
    """Binary sensor for whether there are active incidents."""

    entity_description: WSTRoadSegmentBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        description: WSTRoadSegmentBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, device_key="wst_status_board")
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return True if there are active incidents."""
        if self.coordinator.data is None:
            return False
        return len(self.coordinator.data.active_incidents) > 0

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}
        return {
            "incident_titles": [i.title for i in self.coordinator.data.active_incidents],
        }