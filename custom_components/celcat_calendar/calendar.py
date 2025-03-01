"""Calendar platform for Celcat."""

from __future__ import annotations

from collections.abc import Iterator
from collections import defaultdict
from datetime import datetime, time
from typing import Any
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import CelcatConfigEntry
from .coordinator import CelcatDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CelcatConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the celcat calendar platform."""
    coordinator = entry.runtime_data.coordinator

    entities = [
        CelcatCalendarEntity(
            coordinator=coordinator, entry_id=entry.entry_id, category=category
        )
        for category in coordinator.data
    ]

    async_add_entities(entities, True)


class CelcatCalendarEntity(CalendarEntity):
    """A calendar entity by Celcat."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CelcatDataUpdateCoordinator,
        entry_id: str,
        category: str,
    ) -> None:
        """Initialize Celcat."""
        self.coordinator = coordinator
        self._attr_unique_id = (
            entry_id + (f"-{category}" if category != "all" else "") + "-calendar"
        )
        self._attr_has_entity_name = True
        self._attr_name = None if category == "all" else category
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            manufacturer="Celcat",
        )
        self.category = category

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self.coordinator.data.get(self.category, [])

        if not events:
            return None

        next_event = next(
            (event for event in events if event["end"] >= dt_util.now()), None
        )
        return self._get_calendar_event(next_event) if next_event else None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        if not self.coordinator.data.get(self.category):
            return []

        events = []
        for event in self._get_date_range_events(start_date, end_date):
            events.append(self._get_calendar_event(event))
        return events

    def _get_date_range_events(
        self, start: datetime, end: datetime
    ) -> Iterator[dict[str, Any]]:
        """Get events within the specified date range."""
        range_start = start
        range_end = end

        for event in self.coordinator.data.get(self.category, []):
            event_start = (
                event["start"]
                if isinstance(event["start"], datetime)
                else datetime.combine(event["start"], time.min)
            )
            event_end = (
                event["end"]
                if isinstance(event["end"], datetime)
                else datetime.combine(event["end"], time.max)
            )

            if event_end >= range_start and event_start <= range_end:
                yield event

    def _get_calendar_event(self, event: dict[str, Any]) -> CalendarEvent:
        """Return a CalendarEvent from an API event."""
        description_parts = []
        if event.get("rooms"):
            description_parts.append(f"Rooms: {', '.join(event['rooms'])}")
        if event.get("professors"):
            description_parts.append(
                f"Professors: {', '.join(professor.split()[0] for professor in event['professors'])}"
            )
        if event.get("sites"):
            description_parts.append(f"Sites: {', '.join(event['sites'])}")
        if event.get("faculty"):
            description_parts.append(f"Faculty: {event['faculty']}")
        if event.get("notes"):
            description_parts.append(f"Notes: {event['notes']}")

        if event.get("course") and event.get("category"):
            summary = f"{event['category']} {event['course']}"
        elif event.get("course"):
            summary = event["course"]
        elif event.get("category"):
            summary = event["category"]
        else:
            summary = "Unknown event"

        start = event["start"].date() if event["all_day"] else event["start"]
        end = event["end"].date() if event["all_day"] else event["end"]

        return CalendarEvent(
            summary=summary,
            start=start,
            end=end,
            description=", ".join(description_parts),
            uid=event["id"],
            location=", ".join(event.get("sites", [])),
        )
