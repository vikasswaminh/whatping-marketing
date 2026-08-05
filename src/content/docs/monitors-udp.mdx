---
route: "/docs/monitors/udp"
title: "UDP monitors — WhatPing docs"
description: "Send a real request over UDP and require a real reply. A generic port-open check is not possible, and this page explains why."
h1: "UDP monitors"
---

## Read this first

**There is no "is this UDP port open" check — here or anywhere.**

TCP has a handshake, so a refused connection is a definite answer. UDP has none. You send a
packet and either something comes back or nothing does, and *nothing* is produced equally by
a healthy server that ignores your packet, a firewall dropping it silently, and a service
that died an hour ago.

A monitor built on "did the port accept a packet" therefore reports healthy for a dead
service, which is worse than having no monitor at all. So every UDP check here sends
something a real server answers, and requires the answer.

Uptime Kuma has the same limitation, for the same reason.

## What it checks

Sends a payload to a host and port, and waits for a reply within the timeout.

| Payload | What it sends | Answered by |
|---|---|---|
| `dns` | A query for a name you choose | DNS resolvers |
| `ntp` | An NTPv4 client request | NTP servers |
| `stun` | An RFC 5389 binding request | STUN and TURN servers |
| `raw` | Bytes you supply as hex | anything with a known protocol |

You can also assert the reply starts with a hex prefix. Leaving it blank accepts any reply,
which is usually right — that a server answered at all is the signal.

## Fields

| Field | Range | Default |
|---|---|---|
| Host | hostname or IP | — |
| Port | 1 – 65535 | — |
| Payload | dns, ntp, stun, raw | dns |
| Name to look up | domain, `dns` payload only | example.com |
| Payload hex | required for `raw`, up to 256 bytes | — |
| Expected reply prefix | hex, optional | — |
| Timeout | 1 – 60 s | 10 s |

## The three outcomes

```
up
port unreachable (ICMP): nothing is listening
no reply within timeout (a UDP drop is indistinguishable from a dead service)
```

The middle one is worth knowing about. When a host is reachable but nothing is bound to the
port, it usually returns an ICMP port-unreachable — and that **is** definitive. It is the one
unambiguous negative UDP offers, so it is reported separately from silence.

The third message is deliberately wordy. A UDP timeout genuinely does not prove the service
is down, and an alert that implies certainty it does not have is how people learn to distrust
alerts.

## Worked example

```
Host:     1.1.1.1
Port:     53
Payload:  dns
Name:     example.com
Timeout:  5 s
```

## Related

- [TCP monitors](/docs/monitors/tcp) — where a port check *is* meaningful
- [DNS monitors](/docs/monitors/dns) — for asserting record contents rather than liveness
