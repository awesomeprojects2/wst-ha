"""Binary sensor platform for the WST integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONDITION_OPEN, DOMAIN
from .coordinator import WSTDataUpdateCoordinator
from .data import WSTConfigEntry, WSTData
from .entity import WSTEntity


@dataclass(kw_only=True)
class WSTBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a binary sensor entity."""

    is_on_fn: callable


DISRUPTION_SENSOR = WSTBinarySensorEntityDescription(
    key="disrupted",
    device_class="problem",
    translation_key="disrupted",
    is_on_fn=lambda data: data.situation.condition != CONDITION_OPEN if data else False,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WSTConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WST binary sensor entities from a config entry."""
    coordinator: WSTDataUpdateCoordinator = entry.runtime_data

    entities: list[WSTBinarySensor] = [WSTDisruptionBinarySensor(coordinator, DISRUPTION_SENSOR)]

    async_add_entities(entities)


class WSTBinarySensor(WSTEntity, BinarySensorEntity):
    """Base binary sensor for WST entities."""

    entity_description: WSTBinarySensorEntityDescription

    @property
    def available(self) -> bool:
        """Return True if coordinator data is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None


class WSTDisruptionBinarySensor(WSTBinarySensor):
    """Binary sensor for tunnel disruption status."""

    entity_description: WSTBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        description: WSTBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, device_key="wst_status_board")
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return True if tunnel is disrupted (not OPEN)."""
        if self.coordinator.data is None:
            return False
        return self.entity_description.is_on_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}

        data = self.coordinator.data
        condition = data.situation.condition

        attrs: dict[str, object] = {
            "condition": condition,
        }

        if data.active_incidents:
            incident_names = [i.name for i in data.active_incidents]
            attrs["active_incidents"] = incident_names

        return attrs