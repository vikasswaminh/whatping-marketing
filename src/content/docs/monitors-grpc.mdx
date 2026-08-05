---
route: "/docs/monitors/grpc"
title: "gRPC monitors — WhatPing docs"
description: "Call the standard grpc.health.v1.Health/Check and assert the service reports SERVING."
h1: "gRPC monitors"
---

## What it checks

Calls the standard `grpc.health.v1.Health/Check` method and requires the response to be
`SERVING`. Anything else — `NOT_SERVING`, `SERVICE_UNKNOWN`, a transport failure — fails the
check with the reason attached.

Your server needs the health service registered. Every mainstream gRPC implementation ships
one, and it is usually a few lines to enable.

## Fields

| Field | Range | Default |
|---|---|---|
| Host | hostname or IP | — |
| Port | 1 – 65535 | — |
| Service name | blank, or a registered service | blank |
| TLS | on / off | off |
| Timeout | 1 – 60 s | 10 s |

**A blank service name asks about the server as a whole**, which is what the health
specification defines and what most servers answer. Naming a service asks about that one
service — and a server that does not know it answers `SERVICE_UNKNOWN`, which is reported as
such rather than as a connection failure, because those mean very different things.

## Create it with the API

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "content-type: application/json" \
  -d '{
    "name": "orders-api",
    "type": "grpc",
    "host": "api.example.com",
    "port": 50051,
    "grpc_service": "orders.v1.Orders",
    "tls": true
  }'
```

Field names are snake_case and an unknown one is a `422` naming the field, never a silent
drop. Full reference: [API](/docs/api).

## Failure messages

```
status NotServing
grpc NotFound: unknown service
connect failed: transport error
connect timeout
```

## What it does not do

- **No arbitrary method calls.** Health check only.
- **No client certificates.** TLS is server-authenticated.
- **No reflection.** Service names are not discovered for you.

## Worked example

```
Host:          api.example.com
Port:          50051
Service name:  (blank — the whole server)
TLS:           on
Timeout:       5 s
```

## Related

- [TCP monitors](/docs/monitors/tcp) — a weaker signal on the same port
- [HTTP monitors](/docs/monitors/http)
