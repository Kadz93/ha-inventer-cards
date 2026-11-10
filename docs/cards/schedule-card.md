# Schedule Card Reference (`inventer-e16-schedule-card`)

The **Time Program & Schedule Management Card** (`custom:inventer-e16-schedule-card`) provides an intuitive visual interface to view, configure, and synchronize daily and weekly ventilation schedules across all profiles directly with the inVENTer Easy Connect e16 controller.

---

## 1. Quick Example

```yaml
type: custom:inventer-e16-schedule-card
title: Ventilation Schedules
entity: fan.inventer_living_room   # Optional, auto-detected if omitted
default_profile: living_room       # Profile opened when dashboard loads
```

---

## 2. Configuration Options

| Option | Type | Default | Description |
|---|---|---|---|
| `type` | string | **required** | `custom:inventer-e16-schedule-card` |
| `entity` | string | *auto-detect* | Target inVENTer `fan` entity ID (e.g. `fan.inventer_zone_1`). If omitted, auto-detects the first e16 fan. |
| `title` | string | `inVENTer e16 – Zeitpläne` | Custom title displayed in the card header. |
| `default_profile` | string | `living_room` | Profile selected by default (`standard`, `living_room`, `bedroom`, `bathroom`, `kitchen`, `holiday`, `custom_1` ... `custom_9`). |

---

## 3. Profiles & 1-Click Zone Assignment

The e16 controller maintains independent schedule memory for:
* **Standard Profiles**:
  * `standard` (Default / Standard)
  * `living_room` (Living Room)
  * `bedroom` (Bedroom)
  * `bathroom` (Bathroom)
  * `kitchen` (Kitchen)
  * `holiday` (Holiday / Absence)
* **Custom Profiles**:
  * `custom_1` through `custom_9`

### Active Zone Badges
Beneath the profile selector pills, the card inspects all inVENTer ventilation zones in Home Assistant:
* If a profile is currently active in a zone, it shows a green badge `✓ Active in [Zone Name]`.
* If a profile is not active in that zone, clicking the **+ Assign to [Zone]** button immediately sends a service call (`inventer_e16.set_profile`) to activate that profile for the selected ventilation zone.

---

## 4. Timetable Visualizer

The timetable renders each entry configured in the controller:
* **Start Time**: Formatted in 24-hour format (`HH:MM`).
* **Active Days**: Displayed as compact pills (Monday through Sunday) with quick indicators for Workdays (`Mo–Fr`) or Weekend (`Sa–Su`).
* **Operating Mode & Color Coding**:
  * 🟢 **Heat Recovery (WRG)**: Green badge indicating heat retention with fan direction alternation.
  * 🔵 **Ventilation (Durchlüftung)**: Blue badge indicating direct exhaust / fresh air flow.
  * ⚪ **Pause / Off**: Grey badge indicating fan pause.
* **Fan Speed**: Visual level indicator (Levels 1 to 4).
* **Flap Position**: Indicates whether the automatic inner flap is Open or Closed.

---

## 5. Modal Editor & Slot Allocation

Clicking **Add new entry** or the ✏️ edit icon opens a responsive modal dialog:

1. **Start Time**: Time picker (`00:00` to `23:59`).
2. **Day Selection**:
   * One-click presets: *Workdays (Mon–Fri)*, *Weekend (Sat–Sun)*, or *All days*.
   * Individual day toggles (Mo, Di, Mi, Do, Fr, Sa, So).
3. **Mode & Speed**:
   * Mode radio pills: *Heat recovery*, *Ventilation*, *Pause*.
   * Speed slider: *Level 1* through *Level 4* (disabled if Pause is chosen).
4. **Automated Slot Allocation**:
   * The controller supports up to 32 slots per profile (0 to 31).
   * When adding an entry, the card automatically locates the first vacant slot number and sends the command to the hardware.
   * If all 32 slots are used, the user is notified before making edits.

---

## 6. Pre-Write Sync

Before saving or deleting any entry, the card performs a pre-write synchronization with the physical controller. For full details on the underlying WebSocket communication and race-condition prevention, refer to [Card Lifecycle & Initial Fetching](../lifecycle-and-fetching.md).
