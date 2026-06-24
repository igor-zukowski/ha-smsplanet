# SMSPLANET for Home Assistant

Custom Home Assistant integration for SMSPLANET.

Author: Igor Żukowski <zukowski.igor3@gmail.com>

Repository: https://github.com/igor-zukowski/ha-smsplanet

## MVP features

- UI configuration flow with API token authentication.
- PrePaid balance sensor.
- `notify` entity for sending SMS to configured default recipients.
- `smsplanet.send_sms` action for sending SMS to explicit recipients.
- Home Assistant webhook for SMSPLANET delivery status notifications.
- `smsplanet_delivery_status` events on the Home Assistant event bus.
- MMS sending, reports, sender fields, blacklist, webhooks, and short URL actions.
- Incoming 2WAY SMS webhook URL helper and `smsplanet_incoming_sms` events.

## Usage

Install the integration through HACS or copy `custom_components/smsplanet` into your Home Assistant `custom_components` directory. Add the integration from the Home Assistant UI and provide an SMSPLANET API token.

Configure default sender, recipients and webhook behavior from the integration options.

The `smsplanet.send_sms` action accepts:

- `message` - message text.
- `recipients` - phone number or comma-separated phone numbers.
- `sender_name` - optional SMSPLANET sender field.
- `replace_polish_chars` - replace Polish characters before sending.
- `transactional_channel` - request the transactional SMS channel.
- `test_mode` - validate without sending a real SMS.
- `campaign_name` - optional name shown in SMSPLANET history.

Older action field names are still accepted for compatibility: `target`, `sender`,
`clear_polish`, `transactional`, `test`, and `name`.

Additional actions:

- `smsplanet.send_mms`
- `smsplanet.count_sms_parts`
- `smsplanet.cancel_message`
- `smsplanet.generate_report`
- `smsplanet.get_message_info`
- `smsplanet.refresh_delivery_webhook`
- `smsplanet.remove_delivery_webhook`
- `smsplanet.list_webhooks`
- `smsplanet.get_incoming_sms_webhook_url`
- `smsplanet.get_sender_names`
- `smsplanet.request_sender_name`
- `smsplanet.blacklist_add`
- `smsplanet.blacklist_remove`
- `smsplanet.create_short_url`
- `smsplanet.list_short_urls`
- `smsplanet.remove_short_url`

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

Incoming SMS forwarding fires `smsplanet_incoming_sms` with:

- `raw`
