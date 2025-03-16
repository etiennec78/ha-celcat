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
- **Data Filters**: Standardize data fetched from Celcat.
- **Course Name Replacements**: Manually override course names.

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

### Available Filters 🧹

Data filters can be useful if Celcat contains non-standardized data.

For example, raw data may contain different names for the same course which makes grouping ineffective.

| Filter | Description | Example |
| :---: | :--- | :--- |
| Title case | Capitalize only the first letter of each word | MATHS CLASS -> Maths Class |
| Remove modules | Remove modules from courses names | Maths [DPAMAT2D] -> Maths |
| Remove category | Remove category from course names | Maths CM -> Maths |
| Remove punctuation | Remove ".,:;!?" from text | Math. -> Math |
| Group similar courses | Search for all event names and group ones containing another | Maths, Maths S1 -> Maths |
| Remove redundant parts | Extract parts removed by the previous filter and remove them from all other courses | Physics S1 -> Physics |
| Remove text after number | Remove all text after the first number found | Room 403 32 seats -> Room 403 |
| Remove duplicates | Remove duplicates from the list | Building A, Building A -> Building A |

### Course name replacements 🔄

In case filters couldn't standardize all course names, you can set manual replacements.

To do so, enter source:output combinations to manually replace course names.

Example: `Math Class:Maths` will replace all "Math Class" courses by "Maths".


## Consider supporting ? 🩷

If you enjoyed this integration, don't hesitate to **star it** ! ⭐

And if you would like to go further, I would be really happy to get a [tip](https://www.buymeacoffee.com/etiennec78) ! 💛

## Final words 👋

I can't guarantee that this integration will work with every Celcat server, as Celcat has a quite poorly written API.

However if you find a bug, 👉 open an [issue](https://github.com/etiennec78/Home-Automation/issues/new) or [pull request](https://github.com/etiennec78/Home-Automation/pulls) 😉

I'd be happy to help ! 😄
