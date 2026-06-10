# Westerscheldetunnel (WST) — Home Assistant Integration

A Home Assistant custom component to monitor the status of the Westerscheldetunnel and Sluiskiltunnel in the Netherlands.

## Features

- **Road condition per segment** — Each road has a single sensor showing its condition (`open` / `closed`) with rich attributes (deviation info, incident description, extra travel time)
- **Incident tracking** — Active and scheduled incidents with name, description, and date attributes
- **Disruption alert** — Binary sensor that turns on when the tunnel condition is anything other than `open`
- **12 entities total** (down from 28) — simpler and more informative
- **5-minute minimum poll interval** — prevents API abuse
- **Configurable polling** — adjust the refresh interval from the UI
- **HACS compatible** — install and update via the Home Assistant Community Store

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

Configured entirely through the UI — no YAML needed.

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Westerscheldetunnel**
4. Confirm the setup (optionally adjust the polling interval)

### Options

| Option | Default | Min | Max | Description |
|--------|---------|-----|-----|-------------|
| Polling interval | 300 s | 300 s | 3600 s | How often to poll the API for updates |

To change the polling interval, click **Configure** on the integration card.

## Devices & Entities

### Devices

| Device | Description |
|--------|-------------|
| **Westerscheldetunnel** | Main tunnel complex (6 road segments) |
| **Sluiskiltunnel** | Secondary tunnel (2 road segments) |
| **WST Status Board** | System-level sensors |

### Road Condition Sensors (8 — dynamic, 1 per road)

Each road segment gets a single sensor showing its current condition.

| Entity | Type | State | Attributes |
|--------|------|-------|------------|
| `{road_name} condition` | `sensor` | `open` or `closed` | `direction`, `deviation` (list of `{code, name}`), `description` (incident text), `extra_travel_time` |

**Westerscheldetunnel** (6 road segments):

| API Name | Tube | Direction |
|----------|------|-----------|
| Westbuis richting Zuid | West tube | SOUTH |
| Oostbuis richting Noord | East tube | NORTH |
| Zuidbuis richting Zuid | South tube | SOUTH |
| Noordbuis richting Westerscheldetunnel | North tube | NORTH |
| Tolplein WST richting Zuid | Toll plaza | SOUTH |
| WST Tolplein richting Noord | Toll plaza | NORTH |

**Sluiskiltunnel** (2 road segments):

| API Name | Direction |
|----------|-----------|
| Sluiskil WST richting Noord | NORTH |
| WST Sluiskil richting Zuid | SOUTH |

Sensors are created dynamically based on what the API returns, so new road segments appear automatically.

### System Sensors (3)

| Entity | Type | State | Attributes |
|--------|------|-------|------------|
| Tunnel condition | `sensor` | `open` / `closed` — overall tunnel condition | — |
| Active incidents | `sensor` | Count of active incidents | `incidents` — list of `{name, description, start_date}` |
| Scheduled incidents | `sensor` | Count of scheduled incidents | `incidents` — list of `{name, description, start_date, end_date}` |

### Binary Sensor (1)

| Entity | Type | State | Attributes |
|--------|------|-------|------------|
| Tunnel disrupted | `binary_sensor` | `ON` when condition ≠ `open` | `condition`, `active_incidents` (list of names) |

### Condition Values

The overall tunnel condition and road conditions use two states:

| Value | Meaning |
|-------|---------|
| `open` | Normal operations, no disruptions |
| `closed` | Some or all roads are closed or disrupted |

Road conditions map directly from the API's `roadCondition` field (normalized to lowercase).

## API

This integration queries the public endpoints of the Westerscheldetunnel API:

| Endpoint | Description |
|----------|-------------|
| `GET /situation` | Current road conditions and overall status |
| `GET /incident?phase=ACTIVE` | Active incidents with road status details |
| `GET /incident?phase=SCHEDULED` | Scheduled (planned) incidents |

Base URL: `https://api.verkeer.westerscheldetunnel.nl`

## Requirements

- Home Assistant 2024.1.0 or later

## Credits

Data sourced from [Westerscheldetunnel API](https://api.verkeer.westerscheldetunnel.nl).

## License

MIT