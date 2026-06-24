"""Home Assistant integration for SMSPLANET."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
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
    SERVICE_BLACKLIST_ADD,
    SERVICE_BLACKLIST_REMOVE,
    SERVICE_CANCEL_MESSAGE,
    SERVICE_COUNT_SMS_PARTS,
    SERVICE_CREATE_SHORT_URL,
    SERVICE_GENERATE_REPORT,
    SERVICE_GET_MESSAGE_INFO,
    SERVICE_GET_INCOMING_SMS_WEBHOOK_URL,
    SERVICE_GET_SENDER_NAMES,
    SERVICE_LIST_SHORT_URLS,
    SERVICE_LIST_WEBHOOKS,
    SERVICE_REFRESH_DELIVERY_WEBHOOK,
    SERVICE_REMOVE_DELIVERY_WEBHOOK,
    SERVICE_REMOVE_SHORT_URL,
    SERVICE_REQUEST_SENDER_NAME,
    SERVICE_SEND_MMS,
    SERVICE_SEND_SMS,
)
from .webhook import (
    async_get_incoming_sms_webhook_url,
    async_register_smsplanet_webhook,
    async_unregister_smsplanet_webhook,
)

_LOGGER = logging.getLogger(__name__)

ATTR_CAMPAIGN_NAME = "campaign_name"
ATTR_LEGACY_CLEAR_POLISH = "clear_polish"
ATTR_LEGACY_NAME = "name"
ATTR_LEGACY_SENDER = "sender"
ATTR_LEGACY_TARGET = "target"
ATTR_LEGACY_TEST = "test"
ATTR_LEGACY_TRANSACTIONAL = "transactional"
ATTR_MESSAGE = "message"
ATTR_MESSAGE_ID = "message_id"
ATTR_MESSAGE_IDS = "message_ids"
ATTR_RECIPIENTS = "recipients"
ATTR_REPLACE_POLISH_CHARS = "replace_polish_chars"
ATTR_SENDER_NAME = "sender_name"
ATTR_SEND_AT = "send_at"
ATTR_SUBJECT = "subject"
ATTR_ATTACHMENT = "attachment"
ATTR_TEST_MODE = "test_mode"
ATTR_TRANSACTIONAL_CHANNEL = "transactional_channel"
ATTR_COMPANY_ID = "company_id"
ATTR_PERSONALIZATION_1 = "personalization_1"
ATTR_PERSONALIZATION_2 = "personalization_2"
ATTR_PERSONALIZATION_3 = "personalization_3"
ATTR_PERSONALIZATION_4 = "personalization_4"
ATTR_FROM_DATE = "from_date"
ATTR_TO_DATE = "to_date"
ATTR_DETAILED = "detailed"
ATTR_RESPONSE_TYPE = "response_type"
ATTR_PRODUCT = "product"
ATTR_PHONE_NUMBER = "phone_number"
ATTR_VALID_TO = "valid_to"
ATTR_LONG_URL = "long_url"
ATTR_SHORT_URL = "short_url"
ATTR_CUSTOM_ALIAS = "custom_alias"
ATTR_SAVE = "save"
ATTR_DOMAIN = "domain"
ATTR_ALIAS = "alias"
ATTR_ALIASES = "aliases"


class SmsplanetRuntimeData:
    """Runtime data for a SMSPLANET config entry."""

    def __init__(self, client: SmsplanetClient) -> None:
        """Initialize runtime data."""
        self.client = client


SmsplanetConfigEntry = ConfigEntry[SmsplanetRuntimeData]


SEND_SMS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_RECIPIENTS): vol.Any(cv.string, [cv.string]),
        vol.Optional(ATTR_SENDER_NAME): cv.string,
        vol.Optional(ATTR_REPLACE_POLISH_CHARS): cv.boolean,
        vol.Optional(ATTR_TRANSACTIONAL_CHANNEL): cv.boolean,
        vol.Optional(ATTR_TEST_MODE): cv.boolean,
        vol.Optional(ATTR_CAMPAIGN_NAME): cv.string,
        vol.Optional(ATTR_SEND_AT): cv.string,
        vol.Optional(ATTR_COMPANY_ID): cv.string,
        vol.Optional(ATTR_PERSONALIZATION_1): cv.string,
        vol.Optional(ATTR_PERSONALIZATION_2): cv.string,
        vol.Optional(ATTR_PERSONALIZATION_3): cv.string,
        vol.Optional(ATTR_PERSONALIZATION_4): cv.string,
        vol.Optional(ATTR_LEGACY_TARGET): vol.Any(cv.string, [cv.string]),
        vol.Optional(ATTR_LEGACY_SENDER): cv.string,
        vol.Optional(ATTR_LEGACY_CLEAR_POLISH): cv.boolean,
        vol.Optional(ATTR_LEGACY_TRANSACTIONAL): cv.boolean,
        vol.Optional(ATTR_LEGACY_TEST): cv.boolean,
        vol.Optional(ATTR_LEGACY_NAME): cv.string,
    }
)

COUNT_SMS_PARTS_SCHEMA = vol.Schema({vol.Required(ATTR_MESSAGE): cv.string})
SEND_MMS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Required(ATTR_SUBJECT): cv.string,
        vol.Required(ATTR_ATTACHMENT): cv.string,
        vol.Optional(ATTR_RECIPIENTS): vol.Any(cv.string, [cv.string]),
        vol.Optional(ATTR_SENDER_NAME): cv.string,
        vol.Optional(ATTR_REPLACE_POLISH_CHARS): cv.boolean,
        vol.Optional(ATTR_TEST_MODE): cv.boolean,
        vol.Optional(ATTR_SEND_AT): cv.string,
    }
)
CANCEL_MESSAGE_SCHEMA = vol.Schema({vol.Required(ATTR_MESSAGE_ID): cv.string})
REPORT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_FROM_DATE): cv.string,
        vol.Required(ATTR_TO_DATE): cv.string,
        vol.Optional(ATTR_DETAILED, default=False): cv.boolean,
        vol.Optional(ATTR_RESPONSE_TYPE, default="json"): vol.In(["json", "csv"]),
    }
)
MESSAGE_INFO_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MESSAGE_IDS): vol.Any(cv.string, [cv.string]),
        vol.Optional(ATTR_RESPONSE_TYPE, default="json"): vol.In(["json", "csv"]),
    }
)
SENDER_FIELDS_SCHEMA = vol.Schema({vol.Optional(ATTR_PRODUCT, default="SMS"): vol.In(["SMS", "2WAY", "MMS"])})
REQUEST_SENDER_SCHEMA = vol.Schema({vol.Required(ATTR_SENDER_NAME): cv.string})
BLACKLIST_ADD_SCHEMA = vol.Schema(
    {vol.Required(ATTR_PHONE_NUMBER): cv.string, vol.Optional(ATTR_VALID_TO): cv.string}
)
BLACKLIST_REMOVE_SCHEMA = vol.Schema({vol.Required(ATTR_PHONE_NUMBER): cv.string})
CREATE_SHORT_URL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_LONG_URL): cv.url,
        vol.Optional(ATTR_CUSTOM_ALIAS): cv.string,
        vol.Optional(ATTR_SAVE, default=False): cv.boolean,
        vol.Optional(ATTR_DOMAIN, default="wejdz.do"): vol.In(["wejdz.do", "link.do"]),
    }
)
LIST_SHORT_URLS_SCHEMA = vol.Schema({vol.Optional(ATTR_SHORT_URL): cv.string})
REMOVE_SHORT_URL_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ALIASES): vol.Any(cv.string, [cv.string])}
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up SMSPLANET integration services."""

    async def async_send_sms_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        client = entry.runtime_data.client
        recipients = _recipients_from_value(
            call.data.get(ATTR_RECIPIENTS)
            or call.data.get(ATTR_LEGACY_TARGET)
            or entry.options.get(CONF_DEFAULT_RECIPIENTS, [])
        )
        sender = (
            call.data.get(ATTR_SENDER_NAME)
            or call.data.get(ATTR_LEGACY_SENDER)
            or entry.options.get(CONF_DEFAULT_SENDER, DEFAULT_SENDER)
        )
        try:
            response = await client.async_send_sms(
                sender=sender,
                recipients=recipients,
                message=call.data[ATTR_MESSAGE],
                clear_polish=_get_bool_option(
                    call.data,
                    ATTR_REPLACE_POLISH_CHARS,
                    ATTR_LEGACY_CLEAR_POLISH,
                    entry.options.get(CONF_CLEAR_POLISH, False),
                ),
                transactional=_get_bool_option(
                    call.data,
                    ATTR_TRANSACTIONAL_CHANNEL,
                    ATTR_LEGACY_TRANSACTIONAL,
                    entry.options.get(CONF_TRANSACTIONAL, False),
                ),
                test=_get_bool_option(
                    call.data,
                    ATTR_TEST_MODE,
                    ATTR_LEGACY_TEST,
                    entry.options.get(CONF_TEST_MODE, False),
                ),
                name=call.data.get(ATTR_CAMPAIGN_NAME) or call.data.get(ATTR_LEGACY_NAME),
                send_at=call.data.get(ATTR_SEND_AT),
                company_id=call.data.get(ATTR_COMPANY_ID),
                params=[
                    call.data.get(ATTR_PERSONALIZATION_1, ""),
                    call.data.get(ATTR_PERSONALIZATION_2, ""),
                    call.data.get(ATTR_PERSONALIZATION_3, ""),
                    call.data.get(ATTR_PERSONALIZATION_4, ""),
                ],
            )
        except SmsplanetApiError as err:
            raise HomeAssistantError(f"SMSPLANET rejected SMS: {err}") from err
        except SmsplanetConnectionError as err:
            raise HomeAssistantError(f"Could not connect to SMSPLANET: {err}") from err

        _LOGGER.info("SMSPLANET accepted SMS message_id=%s", response.message_id)

    async def async_send_mms_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        recipients = _recipients_from_value(
            call.data.get(ATTR_RECIPIENTS) or entry.options.get(CONF_DEFAULT_RECIPIENTS, [])
        )
        try:
            response = await entry.runtime_data.client.async_send_mms(
                sender=call.data.get(ATTR_SENDER_NAME)
                or entry.options.get(CONF_DEFAULT_SENDER, DEFAULT_SENDER),
                recipients=recipients,
                subject=call.data[ATTR_SUBJECT],
                message=call.data[ATTR_MESSAGE],
                attachment=call.data[ATTR_ATTACHMENT],
                clear_polish=call.data.get(
                    ATTR_REPLACE_POLISH_CHARS, entry.options.get(CONF_CLEAR_POLISH, False)
                ),
                test=call.data.get(ATTR_TEST_MODE, entry.options.get(CONF_TEST_MODE, False)),
                send_at=call.data.get(ATTR_SEND_AT),
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET rejected MMS: {err}") from err

        _LOGGER.info("SMSPLANET accepted MMS message_id=%s", response.message_id)

    async def async_count_sms_parts_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            parts = await entry.runtime_data.client.async_count_sms_parts(call.data[ATTR_MESSAGE])
        except SmsplanetApiError as err:
            raise HomeAssistantError(f"SMSPLANET rejected SMS parts request: {err}") from err
        _LOGGER.info("SMSPLANET SMS parts count: %s", parts)
        return {"parts": parts}

    async def async_cancel_message_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            await entry.runtime_data.client.async_cancel_message(call.data[ATTR_MESSAGE_ID])
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not cancel message: {err}") from err

    async def async_generate_report_service(call: ServiceCall) -> dict[str, Any]:
        entry = _get_loaded_entry(hass)
        try:
            return await entry.runtime_data.client.async_generate_report(
                date_from=call.data[ATTR_FROM_DATE],
                date_to=call.data[ATTR_TO_DATE],
                detailed=call.data[ATTR_DETAILED],
                response_type=call.data[ATTR_RESPONSE_TYPE],
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not generate report: {err}") from err

    async def async_get_message_info_service(call: ServiceCall) -> dict[str, Any]:
        entry = _get_loaded_entry(hass)
        try:
            return await entry.runtime_data.client.async_get_message_info(
                message_ids=_list_from_value(call.data[ATTR_MESSAGE_IDS]),
                response_type=call.data[ATTR_RESPONSE_TYPE],
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not get message info: {err}") from err

    async def async_refresh_delivery_webhook_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            await entry.runtime_data.client.async_create_delivery_webhook(
                webhook.async_generate_url(hass, f"{DOMAIN}_{entry.entry_id}")
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not refresh webhook: {err}") from err

    async def async_remove_delivery_webhook_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            await entry.runtime_data.client.async_remove_delivery_webhook()
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not remove webhook: {err}") from err

    async def async_list_webhooks_service(call: ServiceCall) -> dict[str, Any]:
        entry = _get_loaded_entry(hass)
        try:
            return {"webhooks": await entry.runtime_data.client.async_list_webhooks()}
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not list webhooks: {err}") from err

    async def async_get_incoming_sms_webhook_url_service(call: ServiceCall) -> dict[str, Any]:
        entry = _get_loaded_entry(hass)
        return {"url": async_get_incoming_sms_webhook_url(hass, entry)}

    async def async_get_sender_names_service(call: ServiceCall) -> dict[str, Any]:
        entry = _get_loaded_entry(hass)
        try:
            return {
                "sender_names": await entry.runtime_data.client.async_get_sender_fields(
                    call.data[ATTR_PRODUCT]
                )
            }
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not get sender names: {err}") from err

    async def async_request_sender_name_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            await entry.runtime_data.client.async_add_sender_field(call.data[ATTR_SENDER_NAME])
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not request sender name: {err}") from err

    async def async_blacklist_add_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            await entry.runtime_data.client.async_add_to_blacklist(
                msisdn=call.data[ATTR_PHONE_NUMBER],
                valid_to=call.data.get(ATTR_VALID_TO),
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not add number to blacklist: {err}") from err

    async def async_blacklist_remove_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            await entry.runtime_data.client.async_remove_from_blacklist(call.data[ATTR_PHONE_NUMBER])
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(
                f"SMSPLANET could not remove number from blacklist: {err}"
            ) from err

    async def async_create_short_url_service(call: ServiceCall) -> dict[str, Any]:
        entry = _get_loaded_entry(hass)
        try:
            short_url = await entry.runtime_data.client.async_create_short_url(
                long_url=call.data[ATTR_LONG_URL],
                custom_alias=call.data.get(ATTR_CUSTOM_ALIAS),
                save=call.data[ATTR_SAVE],
                domain=call.data[ATTR_DOMAIN],
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not create short URL: {err}") from err
        return {"short_url": short_url}

    async def async_list_short_urls_service(call: ServiceCall) -> dict[str, Any]:
        entry = _get_loaded_entry(hass)
        try:
            links = await entry.runtime_data.client.async_list_short_urls(
                call.data.get(ATTR_SHORT_URL)
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not list short URLs: {err}") from err
        return {
            "links": [
                {
                    "date": link.date,
                    "short_url": link.short_url,
                    "long_url": link.long_url,
                    "clicks": link.clicks,
                    "raw": link.raw,
                }
                for link in links
            ]
        }

    async def async_remove_short_url_service(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass)
        try:
            await entry.runtime_data.client.async_remove_short_urls(
                _list_from_value(call.data[ATTR_ALIASES])
            )
        except (SmsplanetApiError, SmsplanetConnectionError) as err:
            raise HomeAssistantError(f"SMSPLANET could not remove short URL: {err}") from err

    hass.services.async_register(DOMAIN, SERVICE_SEND_SMS, async_send_sms_service, schema=SEND_SMS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SEND_MMS, async_send_mms_service, schema=SEND_MMS_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_COUNT_SMS_PARTS,
        async_count_sms_parts_service,
        schema=COUNT_SMS_PARTS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CANCEL_MESSAGE, async_cancel_message_service, schema=CANCEL_MESSAGE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_REPORT,
        async_generate_report_service,
        schema=REPORT_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_MESSAGE_INFO,
        async_get_message_info_service,
        schema=MESSAGE_INFO_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH_DELIVERY_WEBHOOK, async_refresh_delivery_webhook_service
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_DELIVERY_WEBHOOK, async_remove_delivery_webhook_service
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_WEBHOOKS,
        async_list_webhooks_service,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_INCOMING_SMS_WEBHOOK_URL,
        async_get_incoming_sms_webhook_url_service,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_SENDER_NAMES,
        async_get_sender_names_service,
        schema=SENDER_FIELDS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REQUEST_SENDER_NAME,
        async_request_sender_name_service,
        schema=REQUEST_SENDER_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_BLACKLIST_ADD, async_blacklist_add_service, schema=BLACKLIST_ADD_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_BLACKLIST_REMOVE,
        async_blacklist_remove_service,
        schema=BLACKLIST_REMOVE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_SHORT_URL,
        async_create_short_url_service,
        schema=CREATE_SHORT_URL_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_SHORT_URLS,
        async_list_short_urls_service,
        schema=LIST_SHORT_URLS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_SHORT_URL,
        async_remove_short_url_service,
        schema=REMOVE_SHORT_URL_SCHEMA,
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


def _list_from_value(value: Any) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def _get_bool_option(
    data: dict[str, Any],
    primary_key: str,
    legacy_key: str,
    default: bool,
) -> bool:
    """Return a boolean option, preserving old action field names as aliases."""
    if primary_key in data:
        return bool(data[primary_key])
    if legacy_key in data:
        return bool(data[legacy_key])
    return default
