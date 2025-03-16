"""Calendar platform for Celcat."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from datetime import datetime, time
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.translation import async_get_translations
from homeassistant.util import dt as dt_util

from . import CelcatConfigEntry
from .const import DOMAIN
from .coordinator import CelcatDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CelcatConfigEntry,
    async_add_entities: AddEntitiesCallback,
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

    for entity in entities:
        await entity.async_init_translations()


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
        self._attr_entity_registry_visible_default = (
            len(coordinator.data) == 1 or category != "all"
        )
        self.category = category
        self.translations = {}

    async def async_init_translations(self) -> None:
        """Initialize translations."""
        self.translations = await async_get_translations(
            self.hass,
            self.hass.config.language,
            category="entity",
            integrations=[DOMAIN],
        )

    def _get_translation(self, key: str) -> str:
        """Get translation with fallback to English."""
        return self.translations.get(
            f"component.{DOMAIN}.entity.calendar.{DOMAIN}.state_attributes.events.state.{key}",
            key.capitalize(),
        )

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
            key = "rooms" if len(event["rooms"]) > 1 else "room"
            description_parts.append(
                f"{self._get_translation(key)}: {', '.join(event['rooms'])}"
            )
        if event.get("professors"):
            key = "professors" if len(event["professors"]) > 1 else "professor"
            description_parts.append(
                f"{self._get_translation(key)}: {', '.join(professor.split()[0] for professor in event['professors'])}"
            )
        if event.get("sites"):
            key = "sites" if len(event["sites"]) > 1 else "site"
            description_parts.append(
                f"{self._get_translation(key)}: {', '.join(event['sites'])}"
            )
        if event.get("faculty"):
            description_parts.append(
                f"{self._get_translation('faculty')}: {event['faculty']}"
            )
        if event.get("notes"):
            description_parts.append(
                f"{self._get_translation('notes')}: {event['notes']}"
            )

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
