---
route: "/docs/monitors/mail"
title: "SMTP and IMAP monitors — WhatPing docs"
description: "Read the mail server greeting and optionally complete a STARTTLS handshake — where an expired certificate on port 587 shows up."
h1: "SMTP and IMAP monitors"
---

## What it checks

Connects, reads the service greeting, and requires it to be right: `220` for SMTP, `* OK` for
IMAP. With STARTTLS enabled it then negotiates TLS and completes the handshake.

## Why not just a TCP check

Because a TCP check calls a broken mail server healthy.

A port that accepts a connection and then says nothing is a mail server that is listening but
not serving — a common failure when a daemon is wedged, or when a proxy sits in front of
nothing. A bare port check sees a successful connection and reports up. This one waits for
the greeting.

The STARTTLS path matters for a second reason: **it is where an expired certificate on port
587 shows up.** The [certificate monitor](/docs/monitors/ssl) only looks at 443, so a mail
certificate can expire without any other check noticing.

## Fields

| Field | Range | Default |
|---|---|---|
| Type | smtp or imap | — |
| Host | hostname or IP | — |
| Port | 1 – 65535 | — |
| STARTTLS | on / off | on |
| Timeout | 1 – 60 s | 10 s |

Common ports: SMTP `25` and `587`; IMAP `143`. For implicit-TLS ports — `465`, `993` — the
handshake happens before any greeting, so use a [TCP monitor](/docs/monitors/tcp) there for
now.

## Create it with the API

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "content-type: application/json" \
  -d '{
    "name": "mx",
    "type": "smtp",
    "host": "mx.example.com",
    "port": 587,
    "starttls": true,
    "timeout_ms": 15000
  }'
```

Use `"type": "imap"` with port `143` for IMAP. They are two monitor types sharing one page,
not one type with a protocol field.

Field names are snake_case and an unknown one is a `422` naming the field, never a silent
drop. Full reference: [API](/docs/api).

## Failure messages

```
no greeting within timeout
unexpected greeting, wanted `220` and got `554`
server refused STARTTLS
STARTTLS handshake failed: invalid peer certificate: Expired
connection closed before greeting
```

Only the first token of a greeting is ever recorded. A banner can carry an internal hostname
and a software version, and that is the target's information, not ours to store.

## Worked example

```
Type:      smtp
Host:      mx.example.com
Port:      587
STARTTLS:  on
Timeout:   15 s
```

Mail servers are often slow to greet under load, so a longer timeout than the default is
usually right here.

## Related

- [Email authentication monitors](/docs/monitors/email-auth) — SPF and DMARC records
- [Certificate monitors](/docs/monitors/ssl) — port 443
