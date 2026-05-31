"""Data transformation: API models → internal WST models.

Translates the openapi-generator client models into stable internal dataclasses,
decoupling HA entities from API client version changes.
"""

from __future__ import annotations

from .const import STATE_PRIORITY, STATE_NORMAL
from .data import WSTRoadSegment, WSTSituation, WSTIncident


def _get_primary_state(states: list[dict[str, str]]) -> str:
    """Return the most concerning state from a list of state dicts, or STATE_NORMAL if empty.

    States are prioritized by STATE_PRIORITY order - first match wins.
    """
    if not states:
        return STATE_NORMAL

    state_names = {s.get("name", "") for s in states if isinstance(s, dict)}

    for priority_state in STATE_PRIORITY:
        if priority_state in state_names:
            return priority_state

    # Fallback: return first state name if no known priority matches
    for s in states:
        name = s.get("name", "")
        if name:
            return name

    return STATE_NORMAL


def _extract_additional_info(additional_info: list | None) -> list[dict[str, str | bool]]:
    """Extract additional information from API response, normalizing to internal format."""
    if not additional_info:
        return []

    result = []
    for info in additional_info:
        if not isinstance(info, dict):
            continue
        entry: dict[str, str | bool] = {
            "direction": info.get("direction", ""),
            "notify": bool(info.get("notify", False)),
        }
        if "description" in info:
            entry["description"] = str(info["description"])
        result.append(entry)
    return result


def from_api_situation(raw_situation: object) -> WSTSituation:
    """Convert a raw API situation response into a WSTSituation model.

    The raw_situation parameter can be:
    - A generated client model object (with .status, .severity, .publish_date attributes)
    - A dict from the API response
    """
    if isinstance(raw_situation, dict):
        data = raw_situation
    else:
        try:
            data = raw_situation.to_dict()
        except AttributeError:
            data = vars(raw_situation)

    status_data = data.get("status", {})
    if status_data is None:
        status_data = {}

    segments: dict[str, WSTRoadSegment] = {}
    for segment_key, segment_value in status_data.items():
        if segment_value is None:
            continue

        if isinstance(segment_value, dict):
            seg_dict = segment_value
        else:
            try:
                seg_dict = segment_value.to_dict()
            except AttributeError:
                seg_dict = vars(segment_value)

        raw_states = seg_dict.get("states", []) or []
        if isinstance(raw_states, (list, tuple)):
            states_list = [s if isinstance(s, dict) else (s.to_dict() if hasattr(s, "to_dict") else vars(s)) for s in raw_states]
        else:
            states_list = []

        state_names = [s.get("name", "") if isinstance(s, dict) else getattr(s, "name", "") for s in states_list if s]

        raw_additional = seg_dict.get("additionalInformation", seg_dict.get("additional_information", [])) or []

        segments[segment_key] = WSTRoadSegment(
            name=seg_dict.get("name", segment_key),
            direction=seg_dict.get("direction", ""),
            severity=seg_dict.get("severity", "none"),
            states=state_names,
            additional_information=_extract_additional_info(raw_additional),
        )

    return WSTSituation(
        segments=segments,
        overall_severity=data.get("severity", "none"),
        publish_date=data.get("publishDate"),
    )


def from_api_incident(raw_incident: object) -> WSTIncident:
    """Convert a raw API incident response into a WSTIncident model.

    The raw_incident parameter can be:
    - A generated client model object
    - A dict from the API response
    """
    if isinstance(raw_incident, dict):
        data = raw_incident
    else:
        try:
            data = raw_incident.to_dict()
        except AttributeError:
            data = vars(raw_incident)

    road_names: list[str] = []
    descriptions: list[str] = []

    statuses = data.get("statuses", []) or []
    for status in statuses:
        if not isinstance(status, dict):
            try:
                status = status.to_dict()
            except AttributeError:
                status = vars(status)

        for road_status in (status.get("roadStatuses", []) or []):
            if not isinstance(road_status, dict):
                try:
                    road_status = road_status.to_dict()
                except AttributeError:
                    road_status = vars(road_status)
            road = road_status.get("road", {}) or {}
            if not isinstance(road, dict):
                try:
                    road = road.to_dict()
                except AttributeError:
                    road = vars(road)
            road_name = road.get("name", "")
            if road_name and road_name not in road_names:
                road_names.append(road_name)

        for additional_info in (status.get("additionalInformation", status.get("additional_information", [])) or []):
            if not isinstance(additional_info, dict):
                try:
                    additional_info = additional_info.to_dict()
                except AttributeError:
                    additional_info = vars(additional_info)
            desc = additional_info.get("description", "")
            if desc and desc not in descriptions:
                descriptions.append(desc)

    return WSTIncident(
        title=data.get("title", ""),
        start_date=data.get("startDate"),
        phase=data.get("phase"),
        scheduled=bool(data.get("scheduled", False)),
        published=bool(data.get("published", False)),
        road_names=road_names,
        descriptions=descriptions,
    )