"""Webhook handling for SMSPLANET."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from aiohttp import web

from homeassistant.components import webhook
from homeassistant.core import HomeAssistant

from .api import SmsplanetApiError, parse_delivery_notification, verify_webhook_signature
from .const import CONF_SIGNATURE_KEY, DOMAIN, EVENT_DELIVERY_STATUS

if TYPE_CHECKING:
    from . import SmsplanetConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_register_smsplanet_webhook(hass: HomeAssistant, entry: SmsplanetConfigEntry) -> None:
    """Register HA webhook and configure SMSPLANET delivery webhook."""
    webhook_id = _webhook_id(entry)
    webhook.async_register(
        hass,
        DOMAIN,
        "SMSPLANET",
        webhook_id,
        _handle_webhook,
        allowed_methods=("POST",),
    )

    public_url = webhook.async_generate_url(hass, webhook_id)
    try:
        await entry.runtime_data.client.async_create_delivery_webhook(public_url)
    except SmsplanetApiError as err:
        _LOGGER.warning("Could not configure SMSPLANET delivery webhook: %s", err)


async def async_unregister_smsplanet_webhook(hass: HomeAssistant, entry: SmsplanetConfigEntry) -> None:
    """Remove HA webhook registration."""
    webhook.async_unregister(hass, _webhook_id(entry))


async def _handle_webhook(hass: HomeAssistant, webhook_id: str, request: web.Request) -> web.Response:
    """Handle incoming SMSPLANET webhook request."""
    entry = _entry_from_webhook_id(hass, webhook_id)
    if entry is None:
        return web.Response(status=404)

    raw_body = await request.read()
    signature_key = entry.data.get(CONF_SIGNATURE_KEY)
    if signature_key and not verify_webhook_signature(
        raw_body,
        request.headers.get("Signature"),
        signature_key,
    ):
        _LOGGER.warning("Rejected SMSPLANET webhook with invalid signature")
        return web.Response(status=401)

    try:
        payload = json.loads(raw_body.decode("utf-8"))
        notification = parse_delivery_notification(payload)
    except (json.JSONDecodeError, UnicodeDecodeError, SmsplanetApiError) as err:
        _LOGGER.warning("Rejected malformed SMSPLANET webhook payload: %s", err)
        return web.Response(status=400)

    hass.bus.async_fire(
        EVENT_DELIVERY_STATUS,
        {
            "message_id": notification.message_id,
            "recipient": notification.recipient,
            "sender": notification.sender,
            "delivered": notification.delivered,
            "parts": notification.parts,
            "sent_date": notification.sent_date,
            "delivery_date": notification.delivery_date,
            "delivery_error": notification.delivery_error,
            "raw": notification.raw,
        },
    )
    return web.Response(status=200)


def _webhook_id(entry: SmsplanetConfigEntry) -> str:
    return f"{DOMAIN}_{entry.entry_id}"


def _entry_from_webhook_id(hass: HomeAssistant, webhook_id: str) -> SmsplanetConfigEntry | None:
    for entry in hass.config_entries.async_loaded_entries(DOMAIN):
        if _webhook_id(entry) == webhook_id:
            return entry
    return None
