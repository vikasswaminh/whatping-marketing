---
route: "/features/uptime-monitoring"
title: "HTTP and TCP uptime monitoring — WhatPing"
description: "Monitor HTTP and TCP endpoints from 20 seconds up. Accepted status ranges, redirect following, and keyword assertions that catch a 200 serving a broken page."
h1: "When 200 is not the same as working"
---

## The problem

A status code tells you the server answered. It does not tell you it answered correctly.

An application that has lost its database connection often still returns 200 with an error
page rendered inside it. A deploy that shipped a broken build serves 200. A CDN serving a
stale cached error page serves 200. In every case a status-code monitor sits there green
while users see something broken.

The reverse is also common: perfectly healthy endpoints that a naive monitor calls down. An
API returning `204 No Content` on a health route. A site that answers `301` on `/` and serves
from `/en/`. Both are working exactly as designed, and both fail a monitor that only accepts
`200`.

## How it works

**HTTP monitors** take a URL, an interval and a rule for what counts as success.

**Accepted status expressions.** Not a single number — a list of codes and inclusive ranges:

```
200
200-299
200-299,301
200,204,301-302
```

`204` APIs and redirecting sites are monitorable without pretending they are something else.

**Redirect depth.** Set how many redirects to follow, from 0 to 10. Zero means do not follow,
so you can assert that a URL redirects rather than following it to somewhere that works.

**Keyword assertions.** After the status check, assert that the response body contains — or
does *not* contain — a specific string. `Sign in` present means the page rendered. `Application
error` absent means the error page isn't showing. The first 256 KB of the body is read, which
is plenty for the marker and bounded enough that a monitor can't be used to pull large files.

**TCP monitors** take a host and a port. The port either accepts a connection within the
timeout or it doesn't. Databases, SMTP listeners, Redis, game servers, anything without a
meaningful HTTP surface.

## What you'll see when it fires

```
🔴 DOWN — checkout (https://shop.example.com/health): status 503 (accepted: 200-299)

🔴 DOWN — checkout (https://shop.example.com/health): body does not contain "ready"

🔴 DOWN — postgres (db.example.com:5432): connect failed: Connection refused (os error 111)
```

The failure text names the actual reason. "Down" on its own is not information.

## Not paged for a blip

A single failed check does not open an incident. The default is **two consecutive failures**,
adjustable from 1 to 10 per monitor. A monitor that has failed once but not yet crossed its
threshold shows as `pending` — visibly wrong, but not yet worth waking anyone.

Raise the threshold on a flaky network to trade alert speed for fewer false alarms. Drop it to
1 when you would rather know immediately and can tolerate the occasional false positive.

## Limits

| Setting | Range | Default |
|---|---|---|
| Check interval | 20 seconds – 24 hours | 60 seconds |
| Timeout | 1 – 60 seconds | 10 seconds |
| Failures before down | 1 – 10 | 2 |
| Redirects followed | 0 – 10 | 0 |
| Keyword length | up to 200 characters | — |
| Body read for keyword match | up to 256 KB | — |

## Related

- [Concepts: thresholds and incidents](/docs/concepts)
- [HTTP monitor reference](/docs/monitors/http)
- [TCP monitor reference](/docs/monitors/tcp)
- [Alerting](/features/alerting)

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
