---
route: "/docs"
title: "Documentation — WhatPing"
description: "How to monitor an endpoint, a cron job, a certificate, a domain, a DNS record or your email authentication, and how alerting behaves."
h1: "WhatPing documentation"
---

## Start here

**[Quickstart](/docs/quickstart)** — account to first alert in about five minutes.

**[Concepts](/docs/concepts)** — monitors, checks, thresholds, incidents, and why a failing
monitor sits in `pending` before it goes down. Ten minutes here saves an hour of confusion
later.

---

## Monitor types

| Type | Answers | Reference |
|---|---|---|
| **HTTP** | Does this URL respond correctly? | [docs](/docs/monitors/http) |
| **TCP** | Does this port accept a connection? | [docs](/docs/monitors/tcp) |
| **Heartbeat** | Did my cron job run? | [docs](/docs/monitors/heartbeat) |
| **Certificate** | How long until my TLS certificate expires? | [docs](/docs/monitors/ssl) |
| **Domain** | How long until my registration expires? | [docs](/docs/monitors/domain) |
| **DNS** | Does this record still say what it should? | [docs](/docs/monitors/dns) |
| **Email auth** | Are SPF and DMARC still published? | [docs](/docs/monitors/email-auth) |

HTTP, TCP and heartbeat run at your chosen interval, from 20 seconds. The other four default to
once a day, because certificates and registrations change on a scale of months.

---

## Alerting

**[Channels](/docs/alerting/channels)** — email, webhook, ntfy and Telegram, with setup for
each. Includes the Telegram trap that makes a working bot token look broken.

**[Reminders while still down](/docs/alerting/re-alert)** — repeat the alert while an incident
stays open. Off by default.

**[External second opinion](/docs/alerting/second-opinion)** — how WhatPing decides between
"the target is down" and "we cannot reach the target".

---

## Reference

**[Webhook payload](/docs/webhook-payload)** — the full JSON schema, with a real example.

**[Heartbeat ping endpoint](/docs/heartbeat-api)** — URL format, methods, responses, and
snippets for cron, systemd and GitHub Actions.

**[Limits and defaults](/docs/limits)** — every bound in one table.

**[Security model](/docs/security)** — what is validated, what is redacted, what is stored.

**[Troubleshooting](/docs/troubleshooting)** — the questions people actually ask.

**[FAQ](/docs/faq)**

---

## Conventions in these docs

- Every number stated is the value enforced by the product. If a document and the interface
  disagree, the interface is right and the document is a bug — please report it.
- Alert text shown in examples is the literal text WhatPing sends, emoji included.
- Anything not built is not documented. See the [roadmap](/roadmap) for what is planned.
