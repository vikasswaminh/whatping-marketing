---
route: "/features/api"
title: "Uptime monitoring API — WhatPing"
description: "A REST API for monitors, incidents, results and channels. Bearer keys, read/write scopes, cursor pagination and Idempotency-Key, with an OpenAPI 3.1 spec. Free."
h1: "Monitoring you can create from a pipeline"
---

## The problem

Monitors created by hand drift. Someone adds a service and forgets the monitor, someone deletes
a service and leaves the monitor, and six months later the dashboard is a list nobody trusts —
half of it alerting on things that no longer exist, and the parts that matter silently missing.

The fix is not discipline. It is putting monitor creation in the same place as everything else
that describes your infrastructure: the repository, the pipeline, the terraform apply.

## What it covers

```bash
curl https://api.whatping.com/v1/me -H "Authorization: Bearer $KEY"
```

Fifteen endpoints across monitors, incidents, check results and alert channels. Create, read,
update, pause, resume, delete; rotate a heartbeat token; list results in a time window; filter
incidents by status; attach and detach channels.

**Every write runs the same validator the dashboard runs.** That is the constraint the whole
thing was designed around, not a nice property that emerged. An API that validates differently
from the interface is how a monitor gets created that the prober cannot parse — and this
codebase has already had one outage of exactly that shape, where a new monitor type froze the
worker's config parsing for ten minutes. If the interface would refuse your input, the API
refuses it identically, with the offending field named.

## The parts that matter at 3am

**Idempotent creates.** Send `Idempotency-Key` on any `POST` and a retry returns the original
response rather than a second monitor. A pipeline that reruns does not accumulate duplicates:

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "Idempotency-Key: deploy-$(git rev-parse --short HEAD)" \
  -H "content-type: application/json" \
  -d '{"name":"checkout","type":"http","url":"https://shop.example.com/health"}'
```

**Unknown fields are an error, not a shrug.** A typo'd `intervall_sec` returns `422` naming the
field. Silently ignoring it would leave you believing you had set something you had not, which
is the kind of bug that surfaces during the outage it was meant to catch.

**Scoped keys.** A `read` key can call every `GET` and nothing else — which is the key you give
the dashboard that mirrors your incidents onto a wall display.

**Continuous rate limits.** 600 reads and 60 writes a minute, per key, in buckets that refill
continuously rather than resetting on a window edge. There is no boundary to burst across, and
every response carries `ratelimit-remaining` so a client can pace itself instead of discovering
the limit by hitting it.

**Cursor pagination**, never offset — so a page boundary cannot skip or repeat a row while
monitors are being created underneath you.

## What it will not do, deliberately

**No CORS.** None. A key grants full access to its workspace, so a key in browser JavaScript is
a leaked key. Refusing browser requests entirely is a stronger position than documenting that
you shouldn't.

**Channels cannot be created through the API**, only listed and attached. Creating one means
handing over a credential — a webhook URL, a bot token — and that belongs in one place with one
audit trail.

**Destinations come back redacted.** `https://hooks.slack.com/…`, never the full URL, and never
a Telegram bot token. The API cannot be used to read back a secret you stored through it.

**A monitor in another workspace returns `404`, not `403`.** Telling you an ID exists somewhere
you cannot see is itself information about another account.

## A spec you can generate a client from

[`/openapi.json`](/openapi.json) is OpenAPI 3.1, and it is **generated from the API's route
table** rather than written alongside it — so it cannot describe an endpoint that does not
exist, and it cannot miss one that does.

That is not a theoretical benefit. The first version of the generator parsed 13 of 15 routes,
because one mapped pair used JavaScript shorthand property syntax. The check that caught it was
the reverse one: *described in the spec but absent from the route table.*

## What you'll build with it

- Provision monitors from CI as part of the deploy that creates the service.
- Mirror open incidents onto an internal status board with a read-only key.
- Bulk-pause everything for a maintenance window — the feature WhatPing does not have yet, and
  the API is how you work around its absence today.
- Export check results into your own store before the 7-day retention window closes.

## Limits

- 20 monitors per workspace. The API does not raise the cap.
- 600 reads / 60 writes a minute, per key.
- Idempotency records are kept 24 hours.
- Workspaces, members and billing are dashboard-only.

## Related

- [API reference](/docs/api) — every endpoint, with curl for each
- [OpenAPI 3.1 spec](/openapi.json)
- [Webhook payload](/docs/webhook-payload) — the push side of the same integration
- [Security model](/security)

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
**Secondary:** Read the API reference → `/docs/api`
