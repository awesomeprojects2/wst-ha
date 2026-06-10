"""Sensor platform for the WST integration (new entity design)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import WSTDataUpdateCoordinator
from .data import WSTConfigEntry, WSTData, WSTRoadStatus
from .entity import WSTEntity
from .models import get_device_key_for_road, get_road_sensor_id


@dataclass(kw_only=True)
class WSTSystemSensorEntityDescription(SensorEntityDescription):
    """Describes a system-level sensor entity."""

    value_fn: Callable[[WSTData], StateType]
    attr_fn: Callable[[WSTData], dict[str, object]] | None = None


SYSTEM_SENSORS: tuple[WSTSystemSensorEntityDescription, ...] = (
    WSTSystemSensorEntityDescription(
        key="condition",
        icon="mdi:traffic-light",
        translation_key="condition",
        value_fn=lambda data: data.situation.condition.lower() if data else "open",
        attr_fn=None,
    ),
    WSTSystemSensorEntityDescription(
        key="active_incidents",
        icon="mdi:alert-decagram",
        translation_key="active_incidents",
        value_fn=lambda data: len(data.active_incidents) if data else 0,
        attr_fn=lambda data: {
            "incidents": [
                {"name": i.name, "description": i.description, "start_date": i.start_date}
                for i in data.active_incidents
            ] if data else [],
        },
    ),
    WSTSystemSensorEntityDescription(
        key="scheduled_incidents",
        icon="mdi:calendar-clock",
        translation_key="scheduled_incidents",
        value_fn=lambda data: len(data.scheduled_incidents) if data else 0,
        attr_fn=lambda data: {
            "incidents": [
                {"name": i.name, "description": i.description, "start_date": i.start_date, "end_date": i.end_date}
                for i in data.scheduled_incidents
            ] if data else [],
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WSTConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WST sensor entities from a config entry."""
    coordinator: WSTDataUpdateCoordinator = entry.runtime_data

    entities: list[WSTSensor] = []

    for description in SYSTEM_SENSORS:
        entities.append(WSTSystemSensor(coordinator, description))

    async_add_entities(entities)

    async def _async_update_road_sensors():
        """Add road condition sensors dynamically based on API data."""
        if coordinator.data is None:
            return

        new_entities: list[WSTSensor] = []
        existing_ids = coordinator._road_sensor_ids

        situation = coordinator.data.situation
        for road_status in situation.road_statuses:
            unique_id = get_road_sensor_id(road_status, entry.entry_id)
            if unique_id in existing_ids:
                continue

            description = WSTRoadSensorEntityDescription(
                key=unique_id,
                road_id=road_status.road.id,
                road_name=road_status.road.name,
                direction=road_status.road.direction,
                translation_key="road_condition",
                translation_placeholders={"road_name": road_status.road.name},
                value_fn=lambda rs: rs.road_condition.lower() if rs else "open",
            )
            coordinator._road_sensor_ids.add(unique_id)
            new_entities.append(WSTRoadSensor(coordinator, description))

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_update_road_sensors)

    if coordinator.data is not None:
        await _async_update_road_sensors()


class WSTSensor(WSTEntity, SensorEntity):
    """Base sensor for WST entities."""

    entity_description: SensorEntityDescription

    @property
    def available(self) -> bool:
        """Return True if coordinator data is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


@dataclass(kw_only=True)
class WSTRoadSensorEntityDescription(SensorEntityDescription):
    """Describes a road condition sensor entity."""

    road_id: str
    road_name: str
    direction: str
    value_fn: Callable[[WSTRoadStatus], StateType]


class WSTRoadSensor(WSTSensor):
    """Sensor for a road's condition (OPEN/CLOSED)."""

    entity_description: WSTRoadSensorEntityDescription

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        description: WSTRoadSensorEntityDescription,
    ) -> None:
        device_key = get_device_key_for_road(description.road_id, description.road_name)
        super().__init__(coordinator, device_key=device_key)
        self.entity_description = description
        self._attr_unique_id = description.key

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        road_status = self._get_road_status()
        if road_status is None:
            return None
        return self.entity_description.value_fn(road_status)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        road_status = self._get_road_status()
        if road_status is None:
            return {}

        attrs: dict[str, object] = {
            "direction": road_status.road.direction,
        }

        if road_status.deviations:
            deviation_info = []
            for d in road_status.deviations:
                deviation_info.append({"code": d.code, "name": d.name})
            attrs["deviation"] = deviation_info

        incident_desc = self._get_incident_description(road_status)
        if incident_desc:
            attrs["description"] = incident_desc

        travel_time = self._get_travel_time(road_status)
        if travel_time:
            attrs["extra_travel_time"] = travel_time

        return attrs

    def _get_road_status(self) -> WSTRoadStatus | None:
        """Get the road status data for this sensor."""
        if self.coordinator.data is None:
            return None

        for rs in self.coordinator.data.situation.road_statuses:
            if rs.road.id == self.entity_description.road_id:
                return rs
        return None

    def _get_incident_description(self, road_status: WSTRoadStatus) -> str | None:
        """Get description from active incidents affecting this road."""
        if self.coordinator.data is None:
            return None

        for incident in self.coordinator.data.active_incidents:
            for status in incident.statuses:
                for rs in status.road_statuses:
                    if rs.road.id == road_status.road.id:
                        if status.description:
                            return status.description
        return None

    def _get_travel_time(self, road_status: WSTRoadStatus) -> str | None:
        """Get extra travel time from active incidents affecting this road."""
        if self.coordinator.data is None:
            return None

        for incident in self.coordinator.data.active_incidents:
            for status in incident.statuses:
                for rs in status.road_statuses:
                    if rs.road.id == road_status.road.id:
                        if status.additional_travel_time and status.additional_travel_time.text:
                            return status.additional_travel_time.text
        return None


class WSTSystemSensor(WSTSensor):
    """Sensor for overall/system-level WST data."""

    entity_description: WSTSystemSensorEntityDescription

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        description: WSTSystemSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, device_key="wst_status_board")
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes for system sensors."""
        if self.coordinator.data is None:
            return {}

        attr_fn = self.entity_description.attr_fn
        if attr_fn:
            return attr_fn(self.coordinator.data)
        return {}