---
route: "/pricing"
title: "Pricing — WhatPing"
description: "Free while in beta. No card, no trial timer, no seat pricing. 20 monitors per workspace. Paid tiers do not exist yet, and this page says so plainly."
h1: "Free, and here is exactly what that means"
---

## The offer

**Free. No card. No trial timer.**

There is no paid tier, because billing has not been built. That is the honest reason, and it is
better than inventing a "Pro" column with a Contact Us button behind it.

| | Included |
|---|---|
| Monitors | 20 per workspace |
| Monitor types | All seven — HTTP, TCP, heartbeat, certificate, domain, DNS, email auth |
| Check interval | From 20 seconds |
| Alert channels | Email, webhook, ntfy, Telegram — any number per monitor |
| Reminders while down | Included |
| Second opinion | Included |
| Check history | 7 days |
| Team members | Any number, in one workspace |
| Cost | Nothing |

---

## What you should know before relying on it

Stated here rather than in a footnote, because you are deciding whether to trust this with
something that matters.

**It is beta, and there is no SLA.** No uptime guarantee, no support commitment, no
compensation if a check is missed. If your monitoring must itself be contractually reliable,
you need a vendor who will sign something, and this is not that yet.

**One probe location.** Not multi-region.

**20 monitors per workspace.** Not a pricing lever — a deliberate cap while the system is
young.

**7 days of check history.** Raw results are deleted after 7 days and there is no long-term
rollup, so uptime percentages cover the last 24 hours and the last 7 days. Nothing longer.

**No status pages, maintenance windows, incident acknowledgement or on-call scheduling.** All
designed, none built — see the [roadmap](/roadmap).

---

## Will it stay free?

The parts you are using now — the seven monitor types, the alert channels, the reminders, the
second opinion, at the current limits — will stay free.

If paid tiers arrive, they will be for things that cost real money to run: more monitors,
longer retention, higher check frequency. Nobody will wake up to find their existing monitors
switched off, and there will be notice.

That is a statement of intent from a solo developer, not a contract. Weigh it accordingly.

---

## Why free at all?

Because a monitoring product with no users has no signal. Every improvement so far has come
from running it against real targets and finding out where it was wrong — a DNS response shape
that made a dead domain look healthy, a parsing bug that froze the prober, a seed helper that
had been failing silently for days.

Charging before that loop has run would be charging for something that hasn't been tested by
anyone but its author.

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
**Secondary:** See what's on the roadmap → `/roadmap`
