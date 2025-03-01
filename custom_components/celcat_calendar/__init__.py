"""The Celcat Calendar integration."""

from __future__ import annotations

from celcat_scraper import CelcatConfig, CelcatScraperAsync

from homeassistant.const import Platform, CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_SHOW_HOLIDAYS, DEFAULT_SHOW_HOLIDAYS
from .coordinator import CelcatDataUpdateCoordinator, CelcatData, CelcatConfigEntry
from .store import CelcatStore

PLATFORMS: list[Platform] = [Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: CelcatConfigEntry) -> bool:
    """Set up Celcat Calendar from a config entry."""
    hass.data.setdefault(DOMAIN, {})

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
