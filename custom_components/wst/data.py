"""Data types for the WST integration (new API format)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import WSTDataUpdateCoordinator


# Type alias for the WST config entry with runtime_data pointing to the coordinator
type WSTConfigEntry = ConfigEntry[WSTDataUpdateCoordinator]


@dataclass
class WSTDeviation:
    """Represents a deviation for a road."""

    id: str
    code: str
    name: str


@dataclass
class WSTRoad:
    """Represents a road with its metadata."""

    id: str
    name: str
    direction: str


@dataclass
class WSTRoadStatus:
    """Represents the status of a single road."""

    id: str
    road: WSTRoad
    road_condition: str
    deviations: list[WSTDeviation] = field(default_factory=list)


@dataclass
class WSTSituation:
    """Represents the overall tunnel situation."""

    condition: str
    road_statuses: list[WSTRoadStatus] = field(default_factory=list)


@dataclass
class WSTTravelTime:
    """Represents additional travel time information."""

    id: str
    travel_time_option: str | None
    text: str | None


@dataclass
class WSTIncidentStatus:
    """Represents a status within an incident."""

    id: str
    name: str
    description: str | None
    phase: str
    start_offset: int
    road_statuses: list[WSTRoadStatus] = field(default_factory=list)
    additional_travel_time: WSTTravelTime | None = None
    step: str | None = None
    activated_at: str | None = None


@dataclass
class WSTIncident:
    """Represents an incident (active or scheduled)."""

    id: str
    name: str
    description: str | None
    phase: str
    start_date: str | None = None
    end_date: str | None = None
    notify: bool = False
    statuses: list[WSTIncidentStatus] = field(default_factory=list)
    scenario: str | None = None
    expired_at: str | None = None


@dataclass
class WSTData:
    """Holds all data from the WST API coordinated update."""

    situation: WSTSituation
    active_incidents: list[WSTIncident] = field(default_factory=list)
    scheduled_incidents: list[WSTIncident] = field(default_factory=list)