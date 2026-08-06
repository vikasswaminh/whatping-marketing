---
route: "/features/domain-expiry-monitoring"
title: "Domain expiry monitoring — WhatPing"
description: "An expired domain registration is a total outage that no health check predicts. WhatPing reads the registry daily and warns you while renewal is still routine."
h1: "Your domain expires on a Sunday"
---

## The problem

Of every outage in this list, this is the one that ends companies.

When a domain registration lapses, the registrar pulls the nameservers. The zone stops
resolving. Your website, your API, your dashboard, your SSO, your webhooks and your email all
disappear in the same second. Not degraded — gone, with NXDOMAIN.

Then recovery gets worse. Your alerting emails cannot be delivered, because the MX record is
in the zone that no longer resolves. Password resets for your registrar account go to an
address on the domain you just lost. Redemption fees run into the hundreds, and restoration
can take days. In the meantime the domain may be picked up by a drop-catcher.

The warning signs are all things you didn't see: a renewal email to an address nobody reads, a
card that expired eight months ago, an auto-renew toggle that was never on.

**No health check predicts this.** Right up until the moment the registration lapses, every
endpoint returns 200.

## How it works

Give WhatPing a domain. Once a day it queries the **domain registry** — the authoritative
record of who owns the name and when it expires — and reports:

- the registrar of record
- the registration expiry date
- days remaining
- the nameservers currently on file

When days remaining falls below your threshold, the monitor goes down and alerts fire. The
default is 30 days. For a domain that matters, 60 or 90 is more useful: it gives you time to
notice, find whoever owns the registrar account, and fix the card.

**This is a registry lookup, not a DNS lookup.** That distinction matters more than it sounds:
it means WhatPing can monitor a domain whose apex has no A record at all — an apex that only
publishes MX and TXT, which is extremely common for a domain used mainly for email. A tool that
resolves the domain first cannot check exactly the domains most at risk of quietly lapsing.

## What you'll see when it fires

```
🔴 DOWN — example-com-registration (example.com): domain registration expires in 21 days
```

And on the monitor itself:

```
BigRock Solutions Ltd. · expires 2027-05-29T18:41:10 · 297 days remaining
```

## Worth knowing

**Uptime Kuma has no equivalent.** This is a genuine gap in the most popular self-hosted
monitor — see the [comparison](/vs/uptime-kuma).

**Set it once and forget it.** This is the highest-value monitor per second of setup in the
product. Thirty seconds, once, against a failure mode that has no other warning.

**Nameservers are recorded too**, so a registrar-level hijack — where the nameservers change
without your involvement — is visible on the monitor.

## Limits

| Setting | Range | Default |
|---|---|---|
| Warning threshold | 1 – 365 days | 30 days |
| Check interval | 20 seconds – 24 hours | 24 hours |
| Failures before down | 1 – 10 | 2 |

Registry data availability varies by TLD. Most gTLDs (`.com`, `.net`, `.org`, `.io`, `.dev`)
publish an expiry date. Some ccTLDs publish little or nothing — if the registry returns no
expiry date, the monitor reports that plainly rather than guessing.

## Related

- [Domain monitor reference](/docs/monitors/domain)
- [DNS monitoring](/features/dns-monitoring) — for records inside a zone you still own
- [Certificate monitoring](/features/certificate-monitoring)

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
