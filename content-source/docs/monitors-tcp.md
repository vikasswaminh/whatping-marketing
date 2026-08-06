---
route: "/docs/monitors/tcp"
title: "TCP monitors — WhatPing docs"
description: "Check that a host and port accept a connection. For databases, SMTP, Redis and anything without a useful HTTP surface."
h1: "TCP monitors"
---

## What it checks

Opens a TCP connection to a host and port. If the connection is established within the timeout,
the check succeeds. Nothing is sent and nothing is read.

Use it for anything without a meaningful HTTP endpoint: PostgreSQL, MySQL, Redis, SMTP, IMAP,
SSH, a message broker, a game server.

## Fields

| Field | Range | Default |
|---|---|---|
| Host | hostname or IP, no scheme | — |
| Port | 1 – 65535 | — |
| Interval | 20 s – 24 h | 60 s |
| Timeout | 1 – 60 s | 10 s |
| Failures before down | 1 – 10 | 2 |
| Re-alert every | 5 min – 24 h, or off | off |

The host is a bare hostname or IP. `db.example.com`, not `tcp://db.example.com` and not
`db.example.com/health`. A trailing dot is stripped and the host is lower-cased.

## Create it with the API

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "content-type: application/json" \
  -d '{
    "name": "postgres",
    "type": "tcp",
    "host": "db.example.com",
    "port": 5432,
    "interval_sec": 60,
    "timeout_ms": 10000
  }'
```

Field names are snake_case and an unknown one is a `422` naming the field, never a silent
drop. Full reference: [API](/docs/api).

## What it does and does not tell you

**It tells you** the port is open and something accepted a connection.

**It does not tell you** the service behind it is healthy. A PostgreSQL server that has run out
of disk still accepts connections. An SMTP daemon that cannot deliver still answers on 25.

For anything that speaks HTTP, use an [HTTP monitor](/docs/monitors/http) with a keyword
assertion — it is a much stronger signal. TCP is for when there is no better option.

## Failure messages

```
connect failed: Connection refused (os error 111)
connect failed: No route to host (os error 113)
timed out after 10000ms
dns error: failed to lookup address information
```

`Connection refused` means the host is reachable and nothing is listening — usually the service
is down. A timeout more often means a firewall is dropping packets, or the host is gone.

## Restrictions

**Private-network targets are refused** unless the deployment explicitly opts in. Same rules as
HTTP monitors: loopback, RFC1918, link-local, CGNAT, and the IPv6 equivalents.

**No second opinion.** External confirmation works by fetching a URL, so it applies to HTTP
monitors only. TCP incidents are recorded as `skipped`.

## Worked example

```
Host:                 db.example.com
Port:                 5432
Interval:             60 s
Timeout:              5 s
Failures before down: 2
Re-alert every:       30 min
```

Five seconds is deliberate: a TCP handshake that takes longer than that is already a problem
worth knowing about, even if it eventually succeeds.

## Related

- [HTTP monitors](/docs/monitors/http)
- [Concepts](/docs/concepts)
- [Limits](/docs/limits)
