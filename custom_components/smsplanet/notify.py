"""Notify entity for SMSPLANET."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.notify import NotifyEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SmsplanetApiError, SmsplanetConnectionError
from .const import (
    CONF_CLEAR_POLISH,
    CONF_DEFAULT_RECIPIENTS,
    CONF_DEFAULT_SENDER,
    CONF_TEST_MODE,
    CONF_TRANSACTIONAL,
    DEFAULT_SENDER,
    DOMAIN,
)

if TYPE_CHECKING:
    from . import SmsplanetConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmsplanetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SMSPLANET notify entity."""
    async_add_entities([SmsplanetNotifyEntity(entry)])


class SmsplanetNotifyEntity(NotifyEntity):
    """SMSPLANET SMS notifier."""

    _attr_has_entity_name = True
    _attr_translation_key = "sms"
    _attr_icon = "mdi:message-text"

    def __init__(self, entry: SmsplanetConfigEntry) -> None:
        """Initialize the notifier."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_notify"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "SMSPLANET",
        }

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send a message using default recipients from integration options."""
        recipients = self._entry.options.get(CONF_DEFAULT_RECIPIENTS, [])
        if not recipients:
            raise ServiceValidationError(
                "Default recipients are required to use notify.smsplanet; use smsplanet.send_sms to pass target recipients"
            )

        try:
            await self._entry.runtime_data.client.async_send_sms(
                sender=self._entry.options.get(CONF_DEFAULT_SENDER, DEFAULT_SENDER),
                recipients=list(recipients),
                message=message,
                clear_polish=self._entry.options.get(CONF_CLEAR_POLISH, False),
                transactional=self._entry.options.get(CONF_TRANSACTIONAL, False),
                test=self._entry.options.get(CONF_TEST_MODE, False),
                name=title,
            )
        except SmsplanetApiError as err:
            raise HomeAssistantError(f"SMSPLANET rejected SMS: {err}") from err
        except SmsplanetConnectionError as err:
            raise HomeAssistantError(f"Could not connect to SMSPLANET: {err}") from err

        self._async_record_notification()
