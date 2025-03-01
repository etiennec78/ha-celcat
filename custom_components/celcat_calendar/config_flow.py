"""Config flow for the Celcat Calendar integration."""

from __future__ import annotations

import logging
from typing import Any

from celcat_scraper import (
    CelcatConfig,
    CelcatScraperAsync,
    CelcatCannotConnectError,
    CelcatInvalidAuthError,
)

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME, CONF_URL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, DEFAULT_NAME

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
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
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

    async def async_step_reconfigure(self, user_input: dict[str, Any]) -> ConfigFlowResult:
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
            data_schema=self.add_suggested_values_to_schema(STEP_USER_DATA_SCHEMA, data),
            errors=errors,
        )

    async def _validate_input(self, data: dict[str, Any]) -> dict[str, str]:
        """Validate the user input allows us to connect."""
        errors: dict[str, str] = {}

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
