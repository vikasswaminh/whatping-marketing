---
route: "/docs/alerting/channels"
title: "Alert channels — WhatPing docs"
description: "Set up email, webhook, ntfy and Telegram alerts, including the Telegram trap that makes a working bot token look broken."
h1: "Alert channels"
---

## How channels work

A channel is a destination. Create it once in your workspace, attach it to any number of
monitors. A monitor with no channel changes state silently.

Delivery happens **after** monitor state is committed, and every attempt — success or failure —
is recorded in a ledger. A channel that is failing cannot change what a monitor believes about
its target.

<Callout type="note">
Use at least two channels of different kinds for anything important. Email and webhook fail for
different reasons; email and email do not.
</Callout>

---

## Webhook

A JSON `POST`. The body carries the structured payload plus `text` and `content` aliases,
which is what lets one endpoint work with Slack, Discord, Mattermost and plain automation
receivers without provider-specific configuration.

**Setup**
1. **Channels** → **Add** → **Webhook**
2. Paste the URL
3. Attach to a monitor

**Slack** — create an Incoming Webhook in your Slack app settings and paste the
`https://hooks.slack.com/services/...` URL. Slack renders the `text` field.

**Discord** — channel settings → Integrations → Webhooks → New Webhook, copy the URL. Discord
renders the `content` field.

**Mattermost** — same shape as Slack.

**Your own receiver** — the full schema is in [webhook payload](/docs/webhook-payload).

<Callout type="warning">
A webhook URL is a credential — anyone holding it can post to your channel. WhatPing displays
it back to you as scheme and host only.
</Callout>

Timeout is 10 seconds. Any non-2xx response is recorded as a failed delivery.

---

## Email

**Setup**
1. **Channels** → **Add** → **Email**
2. Enter the address
3. Attach to a monitor

The message contains the monitor name, the target, the failure reason and the time the incident
opened.

Do not make email your only channel for an [email authentication
monitor](/docs/monitors/email-auth). If that monitor fires, email is the thing that is broken.

---

## ntfy

Push notifications to your phone with no account, no login and no token.

**Setup**
1. Install the ntfy app (iOS/Android), or open [ntfy.sh](https://ntfy.sh)
2. Subscribe to a topic name nobody could guess: `whatping-a7f3c9d2e1`, not `whatping-alerts`
3. **Channels** → **Add** → **ntfy** → `https://ntfy.sh/whatping-a7f3c9d2e1`
4. Attach to a monitor

Down alerts arrive as high priority with an alarm icon; recoveries at normal priority with a
check mark.

<Callout type="warning">
**The topic name is the credential.** Anyone who knows it can read your alerts and publish fake
ones. Use a random suffix. WhatPing drops the topic name entirely when displaying the channel
back to you, for exactly this reason.
</Callout>

Self-hosted ntfy works — use your own base URL.

---

## Telegram

A message to a chat or a group. Two minutes to set up.

### 1. Create the bot

Message **@BotFather** in Telegram:

```
/newbot
```

Give it a display name, then a username ending in `bot`. BotFather replies with a token:

```
123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. Start a chat with it — do not skip this

Open your new bot and press **Start**, or send it any message.

<Callout type="gotcha">
**This is the step that makes a working token look broken.** Telegram does not allow a bot to
message a user who has never messaged it first. A fresh token with no conversation fails with
`403: bot can't initiate conversation with a user`, which reads exactly like a bad token.

For a group: add the bot to the group, then send any message there.
</Callout>

### 3. Get the chat ID

Open in a browser, with your token:

```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

Find `"chat":{"id":...}`. A personal chat is a positive number; a group is negative, usually
starting `-100`.

If the response is empty, you skipped step 2.

### 4. Add the channel

**Channels** → **Add** → **Telegram** → paste the bot token and the chat ID.

<Callout type="warning">
The bot token grants full control of the bot. WhatPing never displays it back — not even a
prefix, because a prefix is enough to correlate a token across a leak. Telegram delivery
failures report the status code only, never the response body, because Telegram echoes the
request URL — which contains the token — in its errors.
</Callout>

---

## The delivery ledger

Every attempt is recorded: which channel, which incident, which reminder, whether it succeeded,
and the error if not.

This exists because the worst state for an alerting system is one where a channel has been
quietly failing for weeks and everybody assumes it works. Check the ledger after setting up a
channel rather than assuming.

## Proving a channel works

Do not wait for a real outage.

1. Create a throwaway HTTP monitor pointing at a hostname that does not exist
2. Interval 20 s, failures before down 1
3. Attach the channel
4. Wait about a minute for the alert
5. Delete the monitor

## Related

- [Webhook payload](/docs/webhook-payload)
- [Reminders](/docs/alerting/re-alert)
- [Troubleshooting](/docs/troubleshooting)
