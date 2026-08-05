---
route: "/features"
title: "Features — WhatPing"
description: "Eleven monitor types, four alert channels, reminders while you are still down, and a second opinion from a network that is not ours."
h1: "Everything WhatPing watches"
---

## Intro

Most monitoring answers one question: is the server responding? That question matters, and
WhatPing answers it — from 20-second intervals, with status ranges, redirect following and
keyword assertions.

But it is not the question that causes most of the outages that surprise people. Those come
from things with expiry dates and things that get edited: certificates, registrations, DNS
records, SPF. WhatPing watches those on the same schedule, in the same dashboard, through the
same alert channels.

---

## Liveness

**Heading:** Is it up right now?

**[HTTP monitoring](/features/uptime-monitoring)**
Accepted status expressions like `200-299,301`, so a `204` API or a redirecting site is
monitorable. Redirect depth you control. Keyword assertions, including inverted ones, to catch
the case where the server returns 200 and serves a broken page.

**[TCP monitoring](/features/uptime-monitoring)**
For everything that isn't HTTP: a database port, a message broker, a game server. Either the
port accepts a connection or it doesn't.

**ICMP, UDP, gRPC and SMTP/IMAP**
Ping a host and track packet loss. Ask a DNS, NTP or STUN service a real question and require
a real answer — there is no generic "UDP port open" check, because that question cannot be
answered. Call a gRPC health service and require `SERVING`. Read a mail server's greeting and
complete a STARTTLS handshake, which is where an expired certificate on port 587 surfaces.
[ICMP](/docs/monitors/icmp) · [UDP](/docs/monitors/udp) · [gRPC](/docs/monitors/grpc) ·
[SMTP / IMAP](/docs/monitors/mail)

**[Heartbeat monitoring](/features/heartbeat-monitoring)**
Inverted monitoring for things that have no address to poll. Your cron job, backup script or
CI pipeline requests a URL when it succeeds; WhatPing alerts when the request stops arriving.
A backup that silently stopped running two weeks ago is the classic case.

---

## Expiry and drift

**Heading:** Will it still be up next month?

**[Certificate monitoring](/features/certificate-monitoring)**
Days remaining on your TLS certificate, checked daily, with a threshold you set. The default
warns at 30 days, which is enough time for a renewal to be routine rather than an incident.

**[Domain expiry monitoring](/features/domain-expiry-monitoring)**
Read from the domain registry, not inferred from DNS. An expired registration takes down every
service on the domain at once, and there is no health check anywhere that predicts it.

**[DNS monitoring](/features/dns-monitoring)**
Assert that a record still contains what it should. A, AAAA, MX, TXT, CNAME and NS. Catches a
fat-fingered edit, a failed migration, or a record that quietly went missing.

**[Email authentication monitoring](/features/email-auth-monitoring)**
SPF and DMARC, checked daily. This is the one nobody else in this category does, and it
protects the path your alerts travel down.

---

## Alerting

**Heading:** Getting told, reliably

**[Alerting in full](/features/alerting)**

- **Four channels** — email, webhook, ntfy, Telegram. The webhook shape works with Slack,
  Discord and Mattermost as-is.
- **Reminders while still down** — because one alert that fails to deliver is a missed
  outage. Off by default.
- **A second opinion** — WhatPing asks an independent network whether it agrees the target is
  unreachable, and labels the incident with the answer.
- **A delivery ledger** — every send is recorded, so a channel that has been quietly failing
  is visible rather than assumed to be working.

## Automation

**[REST API](/docs/api)** — provision monitors from Terraform or CI and read incidents,
results and uptime back into your own dashboard. Bearer key auth, read/write scopes, cursor
pagination, and `Idempotency-Key` so a rerun does not create duplicates. Writes go through the
same validation the dashboard uses, so the API accepts exactly what the interface accepts.

---

## What WhatPing does not do

Stated plainly, because finding out later is worse.

- **One probe location.** Checks run from a single network. The second opinion gives you one
  independent confirmation, not a global probe fleet.
- **No status pages.** Designed, not built — see the [roadmap](/roadmap).
- **No maintenance windows, incident acknowledgement, or on-call scheduling.** Also on the
  roadmap.
- **No SMS or phone calls.** Email, webhook, ntfy and Telegram only.
- **20 monitors per workspace**, and 7 days of raw check history.
- **No implicit-TLS mail ports** (465, 993) — use a TCP monitor there for now.

If you need multi-region probing and on-call rotation today, [Better
Stack](/vs/better-stack) does that and WhatPing does not.

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
