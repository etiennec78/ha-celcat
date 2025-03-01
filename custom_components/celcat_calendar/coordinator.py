"""The Celcat Calendar integration data coordinator."""

from datetime import datetime, timedelta, date
import logging

import async_timeout
from dataclasses import dataclass

from celcat_scraper import (
    CelcatScraperAsync,
    CelcatCannotConnectError,
    CelcatInvalidAuthError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .store import CelcatStore

_LOGGER = logging.getLogger(__name__)


type CelcatConfigEntry = ConfigEntry[CelcatData]


class CelcatDataUpdateCoordinator(DataUpdateCoordinator[list[dict]]):
    """Class to manage fetching data from Celcat Calendar."""

    def __init__(self, hass: HomeAssistant, entry: CelcatConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data[CONF_NAME],
            update_interval=timedelta(hours=DEFAULT_SCAN_INTERVAL),
            update_method=self._async_update_data,
            always_update=False,
        )
        data = entry.runtime_data
        self.celcat: CelcatScraperAsync = data.client
        self._store: CelcatStore = data.store

    async def _async_update_data(self) -> list[dict]:
        """Update data via library."""
        try:
            return await self._fetch_data()
        except CelcatInvalidAuthError as err:
            raise ConfigEntryAuthFailed from err
        except CelcatCannotConnectError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def _fetch_data(self) -> list[dict]:
        """Fetch data from API and store."""
        _LOGGER.debug("Updating calendar data")

        today = dt_util.now().date()
        end_year = today.year + (1 if today.month >= 9 else 0)
        end = date(year=end_year, month=8, day=31)

        async with async_timeout.timeout(180):
            # Load existing data from the local store
            local_data = await self._store.async_load()
            if local_data:
                for event in local_data:
                    if isinstance(event["start"], str):
                        event["start"] = datetime.fromisoformat(event["start"])
                    if isinstance(event["end"], str):
                        event["end"] = datetime.fromisoformat(event["end"])

                # Fetch future events
                start = today
            else:
                # Fetch past and future events
                start = date(end_year - 1, 9, 1)

            events = await self.celcat.get_calendar_events(
                start=start,
                end=end,
                previous_events=local_data,
            )

            await self.celcat.close()
            await self._store.async_save(events)

            return [
                {
                    **event,
                    "start": dt_util.as_local(event["start"]),
                    "end": dt_util.as_local(event["end"]),
                }
                for event in events
            ]


@dataclass
class CelcatData:
    """Celcat data class."""

    client: CelcatScraperAsync
    store: CelcatStore
    coordinator: CelcatDataUpdateCoordinator
