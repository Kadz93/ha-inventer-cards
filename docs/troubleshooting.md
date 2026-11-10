# Troubleshooting & FAQ

This guide resolves common setup problems, configuration misunderstandings, and network communication issues.

---

## 1. Finding the Card in HACS

### How to locate:
1. Open **HACS** in your Home Assistant dashboard.
2. Select **Frontend** (or **Dashboards**).
3. Search for **inVENTer e16 Lovelace Cards**.
4. Click **Download**.

*Note*: If adding manually as a custom repository during development, remember to select the category **Dashboard** (or **Plugin**), not *Integration*.

---

## 2. "No inVENTer fan entity found"

### Symptom:
The card displays a warning:
> *"No inVENTer fan entity found. Please configure one in card settings."*

### Cause:
The card automatically scans `hass.states` for `fan.*` entities created by the [ha-inventer-e16](https://github.com/Kadz93/ha-inventer-e16) integration. If you have customized entity IDs or have multiple fan integrations, auto-detection might not match.

### Solution:
Explicitly specify your zone fan entity in the card configuration:

```yaml
type: custom:inventer-e16-schedule-card
entity: fan.your_custom_inventer_fan_entity_id
```

You can also use the graphical card editor to pick the fan entity from the dropdown.

---

## 3. Card Stuck on "Loading schedule from controller..."

### Symptom:
When opening the card or clicking refresh, the loading spinner spins indefinitely or displays a timeout error.

### Checklist:
1. **Verify Backend Integration**: Check **Settings → Devices & Services** in Home Assistant. Confirm that the **inVENTer Easy Connect e16** integration is green and active.
2. **Controller IP & Reachability**: Ensure your e16 controller has a static IP / DHCP reservation and is powered on and reachable from your Home Assistant host.
3. **Home Assistant Logs**: Check **Settings → System → Logs**. Search for `inventer_e16` entries. If the controller connection dropped, reload the integration.

---

## 4. "Custom element doesn't exist: inventer-e16-..." After Updating

### Symptom:
After downloading an update via HACS or manual copy, the dashboard card turns into a red error box stating the custom element does not exist.

### Cause:
Your web browser or Home Assistant Companion App has cached the previous version of the JavaScript file.

### Solution:
* **Desktop Browser (Chrome / Edge / Firefox / Safari)**:
  * Perform a hard refresh: Press `Ctrl + F5` (Windows/Linux) or `Cmd + Shift + R` (macOS).
* **Home Assistant Mobile Companion App**:
  * Open **Settings → Companion App → Debugging → Reset frontend cache**.
  * Restart the app.

---

## 5. Manual Installation Resource Path

If you installed manually instead of using HACS:
Ensure the resource URL in **Settings → Dashboards → Resources** matches where you placed the file:

* If placed in `/config/www/inventer-e16-cards.js`:  
  URL: `/local/inventer-e16-cards.js` (Type: **JavaScript Module**)
* If placed in `/config/www/ha-inventer-cards/dist/inventer-e16-cards.js`:  
  URL: `/local/ha-inventer-cards/dist/inventer-e16-cards.js` (Type: **JavaScript Module**)
