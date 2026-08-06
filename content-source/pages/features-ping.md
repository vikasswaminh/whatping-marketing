---
route: "/features/ping-monitoring"
title: "Ping monitoring (ICMP) — WhatPing"
description: "Ping a host, track packet loss and median round-trip time, and alert above a loss threshold you set. Runs unprivileged, with no root and no CAP_NET_RAW."
h1: "The link degraded three days before it failed"
---

## The problem

Network paths rarely die cleanly. They rot: 2% loss on Monday, 8% on Wednesday, and by Friday
the VPN tunnel drops every few minutes and nobody can say when it started.

An HTTP check will not show you this. It retries at the TCP layer, so moderate packet loss
looks like a slightly slower response and nothing else — until loss crosses the point where
retransmits stop covering for it, and then everything fails at once with no history to explain
why.

Ping is the oldest tool in the box for a reason: it is the only check that measures the path
itself rather than something running on top of it.

## How it works

Give it a host. Each check sends a small burst of ICMP echo requests — four by default, up to
ten — and records how many came back and how long they took.

**Latency is the median, not the mean.** A single retransmit moves a four-sample mean
noticeably, and the number an operator glances at during an incident should reflect the typical
packet rather than the worst one. The median ignores one bad sample; the mean reports it as if
the whole path had changed.

**Packet loss has its own threshold**, separate from the up/down decision. Set it to `0` and
any dropped echo fails the check. On a link you already know is lossy — a congested uplink, a
satellite hop, a busy VPN concentrator — set it to `25` or `50` and you get paged for genuine
degradation instead of for weather.

## It runs unprivileged, and that is not a detail

The usual reason a monitoring agent ends up running as root is ICMP. Raw sockets need
privilege, so the agent gets `CAP_NET_RAW` or, more often, just gets run as root and nobody
revisits it.

This one uses a `SOCK_DGRAM` ICMP socket, which Linux permits for any process whose group falls
inside `net.ipv4.ping_group_range`. The deploy grants that to the worker's group alone. No
root, no capability on the binary, no exception carved out for one feature.

## What it will not tell you

Stated plainly, because ping is the check most often asked to mean more than it does.

**A host that answers pings is not a host that works.** A machine with a full disk, a dead
application and a wedged database answers ICMP perfectly, forever. If something is serving
traffic, an [HTTP](/features/uptime-monitoring) or TCP monitor is the check that matters, and
ping is the one that explains *why* it got slow.

**A failed ping is often a firewall, not an outage.** Plenty of networks deprioritise or drop
ICMP entirely. A host that fails ICMP but passes HTTP is a policy decision somewhere upstream.

## What you'll see when it fires

```
🔴 DOWN — gateway (gw.example.com): 50% packet loss exceeds 25% threshold
🔴 DOWN — gateway (gw.example.com): 100% packet loss (4 sent, 0 received)
```

## Limits

- One probe location. Loss measured from one vantage point is loss on one path.
- 20 monitors per workspace, 7 days of history.
- Private and link-local addresses are refused by default.

## Related

- [ICMP reference](/docs/monitors/icmp) — every field and its range
- [UDP monitoring](/features/udp-monitoring)
- [HTTP and TCP monitoring](/features/uptime-monitoring)

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
**Secondary:** Read the ICMP docs → `/docs/monitors/icmp`
