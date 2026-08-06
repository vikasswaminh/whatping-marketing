---
route: "/about"
title: "About — WhatPing"
description: "Built by one developer to solve a specific problem: the outages that never fail a health check. What it is, and what it deliberately is not."
h1: "About WhatPing"
---

## Why it exists

Every monitoring tool answers the same question — is the server responding? — and most of them
answer it well. But the outages that actually surprise people usually don't start with a server
that stopped responding.

They start with a date passing. A certificate expires. A registration lapses. Or with an edit:
a DNS record changed during a migration, an SPF record broken by adding one more `include:`.
In every case, the health check returns 200 right up until everything is down at once.

WhatPing was built to watch those alongside ordinary uptime, in the same dashboard, through the
same alert channels — so the thing that takes you down is being watched by the same tool you
already check.

## Who builds it

One developer. That is worth knowing before you depend on it.

What it means in practice: no support team, no SLA, no roadmap commitments with dates on them,
and no guarantee about how long it will be around. It also means no growth targets pushing
features you didn't ask for, no seat pricing, and no upsell path — because there is nothing to
upsell you to.

## How it's built

Deliberately boring where it matters. A stateless Rust prober that can be restarted mid-outage
without losing anything. A backend that owns every state decision in one place. Idempotent
check results, so a retry cannot page you twice. A dead man's switch on the prober itself, so
the system reports its own death instead of going quiet.

That last one is not decoration. It has already caught a real regression where a parsing bug
froze the prober on a stale configuration — everything looked normal, and the heartbeat was the
only signal anything was wrong.

The [architecture page](/how-it-works) describes it properly.

## What it deliberately is not

**Not a platform.** No logs, no metrics, no APM, no tracing. Those are different products and
doing them badly alongside monitoring helps nobody.

**Not an incident management tool.** No on-call rotations, no escalation policies, no
postmortems. If being paged reliably is someone's job at your company, buy a tool built for
that.

**Not multi-region.** Checks run from one network location. The
[second opinion](/docs/alerting/second-opinion) adds one independent vantage point per incident,
which is genuinely useful and is not a global probe fleet.

**Not self-hostable today.** Hosted only.

## The standard it holds itself to

Everything on this website is checkable against the source. When a number appears — 20 seconds,
30 days, 7 days, 20 monitors — it came from reading the code, not from memory. When something
isn't built, it says so on the [roadmap](/roadmap) rather than appearing as a feature with an
asterisk.

For a young product from an unknown developer, that is the only real asset. Being caught
overstating once would cost more than any feature is worth.

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
