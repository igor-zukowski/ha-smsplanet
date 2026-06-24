"""Data models for SMSPLANET."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SendSmsResponse:
    """Response returned after sending an SMS."""

    message_id: str

    @property
    def buffered(self) -> bool:
        """Return whether the message was accepted into SMSPLANET queue buffer."""
        return self.message_id.startswith("B-")


@dataclass(frozen=True, slots=True)
class SendMmsResponse:
    """Response returned after sending an MMS."""

    message_id: str

    @property
    def buffered(self) -> bool:
        """Return whether the message was accepted into SMSPLANET queue buffer."""
        return self.message_id.startswith("B-")


@dataclass(frozen=True, slots=True)
class BalanceResponse:
    """PrePaid account balance response."""

    balance: int


@dataclass(frozen=True, slots=True)
class DeliveryNotification:
    """Delivery notification sent by SMSPLANET webhook."""

    message_id: str
    recipient: str
    sender: str
    delivered: bool
    parts: int | None
    sent_date: str | None
    delivery_date: str | None
    delivery_error: str | None
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ShortUrlInfo:
    """Short URL information returned by SMSPLANET."""

    date: str | None
    short_url: str
    long_url: str | None
    clicks: int | None
    raw: dict[str, Any]
