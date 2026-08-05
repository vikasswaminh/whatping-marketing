---
route: "/docs/monitors/email-auth"
title: "Email authentication monitors — WhatPing docs"
description: "Check daily that SPF and DMARC are still published for your domain, so your mail — including your alerts — keeps being delivered."
h1: "Email authentication monitors"
---

## What it checks

Once a day, looks up two TXT records:

- **SPF** — a record beginning `v=spf1` on the domain itself
- **DMARC** — a record beginning `v=DMARC1` on `_dmarc.<domain>`

The check fails if either is missing.

## Fields

| Field | Range | Default |
|---|---|---|
| Domain | bare registrable domain | — |
| Interval | 20 s – 24 h | 24 h |
| Failures before down | 1 – 10 | 2 |
| Re-alert every | 5 min – 24 h, or off | off |

No other configuration. SPF and DMARC are either published or they are not.

## Why this is worth a monitor

Email authentication fails in a way that is almost perfectly designed to go unnoticed.

Break SPF — exceed the ten-lookup limit by adding one more `include:`, publish two SPF records
where only one is permitted, or delete it during a cleanup — and receiving servers start
treating your mail as unauthorised. Not with a bounce. With a spam-folder placement.

Then the compounding part: **the alerts that would tell you something is wrong are delivered by
email.** Your monitoring works perfectly and keeps sending messages nobody receives. Every
dashboard is green. You find out from a customer, or from a payment that never got made.

<Callout type="warning">
Attach a non-email channel to this monitor. An email alert about email authentication being
broken is unlikely to arrive. [ntfy](/docs/alerting/channels) takes two minutes and needs no
account.
</Callout>

## A missing `_dmarc` is a finding, not an error

The `_dmarc` subdomain frequently does not exist at all, which a DNS lookup reports as an
error. That is treated as "DMARC is missing" and reported as such, rather than as a broken
check — because "the record isn't there" is the answer you asked for.

## Failure messages

```
🔴 DOWN — example-com-email (example.com): missing DMARC
🔴 DOWN — example-com-email (example.com): missing SPF
🔴 DOWN — example-com-email (example.com): missing SPF and DMARC
```

On the monitor:

```
SPF ok · DMARC ok
```

## What it does not check

Present is not the same as correct. This monitor asserts the records exist and are
recognisable. It does not evaluate:

- **SPF lookup count** against the 10-lookup limit — the single most common way SPF silently
  breaks
- **SPF syntax** beyond the `v=spf1` prefix
- **DKIM** — selectors are not discoverable without knowing their names
- **DMARC policy strength** — `p=none` passes exactly like `p=reject`
- **Alignment** between the From header and the authenticated domain

Those are on the [roadmap](/roadmap). Claiming them now would be the kind of overstatement this
product is trying not to make.

For deep analysis, a dedicated deliverability tool is the right instrument. This monitor exists
to catch the record disappearing, which is the failure that happens on a Tuesday afternoon
during an unrelated DNS change.

## Worked example

```
Domain:               example.com
Interval:             24 hours
Failures before down: 1
Re-alert every:       (off)
Channels:             ntfy + webhook   ← not email
```

## Related

- [DNS monitors](/docs/monitors/dns) — for arbitrary TXT assertions, including SPF content
- [Alert channels](/docs/alerting/channels)
- [Why this matters](/features/email-auth-monitoring)
