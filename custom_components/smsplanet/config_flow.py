"""Config flow for SMSPLANET."""

from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SmsplanetAuthError, SmsplanetClient, SmsplanetConnectionError, SmsplanetError
from .const import (
    CONF_API_TOKEN,
    CONF_CLEAR_POLISH,
    CONF_DEFAULT_RECIPIENTS,
    CONF_DEFAULT_SENDER,
    CONF_ENABLE_DELIVERY_WEBHOOK,
    CONF_SIGNATURE_KEY,
    CONF_TEST_MODE,
    CONF_TRANSACTIONAL,
    DEFAULT_SENDER,
    DOMAIN,
)


class SmsplanetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMSPLANET."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            token = user_input[CONF_API_TOKEN]
            client = SmsplanetClient(async_get_clientsession(self.hass), token)
            try:
                sender_fields = await client.async_get_sender_fields()
            except SmsplanetAuthError:
                errors["base"] = "invalid_auth"
            except SmsplanetConnectionError:
                errors["base"] = "cannot_connect"
            except SmsplanetError:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(_unique_id_from_token(token))
                self._abort_if_unique_id_configured()

                default_sender = (
                    DEFAULT_SENDER
                    if DEFAULT_SENDER in sender_fields
                    else sender_fields[0]
                    if sender_fields
                    else DEFAULT_SENDER
                )
                return self.async_create_entry(
                    title="SMSPLANET",
                    data={
                        CONF_API_TOKEN: token,
                        CONF_SIGNATURE_KEY: user_input.get(CONF_SIGNATURE_KEY, ""),
                    },
                    options={
                        CONF_DEFAULT_SENDER: default_sender,
                        CONF_DEFAULT_RECIPIENTS: [],
                        CONF_CLEAR_POLISH: False,
                        CONF_TRANSACTIONAL: False,
                        CONF_TEST_MODE: False,
                        CONF_ENABLE_DELIVERY_WEBHOOK: True,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): str,
                    vol.Optional(CONF_SIGNATURE_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle reauth request."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reauth confirmation."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            token = user_input[CONF_API_TOKEN]
            client = SmsplanetClient(async_get_clientsession(self.hass), token)
            try:
                await client.async_validate_auth()
            except SmsplanetAuthError:
                errors["base"] = "invalid_auth"
            except SmsplanetConnectionError:
                errors["base"] = "cannot_connect"
            except SmsplanetError:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_API_TOKEN: token},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_TOKEN): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return SmsplanetOptionsFlow(config_entry)


class SmsplanetOptionsFlow(config_entries.OptionsFlow):
    """Handle SMSPLANET options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_DEFAULT_SENDER: user_input[CONF_DEFAULT_SENDER],
                    CONF_DEFAULT_RECIPIENTS: _recipients_from_csv(
                        user_input.get(CONF_DEFAULT_RECIPIENTS, "")
                    ),
                    CONF_CLEAR_POLISH: user_input[CONF_CLEAR_POLISH],
                    CONF_TRANSACTIONAL: user_input[CONF_TRANSACTIONAL],
                    CONF_TEST_MODE: user_input[CONF_TEST_MODE],
                    CONF_ENABLE_DELIVERY_WEBHOOK: user_input[CONF_ENABLE_DELIVERY_WEBHOOK],
                },
            )

        options = self._config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEFAULT_SENDER,
                        default=options.get(CONF_DEFAULT_SENDER, DEFAULT_SENDER),
                    ): cv.string,
                    vol.Optional(
                        CONF_DEFAULT_RECIPIENTS,
                        default=", ".join(options.get(CONF_DEFAULT_RECIPIENTS, [])),
                    ): cv.string,
                    vol.Required(
                        CONF_CLEAR_POLISH,
                        default=options.get(CONF_CLEAR_POLISH, False),
                    ): cv.boolean,
                    vol.Required(
                        CONF_TRANSACTIONAL,
                        default=options.get(CONF_TRANSACTIONAL, False),
                    ): cv.boolean,
                    vol.Required(
                        CONF_TEST_MODE,
                        default=options.get(CONF_TEST_MODE, False),
                    ): cv.boolean,
                    vol.Required(
                        CONF_ENABLE_DELIVERY_WEBHOOK,
                        default=options.get(CONF_ENABLE_DELIVERY_WEBHOOK, True),
                    ): cv.boolean,
                }
            ),
        )


def _unique_id_from_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:16]


def _recipients_from_csv(value: str) -> list[str]:
    return [recipient.strip() for recipient in value.split(",") if recipient.strip()]

