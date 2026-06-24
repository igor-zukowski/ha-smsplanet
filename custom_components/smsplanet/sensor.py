"""Sensors for SMSPLANET."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .api import SmsplanetError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

if TYPE_CHECKING:
    from . import SmsplanetConfigEntry

_LOGGER = logging.getLogger(__name__)


BALANCE_DESCRIPTION = SensorEntityDescription(
    key="balance",
    translation_key="balance",
    icon="mdi:counter",
    native_unit_of_measurement="pts",
    state_class=SensorStateClass.MEASUREMENT,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmsplanetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SMSPLANET sensors."""

    async def async_update_data() -> int:
        try:
            return (await entry.runtime_data.client.async_get_balance()).balance
        except SmsplanetError as err:
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        logger=_LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}_balance",
        update_method=async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
        always_update=False,
    )
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([SmsplanetBalanceSensor(entry, coordinator)])


class SmsplanetBalanceSensor(CoordinatorEntity[DataUpdateCoordinator[int]], SensorEntity):
    """SMSPLANET PrePaid balance sensor."""

    entity_description = BALANCE_DESCRIPTION
    _attr_has_entity_name = True

    def __init__(
        self,
        entry: SmsplanetConfigEntry,
        coordinator: DataUpdateCoordinator[int],
    ) -> None:
        """Initialize the balance sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_balance"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "SMSPLANET",
        }

    @property
    def native_value(self) -> int | None:
        """Return current PrePaid balance."""
        return self.coordinator.data
