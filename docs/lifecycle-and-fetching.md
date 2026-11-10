# Card Lifecycle & Initial Fetching Mechanism

This document provides a detailed technical explanation of how the custom cards initialize, manage their lifecycle, fetch data from the inVENTer e16 controller, and prevent concurrency conflicts.

---

## 1. Lifecycle Overview

The card follows the standard Custom Element lifecycle within Home Assistant Lovelace:

```
┌─────────────────────────┐
│       Constructor       │   • Initialize internal state and default configuration
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│    setConfig(config)    │   • Validate card YAML config
└────────────┬────────────┘   • Store custom titles, default profiles, or explicit entities
             │
┌────────────▼────────────┐
│    connectedCallback    │   • Card inserted into dashboard DOM
└────────────┬────────────┘   • Initial Shadow Root structure prepared
             │
┌────────────▼────────────┐
│      set hass(hass)     │ ◄── Called repeatedly by HA whenever entity states change
└────────────┬────────────┘
             │
             ├─────────────────────────────────────────────────┐
    [First call: !_initialFetchDone]               [Subsequent calls: _initialFetchDone]
             │                                                 │
┌────────────▼────────────┐                       ┌────────────▼────────────┐
│    Initial Fetching     │                       │ Reactive State Updates   │
│   _initialFetchDone = 1 │                       │ Check active profile    │
│   _fetchSchedule()      │                       │ in zones & re-render UI │
└─────────────────────────┘                       └─────────────────────────┘
```

---

## 2. The Initial Fetching Mechanism

### The Problem
In Home Assistant Lovelace dashboards, the `hass` property setter is invoked whenever **any** state in the entire Home Assistant instance changes (often multiple times per second if sensors update frequently). 

Calling the hardware controller every time `hass` updates would overwhelm the local network, drain wireless device batteries, and cause high CPU load on the e16 controller.

### The Solution: `_initialFetchDone` Guard
To prevent duplicate requests, the card uses an internal initialization latch:

```javascript
set hass(hass) {
  this._hass = hass;

  // Initial fetch: executed only once when the card first connects to Home Assistant
  if (!this._initialFetchDone && hass) {
    const entityId = this._getTargetEntity();
    if (entityId) {
      this._initialFetchDone = true;
      this._fetchSchedule(); // or this._fetchDevices(false)
    }
  } else if (this._initialFetchDone && hass) {
    // Lightweight passive update: only re-render if zone profile state changed
    this._checkActiveProfileChange();
  }
}
```

### Entity Auto-Detection
Before initiating the fetch, `this._getTargetEntity()` automatically locates the relevant inVENTer fan entity:
1. **Configured entity**: If specified explicitly via `entity: fan.inventer_zone_1`, the card uses that entity.
2. **Auto-discovery from state attributes**: Scans `hass.states` for any entity with attribute `inventer_e16_profile` or `inventer_e16_zone`.
3. **Domain & Name fallback**: Scans all `fan.*` entities for IDs or friendly names containing `"inventer"` or `"e16"`.
4. If no matching entity is found, the card presents a clear banner prompting the user to select an entity in the card editor.

---

## 3. Step-by-Step: Schedule Fetching (`_fetchSchedule`)

When `_fetchSchedule()` executes:

1. **State Transition to Loading**:
   * Sets `this._loading = true` and `this._errorMessage = ""`.
   * Re-renders the Shadow DOM to display the animated loading spinner and disable action buttons.

2. **WebSocket Dispatch (`sendMessagePromise`)**:
   * The card queries the Home Assistant WebSocket API:
   ```javascript
   const res = await this._hass.connection.sendMessagePromise({
     type: "call_service",
     domain: "inventer_e16",
     service: "get_time_program",
     target: { entity_id: entityId },
     service_data: { profile: this._selectedProfile },
     return_response: true
   });
   ```

3. **Fallback to `callService`**:
   * If the dashboard is running on an older Home Assistant frontend where WebSocket response promises are restricted, it gracefully falls back to:
   ```javascript
   await this._hass.callService("inventer_e16", "get_time_program", {
     profile: this._selectedProfile
   }, { entity_id: entityId });
   ```

4. **Response Processing & State Storage**:
   * The returned response contains the schedule array for the requested profile:
   ```json
   {
     "response": {
       "entries": [
         { "slot": 0, "start_time": "07:00", "weekdays": [1, 2, 3, 4, 5], "mode": "heat_recovery", "speed": 2 },
         { "slot": 1, "start_time": "22:00", "weekdays": [1, 2, 3, 4, 5, 6, 7], "mode": "ventilation", "speed": 1 }
       ]
     }
   }
   ```
   * The card stores these entries in `this._schedules[profile]` and marks the profile as fetched in `this._pulledProfiles.add(profile)`.
   * `this._loading = false` is set and the schedule timetable is rendered.

---

## 4. Pre-Write Synchronization (Read-Before-Write Pattern)

A critical safety mechanism in the inVENTer e16 cards is **Pre-Write Synchronization**.

### Why is this necessary?
The e16 controller has a fixed hardware memory limit of **32 timetable slots (slots 0 to 31)** per profile.
If another user modifies a schedule via the inVENTer mobile app or another dashboard tab, the local browser's cached view could become outdated. Blindly writing slot #3 could overwrite a new entry or create duplicate conflicting time switches.

### How it works:
Whenever a user clicks **Save** (`_saveEntry()`) or **Delete** (`_deleteEntry()`):

1. **Fresh pull from controller**: Before executing the write service call, the card transparently re-runs a fetch against the physical controller:
   ```javascript
   await this._fetchSchedule();
   ```
2. **Integrity Check**:
   * If the pre-fetch fails (e.g., controller dropped offline), the save operation is aborted immediately with an error message, protecting existing schedules.
3. **Dynamic Slot Allocation**:
   * The card scans the fresh list of entries to determine which slots between 0 and 31 are actually available (`_findFreeSlot()`).
4. **Targeted Write**:
   * The entry is committed to the confirmed free slot via `inventer_e16.set_time_program`.
5. **Immediate UI Refresh**:
   * Upon successful service response, the local timetable immediately displays the confirmed schedule.

---

## 5. Force Refresh vs Cached Data in Devices Card

In `custom:inventer-e16-devices-card`:

* **Standard Fetch (`forceRefresh = false`)**:
  * Loads the cached hardware state currently stored in the e16 controller memory.
  * Very fast (almost instantaneous) and avoids generating 868 MHz radio traffic.
* **Force Refresh (`forceRefresh = true`)**:
  * Triggered when the user clicks the 🔄 button in the card header.
  * Sends `{ refresh: true }` in `inventer_e16.get_devices`.
  * Instructs the e16 controller to send over-the-air RF polling pings to all paired fans (`iV14-Zero`, `iV-Twin+`) and wireless sensors.
  * Updates live RSSI signal values (`dBm`), battery levels, temperature/humidity values, and fan runtimes.
  * Displays an animated spinning icon while the RF scan completes.
