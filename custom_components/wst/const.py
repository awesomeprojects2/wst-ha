"""Constants for the Westerscheldetunnel (WST) integration."""

DOMAIN = "wst"

CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
MIN_SCAN_INTERVAL = 30  # 30 seconds minimum to prevent API abuse
MAX_SCAN_INTERVAL = 3600  # 1 hour maximum

# API base URL
API_BASE_URL = "https://api.wststatusboard.nl"

# Road segment keys (matching API response keys)
ROAD_TOLL_SQUARE_TO_WST = "toll-square-to-westerscheldetunnel"
ROAD_WST_WEST = "westerscheldetunnel-west"
ROAD_WST_TO_AXELSCHE_GAT = "westerscheldetunnel-to-axelsche-gat"
ROAD_SLUISKIL_SOUTH = "sluiskiltunnel-south"
ROAD_WST_TO_TOLL_SQUARE = "westerscheldetunnel-to-toll-square"
ROAD_WST_EAST = "westerscheldetunnel-east"
ROAD_AXELSCHE_GAT_TO_WST = "axelsche-gat-to-westerscheldetunnel"
ROAD_SLUISKIL_NORTH = "sluiskiltunnel-north"

# All road segments
ALL_ROAD_SEGMENTS: list[str] = [
    ROAD_TOLL_SQUARE_TO_WST,
    ROAD_WST_WEST,
    ROAD_WST_TO_AXELSCHE_GAT,
    ROAD_SLUISKIL_SOUTH,
    ROAD_WST_TO_TOLL_SQUARE,
    ROAD_WST_EAST,
    ROAD_AXELSCHE_GAT_TO_WST,
    ROAD_SLUISKIL_NORTH,
]

# Segments belonging to Westerscheldetunnel device
WESTERSCHELDE_SEGMENTS: list[str] = [
    ROAD_TOLL_SQUARE_TO_WST,
    ROAD_WST_WEST,
    ROAD_WST_TO_AXELSCHE_GAT,
    ROAD_WST_TO_TOLL_SQUARE,
    ROAD_WST_EAST,
    ROAD_AXELSCHE_GAT_TO_WST,
]

# Segments belonging to Sluiskiltunnel device
SLUISKIL_SEGMENTS: list[str] = [
    ROAD_SLUISKIL_SOUTH,
    ROAD_SLUISKIL_NORTH,
]

# Map road segment key → device key
SEGMENT_TO_DEVICE: dict[str, str] = {
    **{s: "westerscheldetunnel" for s in WESTERSCHELDE_SEGMENTS},
    **{s: "sluiskiltunnel" for s in SLUISKIL_SEGMENTS},
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

# Known severity levels from the API
SEVERITY_NONE = "none"
SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"
SEVERITY_CRITICAL = "critical"

SEVERITY_LEVELS: list[str] = [
    SEVERITY_NONE,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
]

# Known state names from the API (used for status sensors and binary sensors)
STATE_CLOSED = "closed"
STATE_DETOUR = "detour"
STATE_TWO_WAY_TRAFFIC = "two-way-traffic"
STATE_SINGLE_LANE = "single-lane"
STATE_TRAFFIC_QUEUES = "traffic-queues"
STATE_METERING_LIGHT = "metering-light"
STATE_ROADWORKS = "roadworks"
STATE_MAXIMUM_WIDTH = "maximum-width"
STATE_MAXIMUM_WIDTH_300 = "maximum-width-300"
STATE_MAXIMUM_WIDTH_200 = "maximum-width-200"
STATE_SPEED_LIMIT_30 = "speed-limit-30"
STATE_SPEED_LIMIT_50 = "speed-limit-50"
STATE_SPEED_LIMIT_70 = "speed-limit-70"
STATE_SPEED_LIMIT_80 = "speed-limit-80"
STATE_FOG_LIKELY = "fog-likely"
STATE_SLIPPERY_ROAD = "slippery-road-surface"
STATE_SNOW_OR_ICE = "snow-or-ice"
STATE_OTHER = "other"

# State priority: higher index = lower concern. First match when iterating = most concerning.
STATE_PRIORITY: list[str] = [
    STATE_CLOSED,
    STATE_DETOUR,
    STATE_TWO_WAY_TRAFFIC,
    STATE_SINGLE_LANE,
    STATE_TRAFFIC_QUEUES,
    STATE_METERING_LIGHT,
    STATE_ROADWORKS,
    STATE_MAXIMUM_WIDTH,
    STATE_MAXIMUM_WIDTH_300,
    STATE_MAXIMUM_WIDTH_200,
    STATE_SPEED_LIMIT_30,
    STATE_SPEED_LIMIT_50,
    STATE_SPEED_LIMIT_70,
    STATE_SPEED_LIMIT_80,
    STATE_FOG_LIKELY,
    STATE_SLIPPERY_ROAD,
    STATE_SNOW_OR_ICE,
    STATE_OTHER,
]

# Default status when no states are active
STATE_NORMAL = "normal"

# Known direction values
DIRECTION_NORTH = "north"
DIRECTION_SOUTH = "south"

# Incident phases
PHASE_ACTIVE = "active"
PHASE_EXPIRED = "expired"

# Platforms
PLATFORMS = ["sensor", "binary_sensor"]

# Unique ID for config entry
ENTRY_UNIQUE_ID = "wst_status_board"