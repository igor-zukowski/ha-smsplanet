"""Constants for the SMSPLANET integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "smsplanet"

API_BASE_URL = "https://api2.smsplanet.pl"
API_TIMEOUT = 15

CONF_API_TOKEN = "api_token"
CONF_SIGNATURE_KEY = "signature_key"
CONF_DEFAULT_SENDER = "default_sender"
CONF_DEFAULT_RECIPIENTS = "default_recipients"
CONF_CLEAR_POLISH = "clear_polish"
CONF_TRANSACTIONAL = "transactional"
CONF_TEST_MODE = "test_mode"
CONF_ENABLE_DELIVERY_WEBHOOK = "enable_delivery_webhook"

DEFAULT_SENDER = "TEST"
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

EVENT_DELIVERY_STATUS = f"{DOMAIN}_delivery_status"
EVENT_INCOMING_SMS = f"{DOMAIN}_incoming_sms"

WEBHOOK_TYPE_MESSAGE_NOTIFICATION = "MESSAGE_NOTIFICATION_WEBHOOK"

PLATFORMS = ["sensor", "notify"]

SERVICE_SEND_SMS = "send_sms"
SERVICE_COUNT_SMS_PARTS = "count_sms_parts"

