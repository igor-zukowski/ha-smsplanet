"""Async SMSPLANET API client."""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
from collections.abc import Mapping, Sequence
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession
from async_timeout import timeout

from .const import API_BASE_URL, API_TIMEOUT, WEBHOOK_TYPE_MESSAGE_NOTIFICATION
from .models import BalanceResponse, DeliveryNotification, SendSmsResponse

_LOGGER = logging.getLogger(__name__)


class SmsplanetError(Exception):
    """Base SMSPLANET error."""


class SmsplanetApiError(SmsplanetError):
    """SMSPLANET returned an API-level error."""

    def __init__(self, message: str, code: int | None = None) -> None:
        """Initialize the API error."""
        super().__init__(message)
        self.code = code


class SmsplanetAuthError(SmsplanetApiError):
    """Authentication failed."""


class SmsplanetRateLimitError(SmsplanetApiError):
    """SMSPLANET API rate limit was reached."""


class SmsplanetConnectionError(SmsplanetError):
    """Connection to SMSPLANET failed."""


AUTH_ERROR_CODES = {101, 102, 200, 201, 202, 203}


class SmsplanetClient:
    """Minimal async client for SMSPLANET API v2."""

    def __init__(
        self,
        session: ClientSession,
        api_token: str,
        *,
        base_url: str = API_BASE_URL,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._api_token = api_token
        self._base_url = base_url.rstrip("/")

    async def async_validate_auth(self) -> None:
        """Validate API token with a low-cost authenticated endpoint."""
        await self.async_get_sender_fields()

    async def async_get_balance(self) -> BalanceResponse:
        """Fetch PrePaid account balance."""
        data = await self._request("POST", "/getBalance")
        try:
            return BalanceResponse(balance=int(data["balance"]))
        except (KeyError, TypeError, ValueError) as err:
            raise SmsplanetApiError("Invalid balance response") from err

    async def async_get_sender_fields(self, product: str = "SMS") -> list[str]:
        """Fetch available sender fields."""
        data = await self._request("POST", "/getSenderFields", data={"product": product})
        sender_fields = data.get("senderFields", "")
        if not isinstance(sender_fields, str):
            raise SmsplanetApiError("Invalid sender fields response")
        return [field.strip() for field in sender_fields.split(",") if field.strip()]

    async def async_send_sms(
        self,
        *,
        sender: str,
        recipients: Sequence[str],
        message: str,
        clear_polish: bool = False,
        transactional: bool = False,
        test: bool = False,
        name: str | None = None,
    ) -> SendSmsResponse:
        """Send an SMS message."""
        if not recipients:
            raise SmsplanetApiError("At least one recipient is required")

        form: list[tuple[str, str]] = [
            ("from", sender),
            ("msg", message),
            ("clear_polish", _bool_int(clear_polish)),
            ("transactional", _bool_int(transactional)),
            ("test", _bool_int(test)),
        ]
        form.extend(("to", recipient) for recipient in recipients)
        if name:
            form.append(("name", name))

        data = await self._request("POST", "/sms", data=form)
        message_id = data.get("messageId")
        if not isinstance(message_id, str) or not message_id:
            raise SmsplanetApiError("Invalid send SMS response")
        return SendSmsResponse(message_id=message_id)

    async def async_count_sms_parts(self, content: str) -> int:
        """Return the number of SMS parts for content."""
        data = await self._request_text("GET", "/sms/parts-count", params={"content": content})
        try:
            return int(data)
        except ValueError as err:
            raise SmsplanetApiError("Invalid SMS parts count response") from err

    async def async_create_delivery_webhook(self, url: str) -> None:
        """Create or replace the delivery notification webhook."""
        await self._request(
            "POST",
            "/webhooks/create",
            data={"url": url, "type": WEBHOOK_TYPE_MESSAGE_NOTIFICATION},
        )

    async def async_remove_delivery_webhook(self) -> None:
        """Remove the delivery notification webhook."""
        await self._request(
            "POST",
            "/webhooks/remove",
            data={"type": WEBHOOK_TYPE_MESSAGE_NOTIFICATION},
        )

    async def async_list_webhooks(self) -> list[dict[str, Any]]:
        """List configured SMSPLANET webhooks."""
        data = await self._request("GET", "/webhooks/list")
        webhooks = data.get("webhooks", [])
        if not isinstance(webhooks, list):
            raise SmsplanetApiError("Invalid webhook list response")
        return webhooks

    async def _request(
        self,
        method: str,
        path: str,
        *,
        data: Mapping[str, Any] | Sequence[tuple[str, str]] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform an API request and parse JSON response."""
        response = await self._request_json(method, path, data=data, params=params)
        if not isinstance(response, dict):
            raise SmsplanetApiError("Invalid API response")

        error_message = response.get("errorMsg")
        if error_message:
            code = _int_or_none(response.get("errorCode"))
            if code in AUTH_ERROR_CODES:
                raise SmsplanetAuthError(str(error_message), code)
            if code == 105:
                raise SmsplanetRateLimitError(str(error_message), code)
            raise SmsplanetApiError(str(error_message), code)

        return response

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        data: Mapping[str, Any] | Sequence[tuple[str, str]] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """Perform a request and decode JSON."""
        try:
            async with timeout(API_TIMEOUT):
                async with self._session.request(
                    method,
                    f"{self._base_url}{path}",
                    headers=self._headers,
                    data=data,
                    params=params,
                ) as response:
                    response.raise_for_status()
                    return await response.json(content_type=None)
        except ClientResponseError as err:
            if err.status == 429:
                raise SmsplanetRateLimitError("SMSPLANET API rate limit exceeded") from err
            raise SmsplanetConnectionError(f"HTTP error from SMSPLANET: {err.status}") from err
        except ClientError as err:
            raise SmsplanetConnectionError("Could not connect to SMSPLANET") from err
        except TimeoutError as err:
            raise SmsplanetConnectionError("Timed out connecting to SMSPLANET") from err

    async def _request_text(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> str:
        """Perform a request and return text response."""
        try:
            async with timeout(API_TIMEOUT):
                async with self._session.request(
                    method,
                    f"{self._base_url}{path}",
                    headers=self._headers,
                    params=params,
                ) as response:
                    response.raise_for_status()
                    return await response.text()
        except ClientResponseError as err:
            if err.status == 429:
                raise SmsplanetRateLimitError("SMSPLANET API rate limit exceeded") from err
            raise SmsplanetConnectionError(f"HTTP error from SMSPLANET: {err.status}") from err
        except ClientError as err:
            raise SmsplanetConnectionError("Could not connect to SMSPLANET") from err
        except TimeoutError as err:
            raise SmsplanetConnectionError("Timed out connecting to SMSPLANET") from err

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }


def verify_webhook_signature(raw_body: bytes, signature: str | None, signature_key: str) -> bool:
    """Verify SMSPLANET webhook HMAC SHA256 Base64 signature."""
    if not signature:
        return False
    digest = hmac.new(signature_key.encode(), raw_body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)


def parse_delivery_notification(payload: Mapping[str, Any]) -> DeliveryNotification:
    """Parse SMSPLANET delivery notification payload."""
    notification = payload.get("notification")
    if not isinstance(notification, dict):
        raise SmsplanetApiError("Missing notification payload")

    message_id = str(notification.get("messageId") or "")
    recipient = str(notification.get("to") or "")
    sender = str(notification.get("from") or "")
    if not message_id or not recipient:
        raise SmsplanetApiError("Invalid notification payload")

    return DeliveryNotification(
        message_id=message_id,
        recipient=recipient,
        sender=sender,
        delivered=_bool_from_api(notification.get("delivered")),
        parts=_int_or_none(notification.get("parts")),
        sent_date=_str_or_none(notification.get("sentDate")),
        delivery_date=_str_or_none(notification.get("deliveryDate")),
        delivery_error=_str_or_none(notification.get("deliveryError")),
        raw=dict(notification),
    )


def _bool_int(value: bool) -> str:
    return "1" if value else "0"


def _bool_from_api(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _str_or_none(value: Any) -> str | None:
    if value is None:
        return None
    value_str = str(value)
    return value_str or None
