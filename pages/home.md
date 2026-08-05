---
route: "/"
title: "WhatPing — uptime monitoring that watches your certificate, domain and DNS"
description: "Free uptime monitoring for HTTP, TCP and cron jobs — plus TLS expiry, domain registration, DNS records and SPF/DMARC. Alerts by email, webhook, ntfy or Telegram."
h1: "The outage that returns HTTP 200 right up until it doesn't"
---

## Hero

**H1:** The outage that returns HTTP 200 right up until it doesn't

**Sub:** Your certificate expires. Your domain registration lapses. Someone edits a DNS
record. Your SPF breaks and your email stops arriving. A health check sees none of it — and
then everything is down at once. WhatPing watches all four, alongside ordinary HTTP, TCP and
cron monitoring.

**Primary CTA:** Start monitoring — free → `https://monitor.whatping.com`
**Secondary CTA:** See how it works → `/how-it-works`

**Beta strip (small, under the CTAs):**
Free while in beta · no card · 20 monitors per workspace · one probe location

---

## Section 2 — The gap

**Heading:** Four outages your health check will never predict

Three cards, then the closing line.

**Card 1 — Your domain expires on a Sunday**
Registration lapses, the zone stops resolving, and every service on that domain disappears
at once. Email included, so you may not even get told.
*A health check would have returned 200 the whole time.*

**Card 2 — Your certificate ran out overnight**
Not down. Worse than down: browsers show an interstitial, API clients throw TLS errors, and
mobile apps fail silently. The server is fine, and it will keep telling you so.
*A health check would have returned 200 the whole time.*

**Card 3 — Your SPF record broke**
Your mail starts landing in spam — including the alert emails that were supposed to tell you
something is wrong. The monitoring is up. The path from the monitoring to you is not.
*A health check would have returned 200 the whole time.*

**Closing line:** Every one of these is a total outage with no warning signal in the place
everyone looks. So WhatPing looks somewhere else as well.

---

## Section 3 — Monitor types

**Heading:** Everything worth watching

`MonitorTypeGrid`, each card links to its feature page.

| Type | One line | Link |
|---|---|---|
| **HTTP** | Status ranges, redirects, and a keyword assertion for when 200 is a lie | `/features/uptime-monitoring` |
| **TCP** | A port either accepts a connection or it doesn't | `/features/uptime-monitoring` |
| **Heartbeat** | Your cron job pings on success; we alert when it stops | `/features/heartbeat-monitoring` |
| **Certificate** | Days until your TLS certificate expires, checked daily | `/features/certificate-monitoring` |
| **Domain** | Days until your registration expires, read from the registry | `/features/domain-expiry-monitoring` |
| **DNS** | Assert an A, AAAA, MX, TXT, CNAME or NS record still says what it should | `/features/dns-monitoring` |
| **Email auth** | SPF and DMARC present and valid, so your mail keeps arriving | `/features/email-auth-monitoring` |
| **ICMP · UDP · gRPC · Mail** | The protocols a health check cannot reach | `/docs` |

---

## Section 4 — Alerting

**Heading:** Alerts that keep working when the first one doesn't

**Body:** Email, webhook, ntfy and Telegram. The webhook payload carries `text` and `content`
aliases, so one endpoint works for Slack, Discord, Mattermost and plain automation receivers
without per-provider setup.

Two things that are unusual, and both exist because a single alert is a single point of
failure:

**Reminders while you are still down.** Most tools alert once, on the transition. If that one
message fails to deliver — SMTP hiccup, webhook 500, phone face-down — a six-hour outage is
indistinguishable from everything being fine. Set a reminder interval and WhatPing repeats
while the incident stays open. It is off unless you turn it on, because a repeating alert on
a flapping monitor is how people learn to filter your notifications.

**A second opinion.** When a check fails, WhatPing asks a network that isn't ours whether it
agrees, and says so in the alert. "The site is down" and "*we* can't reach the site" are
different problems, and until you can tell them apart you are guessing.

`AlertSample`:

```
🔴 DOWN — api (https://api.example.com): connect failed: Connection refused (os error 111)

🔴 STILL DOWN (1h 35m) — api (https://api.example.com): connect failed: Connection refused
(os error 111) · confirmed unreachable from a second network
```

**Link:** How alerting works → `/features/alerting`

---

## Section 5 — How it works

**Heading:** Three moving parts

1. **A stateless Rust prober** runs the checks. It holds no state of its own, so it can be
   restarted mid-outage without losing or duplicating anything.
2. **A backend that owns every decision.** The prober reports raw observations; whether that
   means "down" is decided in one place, against your threshold.
3. **Certificate, domain, DNS and email checks run on a daily schedule**, because a
   certificate does not stop being valid between one minute and the next.

**Link:** The architecture in detail → `/how-it-works`

---

## Section 6 — Proof

**Heading:** No testimonials. Here is what you can check instead.

**It monitors its own prober.** A heartbeat monitor watches the probe worker itself, so if the
worker dies the system tells you rather than going quiet. This is not theoretical — it caught
a real regression where a parsing bug froze the worker on a stale configuration, and it was
the only signal that anything was wrong.
→ `/docs/monitors/heartbeat`

**A broken alert channel cannot corrupt your monitoring.** Delivery is attempted after state
is already committed, and every attempt — success or failure — is recorded in a ledger.
A webhook returning 500 forever will never make a monitor look up or down.
→ `/docs/alerting/channels`

**A retry cannot double-page you.** Every check result carries a producer-generated ID, so if
the prober retries after a network blip, the replay is discarded rather than opening a second
incident.
→ `/docs/concepts`

**Nothing is claimed here that isn't tested.** 187 backend tests and 22 prober tests, and
every monitor type was verified against a live target with a known-true answer before it
shipped.

---

## Section 7 — Final CTA

**Heading:** Start with the one you keep forgetting

**Body:** Add a domain expiry monitor. It takes about thirty seconds, it costs nothing, and it
covers the failure that no amount of health checking will ever warn you about.

**CTA:** Start monitoring — free → `https://monitor.whatping.com`
**Secondary:** Read the docs → `/docs`
