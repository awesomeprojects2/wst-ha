"""Test models data transformation."""

from custom_components.wst.models import (
    _extract_additional_info,
    _get_primary_state,
    from_api_incident,
    from_api_situation,
)
from custom_components.wst.const import STATE_CLOSED, STATE_NORMAL, STATE_TRAFFIC_QUEUES


def test_get_primary_state_empty():
    assert _get_primary_state([]) == STATE_NORMAL


def test_get_primary_state_single():
    states = [{"name": "traffic-queues", "severity": "medium"}]
    assert _get_primary_state(states) == STATE_TRAFFIC_QUEUES


def test_get_primary_state_priority():
    states = [
        {"name": "other", "severity": "medium"},
        {"name": "closed", "severity": "high"},
    ]
    assert _get_primary_state(states) == STATE_CLOSED


def test_get_primary_state_unknown_state():
    states = [{"name": "unknown-state", "severity": "low"}]
    assert _get_primary_state(states) == "unknown-state"


def test_extract_additional_info_empty():
    assert _extract_additional_info(None) == []
    assert _extract_additional_info([]) == []


def test_extract_additional_info_with_data():
    info = [
        {"direction": "north", "description": "Traffic delays.", "notify": True},
        {"direction": "south", "notify": False},
    ]
    result = _extract_additional_info(info)
    assert len(result) == 2
    assert result[0]["direction"] == "north"
    assert result[0]["description"] == "Traffic delays."
    assert result[0]["notify"] is True
    assert result[1]["direction"] == "south"
    assert result[1]["notify"] is False


def test_from_api_situation_dict():
    data = {
        "status": {
            "westerscheldetunnel-east": {
                "direction": "north",
                "name": "westerscheldetunnel-east",
                "severity": "medium",
                "states": [{"name": "traffic-queues", "severity": "medium", "priority": 0}],
                "additionalInformation": [{"direction": "north", "description": "Queues.", "notify": True}],
            }
        },
        "severity": "medium",
        "publishDate": "2022-10-01T18:56:28+00:00",
    }
    result = from_api_situation(data)
    assert result.overall_severity == "medium"
    assert result.publish_date == "2022-10-01T18:56:28+00:00"
    assert "westerscheldetunnel-east" in result.segments
    seg = result.segments["westerscheldetunnel-east"]
    assert seg.direction == "north"
    assert seg.severity == "medium"
    assert "traffic-queues" in seg.states


def test_from_api_situation_empty_status():
    data = {"status": None, "severity": "none", "publishDate": None}
    result = from_api_situation(data)
    assert result.overall_severity == "none"
    assert len(result.segments) == 0


def test_from_api_incident_dict():
    data = {
        "title": "Traffic incident",
        "startDate": "2022-10-06T14:47:46+00:00",
        "phase": "active",
        "scheduled": False,
        "published": True,
        "statuses": [
            {
                "roadStatuses": [
                    {
                        "road": {"name": "westerscheldetunnel-east", "direction": "north"},
                        "states": [{"name": "traffic-queues", "severity": "medium"}],
                    }
                ],
                "phase": "active",
                "additionalInformation": [
                    {"direction": "north", "description": "Heavy traffic.", "notify": True}
                ],
            }
        ],
    }
    result = from_api_incident(data)
    assert result.title == "Traffic incident"
    assert result.phase == "active"
    assert result.scheduled is False
    assert "westerscheldetunnel-east" in result.road_names
    assert "Heavy traffic." in result.descriptions