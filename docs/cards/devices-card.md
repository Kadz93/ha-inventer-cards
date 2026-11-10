# Devices & Zone Management Card Reference (`inventer-e16-devices-card`)

The **Devices & Zone Management Card** (`custom:inventer-e16-devices-card`) enables monitoring and organization of all wireless hardware units (fans, wireless indoor/outdoor sensors, and controller interfaces) paired with the inVENTer Easy Connect e16 system.

---

## 1. Quick Example

```yaml
type: custom:inventer-e16-devices-card
title: Hardware Devices & Zones
entity: fan.inventer_living_room   # Optional, auto-detected if omitted
```

---

## 2. Configuration Options

| Option | Type | Default | Description |
|---|---|---|---|
| `type` | string | **required** | `custom:inventer-e16-devices-card` |
| `entity` | string | *auto-detect* | Target inVENTer `fan` entity ID. If omitted, automatically discovers the first e16 zone fan. |
| `title` | string | `inVENTer e16 – Geräte & Zonen` | Header title displayed on the card. |

---

## 3. Hardware Monitoring & Telemetry

The card displays an overview of all 868 MHz RF devices linked to the e16 controller:

### Supported Hardware Types
* **Fans**:
  * `iV14-Zero` (Single-room heat recovery fan)
  * `iV-Twin+` (Twin-fan system with counter-current flow)
  * `iV-Smart+`
  * `aV100` / `aV160`
* **Sensors**:
  * `Wireless Indoor Sensor` (Temperature & relative humidity %rH)
  * `Wireless Outdoor Sensor` (External temperature & relative humidity)
* **Controllers**:
  * `Easy Connect e16 Base Station`

### Live Metrics Displayed
* **RF Signal Strength (RSSI)**: Displayed in `-dBm` with color-coded quality bars (Green > -70 dBm, Yellow -70 to -85 dBm, Red < -85 dBm).
* **Battery Status**: Battery percentage and warning badges for wireless sensors.
* **Environmental Data**: Current temperature (°C) and relative humidity (%) reported by wireless sensor units.
* **Operating Hours**: Total operational runtime hours and fan filter maintenance countdowns.
* **Firmware Version**: Installed firmware revision on each fan module.

---

## 4. 1-Click Zone Reassignment

Fans and sensors in the inVENTer e16 ecosystem belong to logical ventilation zones (e.g. Zone 1: Living Area, Zone 2: Bedrooms, Zone 3: Basements).

### How to reassign:
1. Locate the device card for any fan or sensor.
2. Click the **Zone Selector** dropdown.
3. Select the desired destination zone.
4. The card dispatches the `inventer_e16.assign_device_zone` service call to the controller and updates the UI immediately.

---

## 5. Dynamic Zones (Scheduled Night-Time Shifts)

A unique capability supported by the card is **Dynamic Zone Switching**.

### Use Case
During the daytime, fans in a hallway or study may operate in tandem with the primary living room zone. At night (e.g., from 22:00 to 07:00), you may want those specific fans to decouple from the living room and join the silent bedroom zone or run a gentle exhaust mode.

### Setup:
1. Enable **Dynamic Zone** on the desired device in the card.
2. Select the **Secondary Zone**.
3. Define the active time window (e.g., `22:00 – 07:00`).
4. The card and underlying automation will temporarily migrate the device to the secondary zone during the scheduled window and seamlessly return it to its home zone afterwards.

---

## 6. Force RF Refresh

Clicking the 🔄 icon in the top right corner triggers an active over-the-air RF poll across the 868 MHz wireless mesh network. For more information, see [Card Lifecycle & Initial Fetching](../lifecycle-and-fetching.md).
