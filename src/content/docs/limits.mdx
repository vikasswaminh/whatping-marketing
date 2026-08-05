---
route: "/docs/limits"
title: "Limits and defaults — WhatPing docs"
description: "Every bound and default in one table — intervals, timeouts, thresholds, retention and the monitor cap."
h1: "Limits and defaults"
---

## Workspace

| Limit | Value |
|---|---|
| Monitors per workspace | 20 |
| Members per workspace | no limit |
| Alert channels per workspace | no limit |
| Channels per monitor | no limit |

## Timing

| Setting | Range | Default |
|---|---|---|
| Check interval | 20 seconds – 24 hours | 60 seconds (probed types) |
| Check interval | 20 seconds – 24 hours | 24 hours (certificate, domain, DNS, email auth) |
| Timeout | 1 – 60 seconds | 10 seconds |
| Failures before down | 1 – 10 | 2 |
| Re-alert interval | 5 minutes – 24 hours, or off | off |

## HTTP monitors

| Setting | Range | Default |
|---|---|---|
| URL length | up to 2048 characters | — |
| Accepted status | codes and inclusive ranges, e.g. `200-299,301` | `200` |
| Max redirects | 0 – 10 | 0 |
| Keyword length | up to 200 characters | none |
| Response body read for keyword match | up to 256 KB | — |
| Second opinion | on / off | on |

## TCP monitors

| Setting | Range |
|---|---|
| Port | 1 – 65535 |

## Heartbeat monitors

| Setting | Range | Default |
|---|---|---|
| Expected ping interval | 1 minute – 7 days | 1 hour |
| Grace period | 0 seconds and up | 5 minutes |
| Ping token length | up to 128 characters | — |

## Certificate and domain monitors

| Setting | Range | Default |
|---|---|---|
| Warning threshold | 1 – 365 days | 30 days |

## DNS monitors

| Setting | Values | Default |
|---|---|---|
| Record type | A, AAAA, MX, TXT, CNAME, NS | A |
| Expected value | any substring, optional | none |

## ICMP monitors

| Setting | Range | Default |
|---|---|---|
| Echo requests per check | 1 – 10 | 4 |
| Packet-loss threshold | 0 – 99 % | 0 % |

## UDP monitors

| Setting | Values | Default |
|---|---|---|
| Payload | dns, ntp, stun, raw | dns |
| Raw payload / expected reply | hex, up to 256 bytes | — |

## gRPC monitors

| Setting | Values | Default |
|---|---|---|
| Service name | blank asks about the server as a whole | blank |
| TLS | on / off | off |

## API

| Limit | Value |
|---|---|
| Read requests | 600 per minute, per key |
| Write requests | 60 per minute, per key |
| Page size | 1 – 100, default 25 |
| Idempotency-Key replay window | 24 hours |

## SMTP and IMAP monitors

| Limit | Value |
|---|---|
| Port | 1 – 65535 |
| STARTTLS | on or off; on by default |
| Timeout | 1 – 60 s, default 10 s |
| Greeting recorded | first token only |

Implicit-TLS ports — 465 and 993 — are not supported; the handshake precedes the greeting.
Use a TCP monitor there.

## Data

| Item | Value |
|---|---|
| Raw check result retention | 7 days |
| Uptime windows available | last 24 hours, last 7 days |
| Long-term aggregation | none |
| Incident retention | until the monitor is deleted |
| Monitor name length | up to 80 characters |
| Stored error message length | up to 200 characters |

## Targets

| Rule | Applies to |
|---|---|
| `http` and `https` schemes only | HTTP monitors |
| URLs with embedded credentials rejected | HTTP monitors |
| Private-network targets refused by default | HTTP and TCP monitors |
| Bare domain required — no scheme, port, path or IP literal | certificate, domain, DNS, email auth |

"Private-network" covers loopback, RFC1918, link-local (including the cloud metadata address),
CGNAT, IETF protocol assignments, benchmarking and multicast ranges, plus the IPv6 equivalents
and internal-only hostname suffixes. Detail: [security model](/docs/security).

## Not limits — things that do not exist

So you do not go looking for the setting:

- No probe location selection. Checks run from one location.
- No status pages, maintenance windows, incident acknowledgement, tags or on-call scheduling.
  See the [roadmap](/roadmap).
- No SMS or phone alerts.
- No generic "UDP port open" check — see [UDP monitors](/docs/monitors/udp) for why that
  question cannot be answered.

## Related

- [Concepts](/docs/concepts)
- [Pricing](/pricing)
