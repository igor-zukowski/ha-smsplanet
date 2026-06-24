"""Tests for the SMSPLANET API client helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import sys
import types
from pathlib import Path

import pytest

if "aiohttp" not in sys.modules:
    aiohttp = types.ModuleType("aiohttp")

    class ClientError(Exception):
        """aiohttp.ClientError test stub."""

    class ClientResponseError(Exception):
        """aiohttp.ClientResponseError test stub."""

        def __init__(self, *args: object, status: int = 0, **kwargs: object) -> None:
            super().__init__(*args)
            self.status = status

    class ClientSession:
        """aiohttp.ClientSession test stub."""

    aiohttp.ClientError = ClientError
    aiohttp.ClientResponseError = ClientResponseError
    aiohttp.ClientSession = ClientSession
    sys.modules["aiohttp"] = aiohttp

if "async_timeout" not in sys.modules:
    import asyncio

    async_timeout = types.ModuleType("async_timeout")
    async_timeout.timeout = asyncio.timeout
    sys.modules["async_timeout"] = async_timeout

SMSPLANET_PATH = Path(__file__).parents[1] / "custom_components" / "smsplanet"
package = types.ModuleType("custom_components.smsplanet")
package.__path__ = [str(SMSPLANET_PATH)]
sys.modules.setdefault("custom_components.smsplanet", package)

from custom_components.smsplanet.api import (
    SmsplanetAuthError,
    SmsplanetClient,
    parse_delivery_notification,
    verify_webhook_signature,
)


def test_verify_webhook_signature() -> None:
    """Verify HMAC signature matches SMSPLANET documentation."""
    body = (
        b'{"notification":{"deliveryError":"","sentDate":"24-05-2024 11:45:24",'
        b'"parts":"1","messageId":"1234567","from":"AUTO HANDEL",'
        b'"delivered":"true","to":"600700800","deliveryDate":"24-05-2024 11:45:30"}}'
    )
    key = "3e13a3d9d531cdb791b96b01b733f27c"
    signature = base64.b64encode(hmac.new(key.encode(), body, hashlib.sha256).digest()).decode()

    assert signature == "Upe2XxZCyeQyqADt0RuQ4l8RtWgjaSlKzyB7ogGjs4g="
    assert verify_webhook_signature(body, signature, key)
    assert not verify_webhook_signature(body + b" ", signature, key)


def test_parse_delivery_notification() -> None:
    """Parse a delivery webhook payload."""
    notification = parse_delivery_notification(
        {
            "notification": {
                "deliveryError": "",
                "sentDate": "24-05-2024 11:45:24",
                "parts": "1",
                "messageId": "1234567",
                "from": "AUTO HANDEL",
                "delivered": "true",
                "to": "600700800",
                "deliveryDate": "24-05-2024 11:45:30",
            }
        }
    )

    assert notification.message_id == "1234567"
    assert notification.recipient == "600700800"
    assert notification.sender == "AUTO HANDEL"
    assert notification.delivered is True
    assert notification.parts == 1


@pytest.mark.asyncio
async def test_send_sms_posts_repeated_recipients() -> None:
    """Send SMS uses repeated `to` form fields."""
    session = FakeSession({"messageId": "191919"})
    client = SmsplanetClient(session, "token", base_url="https://example.invalid")

    response = await client.async_send_sms(
        sender="TEST",
        recipients=["600111222", "700333444"],
        message="Hello",
    )

    assert response.message_id == "191919"
    assert session.calls[0]["data"].count(("to", "600111222")) == 1
    assert session.calls[0]["data"].count(("to", "700333444")) == 1


@pytest.mark.asyncio
async def test_api_auth_error_mapping() -> None:
    """Authentication API errors are mapped to auth exceptions."""
    session = FakeSession({"errorMsg": "Nieprawidlowy token", "errorCode": 201})
    client = SmsplanetClient(session, "token", base_url="https://example.invalid")

    with pytest.raises(SmsplanetAuthError):
        await client.async_get_sender_fields()


class FakeResponse:
    """Small aiohttp response test double."""

    def __init__(self, payload: object) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        """Fake status validation."""

    async def json(self, content_type: str | None = None) -> object:
        """Return JSON payload."""
        return self._payload

    async def text(self) -> str:
        """Return text payload."""
        return str(self._payload)


class FakeRequestContext:
    """Async context manager returned by fake session."""

    def __init__(self, response: FakeResponse) -> None:
        self._response = response

    async def __aenter__(self) -> FakeResponse:
        return self._response

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class FakeSession:
    """Small aiohttp session test double."""

    def __init__(self, payload: object) -> None:
        self._payload = payload
        self.calls: list[dict[str, object]] = []

    def request(self, method: str, url: str, **kwargs: object) -> FakeRequestContext:
        """Record request and return fake response."""
        self.calls.append({"method": method, "url": url, **kwargs})
        return FakeRequestContext(FakeResponse(self._payload))
