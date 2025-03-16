"""The Celcat Calendar integration."""

from __future__ import annotations

import logging

from celcat_scraper import (
    CelcatConfig,
    CelcatFilterConfig,
    CelcatScraperAsync,
    FilterType,
)

from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_FILTERS,
    CONF_REPLACEMENTS,
    CONF_SHOW_HOLIDAYS,
    DEFAULT_FILTERS,
    DEFAULT_REPLACEMENTS,
    DEFAULT_SHOW_HOLIDAYS,
    DOMAIN,
    REMEMBERED_STRIPS,
)
from .coordinator import CelcatConfigEntry, CelcatData, CelcatDataUpdateCoordinator
from .store import CelcatStore
from .util import list_to_dict

PLATFORMS: list[Platform] = [Platform.CALENDAR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: CelcatConfigEntry) -> bool:
    """Set up Celcat Calendar from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    filter_types = []
    for filter_string in entry.options.get(CONF_FILTERS, DEFAULT_FILTERS):
        try:
            filter_types.append(FilterType(filter_string))
        except ValueError:
            _LOGGER.warning("Ignoring invalid filter: %s", filter_string)

    replacements = await list_to_dict(
        entry.options.get(CONF_REPLACEMENTS, DEFAULT_REPLACEMENTS)
    )
    filter_config = CelcatFilterConfig(
        filters=filter_types,
        course_remembered_strips=entry.data.get(REMEMBERED_STRIPS, []),
        course_replacements=replacements,
    )

    celcat = CelcatScraperAsync(
        CelcatConfig(
            url=entry.data[CONF_URL],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            include_holidays=entry.options.get(
                CONF_SHOW_HOLIDAYS, DEFAULT_SHOW_HOLIDAYS
            ),
            rate_limit=0.1,
            session=async_get_clientsession(hass),
            filter_config=filter_config,
        )
    )

    store = CelcatStore(hass, entry.entry_id)

    entry.runtime_data = CelcatData(celcat, store, None)

    coordinator = CelcatDataUpdateCoordinator(hass, entry)
    entry.runtime_data.coordinator = coordinator

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: CelcatConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.client.close()
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: CelcatConfigEntry) -> None:
    """Handle removal of an entry."""
    store = CelcatStore(hass, entry.entry_id)
    await store.async_remove()
