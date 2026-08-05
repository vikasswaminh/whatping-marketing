---
route: "/docs/monitors/icmp"
title: "ICMP monitors — WhatPing docs"
description: "Ping a host, report the median round-trip time, and fail above a packet-loss threshold you set."
h1: "ICMP monitors"
---

## What it checks

Sends ICMP echo requests to a host and reports the **median** round-trip time. The check
fails when packet loss exceeds your threshold, or when nothing comes back at all.

Median rather than mean, deliberately: one retransmit on a four-packet sample moves a mean
noticeably, and the number an operator glances at should reflect the typical case.

## Fields

| Field | Range | Default |
|---|---|---|
| Host | hostname or IP, no scheme | — |
| Echo requests per check | 1 – 10 | 4 |
| Packet-loss threshold | 0 – 99 % | 0 % |
| Interval | 20 s – 24 h | 60 s |
| Timeout | 1 – 60 s | 10 s |
| Failures before down | 1 – 10 | 2 |

A threshold of `0` means any lost packet fails the check. On a link you know is lossy, `25`
or `50` reports genuine degradation without paging you for one dropped echo.

## Create it with the API

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "content-type: application/json" \
  -d '{
    "name": "gateway",
    "type": "icmp",
    "host": "gw.example.com",
    "packet_count": 4,
    "loss_threshold_pct": 25,
    "interval_sec": 60
  }'
```

Field names are snake_case and an unknown one is a `422` naming the field, never a silent
drop. Full reference: [API](/docs/api).

## What it tells you, and what it does not

ICMP proves a host is reachable and how far away it is. It says **nothing about whether the
service on that host works** — a machine with a full disk and a dead application answers
pings perfectly.

Use it for network reachability: a gateway, a router, a VPN endpoint, or a host you want
latency history for. For anything serving traffic, an [HTTP](/docs/monitors/http) or
[TCP](/docs/monitors/tcp) monitor is the stronger signal.

Many networks also deprioritise or drop ICMP entirely. A host that fails an ICMP check but
passes an HTTP check is usually a firewall policy, not an outage.

## Failure messages

```
100% packet loss (4 sent, 0 received)
50% packet loss exceeds 25% threshold
host did not resolve
```

## Running unprivileged

Worth stating, because it is the usual reason a monitoring agent ends up running as root:
this one does not. ICMP here uses a `SOCK_DGRAM` socket, which Linux permits for process
groups inside `net.ipv4.ping_group_range`, and the deploy grants that to the worker's group
alone — not to every group on the host, and without `CAP_NET_RAW` on the binary.

If ICMP monitors report `icmp socket unavailable`, that sysctl is the thing to check.

## Worked example

```
Host:                   gateway.example.com
Echo requests:          4
Packet-loss threshold:  25%
Interval:               60 s
Failures before down:   2
```

## Related

- [TCP monitors](/docs/monitors/tcp)
- [Limits](/docs/limits)
