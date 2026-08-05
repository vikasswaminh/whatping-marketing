---
route: "/docs/monitors/ssl"
title: "Certificate monitors — WhatPing docs"
description: "Check TLS certificate validity and days remaining, with a warning threshold you set per monitor."
h1: "Certificate monitors"
---

## What it checks

Once a day, reads the live TLS certificate for a domain and records the issuer, the expiry date
and the days remaining.

The check fails when either:

- the certificate is not currently valid, or
- days remaining is **below** your warning threshold

## Fields

| Field | Range | Default |
|---|---|---|
| Domain | bare hostname | — |
| Warn below | 1 – 365 days | 30 days |
| Interval | 20 s – 24 h | 24 h |
| Failures before down | 1 – 10 | 2 |
| Re-alert every | 5 min – 24 h, or off | off |

The domain is a bare hostname: `api.example.com`. No scheme, no port, no path, and no IP
literals — a scheme or path is stripped where it is unambiguous and rejected where it is not.

Certificates are checked on port 443.

## Choosing a threshold

| Situation | Suggested |
|---|---|
| Automated renewal (Let's Encrypt, ACME) | 14 days — renewal happens at 30, so 14 means it has already failed twice |
| Manual renewal | 45–60 days |
| Involves purchasing or a third party | 90 days |

The default of 30 matches Uptime Kuma and is a reasonable middle. The question to ask is: how
long would it take me to fix this if the automation had already stopped working?

## Why daily

A certificate does not stop being valid between one minute and the next. Its expiry is known
months ahead. Checking hourly returns the same answer 24 times a day and adds nothing.

You can lower the interval. It is rarely useful.

## Failure and detail messages

```
🔴 DOWN — api-cert (api.example.com): certificate expires in 12 days
🔴 DOWN — api-cert (api.example.com): certificate is not valid
```

On the monitor:

```
Let's Encrypt R3 · expires Sep 20 16:23:22 2026 GMT · 12 days remaining
```

## What it does not check

- **Certificate chain completeness.** A server serving a leaf without its intermediate breaks
  some clients and is not detected here.
- **Revocation.** OCSP and CRL status are not queried.
- **Hostname match.** The certificate is read for the domain you gave; a mismatch between the
  certificate's names and the domain is not asserted separately.
- **Non-443 ports.**

For chain problems, an [HTTP monitor](/docs/monitors/http) against the same host is a useful
companion — a broken chain usually shows up as a TLS error there.

## Requires a resolving domain

Unlike [domain expiry monitoring](/docs/monitors/domain), this check connects to the host, so
the domain must resolve. A domain whose apex publishes only MX records cannot have a certificate
monitor on the apex — monitor the subdomain that actually serves TLS.

## Worked example

```
Domain:               api.example.com
Warn below:           14 days
Interval:             24 hours
Failures before down: 1
Re-alert every:       24 hours
```

Threshold 1 and a daily reminder: with a once-a-day check, waiting for a second consecutive
failure costs a full day, and a daily nudge is proportionate for something with a deadline
weeks away.

## Related

- [Domain expiry monitors](/docs/monitors/domain)
- [DNS monitors](/docs/monitors/dns)
- [Limits](/docs/limits)
