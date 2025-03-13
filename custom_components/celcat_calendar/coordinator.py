"""The Celcat Calendar integration data coordinator."""

from datetime import datetime, timedelta, date
import logging

import async_timeout
from dataclasses import dataclass
from typing import Any

from celcat_scraper import (
    CelcatScraperAsync,
    CelcatCannotConnectError,
    CelcatInvalidAuthError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_GROUP_BY,
    DEFAULT_GROUP_BY,
    GROUP_BY_OFF,
    GROUP_BY_CATEGORY,
    GROUP_BY_CATEGORY_COURSE,
    GROUP_BY_COURSE,
)
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
            update_interval=timedelta(
                hours=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
            update_method=self._async_update_data,
            always_update=False,
        )
        data = entry.runtime_data
        self.celcat: CelcatScraperAsync = data.client
        self._store: CelcatStore = data.store
        self.options = entry.options

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

            tz_events = [
                {
                    **event,
                    "start": dt_util.as_local(event["start"]),
                    "end": dt_util.as_local(event["end"]),
                }
                for event in events
            ]

            return await self._group_events(tz_events)

    async def _group_events(
        self, events: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        """Group events by course or category based on configuration."""
        grouped_events: dict[str, list[dict[str, Any]]] = {"all": events}

        group_by = self.options.get(CONF_GROUP_BY, DEFAULT_GROUP_BY)
        if group_by == GROUP_BY_OFF:
            return grouped_events

        def get_group_by_category(event: dict[str, Any]) -> str:
            return event.get("category") or "unknown"

        def get_group_by_course(event: dict[str, Any]) -> str:
            return event.get("course") or "unknown"

        def get_group_by_category_course(event: dict[str, Any]) -> str:
            category = event.get("category", "")
            course = event.get("course", "")

            if category and course:
                return f"{category} {course}"
            elif category:
                return category
            elif course:
                return course
            return "unknown"

        grouping_strategies = {
            GROUP_BY_CATEGORY: get_group_by_category,
            GROUP_BY_COURSE: get_group_by_course,
            GROUP_BY_CATEGORY_COURSE: get_group_by_category_course,
        }

        get_group = grouping_strategies.get(group_by, lambda e: "unknown")

        for event in events:
            group = get_group(event)
            if group not in grouped_events:
                grouped_events[group] = []
            grouped_events[group].append(event)

        return grouped_events


@dataclass
class CelcatData:
    """Celcat data class."""

    client: CelcatScraperAsync
    store: CelcatStore
    coordinator: CelcatDataUpdateCoordinator
