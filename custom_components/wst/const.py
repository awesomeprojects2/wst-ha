"""Constants for the Westerscheldetunnel (WST) integration."""

DOMAIN = "wst"

CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
MIN_SCAN_INTERVAL = 300  # 5 minutes minimum to prevent API abuse
MAX_SCAN_INTERVAL = 3600  # 1 hour maximum

# API base URL (new API)
API_BASE_URL = "https://api.verkeer.westerscheldetunnel.nl"

# Road UUID to slug mapping for stable unique IDs
ROAD_ID_TO_SLUG: dict[str, str] = {
    "8ac445f0-bc74-4789-a994-5b3be105b5b3": "westbuis_zuid",
    "dcc1c0df-6461-468b-84e0-1124fb689477": "oostbuis_noord",
    "b6e3aeeb-42e3-43ba-8be1-0366fe51b1b8": "zuidbuis_zuid",
    "fc304bb7-3c57-4dd0-961f-0106f648156d": "noordbuis_noord",
    "4789380f-418c-4cf0-b947-8bb8b1717d8c": "tolplein_wst_zuid",
    "fc4086fe-acd0-403c-8fe4-07176937a355": "wst_tolplein_noord",
    "331646fc-ea99-48a8-aeee-5bbb6975ed6a": "sluiskil_wst_noord",
    "dab49083-3f4a-4f21-bef4-57243140ea66": "wst_sluiskil_zuid",
}

# Device identifiers and names
DEVICE_INFO: dict[str, dict[str, str]] = {
    "westerscheldetunnel": {
        "name": "Westerscheldetunnel",
        "model": "Westerscheldetunnel",
        "manufacturer": "WST Status Board",
    },
    "sluiskiltunnel": {
        "name": "Sluiskiltunnel",
        "model": "Sluiskiltunnel",
        "manufacturer": "WST Status Board",
    },
    "wst_status_board": {
        "name": "WST Status Board",
        "model": "Status Board",
        "manufacturer": "WST Status Board",
    },
}

# Known road condition values
CONDITION_OPEN = "open"
CONDITION_CLOSED = "closed"

# Known direction values (API uses UPPERCASE)
DIRECTION_NORTH = "NORTH"
DIRECTION_SOUTH = "SOUTH"

# Platforms
PLATFORMS = ["sensor", "binary_sensor"]

# Unique ID for config entry
ENTRY_UNIQUE_ID = "wst_status_board"


def get_road_slug(road_id: str, road_name: str) -> str:
    """Get a stable slug for a road based on UUID or name."""
    if road_id in ROAD_ID_TO_SLUG:
        return ROAD_ID_TO_SLUG[road_id]

    slug = road_name.lower().replace(" ", "_").replace("-", "_")
    if " richting " in slug:
        slug = slug.split(" richting ")[0]
    return slug


def get_device_for_road(road_name: str) -> str:
    """Determine which device a road belongs to based on road name."""
    if "Sluiskil" in road_name or "sluiskil" in road_name.lower():
        return "sluiskiltunnel"
    return "westerscheldetunnel"