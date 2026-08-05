---
route: "/docs/alerting/re-alert"
title: "Reminders while still down — WhatPing docs"
description: "Repeat the alert while an incident stays open, so one failed delivery is not a missed outage. Off by default."
h1: "Reminders while still down"
---

## The problem it solves

Alerts fire on transitions: when a monitor goes down, and when it recovers. That means a
six-hour outage produces exactly one notification, at minute zero.

That single message is a single point of failure. If SMTP hiccups, if your webhook endpoint was
briefly returning 500, if your phone was face down — you now have an ongoing outage that is
indistinguishable from everything being fine.

Reminders repeat the alert while the incident stays open.

## Configuration

One field per monitor: **Re-alert every**, in minutes.

| Value | Meaning |
|---|---|
| `0` | Off. This is the default. |
| `5` – `1440` | Repeat every N minutes while the incident is open |

Anything between 1 and 4 is rejected. A one-minute reminder is a firehose, not an alert.

## Off by default, deliberately

A repeating alert on a flapping monitor is how people learn to filter your notifications into a
folder they stop opening — and then the alert that mattered is in there too.

Turn reminders on for the monitors where a missed alert is genuinely expensive. Leave them off
for everything else.

## Choosing an interval

| Monitor | Suggested |
|---|---|
| Production API or checkout | 15–30 minutes |
| Internal service | 60 minutes |
| Nightly backup heartbeat | 6 hours |
| Certificate or domain expiry | 24 hours, or off |

For a certificate expiring in 12 days, a 30-minute reminder is noise. A daily nudge is
proportionate.

## What a reminder looks like

Reminders are not a copy of the original. They carry the elapsed time and, where one has been
recorded, the [second-opinion verdict](/docs/alerting/second-opinion):

```
🔴 DOWN — api (https://api.example.com): connect failed: Connection refused (os error 111)

🔴 STILL DOWN (35m) — api (https://api.example.com): connect failed: Connection refused
(os error 111) · confirmed unreachable from a second network

🔴 STILL DOWN (1h 5m) — api (https://api.example.com): connect failed: Connection refused
(os error 111) · confirmed unreachable from a second network
```

The webhook payload carries an `attempt` field — `0` for the original, `1`, `2`, `3` for
reminders — so a receiver can group, thread or suppress them. See
[webhook payload](/docs/webhook-payload).

## Behaviour worth knowing

**The clock advances before the send, not after.** If a channel is failing, the reminder is
still marked as attempted, so the incident does not stay permanently due and re-alert on every
sweep. The failure is recorded in the delivery ledger, and the next reminder comes at the normal
interval.

The consequence, stated plainly: **a failed reminder is not retried immediately.** It waits for
the next interval. The reminder mechanism *is* the retry.

**Each reminder is a separate ledger entry.** The original alert and every reminder are recorded
independently, so "we sent it" and "it was delivered" stay distinguishable per attempt.

**Reminders stop when the incident resolves.** The recovery alert is sent once, and the
reminder counter ends with the incident.

**Reminders only apply to open incidents.** A monitor failing but still below its threshold — in
`pending` — has no incident and produces no reminders.

## Worked example

A checkout endpoint where downtime costs money:

```
URL:                  https://shop.example.com/checkout
Interval:             30 s
Failures before down: 2
Re-alert every:       15 min
Channels:             webhook (Slack) + ntfy
```

Down within a minute, then every 15 minutes until it recovers, on two channels that fail
independently.

## Related

- [Alert channels](/docs/alerting/channels)
- [Second opinion](/docs/alerting/second-opinion)
- [Webhook payload](/docs/webhook-payload)
