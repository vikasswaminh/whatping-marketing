---
route: "/features/email-auth-monitoring"
title: "SPF and DMARC monitoring — WhatPing"
description: "A broken SPF record stops your email being delivered — including the alerts telling you something is wrong. WhatPing checks SPF and DMARC every day."
h1: "The monitoring is up. The path from the monitoring to you is not."
---

## The problem

Alerts are mostly delivered by email. So is your password reset, your invoice, your signup
confirmation and your customer's receipt.

All of that depends on two DNS records that nobody watches.

**SPF** declares which servers may send mail as your domain. Break it — exceed the ten-lookup
limit by adding one more `include:`, delete it during a cleanup, or publish two SPF records
where only one is permitted — and receiving servers begin treating your mail as unauthorised.
Not with a bounce you'd notice. With a spam-folder placement you won't.

**DMARC** tells receivers what to do when SPF or DKIM fails. Get it wrong in the other
direction — publish `p=reject` before your alignment is correct — and you have instructed the
world to throw your mail away.

The compounding failure is the reason this page exists: **when your email authentication
breaks, the alerts telling you something is wrong are delivered by email.** Your monitoring
keeps working perfectly and keeps sending you messages that land in spam. Every dashboard is
green. Nothing arrives. You find out from a customer.

## How it works

Give WhatPing a domain. Once a day it checks:

- **SPF** — a `v=spf1` record published on the domain
- **DMARC** — a `v=DMARC1` record published on `_dmarc.<domain>`

If either is missing, the monitor goes down and you are alerted — on every channel you have
configured, which is exactly why having a webhook or Telegram channel alongside email is worth
the two minutes it takes.

A `_dmarc` subdomain that does not exist is treated as a missing DMARC record, not as a broken
check. That distinction matters: "the record isn't there" is a finding, and reporting it as a
lookup error would bury the answer you actually wanted.

## What you'll see when it fires

```
🔴 DOWN — example-com-email (example.com): missing DMARC

🔴 DOWN — example-com-email (example.com): missing SPF and DMARC
```

And when it's healthy, on the monitor:

```
SPF ok · DMARC ok
```

## Worth knowing

**Nothing else in this category does this.** Not Uptime Kuma, not Better Stack. Email
authentication is treated as a deliverability concern and lives in a separate class of tool,
usually one you pay for and check monthly. It belongs next to your uptime monitoring, because
it is on the critical path of your uptime monitoring.

**Pair it with a webhook channel.** If email auth is what breaks, an email alert about email
auth breaking is not going to reach you. A ntfy topic or a Telegram chat costs nothing and
routes around the failure.

**Present is not the same as correct.** WhatPing checks that SPF and DMARC records exist and
are recognisable. It does not evaluate SPF lookup counts, alignment, or DMARC policy strength —
those are on the [roadmap](/roadmap), and claiming them now would be exactly the kind of
overstatement this product avoids.

## Limits

| Setting | Range | Default |
|---|---|---|
| Check interval | 20 seconds – 24 hours | 24 hours |
| Failures before down | 1 – 10 | 2 |

No other configuration: SPF and DMARC are either published or they are not.

## Related

- [Email auth monitor reference](/docs/monitors/email-auth)
- [DNS monitoring](/features/dns-monitoring) — for arbitrary record assertions
- [Alert channels](/docs/alerting/channels) — set up a non-email channel

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
