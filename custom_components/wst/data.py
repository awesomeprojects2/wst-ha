"""Data types for the WST integration."""

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
class WSTRoadSegment:
    """Represents the status of a single road segment."""

    name: str
    direction: str
    severity: str
    states: list[str] = field(default_factory=list)
    additional_information: list[dict[str, str | bool]] = field(default_factory=list)


@dataclass
class WSTSituation:
    """Represents the overall tunnel situation."""

    segments: dict[str, WSTRoadSegment]
    overall_severity: str
    publish_date: str | None = None


@dataclass
class WSTIncident:
    """Represents an incident (active or scheduled)."""

    title: str
    start_date: str | None = None
    phase: str | None = None
    scheduled: bool = False
    published: bool = False
    road_names: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)


@dataclass
class WSTData:
    """Holds all data from the WST API coordinated update."""

    situation: WSTSituation
    active_incidents: list[WSTIncident] = field(default_factory=list)
    scheduled_incidents: list[WSTIncident] = field(default_factory=list)