---
route: "/docs/api"
title: "API reference — WhatPing docs"
description: "REST API for monitors, incidents, check results and alert channels. Bearer key auth, cursor pagination, idempotent creates."
h1: "API reference"
---

Provision monitors from Terraform or CI, and read state back into your own dashboard.

```
https://api.whatping.com/v1
```

`monitor-site.whatping.com/v1` answers identically and is not going away — it is the same
origin under a second name. Anything already integrated against it keeps working.

## Authentication

Create a key in workspace settings. It is shown once and stored hashed, so it cannot be
recovered — only rotated.

```bash
curl https://api.whatping.com/v1/me \
  -H "Authorization: Bearer sk_your_key_here"
```

Keys carry a scope. A `read` key can call every `GET`; a `write` key can call everything.
There is no way to widen a key's scope after issue — create a new one.

<Callout type="warning">
A key grants full access to its workspace. Put it in a CI secret or an environment variable,
never in front-end code and never in a repository. There is no CORS on this API for exactly
that reason: a key in browser JavaScript is a leaked key.
</Callout>

Every rejection — unknown key, revoked key, expired key — returns the same `401`. That is
deliberate: distinguishing them would let someone probe which keys once existed.

## Conventions

**Errors** always take one shape:

```json
{ "error": { "code": "invalid_request", "message": "Interval must be between 20 and 86400 seconds" } }
```

`422` carries a `field` when one input is at fault. Validation is the *same code the
dashboard runs* — if the interface would refuse it, the API refuses it identically.

**Pagination** is by cursor, never offset:

```bash
curl "https://api.whatping.com/v1/monitors?limit=50" -H "Authorization: Bearer $KEY"
# -> { "data": [...], "next_cursor": "..." }
curl "https://api.whatping.com/v1/monitors?cursor=..." -H "Authorization: Bearer $KEY"
```

`next_cursor` is `null` on the last page. `limit` is 1–100, default 25.

**Rate limits** are 600 reads and 60 writes a minute, per key, in continuously refilling
buckets — so there is no window edge to burst across. Every response carries them:

```
ratelimit-limit: 600
ratelimit-remaining: 587
ratelimit-policy: 600;w=60
```

A `429` includes `retry-after` in seconds.

**Idempotency** — send `Idempotency-Key` on any `POST` and a retry returns the original
response with `idempotent-replay: true` instead of creating a second monitor. Reusing a key
with a different body is a `409`. Records are kept 24 hours.

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "Idempotency-Key: deploy-$(git rev-parse --short HEAD)" \
  -H "content-type: application/json" \
  -d '{"name":"api","type":"http","url":"https://api.example.com/health"}'
```

That pattern is the point of the header: a pipeline that reruns does not accumulate monitors.

**Field names are snake_case**, and an unknown field is an error rather than being ignored —
a typo'd `intervall_sec` that silently vanished would leave you believing you set something
you did not.

## Endpoints

| Method | Path | Scope |
|---|---|---|
| GET | `/v1/me` | read |
| GET | `/v1/monitors` | read |
| POST | `/v1/monitors` | write |
| GET | `/v1/monitors/{id}` | read |
| PATCH | `/v1/monitors/{id}` | write |
| DELETE | `/v1/monitors/{id}` | write |
| POST | `/v1/monitors/{id}/pause` | write |
| POST | `/v1/monitors/{id}/resume` | write |
| POST | `/v1/monitors/{id}/rotate-token` | write |
| GET | `/v1/monitors/{id}/results` | read |
| GET | `/v1/monitors/{id}/channels` | read |
| PUT | `/v1/monitors/{id}/channels/{channelId}` | write |
| DELETE | `/v1/monitors/{id}/channels/{channelId}` | write |
| GET | `/v1/incidents` | read |
| GET | `/v1/channels` | read |

## Creating a monitor

The `type` decides which other fields apply. Full field reference is on each monitor type's
page under [monitor types](/docs).

```bash
# HTTP with a status range and a body assertion
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" -H "content-type: application/json" \
  -d '{
    "name": "checkout",
    "type": "http",
    "url": "https://shop.example.com/health",
    "accepted_status": "200-299",
    "expected_keyword": "ready",
    "interval_sec": 60,
    "repeat_every_min": 30
  }'
```

```bash
# ICMP
-d '{"name":"gateway","type":"icmp","host":"gw.example.com","packet_count":4,"loss_threshold_pct":25}'

# UDP against a resolver
-d '{"name":"dns","type":"udp","host":"1.1.1.1","port":53,"udp_payload":"dns","dns_query_name":"example.com"}'

