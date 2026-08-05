---
route: "/docs/alerting/second-opinion"
title: "External second opinion — WhatPing docs"
description: "When an HTTP incident opens, an independent network is asked whether it agrees the target is unreachable, and the incident is labelled with the answer."
h1: "External second opinion"
---

## The problem it solves

Every failure verdict comes from one vantage point. So these two situations look identical:

- your service is down
- your service is fine, and the path between our probe and it is broken

Until you can tell them apart you are guessing — usually at 3am, usually while deciding whether
to wake someone else up.

## What it does

When an incident opens on an **HTTP monitor**, WhatPing asks an independent network to fetch the
same URL, and records what happened on the incident.

| Verdict | Meaning | What to do |
|---|---|---|
| **agreed** | The other network could not reach it either | Treat it as a real outage |
| **disagreed** | The other network reached it fine | Still a real failure on one network path — but look at routing, DNS and firewalls before assuming your service is down |
| **unavailable** | The check could not be performed | No information either way; rely on the original check |
| **skipped** | Not applicable — not an HTTP monitor, or turned off | — |

## It never delays the alert

Worth being explicit, because the obvious design is to confirm first and alert second.

Confirming an unreachable target takes up to 30 seconds — an unreachable host is exactly the
case that takes longest to give up on. Gating the alert on that would add half a minute to every
real outage, which is the wrong trade in the situation the product exists for.

So the alert goes out immediately, and the verdict is attached when it arrives — appearing on
the incident in the dashboard and in any [reminder](/docs/alerting/re-alert).

**The first alert never carries a verdict**, because the check has not finished when it is sent.
That is expected, not a bug.

## It annotates, it does not suppress

A `disagreed` verdict does **not** cancel the alert or close the incident.

If our probe cannot reach your service and another network can, that is still a real
reachability failure on one network path — and your users on that path are seeing it too.
Silencing the alert would turn a partial outage into silence, which is the failure mode this
whole product is built against.

## When it says unavailable

`unavailable` is used whenever the result says nothing about your target:

- **Private or internal address.** The external fetcher will not request a private address, so a
  LAN or VPN target can never be confirmed. On a deployment monitoring internal services, this
  will be most of them.
- **Rate limit or authentication failure** on the confirmation service.
- **The confirmation service itself failing.**

The rule is fail open: a fault on the confirmation path is never allowed to look like evidence
about your service.

## Configuration

One toggle per HTTP monitor: **Confirm externally**, on by default.

Turn it off for monitors where the answer will always be `unavailable` — anything private —
to keep incidents clean.

## What it is not

**One independent network path, not a global probe fleet.** It distinguishes "the target is
down" from "our path to the target is broken", which is genuinely useful, and it is not
multi-region probing.

If you need to know that your service is unreachable from a particular region specifically,
that is a real requirement and WhatPing does not meet it. [Better
Stack](/vs/better-stack) does.

## What you'll see

In the incident list:

```
09:14  open   connect failed: Connection refused
              confirmed unreachable externally
```

In a reminder:

```
🔴 STILL DOWN (35m) — api (https://api.example.com): connect failed: Connection refused
(os error 111) · confirmed unreachable from a second network
```

And when the verdicts disagree:

```
🔴 STILL DOWN (35m) — api (https://api.example.com): timed out after 10000ms
· reachable externally — may be a local network issue
```

In the webhook payload, as `incident.externalCheck`. See
[webhook payload](/docs/webhook-payload).

## Related

- [Reminders](/docs/alerting/re-alert)
- [HTTP monitors](/docs/monitors/http)
- [How WhatPing works](/how-it-works)
