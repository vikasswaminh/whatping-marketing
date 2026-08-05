---
route: "/features/certificate-monitoring"
title: "TLS certificate expiry monitoring — WhatPing"
description: "Know weeks before a certificate expires, not minutes after. Daily checks, issuer and days remaining, with a warning threshold you set per monitor."
h1: "Certificates don't fail gracefully"
---

## The problem

An expired certificate is worse than a server being down.

A down server produces a connection error that most clients retry and most humans recognise.
An expired certificate produces a full-page browser interstitial that looks like a security
incident, TLS handshake failures in every API client, and mobile apps that fail without
explaining why. Meanwhile the server is fine, the process is running, and every health check
you have is green.

Automated renewal helps and does not solve it. Renewal hooks fail silently. A DNS challenge
breaks after a nameserver change. A certificate gets pinned to a load balancer that nobody
remembers to update. The renewal you set up two years ago has been failing for two months and
nothing told you.

## How it works

Give WhatPing a domain. Once a day it reads the live certificate and records:

- whether it is currently valid
- who issued it
- the exact expiry date
- how many days remain

You set the warning threshold per monitor. The default is **30 days**, matching Uptime Kuma's
default, which is enough runway for a renewal to be a task rather than an incident. Anything
from 1 to 365 days is accepted — set it to 7 for a certificate you know renews automatically
and 60 for one that involves a human and a purchase order.

When days remaining drops below your threshold, the monitor goes down and alerts fire on your
normal channels. It is not a separate notification system: a certificate warning reaches you
the same way a 500 does.

**Once a day is deliberate.** A certificate does not stop being valid between one minute and
the next. Checking hourly would produce the same answer 24 times and add nothing but noise.

## What you'll see when it fires

```
🔴 DOWN — api-cert (api.example.com): certificate expires in 12 days
```

And on the monitor itself:

```
Let's Encrypt R3 · expires Sep 20 16:23:22 2026 GMT · 12 days remaining
```

## Limits

| Setting | Range | Default |
|---|---|---|
| Warning threshold | 1 – 365 days | 30 days |
| Check interval | 20 seconds – 24 hours | 24 hours |
| Failures before down | 1 – 10 | 2 |

The target is a domain name — no scheme, no port, no path, and no IP literals. `api.example.com`,
not `https://api.example.com/health`.

## Related

- [Certificate monitor reference](/docs/monitors/ssl)
- [Domain expiry monitoring](/features/domain-expiry-monitoring) — the other expiry date that takes you down
- [Alerting](/features/alerting)

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
