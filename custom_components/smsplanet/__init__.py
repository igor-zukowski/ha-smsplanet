"""Home Assistant integration for SMSPLANET."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SmsplanetApiError, SmsplanetAuthError, SmsplanetClient, SmsplanetConnectionError
from .const import (
    CONF_API_TOKEN,
    CONF_CLEAR_POLISH,
    CONF_DEFAULT_RECIPIENTS,
    CONF_DEFAULT_SENDER,
    CONF_ENABLE_DELIVERY_WEBHOOK,
    CONF_TEST_MODE,
    CONF_TRANSACTIONAL,
    DEFAULT_SENDER,
    DOMAIN,
    PLATFORMS,
    SERVICE_COUNT_SMS_PARTS,
    SERVICE_SEND_SMS,
)
from .webhook import async_register_smsplanet_webhook, async_unregister_smsplanet_webhook

_LOGGER = logging.getLogger(__name__)


class SmsplanetRuntimeData:
    """Runtime data for a SMSPLANET config entry."""

    def __init__(self, client: SmsplanetClient) -> None:
        """Initialize runtime data."""
        self.client = client


SmsplanetConfigEntry = ConfigEntry[SmsplanetRuntimeData]


SEND_SMS_SCHEMA = vol.Schema(
    {
        vol.Required("message"): cv.string,
        vol.Optional("target"): vol.Any(cv.string, [cv.string]),
        vol.Optional("sender"): cv.string,
        vol.Optional("clear_polish"): cv.boolean,
        vol.Optional("transactional"): cv.boolean,
        vol.Optional("test"): cv.boolean,
        vol.Optional("name"): cv.string,
    }
)

COUNT_SMS_PARTS_SCHEMA = vol.Schema({vol.Required("message"): cv.string})


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up SMSPLANET integration services."""

    async def async_send_sms_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        client = entry.runtime_data.client
        recipients = _recipients_from_value(
            call.data.get("target") or entry.options.get(CONF_DEFAULT_RECIPIENTS, [])
        )
        sender = call.data.get("sender") or entry.options.get(CONF_DEFAULT_SENDER, DEFAULT_SENDER)
        try:
            response = await client.async_send_sms(
                sender=sender,
                recipients=recipients,
                message=call.data["message"],
                clear_polish=call.data.get(
                    "clear_polish", entry.options.get(CONF_CLEAR_POLISH, False)
                ),
                transactional=call.data.get(
                    "transactional", entry.options.get(CONF_TRANSACTIONAL, False)
                ),
                test=call.data.get("test", entry.options.get(CONF_TEST_MODE, False)),
                name=call.data.get("name"),
            )
        except SmsplanetApiError as err:
            raise HomeAssistantError(f"SMSPLANET rejected SMS: {err}") from err
        except SmsplanetConnectionError as err:
            raise HomeAssistantError(f"Could not connect to SMSPLANET: {err}") from err

        _LOGGER.info("SMSPLANET accepted SMS message_id=%s", response.message_id)

    async def async_count_sms_parts_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            parts = await entry.runtime_data.client.async_count_sms_parts(call.data["message"])
        except SmsplanetApiError as err:
            raise HomeAssistantError(f"SMSPLANET rejected SMS parts request: {err}") from err
        _LOGGER.info("SMSPLANET SMS parts count: %s", parts)

    hass.services.async_register(DOMAIN, SERVICE_SEND_SMS, async_send_sms_service, schema=SEND_SMS_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_COUNT_SMS_PARTS,
        async_count_sms_parts_service,
        schema=COUNT_SMS_PARTS_SCHEMA,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SmsplanetConfigEntry) -> bool:
    """Set up SMSPLANET from a config entry."""
    session = async_get_clientsession(hass)
    client = SmsplanetClient(session, entry.data[CONF_API_TOKEN])

    try:
        await client.async_validate_auth()
    except SmsplanetAuthError as err:
        raise ConfigEntryAuthFailed(str(err)) from err
    except SmsplanetConnectionError as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = SmsplanetRuntimeData(client)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if entry.options.get(CONF_ENABLE_DELIVERY_WEBHOOK, True):
        await async_register_smsplanet_webhook(hass, entry)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SmsplanetConfigEntry) -> bool:
    """Unload a SMSPLANET config entry."""
    await async_unregister_smsplanet_webhook(hass, entry)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: SmsplanetConfigEntry) -> None:
    """Handle options updates."""
    await hass.config_entries.async_reload(entry.entry_id)


def _get_loaded_entry(hass: HomeAssistant) -> SmsplanetConfigEntry:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError("SMSPLANET integration is not loaded")
    return entries[0]


def _recipients_from_value(value: Any) -> list[str]:
    if isinstance(value, str):
        recipients = [item.strip() for item in value.split(",")]
    else:
        recipients = [str(item).strip() for item in value]
    recipients = [item for item in recipients if item]
    if not recipients:
        raise ServiceValidationError("At least one SMS recipient is required")
    return recipients
