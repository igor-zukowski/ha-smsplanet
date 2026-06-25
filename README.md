# SMSPLANET for Home Assistant

Home Assistant custom integration for sending SMS and MMS messages through
[SMSPLANET](https://smsplanet.pl/) API v2.

Author: Igor Żukowski <zukowski.igor3@gmail.com>

Repository: https://github.com/igor-zukowski/ha-smsplanet

## Features

- Home Assistant UI setup flow with SMSPLANET API token authentication.
- Options flow for default sender, default recipients, SMS character handling, transactional channel, test mode, and delivery webhook behavior.
- PrePaid balance sensor updated every hour.
- `notify.smsplanet` notify entity for automations that should send SMS messages to configured default recipients.
- `smsplanet.send_sms` action for direct SMS sending to explicit or default recipients.
- `smsplanet.send_mms` action for MMS sending with subject and attachment.
- SMS part counting before sending.
- Scheduled message cancellation.
- Sending reports and message details.
- Delivery status webhook registration and event forwarding.
- Incoming 2WAY SMS webhook URL helper and event forwarding.
- Sender field listing and sender field requests.
- SMSPLANET blacklist add/remove actions.
- SMSPLANET short URL create/list/remove actions.
- English and Polish UI translations for setup, options, entities, and actions.

## Requirements

- Home Assistant 2025.6.0 or newer.
- HACS, or manual access to the Home Assistant `custom_components` directory.
- SMSPLANET account with an API token created in the SMSPLANET customer panel.
- SMSPLANET account permissions for the actions you want to use, for example sender fields, transactional SMS, MMS, 2WAY SMS, webhooks, or short URLs.
- Public Home Assistant URL if you want SMSPLANET to call delivery or incoming SMS webhooks.

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Add this repository as a custom integration repository if it is not yet available in the default HACS store.
3. Install **SMSPLANET**.
4. Restart Home Assistant.
5. Go to **Settings > Devices & services > Add integration** and search for **SMSPLANET**.

### Manual

1. Copy `custom_components/smsplanet` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & services > Add integration** and search for **SMSPLANET**.

## Setup

The setup form asks for:

| Field | Description |
| --- | --- |
| API token | Token used in the `Authorization: Bearer <token>` header for SMSPLANET API calls. |
| Webhook signature key | Optional key used to verify delivery status webhook signatures. Leave empty if you do not use SMSPLANET webhook signing. |

During setup the integration validates the token by calling the sender fields endpoint. If the token is valid, the integration creates one Home Assistant config entry named **SMSPLANET**.

## Options

Open the integration options from **Settings > Devices & services > SMSPLANET > Configure**.

| Option | Description |
| --- | --- |
| Default sender | Sender field used by `notify.smsplanet` and by send actions when `sender_name` is empty. The setup flow prefers `TEST` when it is available, otherwise it uses the first sender field returned by SMSPLANET. |
| Default recipients | Comma-separated phone numbers used by `notify.smsplanet` and by send actions when `recipients` is empty. |
| Replace Polish characters | Default for replacing Polish characters with ASCII equivalents before sending. This can reduce the number of SMS parts. |
| Use transactional channel | Default for requesting SMSPLANET transactional SMS channel. Use only for non-marketing one-time messages, such as alerts or login codes, and only when enabled on your SMSPLANET account. |
| Test mode | Default for validating send requests without sending real messages. |
| Enable delivery status webhook | When enabled, the integration registers a Home Assistant webhook and configures SMSPLANET to send delivery notifications to it. |

Changing options reloads the integration.

## Entities

### Balance Sensor

The integration creates a `sensor` entity named **SMSPLANET Balance**. It shows the current PrePaid balance in `pts` and refreshes once per hour.

### Notify Entity

The integration creates `notify.smsplanet`. It sends an SMS to the default recipients configured in the integration options.

Example automation action:

```yaml
action: notify.smsplanet
data:
  message: "Alarm zostal uzbrojony."
  title: "Home Assistant"
```

`title` is passed to SMSPLANET as the campaign name. Default recipients are required for `notify.smsplanet`; use `smsplanet.send_sms` when recipients should be selected per automation.

## Actions

All actions use the first loaded SMSPLANET config entry.

Phone numbers can be written as one number, a comma-separated string, or a YAML list where supported. SMSPLANET accepts formats such as `600111222`, `48600111222`, and `+48600111222`.

Dates accepted by SMSPLANET can be Unix time or `dd-MM-yyyy HH:mm:ss`, for example `24-06-2026 12:00:00`. SMSPLANET schedules messages in the Polish time zone.

### `smsplanet.send_sms`

Sends an SMS message.

| Field | Required | Description |
| --- | --- | --- |
| `message` | Yes | Exact SMS text. Long messages may be split into multiple SMS parts, which can affect cost. |
| `recipients` | No | One phone number, comma-separated numbers, or a YAML list. Uses default recipients when empty. |
| `sender_name` | No | SMS sender field. Uses the default sender when empty. |
| `replace_polish_chars` | No | Replaces Polish characters with ASCII equivalents before sending. |
| `transactional_channel` | No | Requests SMSPLANET transactional channel. |
| `test_mode` | No | Validates the request without sending a real SMS. |
| `campaign_name` | No | Name saved in SMSPLANET history. |
| `send_at` | No | Scheduled send date. Empty or past dates send immediately. |
| `company_id` | No | Optional SMSPLANET company identifier for referral or accounting scenarios. |
| `personalization_1` | No | Values for `[%parametr1%]`. Use pipe-separated values for multiple recipients. |
| `personalization_2` | No | Values for `[%parametr2%]`. |
| `personalization_3` | No | Values for `[%parametr3%]`. |
| `personalization_4` | No | Values for `[%parametr4%]`. |

Legacy field aliases are still accepted: `target`, `sender`, `clear_polish`, `transactional`, `test`, and `name`.

Example:

```yaml
action: smsplanet.send_sms
data:
  recipients: "+48600111222, +48600333444"
  message: "Brama zostala otwarta."
  sender_name: "TEST"
  replace_polish_chars: true
  campaign_name: "Home Assistant"
```

Personalized example:

```yaml
action: smsplanet.send_sms
data:
  recipients:
    - "+48600111222"
    - "+48600333444"
  message: "Czesc [%parametr1%], temperatura wynosi [%parametr2%] C."
  personalization_1: "Jan|Anna"
  personalization_2: "21|22"
```

### `smsplanet.send_mms`

Sends an MMS message.

| Field | Required | Description |
| --- | --- | --- |
| `message` | Yes | MMS text body. |
| `subject` | Yes | MMS subject. SMSPLANET recommends setting it because some phones reject MMS without a subject. |
| `attachment` | Yes | Full URL to the attachment or Base64 content. The whole MMS must fit SMSPLANET size limits. |
| `recipients` | No | One phone number, comma-separated numbers, or a YAML list. Uses default recipients when empty. |
| `sender_name` | No | MMS sender number or sender field. Uses the default sender when empty. |
| `replace_polish_chars` | No | Replaces Polish characters with ASCII equivalents before sending. |
| `test_mode` | No | Validates the request without sending a real MMS. |
| `send_at` | No | Scheduled send date. Empty or past dates send immediately. |

Example:

```yaml
action: smsplanet.send_mms
data:
  recipients: "+48600111222"
  subject: "Zdjecie z podjazdu"
  message: "Wykryto ruch."
  attachment: "https://example.com/snapshot.jpg"
```

### `smsplanet.count_sms_parts`

Checks how many SMS parts SMSPLANET will use for a message. This action returns response data.

| Field | Required | Description |
| --- | --- | --- |
| `message` | Yes | SMS text to check. |

Response:

```yaml
parts: 1
```

### `smsplanet.cancel_message`

Cancels a scheduled SMS or MMS by message ID. SMSPLANET buffered IDs beginning with `B-` cannot be cancelled.

| Field | Required | Description |
| --- | --- | --- |
| `message_id` | Yes | Message ID returned by SMSPLANET when the message was created. |

### `smsplanet.generate_report`

Generates a sending report for a date range. This action returns response data.

| Field | Required | Description |
| --- | --- | --- |
| `from_date` | Yes | Report start date. |
| `to_date` | Yes | Report end date. |
| `detailed` | No | Include per-recipient delivery details when available. |
| `response_type` | No | `json` or `csv`. Default: `json`. |

Response contains the raw `message` returned by SMSPLANET and parsed CSV `rows` when the response contains semicolon-separated data.

### `smsplanet.get_message_info`

Gets detailed information for one or more SMSPLANET message IDs. SMSPLANET limits this endpoint to once every 3 minutes. This action returns response data.

| Field | Required | Description |
| --- | --- | --- |
| `message_ids` | Yes | One message ID, comma-separated IDs, or a YAML list. Maximum 1000 IDs per request. |
| `response_type` | No | `json` or `csv`. Default: `json`. |

Response contains the raw `message` returned by SMSPLANET and parsed CSV `rows` when possible.

### `smsplanet.refresh_delivery_webhook`

Creates or updates the SMSPLANET delivery status webhook URL for this Home Assistant instance.

The integration also performs this automatically on startup when **Enable delivery status webhook** is enabled.

### `smsplanet.remove_delivery_webhook`

Removes the delivery status webhook from SMSPLANET.

### `smsplanet.list_webhooks`

Lists webhooks currently configured in SMSPLANET. This action returns response data.

Response:

```yaml
webhooks:
  - type: MESSAGE_NOTIFICATION_WEBHOOK
    url: https://example.ui.nabu.casa/api/webhook/...
```

Actual webhook fields depend on SMSPLANET API response.

### `smsplanet.get_incoming_sms_webhook_url`

Returns the Home Assistant webhook URL that should be pasted into SMSPLANET 2WAY incoming SMS forwarding settings. This action returns response data.

Response:

```yaml
url: https://example.ui.nabu.casa/api/webhook/...
```

### `smsplanet.get_sender_names`

Lists approved sender fields for a SMSPLANET product. This action returns response data.

| Field | Required | Description |
| --- | --- | --- |
| `product` | No | `SMS`, `2WAY`, or `MMS`. Default: `SMS`. |

Response:

```yaml
sender_names:
  - TEST
```

### `smsplanet.request_sender_name`

Requests a new SMS sender field in SMSPLANET.

| Field | Required | Description |
| --- | --- | --- |
| `sender_name` | Yes | Sender field to request. SMSPLANET allows up to 11 supported characters. |

### `smsplanet.blacklist_add`

Adds a phone number to the SMSPLANET blacklist.

| Field | Required | Description |
| --- | --- | --- |
| `phone_number` | Yes | Phone number to block. |
| `valid_to` | No | Optional expiry date in `dd-MM-yyyy` format. |

### `smsplanet.blacklist_remove`

Removes a phone number from the SMSPLANET blacklist.

| Field | Required | Description |
| --- | --- | --- |
| `phone_number` | Yes | Phone number to unblock. |

### `smsplanet.create_short_url`

Creates a short URL using SMSPLANET shortener. This action returns response data.

| Field | Required | Description |
| --- | --- | --- |
| `long_url` | Yes | Full URL to shorten. |
| `custom_alias` | No | Preferred alias. SMSPLANET uses it only if available. |
| `save` | No | Save the short URL in the SMSPLANET panel. Default: `false`. |
| `domain` | No | `wejdz.do` or `link.do`. Default: `wejdz.do`. |

Response:

```yaml
short_url: https://wejdz.do/example
```

### `smsplanet.list_short_urls`

Lists saved SMSPLANET short URLs, optionally filtered by a specific short URL. This action returns response data.

| Field | Required | Description |
| --- | --- | --- |
| `short_url` | No | Optional short URL filter. |

Response:

```yaml
links:
  - date: "24-06-2026"
    short_url: "https://wejdz.do/example"
    long_url: "https://example.com"
    clicks: 0
    raw: {}
```

Actual fields depend on SMSPLANET API response.

### `smsplanet.remove_short_url`

Removes one or more short URLs from SMSPLANET.

| Field | Required | Description |
| --- | --- | --- |
| `aliases` | Yes | One alias, one short URL, comma-separated values, or a YAML list. |

## Events

### `smsplanet_delivery_status`

Delivery webhooks fire `smsplanet_delivery_status` on the Home Assistant event bus.

Event data:

| Field | Description |
| --- | --- |
| `message_id` | SMSPLANET message ID. |
| `recipient` | Recipient phone number. |
| `sender` | Sender field or sender number. |
| `delivered` | Boolean delivery status. |
| `parts` | Number of SMS parts when provided by SMSPLANET. |
| `sent_date` | Send date reported by SMSPLANET. |
| `delivery_date` | Delivery date reported by SMSPLANET. |
| `delivery_error` | Delivery error text when present. |
| `raw` | Raw SMSPLANET notification payload. |

Example automation trigger:

```yaml
trigger:
  - platform: event
    event_type: smsplanet_delivery_status
```

If a webhook signature key is configured, delivery webhooks are accepted only when the `Signature` header matches the HMAC SHA256 Base64 signature of the raw request body.

### `smsplanet_incoming_sms`

Incoming 2WAY SMS forwarding fires `smsplanet_incoming_sms` on the Home Assistant event bus.

Event data:

| Field | Description |
| --- | --- |
| `raw` | Raw query parameters, JSON body, or form body received by the Home Assistant webhook. |

Example automation trigger:

```yaml
trigger:
  - platform: event
    event_type: smsplanet_incoming_sms
```

## Troubleshooting

- If setup fails with invalid authentication, create a new API token in the SMSPLANET panel and reauthenticate the integration.
- If `notify.smsplanet` fails, configure default recipients in the integration options or use `smsplanet.send_sms` with explicit `recipients`.
- If webhook events do not arrive, verify that Home Assistant has a public URL reachable by SMSPLANET and run `smsplanet.refresh_delivery_webhook`.
- If scheduled cancellation fails for an ID starting with `B-`, the message was accepted into SMSPLANET buffer and cannot be cancelled through the cancellation endpoint.
- If transactional SMS fails, verify that SMSPLANET enabled the transactional channel for your account.

## Development

Local checks:

```bash
python -m pytest
python -m ruff check .
```

The repository includes GitHub workflows for HACS validation, Hassfest validation, linting, and tests. A new GitHub release should be created after these workflows pass.