# gRPC health
-d '{"name":"svc","type":"grpc","host":"svc.example.com","port":50051,"grpc_service":"my.Service","tls":true}'

# SMTP with STARTTLS
-d '{"name":"mx","type":"smtp","host":"mx.example.com","port":587,"starttls":true}'

# Heartbeat — the response carries `push_token` exactly once
-d '{"name":"nightly-backup","type":"push","push_expected_interval_sec":86400,"push_grace_sec":3600}'
```

`type` is immutable. To change it, delete the monitor and create a new one.

## Reading state

```bash
# Everything currently down
curl "https://api.whatping.com/v1/monitors?state=down" -H "Authorization: Bearer $KEY"

# Open incidents
curl "https://api.whatping.com/v1/incidents?status=open" -H "Authorization: Bearer $KEY"

# Check results since a timestamp (epoch ms)
curl "https://api.whatping.com/v1/monitors/$ID/results?since=1785000000000" \
  -H "Authorization: Bearer $KEY"
```

Results responses include `retention_days`, so an integration knows the horizon rather than
discovering it when a window comes back short. It is 7.

## Alert channels

Channels are created in the dashboard, because creating one means handing over a credential.
The API lists them and attaches them:

```bash
curl https://api.whatping.com/v1/channels -H "Authorization: Bearer $KEY"
curl -X PUT "https://api.whatping.com/v1/monitors/$ID/channels/$CHANNEL" \
  -H "Authorization: Bearer $KEY"
```

Destinations come back redacted — `https://hooks.slack.com/…`, never the full URL, and never
a Telegram bot token. The API cannot be used to read back a credential you stored.

## What the API does not do

- **No CORS.** Server-side and CI use only.
- **Channels cannot be created** through it, only listed and attached.
- **Workspaces, members and billing** are dashboard-only.
- A monitor in another workspace returns `404`, not `403` — telling you an ID exists
  elsewhere would itself be information about another account.

## The OpenAPI document

[`/openapi.json`](/openapi.json) is OpenAPI 3.1, and it is **generated from the route table**
rather than maintained beside it — so it cannot describe an endpoint that does not exist, and
it cannot omit one that does. Point a generator at it:

```bash
curl -O https://whatping.com/openapi.json
openapi-generator-cli generate -i openapi.json -g go -o ./whatping
```

## Recipes

**Provision from CI, idempotently.** Key the header on the commit so a rerun of the same
pipeline is a no-op rather than a duplicate:

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "Idempotency-Key: $SERVICE-$(git rev-parse --short HEAD)" \
  -H "content-type: application/json" \
  -d "{\"name\":\"$SERVICE\",\"type\":\"http\",\"url\":\"$HEALTH_URL\"}"
```

**Mirror open incidents onto an internal board.** Use a `read` key — it can call every `GET`
and nothing else, so a compromised wall display cannot delete a monitor:

```bash
curl -s "https://api.whatping.com/v1/incidents?status=open" \
  -H "Authorization: Bearer $READ_KEY" \
  | jq -r '.data[] | [.monitor_id, .opened_at, .reason] | @tsv'
```

An incident carries `monitor_id`, not a name, so a board that shows names joins the two:

```bash
KEY_HDR="Authorization: Bearer $READ_KEY"
names=$(curl -s https://api.whatping.com/v1/monitors -H "$KEY_HDR")
curl -s "https://api.whatping.com/v1/incidents?status=open" -H "$KEY_HDR"   | jq -r --argjson m "$names" '
      .data[] as $i
      | ($m.data[] | select(.id == $i.monitor_id) | .name) as $name
      | [$name, $i.opened_at, $i.reason] | @tsv'
```

Each incident also carries `external_check` — `agreed`, `disagreed` or `unavailable` — the
[second opinion](/docs/alerting/second-opinion) verdict, which belongs on the board beside the
reason.
**Pause everything for a deploy.** Maintenance windows do not exist yet; this is how you work
around that today, and it is honest about what it is:

```bash
for id in $(curl -s https://api.whatping.com/v1/monitors \
    -H "Authorization: Bearer $KEY" | jq -r '.data[].id'); do
  curl -X POST "https://api.whatping.com/v1/monitors/$id/pause" -H "Authorization: Bearer $KEY"
done
```

**Export results before they age out.** Retention is 7 days and every results response carries
`retention_days`, so a job that runs daily never silently loses a window.

## Related

- [API overview](/features/api) — why it is shaped this way
- [OpenAPI 3.1 spec](/openapi.json)
- [Webhook payload](/docs/webhook-payload) — the push side
- [Heartbeat ping endpoint](/docs/heartbeat-api)
- [Limits](/docs/limits)
