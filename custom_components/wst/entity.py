"""Base entity for the WST integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEVICE_INFO
from .coordinator import WSTDataUpdateCoordinator


class WSTEntity(CoordinatorEntity[WSTDataUpdateCoordinator]):
    """Base entity for WST integration."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WSTDataUpdateCoordinator,
        device_key: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._device_key = device_key or "wst_status_board"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the tunnel device this entity belongs to."""
        entry = self.coordinator.config_entry
        device_config = DEVICE_INFO[self._device_key]
        return DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{self._device_key}")},
            name=device_config["name"],
            model=device_config["model"],
            manufacturer=device_config["manufacturer"],
        )