# Westerscheldetunnel (WST) Status Board - Home Assistant Integration

A Home Assistant custom component to monitor the status of the Westerscheldetunnel and Sluiskiltunnel in the Netherlands.

## Features

- **Real-time tunnel status** — Monitors all 8 road segments across both tunnels
- **Incident tracking** — Active and scheduled incidents with details
- **28 entities** — Comprehensive monitoring with status, severity, and binary sensors
- **Configurable polling** — Adjust the refresh interval from the UI
- **HACS compatible** — Install and update via the Home Assistant Community Store

## Installation

### HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository as a custom repository in HACS
3. Search for "Westerscheldetunnel" and install
4. Restart Home Assistant
5. Add the integration via **Settings → Devices & Services → Add Integration**

### Manual Installation

1. Copy the `custom_components/wst/` directory to your Home Assistant `custom_components/` directory
2. Restart Home Assistant
3. Add the integration via **Settings → Devices & Services → Add Integration**

## Configuration

This integration is configured entirely through the UI. No YAML configuration is needed.

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Westerscheldetunnel**
4. Confirm the setup (optionally adjust the polling interval)

### Options

| Option | Default | Min | Max | Description |
|--------|---------|-----|-----|-------------|
| Polling interval | 300s | 30s | 3600s | How often to poll the API for updates |

To change the polling interval, click **Configure** on the integration card.

## Devices & Entities

### Devices

| Device | Description |
|--------|-------------|
| **Westerscheldetunnel** | Main tunnel complex (6 road segments) |
| **Sluiskiltunnel** | Secondary tunnel (2 road segments) |
| **WST Status Board** | System-level sensors |

### Road Segment Entities (per segment × 8)

Each of the 8 road segments has:

| Entity | Type | Description |
|--------|------|-------------|
| `{segment} status` | `sensor` | Primary status: normal, closed, traffic-queues, etc. |
| `{segment} severity` | `sensor` | Severity level: none, low, medium, high, critical |
| `{segment} closed` | `binary_sensor` | ON when the segment is closed |

**Road Segments:**
- Toll square → Westerscheldetunnel (south)
- Westerscheldetunnel West tube (south)
- Westerscheldetunnel → Axelsche gat (south)
- Sluiskiltunnel south
- Westerscheldetunnel → Toll square (north)
- Westerscheldetunnel East tube (north)
- Axelsche gat → Westerscheldetunnel (north)
- Sluiskiltunnel north

### System Entities

| Entity | Type | Description |
|--------|------|-------------|
| Overall severity | `sensor` | Worst severity across all segments |
| Active incidents | `sensor` | Count of active incidents (titles & dates as attributes) |
| Scheduled incidents | `sensor` | Count of scheduled incidents (titles & dates as attributes) |
| Last updated | `sensor` | Timestamp of last API data refresh |
| Active incident | `binary_sensor` | ON when any active incident exists |

### Status Values

The status sensor can report the following states, in order of priority:

`closed` → `detour` → `two-way-traffic` → `single-lane` → `traffic-queues` → `metering-light` → `roadworks` → `maximum-width` → `speed-limit-30` → `speed-limit-50` → `speed-limit-70` → `speed-limit-80` → `fog-likely` → `slippery-road-surface` → `snow-or-ice` → `other` → `normal` (when no states are active)

## Requirements

- Home Assistant 2024.1.0 or later
- `wst_api_client` Python package (automatically installed)

## Credits

Data sourced from [WST Status Board API](https://api.wststatusboard.nl).

## License

MIT