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

Eleven types is enough to be worth a decision column. The middle column is the question the
type answers; the third is when to reach for it rather than something adjacent.

| Type | Answers | Reach for it when | Reference |
|---|---|---|---|
| **HTTP** | Does this URL respond correctly? | Anything served over HTTP. Start here | [docs](/docs/monitors/http) |
| **TCP** | Does this port accept a connection? | A port with no protocol you can assert on — a broker, a game server | [docs](/docs/monitors/tcp) |
| **Heartbeat** | Did my cron job run? | The thing has no address to poll. Backups, cron, CI | [docs](/docs/monitors/heartbeat) |
| **Certificate** | How long until my TLS certificate expires? | Anything on 443. Renewal should be routine, not an incident | [docs](/docs/monitors/ssl) |
| **Domain** | How long until my registration expires? | Every domain you own. Nothing else predicts this failure | [docs](/docs/monitors/domain) |
| **DNS** | Does this record still say what it should? | A record you would notice being wrong only after users did | [docs](/docs/monitors/dns) |
| **Email auth** | Are SPF and DMARC still published? | You send mail — including your own alert emails | [docs](/docs/monitors/email-auth) |
| **ICMP** | Is this host reachable, and how lossy is the path? | You want latency history, or the host serves nothing to poll | [docs](/docs/monitors/icmp) |
| **UDP** | Does this DNS, NTP or STUN service answer? | A resolver, time server or STUN/TURN endpoint | [docs](/docs/monitors/udp) |
| **gRPC** | Does the health service report SERVING? | gRPC, where a bound port is not a ready service | [docs](/docs/monitors/grpc) |
| **SMTP / IMAP** | Does the mail server greet, and does STARTTLS work? | A mail server — and its certificate, which is not on 443 | [docs](/docs/monitors/mail) |

**Two common mistakes.** A TCP monitor on a mail server or a gRPC port reports up while the
service is broken — use the specific type. And an ICMP monitor is not a substitute for an HTTP
one: a machine with a dead application answers pings perfectly.

HTTP, TCP, ICMP, UDP, gRPC, SMTP and IMAP run at your chosen interval, from 20 seconds.
Certificate, domain, DNS and email auth default to once a day, because certificates and
registrations change on a scale of months.

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

**[API reference](/docs/api)** — provision monitors and read state from Terraform, CI or your
own dashboard. Bearer key auth, cursor pagination, idempotent creates.

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
