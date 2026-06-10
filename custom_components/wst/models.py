"""Data transformation: API models -> internal WST models."""

from __future__ import annotations

from .const import get_device_for_road, get_road_slug
from .data import (
    WSTData,
    WSTDeviation,
    WSTIncident,
    WSTIncidentStatus,
    WSTRoad,
    WSTRoadStatus,
    WSTSituation,
    WSTTravelTime,
)


def _parse_deviation(data: dict) -> WSTDeviation:
    """Parse a deviation from API data."""
    return WSTDeviation(
        id=data.get("id", ""),
        code=data.get("code", ""),
        name=data.get("name", ""),
    )


def _parse_road(data: dict) -> WSTRoad:
    """Parse a road from API data."""
    return WSTRoad(
        id=data.get("id", ""),
        name=data.get("name", ""),
        direction=data.get("direction", ""),
    )


def _parse_road_status(data: dict) -> WSTRoadStatus:
    """Parse a road status from API data."""
    road_data = data.get("road", {}) or {}
    deviations_data = data.get("deviations", []) or []

    return WSTRoadStatus(
        id=data.get("id", ""),
        road=_parse_road(road_data),
        road_condition=data.get("roadCondition", "OPEN").lower(),
        deviations=[_parse_deviation(d) for d in deviations_data],
    )


def _parse_travel_time(data: dict | None) -> WSTTravelTime | None:
    """Parse travel time from API data."""
    if not data:
        return None
    return WSTTravelTime(
        id=data.get("id", ""),
        travel_time_option=data.get("travelTimeOption"),
        text=data.get("text"),
    )


def _parse_incident_status(data: dict) -> WSTIncidentStatus:
    """Parse an incident status from API data."""
    road_statuses_data = data.get("roadStatuses", []) or []

    phase_raw = data.get("phase", "")
    return WSTIncidentStatus(
        id=data.get("id", ""),
        name=data.get("name", ""),
        description=data.get("description"),
        phase=phase_raw.lower() if phase_raw else "",
        start_offset=data.get("startOffset", 0),
        road_statuses=[_parse_road_status(rs) for rs in road_statuses_data],
        additional_travel_time=_parse_travel_time(data.get("additionalTravelTime")),
        step=data.get("step"),
        activated_at=data.get("activatedAt"),
    )


def _parse_incident(data: dict) -> WSTIncident:
    """Parse an incident from API data."""
    statuses_data = data.get("statuses", []) or []

    phase_raw = data.get("phase", "")
    return WSTIncident(
        id=data.get("id", ""),
        name=data.get("name", ""),
        description=data.get("description"),
        phase=phase_raw.lower() if phase_raw else "",
        start_date=data.get("startDate"),
        end_date=data.get("endDate"),
        notify=bool(data.get("notify", False)),
        statuses=[_parse_incident_status(s) for s in statuses_data],
        scenario=data.get("scenario"),
        expired_at=data.get("expiredAt"),
    )


def from_api_situation(raw_situation: dict) -> WSTSituation:
    """Convert a raw API situation response into a WSTSituation model."""
    road_statuses_data = raw_situation.get("roadStatuses", []) or []

    return WSTSituation(
        condition=raw_situation.get("condition", "OPEN").lower(),
        road_statuses=[_parse_road_status(rs) for rs in road_statuses_data],
    )


def from_api_incidents(raw_response: dict) -> list[WSTIncident]:
    """Convert a raw API incidents response into a list of WSTIncident models."""
    items = raw_response.get("items", []) or []
    return [_parse_incident(item) for item in items]


def from_api_situation_dict(raw: dict) -> WSTSituation:
    """Convert a raw API situation dict into a WSTSituation model."""
    return from_api_situation(raw)


def from_api_incident_dict(raw: dict) -> WSTIncident:
    """Convert a raw API incident dict into a WSTIncident model."""
    return _parse_incident(raw)


def to_wst_data(
    situation_raw: dict,
    active_incidents_raw: dict,
    scheduled_incidents_raw: dict,
) -> WSTData:
    """Build WSTData from raw API responses."""
    situation = from_api_situation(situation_raw)
    active_incidents = from_api_incidents(active_incidents_raw)
    scheduled_incidents = from_api_incidents(scheduled_incidents_raw)

    return WSTData(
        situation=situation,
        active_incidents=active_incidents,
        scheduled_incidents=scheduled_incidents,
    )


def get_road_sensor_id(road_status: WSTRoadStatus, entry_id: str) -> str:
    """Generate stable unique ID for a road status sensor."""
    slug = get_road_slug(road_status.road.id, road_status.road.name)
    return f"{entry_id}_{slug}"


def get_device_key_for_road(road_name: str) -> str:
    """Get the device key for a road based on its name."""
    return get_device_for_road(road_name)