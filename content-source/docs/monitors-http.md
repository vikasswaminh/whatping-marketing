---
route: "/docs/monitors/http"
title: "HTTP monitors — WhatPing docs"
description: "Monitor an HTTP or HTTPS endpoint with accepted status ranges, redirect control and keyword assertions."
h1: "HTTP monitors"
---

## What it checks

Requests a URL on a schedule and decides success from three things, in order:

1. The request completed within the timeout
2. The response status is in your accepted set
3. The keyword assertion passes, if you set one

Any of them failing counts as one failed check.

## Fields

| Field | Range | Default | Notes |
|---|---|---|---|
| URL | up to 2048 chars | — | `http` or `https` only |
| Interval | 20 s – 24 h | 60 s | |
| Timeout | 1 – 60 s | 10 s | Whole request |
| Failures before down | 1 – 10 | 2 | |
| Accepted status | codes and ranges | `200` | e.g. `200-299,301` |
| Max redirects | 0 – 10 | 0 | 0 = do not follow |
| Keyword | up to 200 chars | none | |
| Keyword inverted | on / off | off | Fail if the keyword **is** present |
| Re-alert every | 5 min – 24 h, or off | off | |
| Second opinion | on / off | on | |

## Create it with the API

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "content-type: application/json" \
  -d '{
    "name": "checkout",
    "type": "http",
    "url": "https://shop.example.com/health",
    "accepted_status": "200-299",
    "expected_keyword": "ready",
    "max_redirects": 3,
    "interval_sec": 60,
    "down_threshold": 2
  }'
```

Field names are snake_case and an unknown one is a `422` naming the field, never a silent
drop. Full reference: [API](/docs/api).

## Accepted status expressions

A comma-separated list of codes and inclusive ranges:

```
200
200-299
200-299,301
200,204,301-302
```

Whitespace is ignored, so `200-299 , 301` is fine. A reversed range (`299-200`) is rejected at
save time rather than silently never matching.

**Use a range, not a single code.** `200` alone means a `204 No Content` health endpoint pages
you at 3am for working correctly.

## Redirects

`0` means do not follow — the redirect status itself is what gets checked. Combine with an
accepted status of `301` to assert that a URL *does* redirect:

```
URL:             http://example.com/
Accepted status: 301
Max redirects:   0
```

That monitor fails if the redirect ever stops happening — which is the actual thing you wanted
to know.

Set a non-zero value to follow to the final response. Each hop counts against the timeout.

## Keyword assertions

After the status check, assert on the response body.

**Normal** — the body must contain the keyword. Use a marker that only appears when the page
genuinely rendered: a heading, a nav item, or something that appears after the database call.
Do not use text from a template shell that renders even when the app is broken.

**Inverted** — the body must *not* contain the keyword. Use for error markers: `Application
error`, `502 Bad Gateway`, `Under maintenance`.

The first **256 KB** of the body is read. Anything past that is not searched, so put your marker
where it will actually appear.

An empty keyword means no assertion. Clearing the field removes the assertion rather than
matching an empty string.

## Failure messages

```
status 503 (accepted: 200-299)
body does not contain "ready"
body contains "Application error"
connect failed: Connection refused (os error 111)
dns error: failed to lookup address information
timed out after 10000ms
```

## Restrictions

**Private-network targets are refused** unless the deployment explicitly opts in. That covers
loopback, RFC1918, link-local including the cloud metadata address, and CGNAT ranges, with the
IPv6 equivalents.

**Credentials in the URL are rejected.** `https://user:pass@example.com/` is refused, because
those credentials would be sent to the target on every check. Use a header-free health endpoint,
or a token in the path.

**Only `http` and `https`.**

## Worked example

Monitoring an API health endpoint that returns `204` and sits behind a redirect:

```
URL:                  https://api.example.com/health
Interval:             60 s
Timeout:              10 s
Accepted status:      200-299
Max redirects:        2
Keyword:              (none — a 204 has no body)
Failures before down: 2
Re-alert every:       30 min
```

## Related

- [Concepts: thresholds and incidents](/docs/concepts)
- [Second opinion](/docs/alerting/second-opinion) — HTTP monitors only
- [Troubleshooting](/docs/troubleshooting)
