# SMSPLANET for Home Assistant

Custom Home Assistant integration for SMSPLANET.

## MVP features

- UI configuration flow with API token authentication.
- PrePaid balance sensor.
- `notify` entity for sending SMS to configured default recipients.
- `smsplanet.send_sms` action for sending SMS to explicit recipients.
- Home Assistant webhook for SMSPLANET delivery status notifications.
- `smsplanet_delivery_status` events on the Home Assistant event bus.

## Usage

Install the integration through HACS or copy `custom_components/smsplanet` into your Home Assistant `custom_components` directory. Add the integration from the Home Assistant UI and provide an SMSPLANET API token.

Configure default sender, recipients and webhook behavior from the integration options.

## Events

Delivery webhooks fire `smsplanet_delivery_status` with:

- `message_id`
- `recipient`
- `sender`
- `delivered`
- `parts`
- `sent_date`
- `delivery_date`
- `delivery_error`
- `raw`

