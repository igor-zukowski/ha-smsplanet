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
SERVICE_SEND_MMS = "send_mms"
SERVICE_COUNT_SMS_PARTS = "count_sms_parts"
SERVICE_CANCEL_MESSAGE = "cancel_message"
SERVICE_GENERATE_REPORT = "generate_report"
SERVICE_GET_MESSAGE_INFO = "get_message_info"
SERVICE_REFRESH_DELIVERY_WEBHOOK = "refresh_delivery_webhook"
SERVICE_REMOVE_DELIVERY_WEBHOOK = "remove_delivery_webhook"
SERVICE_LIST_WEBHOOKS = "list_webhooks"
SERVICE_GET_INCOMING_SMS_WEBHOOK_URL = "get_incoming_sms_webhook_url"
SERVICE_REQUEST_SENDER_NAME = "request_sender_name"
SERVICE_GET_SENDER_NAMES = "get_sender_names"
SERVICE_BLACKLIST_ADD = "blacklist_add"
SERVICE_BLACKLIST_REMOVE = "blacklist_remove"
SERVICE_CREATE_SHORT_URL = "create_short_url"
SERVICE_LIST_SHORT_URLS = "list_short_urls"
SERVICE_REMOVE_SHORT_URL = "remove_short_url"
