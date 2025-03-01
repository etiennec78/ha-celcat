# Celcat Calendar integration for Home Assistant 📆

## Components 🌟

### Calendars 📅
- **Single Calendar**: Contains all events fetched from Celcat Calendar.
- **Calendars by course**: One calendar per course (disabled by default).

## Installation 🚀

### Option 1: Install via HACS (Recommended) 🛒

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=etiennec78&repository=ha-celcat&category=integration)

1. Make sure you have [HACS](https://hacs.xyz/) installed in Home Assistant.
2. Click the button above to add the integration.
3. Restart Home Assistant.
4. [Configure](https://my.home-assistant.io/redirect/config_flow_start/?domain=celcat_calendar) the integration through the UI.

### Option 2: Manual Installation 📖

1. Create the `custom_components` directory inside your Home Assistant configuration directory.
2. Copy the `custom_components/celcat_calendar` folder into `custom_components`.
3. Restart Home Assistant.
4. [Configure](https://my.home-assistant.io/redirect/config_flow_start/?domain=celcat_calendar) the integration through the UI.


## Configuration 🔧

Celcat Calenddar is configured via the UI. See [the HA docs](https://www.home-assistant.io/getting-started/integration/) for more details.

1. Go to **Settings > Devices & services**.
2. Click on `+ ADD INTEGRATION`, then search for `Celcat Calendar`.
3. Fill the calendar name and your creditentials.
   - Example: If your Celcat login page is hosted at `https://university.com/calendar/LdapLogin`, use `https://university.com/calendar` for the URL.
4. Click `SUBMIT`.

> Note: As all events must be retrieved individually from Celcat during configuration, loading may take some time

## Customization Options ⚙️

You may edit options like:
- **Scan Interval**: Adjust how frequently events are updated.
- **Holidays Inclusion**: Decide whether to include holidays in the calendar.
- **Event Grouping**: Group events for better organization and colors.

### How to Edit Options:

1. Go to the [Settings > Devices & services](https://my.home-assistant.io/redirect/integrations/).
2. Click on the [`Celcat Calendar`](https://my.home-assistant.io/redirect/integration/?domain=celcat_calendar) integration.
3. Next to your calendar, click on `CONFIGURE`.
4. Edit the options and click on `SUBMIT`.


### Hide Duplicate Events (with Event Grouping) 😶‍🌫️

When event grouping is enabled, the main calendar remains for automation purposes.
To avoid seeing duplicate events in the UI, it is recommend to hide the main calendar:

1. Go to **Settings > Devices & Services**.
2. Click on the `[Celcat Calendar](https://my.home-assistant.io/redirect/integration/?domain=celcat_calendar)` integration.
3. Click on `"X" entities`.
4. Click on the main calendar (it should be at the top).
5. Select the settings cog in the upper-right corner.
6. Toggle off the `Visible` option.

## Consider supporting ? 🩷

If you enjoyed this integration, don't hesitate to **star it** ! ⭐

And if you would like to go further, I would be really happy to get a [tip](https://www.buymeacoffee.com/etiennec78) ! 💛

## Final words 👋

I can't guarantee that this integration will work with every Celcat server, as Celcat has a quite poorly written API.

However if you find a bug, 👉 open an [issue](https://github.com/etiennec78/Home-Automation/issues/new) or [pull request](https://github.com/etiennec78/Home-Automation/pulls) 😉

I'd be happy to help ! 😄
