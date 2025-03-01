"""Provide info to system health."""

from typing import Any

from homeassistant.components import system_health
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


@callback
def async_register(
    hass: HomeAssistant, register: system_health.SystemHealthRegistration
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get info for the info page."""

    entries = hass.config_entries.async_entries(DOMAIN)

    if not entries:
        return {}

    total_entries = len(entries)
    total_events = 0
    checked_urls = {}
    reachable_entries = 0

    for entry in entries:
        url = entry.data.get(CONF_URL)

        if url not in checked_urls:
            checked_urls[url] = await system_health.async_check_can_reach_url(hass, url)

        if checked_urls[url]:
            reachable_entries += 1

        total_events += len(entry.runtime_data.coordinator.data)

    return {
        "reachable_instances": f"{reachable_entries}/{total_entries}",
        "total_events": total_events,
    }
