---
route: "/docs/faq"
title: "FAQ — WhatPing docs"
description: "Cost, probe locations, retention, self-hosting, and the other questions worth answering before you sign up."
h1: "FAQ"
---

> **Build note:** render this page with `FAQPage` JSON-LD. Keep the question wording — it is
> written to match how people search.

## Is it really free?

Yes. No card, no trial timer, and no paid tier — because billing has not been built. See
[pricing](/pricing) for exactly what that includes and what it does not.

## How many locations do you check from?

**One.** WhatPing does not have probes in multiple regions and does not claim to.

When an HTTP incident opens, an independent network is asked whether it agrees the target is
unreachable, and the incident is labelled with the answer. That distinguishes "your service is
down" from "our path to it is broken" — it is one extra vantage point, not a fleet. See
[second opinion](/docs/alerting/second-opinion).

If you need regional coverage, [Better Stack](/vs/better-stack) sells it.

## How often can it check?

Every 20 seconds at the fastest, for HTTP, TCP and heartbeat monitors.

Certificate, domain, DNS and email-auth monitors default to once a day. You can shorten it, but
a certificate does not stop being valid between one minute and the next.

## How long is history kept?

**7 days.** Raw check results are deleted after that, and there is no long-term rollup, so
uptime percentages cover the last 24 hours and the last 7 days.

Longer retention needs aggregated summaries and is on the [roadmap](/roadmap).

## Can I self-host it?

Not today. WhatPing is hosted only.

If self-hosting is a requirement, [Uptime Kuma](/vs/uptime-kuma) is the right tool and is
genuinely excellent at it.

## Can I get a status page?

Not yet. It is designed and on the [roadmap](/roadmap), and the technical blocker has been
removed — but it is not in the product, and nothing here should imply otherwise.

## Do you support Slack and Discord?

Yes, through the webhook channel. The payload carries both `text` and `content`, which is what
Slack and Discord respectively render, so one endpoint works for either without configuration.

There is no native Slack or Discord app.

## Do you send SMS or phone calls?

No. Email, webhook, ntfy and Telegram.

ntfy delivers push notifications to your phone with no account and no app store login, which
covers most of what people want SMS for.

## Can it monitor something on my LAN?

Private-network targets are refused by default. A deployment can opt in deliberately, but the
hosted service does not — a probe that will fetch arbitrary private addresses is a liability.

## What happens if WhatPing itself goes down?

Checks stop running and you are not alerted. There is no SLA and no guarantee.

The prober is watched by a heartbeat monitor evaluated in a separate process, so an internal
failure is detected and reported rather than going quiet — but that does not help if the whole
service is unavailable.

The honest advice: for anything critical, run a second monitoring system and have each one watch
the other's host. That is true of any single monitoring vendor, paid or free.

## Can I use it for a client's site?

Yes. Monitor anything you own or are authorised to monitor.

## Is there an API?

Yes. A REST API at `https://monitor-site.whatping.com/v1` covers monitors, incidents, check
results and alert channels — enough to provision from Terraform or CI and read state back
into your own dashboard.

Authenticate with `Authorization: Bearer sk_…` using a key from your workspace settings.
Keys are scoped read or write, and rate limits are 600 reads and 60 writes a minute.

See the [API reference](/docs/api). Outbound webhooks remain the push side.

## Do you support ping (ICMP)?

Yes. An ICMP monitor sends echo requests, reports the median round-trip time, and fails
above a packet-loss threshold you set.

## Do you support UDP?

Yes, with a constraint worth understanding before you rely on it: a generic "is this UDP
port open" check is **not possible**. UDP has no handshake, so a port that never replies is
indistinguishable from a firewall dropping your packets — a monitor built that way reports
healthy for a dead service.

So a UDP monitor sends something a real server answers — a DNS query, an NTP request, a STUN
binding request, or raw bytes you supply — and requires a reply. See
[UDP monitors](/docs/monitors/udp).

## Why 20 monitors?

A conservative cap while the system is young, not a pricing lever. It will rise.

## What does the second opinion actually do?

Fetches your URL from a network that is not ours, and labels the incident `agreed`,
`disagreed` or `unavailable`.

It never delays the alert — confirming an unreachable target can take 30 seconds — and it never
suppresses one. If our probe cannot reach your service and another network can, that is still a
real failure on one network path, and your users on that path see it too.

## Do you monitor email deliverability?

Partly. WhatPing checks daily that SPF and DMARC records are still published for your domain,
which catches the record disappearing or being broken during an unrelated DNS change.

It does not evaluate SPF lookup counts, DKIM selectors, DMARC policy strength or alignment.
See [email auth monitors](/docs/monitors/email-auth).

## Who builds this?

One developer. See [about](/about), which is honest about what that means.

## Will my monitors get switched off if you start charging?

No. If paid tiers arrive they will be for things that cost real money — more monitors, longer
retention, higher frequency — and existing monitors will not be switched off without notice.

That is a statement of intent, not a contract. Weigh it accordingly.
