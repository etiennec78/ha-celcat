"""Provides diagnostics for Celcat Calendar."""

import datetime
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .coordinator import CelcatConfigEntry
from .const import DOMAIN

TO_REDACT = {"id", "rooms", "professors", "modules", "department", "sites"}


def redact_store(data: dict[str, Any]) -> dict[str, Any]:
    """Redact personal information from calendar events in the store."""
    diagnostics = []
    for event in data:
        diagnostics.append(
            async_redact_data(event, TO_REDACT),
        )
    return diagnostics


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: CelcatConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    payload: dict[str, Any] = {
        "now": dt_util.now().isoformat(),
        "timezone": str(dt_util.get_default_time_zone()),
        "system_timezone": str(datetime.datetime.now().astimezone().tzinfo),
    }

    store = entry.runtime_data.store
    data = await store.async_load()
    payload["store"] = redact_store(data)
    return payload
