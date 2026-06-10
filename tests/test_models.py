"""Test models data transformation (new API format)."""

from custom_components.wst.models import (
    from_api_situation,
    from_api_incidents,
    to_wst_data,
    get_road_slug,
    get_device_key_for_road,
)
from custom_components.wst.const import CONDITION_OPEN, CONDITION_CLOSED


def test_from_api_situation():
    """Test parsing a situation response."""
    data = {
        "condition": "OPEN",
        "roadStatuses": [
            {
                "id": "status-1",
                "road": {
                    "id": "8ac445f0-bc74-4789-a994-5b3be105b5b3",
                    "name": "Westbuis richting Zuid",
                    "direction": "SOUTH"
                },
                "roadCondition": "OPEN",
                "deviations": []
            },
            {
                "id": "status-2",
                "road": {
                    "id": "b6e3aeeb-42e3-43ba-8be1-0366fe51b1b8",
                    "name": "Zuidbuis richting Zuid",
                    "direction": "SOUTH"
                },
                "roadCondition": "CLOSED",
                "deviations": [
                    {"id": "dev-1", "code": "U65", "name": "Richting Oostburg/Borssele"}
                ]
            }
        ]
    }

    result = from_api_situation(data)

    assert result.condition == CONDITION_OPEN
    assert len(result.road_statuses) == 2

    assert result.road_statuses[0].road_condition == CONDITION_OPEN
    assert result.road_statuses[0].road.name == "Westbuis richting Zuid"
    assert result.road_statuses[0].road.direction == "SOUTH"

    assert result.road_statuses[1].road_condition == CONDITION_CLOSED
    assert len(result.road_statuses[1].deviations) == 1
    assert result.road_statuses[1].deviations[0].code == "U65"


def test_from_api_incidents():
    """Test parsing incidents response."""
    data = {
        "items": [
            {
                "id": "incident-1",
                "name": "Test incident",
                "description": "Test description",
                "phase": "ACTIVE",
                "startDate": "2026-06-10T17:00:00+00:00",
                "endDate": "2026-06-11T03:00:00+00:00",
                "notify": True,
                "statuses": [
                    {
                        "id": "status-1",
                        "name": "Afgesloten",
                        "description": "Road is closed",
                        "phase": "ACTIVE",
                        "startOffset": 0,
                        "roadStatuses": [
                            {
                                "id": "rs-1",
                                "road": {
                                    "id": "fc304bb7-3c57-4dd0-961f-0106f648156d",
                                    "name": "Noordbuis richting Westerscheldetunnel",
                                    "direction": "NORTH"
                                },
                                "roadCondition": "CLOSED",
                                "deviations": []
                            }
                        ],
                        "additionalTravelTime": {
                            "id": "tt-1",
                            "travelTimeOption": None,
                            "text": "Enkele minuten"
                        },
                        "step": None,
                        "activatedAt": "2026-06-10T17:00:02+00:00"
                    }
                ],
                "scenario": None,
                "expiredAt": None
            }
        ]
    }

    result = from_api_incidents(data)

    assert len(result) == 1
    incident = result[0]
    assert incident.id == "incident-1"
    assert incident.name == "Test incident"
    assert incident.phase == "active"
    assert incident.notify is True
    assert len(incident.statuses) == 1

    status = incident.statuses[0]
    assert status.name == "Afgesloten"
    assert status.road_statuses[0].road_condition == CONDITION_CLOSED
    assert status.additional_travel_time.text == "Enkele minuten"


def test_to_wst_data():
    """Test building WSTData from raw API responses."""
    situation = {
        "condition": "OPEN",
        "roadStatuses": []
    }
    active_incidents = {"items": []}
    scheduled_incidents = {"items": []}

    result = to_wst_data(situation, active_incidents, scheduled_incidents)

    assert result.situation.condition == CONDITION_OPEN
    assert len(result.active_incidents) == 0
    assert len(result.scheduled_incidents) == 0


def test_road_id_to_slug():
    """Test road ID to slug mapping."""
    assert get_road_slug("8ac445f0-bc74-4789-a994-5b3be105b5b3", "Westbuis") == "westbuis_zuid"
    assert get_road_slug("unknown-id", "Some Road Name") == "some_road_name"


def test_device_key_for_road():
    """Test device key determination based on road UUID."""
    assert get_device_key_for_road("8ac445f0-bc74-4789-a994-5b3be105b5b3") == "westerscheldetunnel"
    assert get_device_key_for_road("dcc1c0df-6461-468b-84e0-1124fb689477") == "westerscheldetunnel"
    assert get_device_key_for_road("fc304bb7-3c57-4dd0-961f-0106f648156d") == "sluiskiltunnel"
    assert get_device_key_for_road("b6e3aeeb-42e3-43ba-8be1-0366fe51b1b8") == "sluiskiltunnel"
    assert get_device_key_for_road("4789380f-418c-4cf0-b947-8bb8b1717d8c") == "roads"
    assert get_device_key_for_road("fc4086fe-acd0-403c-8fe4-07176937a355") == "roads"
    assert get_device_key_for_road("331646fc-ea99-48a8-aeee-5bbb6975ed6a") == "roads"
    assert get_device_key_for_road("dab49083-3f4a-4f21-bef4-57243140ea66") == "roads"
    assert get_device_key_for_road("unknown-id", "Sluiskil road") == "sluiskiltunnel"
    assert get_device_key_for_road("unknown-id", "Some other road") == "westerscheldetunnel"