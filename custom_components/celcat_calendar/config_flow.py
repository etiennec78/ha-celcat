"""Config flow for the Celcat Calendar integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from celcat_scraper import (
    CelcatCannotConnectError,
    CelcatConfig,
    CelcatInvalidAuthError,
    CelcatScraperAsync,
    FilterType,
)

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    CONF_FILTERS,
    CONF_GROUP_BY,
    CONF_REPLACEMENTS,
    CONF_SHOW_HOLIDAYS,
    DEFAULT_FILTERS,
    DEFAULT_GROUP_BY,
    DEFAULT_NAME,
    DEFAULT_REPLACEMENTS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SHOW_HOLIDAYS,
    DOMAIN,
    GROUP_BY_CATEGORY,
    GROUP_BY_CATEGORY_COURSE,
    GROUP_BY_COURSE,
    GROUP_BY_OFF,
)
from .util import list_to_dict

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_URL): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        vol.Optional(
            CONF_SHOW_HOLIDAYS, default=DEFAULT_SHOW_HOLIDAYS
        ): BooleanSelector(),
        vol.Optional(CONF_GROUP_BY, default=DEFAULT_GROUP_BY): SelectSelector(
            SelectSelectorConfig(
                options=[
                    GROUP_BY_OFF,
                    GROUP_BY_COURSE,
                    GROUP_BY_CATEGORY,
                    GROUP_BY_CATEGORY_COURSE,
                ],
                translation_key=CONF_GROUP_BY,
            )
        ),
        vol.Optional(CONF_FILTERS, default=DEFAULT_FILTERS): SelectSelector(
            SelectSelectorConfig(
                options=[filter_type.value for filter_type in FilterType],
                translation_key=CONF_FILTERS,
                multiple=True,
            )
        ),
        vol.Optional(CONF_REPLACEMENTS, default=DEFAULT_REPLACEMENTS): SelectSelector(
            SelectSelectorConfig(
                options=[],
                multiple=True,
                custom_value=True,
            )
        ),
    }
)


class CelcatConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Celcat Calendar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME].lower()
            await self.async_set_unique_id(username)
            self._abort_if_unique_id_configured()

            if not (errors := await self._validate_input(user_input)):
                self.data = user_input
                return await self.async_step_options()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle options setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await list_to_dict(
                    user_input.get(CONF_REPLACEMENTS, DEFAULT_REPLACEMENTS)
                )
                return self.async_create_entry(
                    title=self.data[CONF_NAME],
                    data=self.data,
                    options=user_input
                )
            except ValueError:
                errors[CONF_REPLACEMENTS] = "invalid_replacements_value"

        return self.async_show_form(
            step_id="options",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, {}
            ),
            errors=errors,
            description_placeholders={
                "name": self.data[CONF_NAME],
            },
        )

    async def async_step_reauth(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauth confirm."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if not (errors := await self._validate_input(user_input)):
                return self.async_update_reload_and_abort(
                    self.reauth_entry,
                    data={
                        **self.reauth_entry.data,
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                    reason="reauth_successful",
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            username = user_input[CONF_USERNAME].lower()
            await self.async_set_unique_id(username)
            self._abort_if_unique_id_mismatch()

            if not (errors := await self._validate_input(user_input)):
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data_updates=user_input,
                )

        data = reconfigure_entry.data.copy()
        data[CONF_PASSWORD] = ""
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, data
            ),
            errors=errors,
        )

    async def _validate_input(self, data: dict[str, Any]) -> dict[str, str]:
        """Validate the user input allows us to connect."""
        errors: dict[str, str] = {}

        await self._strip_url(data)

        try:
            celcat = CelcatScraperAsync(
                CelcatConfig(
                    url=data[CONF_URL],
                    username=data[CONF_USERNAME],
                    password=data[CONF_PASSWORD],
                    rate_limit=0.1,
                    session=async_get_clientsession(self.hass),
                )
            )
            await celcat.login()

        except ValueError:
            errors["base"] = "invalid_url"
        except CelcatInvalidAuthError:
            errors["base"] = "invalid_auth"
        except CelcatCannotConnectError:
            errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        finally:
            await celcat.close()

        return errors

    async def _strip_url(self, data) -> None:
        """Strip the URL to get the base URL."""
        data[CONF_URL] = data[CONF_URL].split("?")[0].rstrip("/")
        for suffix in ["/cal", "/LdapLogin"]:
            if data[CONF_URL].endswith(suffix):
                data[CONF_URL] = data[CONF_URL][: -len(suffix)]
                break

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await list_to_dict(
                    user_input.get(CONF_REPLACEMENTS, DEFAULT_REPLACEMENTS)
                )
            except ValueError:
                errors[CONF_REPLACEMENTS] = "invalid_replacements_value"

            if not errors:
                old_group_by = self.config_entry.options.get(
                    CONF_GROUP_BY, DEFAULT_GROUP_BY
                )
                new_group_by = user_input.get(CONF_GROUP_BY, DEFAULT_GROUP_BY)

                old_filters = self.config_entry.options.get(
                    CONF_FILTERS, DEFAULT_FILTERS
                )
                new_filters = user_input.get(CONF_FILTERS, DEFAULT_FILTERS)

                old_replacements = self.config_entry.options.get(
                    CONF_REPLACEMENTS, DEFAULT_REPLACEMENTS
                )
                new_replacements = user_input.get(
                    CONF_REPLACEMENTS, DEFAULT_REPLACEMENTS
                )

                filters_removed = False
                for old_filter in old_filters:
                    if old_filter not in new_filters:
                        filters_removed = True
                        break

                if filters_removed:
                    _LOGGER.info(
                        "A data filter has been removed, resetting stored data"
                    )
                    store = self.config_entry.runtime_data.store

                    await store.async_save([])

                if (
                    old_group_by != new_group_by
                    or old_filters != new_filters
                    or old_replacements != new_replacements
                ):
                    _LOGGER.info("Reorganizing calendar entities")

                    entity_registry = er.async_get(self.hass)

                    entities = er.async_entries_for_config_entry(
                        entity_registry, self.config_entry.entry_id
                    )

                    for entity in entities:
                        if entity.domain == "calendar":
                            entity_registry.async_remove(entity.entity_id)

                self.hass.config_entries.async_update_entry(
                    self.config_entry, options=user_input
                )

                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self.config_entry.entry_id)
                )

                return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
            errors=errors,
        )
