# Architecture & Integration Boundaries

This document describes the architectural design of **inVENTer e16 Lovelace Cards** and how they interface with Home Assistant and the inVENTer Easy Connect e16 hardware.

---

## 1. Component Separation & Boundaries

It is essential to understand the distinction between the **Frontend Cards** and the **Backend Integration**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Browser (Lovelace UI)                      │
│                                                                        │
│   ┌────────────────────────────────┐  ┌────────────────────────────┐   │
│   │  inventer-e16-schedule-card    │  │  inventer-e16-devices-card │   │
│   └────────────────────────────────┘  └────────────────────────────┘   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ WebSocket API (sendMessagePromise)
                                    │ State Subscription (hass.states)
┌───────────────────────────────────▼────────────────────────────────────┐
│                       Home Assistant Core Server                       │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ Backend Integration: ha-inventer-e16 (custom_components)      │   │
│   │                                                                │   │
│   │  • Fan Entities: fan.inventer_zone_1, fan.inventer_zone_2      │   │
│   │  • Service: inventer_e16.get_time_program (returns response)   │   │
│   │  • Service: inventer_e16.set_time_program                     │   │
│   │  • Service: inventer_e16.delete_entry                          │   │
│   │  • Service: inventer_e16.set_profile                           │   │
│   │  • Service: inventer_e16.get_devices (returns response)        │   │
│   │  • Service: inventer_e16.assign_device_zone                    │   │
│   └────────────────────────────────┬───────────────────────────────┘   │
└────────────────────────────────────┼───────────────────────────────────┘
                                     │ Local Network (HTTP REST / TCP)
┌────────────────────────────────────▼───────────────────────────────────┐
│              inVENTer Easy Connect e16 Controller Hardware             │
│                                                                        │
│   • Timetable Slot Memory (32 slots per profile)                       │
│   • 868 MHz Wireless Mesh Network (Fans, Sensors, Controllers)         │
└────────────────────────────────────────────────────────────────────────┘
```

### Why two separate repositories?
1. **Frontend Isolation**: Lovelace custom cards are written in standard web technologies (JavaScript, HTML, Web Components, Shadow DOM) and execute purely inside the user's web browser or mobile Home Assistant app.
2. **Backend Hardware Driver**: Communication with the physical e16 controller (cryptographic challenge/tokens, raw socket TCP commands, REST queries, and Home Assistant entity lifecycle) requires Python and Home Assistant Core APIs, which are provided by the [ha-inventer-e16](https://github.com/Kadz93/ha-inventer-e16) custom component.

---

## 2. Communication Mechanisms

The frontend cards communicate with Home Assistant through two primary channels:

### A. Passive State Observation (`set hass(hass)`)
Home Assistant automatically invokes `set hass(hass)` whenever any entity in the system updates its state.
* The cards read active ventilation attributes from `this._hass.states[entity_id]`:
  * Current operating mode (`heat_recovery`, `ventilation`, `off`)
  * Current fan speed (`1`, `2`, `3`, `4`)
  * Current active profile (`living_room`, `bedroom`, `standard`, etc.)
  * Zone definitions and names
* This passive push mechanism allows the cards to update UI badges (such as which profile is active in which zone) without initiating network requests.

### B. Active Service Calls with Return Data (`sendMessagePromise`)
Home Assistant 2023.7 introduced service call response data. The cards use this capability via the underlying WebSocket connection:

```javascript
const response = await this._hass.connection.sendMessagePromise({
  type: "call_service",
  domain: "inventer_e16",
  service: "get_time_program",
  target: { entity_id: entityId },
  service_data: { profile: "living_room" },
  return_response: true
});
```

Using `sendMessagePromise` provides:
* **Immediate synchronous response**: The card awaits the actual payload returned by the physical controller through the backend integration.
* **Granular error handling**: If the controller is offline or returns an error, the WebSocket call rejects, allowing the card to render a user-friendly error message in the UI rather than failing silently.

---

## 3. Web Component & Shadow DOM Architecture

Both cards are implemented as standard native Custom Elements extending `HTMLElement`:
* **Shadow DOM (`mode: 'open'`)**: Ensures complete style isolation so dashboard themes or global CSS cannot distort the cards' layouts, timetables, or modal dialogs.
* **No external framework dependencies**: Implemented using vanilla ES6+ without requiring LitElement, React, or heavy bundle overhead, ensuring lightning-fast load times on mobile devices and wall-mounted dashboard tablets.
* **Built-in Visual Editors**: Each card accompanies an editor (`inventer-e16-schedule-card-editor` and `inventer-e16-devices-card-editor`) implementing `getConfigElement()` and `getStubConfig()` for seamless integration into the Home Assistant UI card picker.
