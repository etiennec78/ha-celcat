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
from .const import (
    ATTRIBUTES_SINGULAR,
    CONF_DESCRIPTION,
    CONF_TITLE,
    DEFAULT_DESCRIPTION,
    DEFAULT_TITLE,
    DOMAIN,
)
from .coordinator import CelcatDataUpdateCoordinator
from .util import get_translation

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CelcatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the celcat calendar platform."""
    coordinator = entry.runtime_data.coordinator

    translations = await async_get_translations(
        hass,
        hass.config.language,
        category="selector",
        integrations=[DOMAIN],
    )

    entities = [
        CelcatCalendarEntity(coordinator, entry, category, translations)
        for category in coordinator.data
    ]
    async_add_entities(entities, True)


class CelcatCalendarEntity(CalendarEntity):
    """A calendar entity by Celcat."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CelcatDataUpdateCoordinator,
        entry: CelcatConfigEntry,
        category: str,
        translations: dict[str, str],
    ) -> None:
        """Initialize Celcat."""
        self.coordinator = coordinator
        self.entry = entry
        self._attr_unique_id = (
            entry.entry_id + (f"-{category}" if category != "all" else "") + "-calendar"
        )
        self._attr_has_entity_name = True
        self._attr_name = None if category == "all" else category
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Celcat",
        )
        self._attr_entity_registry_visible_default = (
            len(coordinator.data) == 1 or category != "all"
        )
        self.category = category
        self.translations = translations

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
        title_parts = self._assemble_attributes(
            event,
            self.entry.options.get(
                CONF_TITLE,
                DEFAULT_TITLE,
            ),
            include_names=False,
        )

        description_parts = self._assemble_attributes(
            event,
            self.entry.options.get(
                CONF_DESCRIPTION,
                DEFAULT_DESCRIPTION,
            ),
            include_names=True,
        )

        start = event["start"].date() if event["all_day"] else event["start"]
        end = event["end"].date() if event["all_day"] else event["end"]

        return CalendarEvent(
            summary=" ".join(title_parts),
            start=start,
            end=end,
            description=", ".join(description_parts),
            uid=event["id"],
            location=", ".join(event.get("sites", [])),
        )

    def _assemble_attributes(
        self, event: dict[str, Any], attributes: list[str], include_names: bool
    ) -> list[str]:
        parts = []
        for attribute in attributes:
            if event.get(attribute):
                if (
                    type(event[attribute]) == list
                    and len(event[attribute]) == 1
                    and attribute in ATTRIBUTES_SINGULAR
                ):
                    key = ATTRIBUTES_SINGULAR[attribute]
                else:
                    key = attribute

                prefix = (
                    f"{get_translation(self.translations, key)}: "
                    if include_names
                    else ""
                )
                if type(event[attribute]) == list:
                    parts.append(f"{prefix}{', '.join(event[attribute])}")
                else:
                    parts.append(f"{prefix}{event[attribute]}")

        if not parts:
            parts = ["Unknown"]

        return parts
