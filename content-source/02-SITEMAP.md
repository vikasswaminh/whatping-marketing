# Sitemap — routes, metadata, navigation

Descriptions are 140–160 characters and written to be the search snippet. Do not rewrite them
to be prettier; they are targeting the query, not the reader who already arrived.

## Marketing

| Route | Content file | Title | Description | Priority |
|---|---|---|---|---|
| `/` | `pages/home.md` | WhatPing — uptime monitoring that watches your certificate, domain and DNS | Free uptime monitoring for HTTP, TCP and cron jobs — plus TLS expiry, domain registration, DNS records and SPF/DMARC. Alerts by email, webhook, ntfy or Telegram. | 1.0 |
| `/features` | `pages/features.md` | Features — WhatPing | Eleven monitor types, four alert channels, reminders while you are still down, and a second opinion from a network that is not ours. | 0.9 |
| `/features/uptime-monitoring` | `pages/features-uptime.md` | HTTP and TCP uptime monitoring — WhatPing | Monitor HTTP and TCP endpoints from 20 seconds up. Accepted status ranges, redirect following, and keyword assertions that catch a 200 serving a broken page. | 0.8 |
| `/features/heartbeat-monitoring` | `pages/features-heartbeat.md` | Cron and backup monitoring (heartbeat) — WhatPing | Get told when a cron job, backup or CI pipeline silently stops running. Your job pings a URL on success; WhatPing alerts when the ping does not arrive. | 0.8 |
| `/features/certificate-monitoring` | `pages/features-certificate.md` | TLS certificate expiry monitoring — WhatPing | Know weeks before a certificate expires, not minutes after. Daily checks, issuer and days remaining, with a warning threshold you set per monitor. | 0.8 |
| `/features/domain-expiry-monitoring` | `pages/features-domain.md` | Domain expiry monitoring — WhatPing | An expired domain registration is a total outage that no health check predicts. WhatPing reads the registry daily and warns you while renewal is still routine. | 0.9 |
| `/features/dns-monitoring` | `pages/features-dns.md` | DNS record monitoring — WhatPing | Assert that your A, AAAA, MX, TXT, CNAME or NS records still say what they should. Catch a wrong record or a hijacked zone before your users do. | 0.8 |
| `/features/email-auth-monitoring` | `pages/features-email-auth.md` | SPF and DMARC monitoring — WhatPing | A broken SPF record stops your email being delivered — including the alerts telling you something is wrong. WhatPing checks SPF and DMARC every day. | 0.9 |
| `/features/ping-monitoring` | `pages/features-ping.md` | Ping monitoring (ICMP) — WhatPing | Ping a host, track packet loss and median round-trip time, and alert above a loss threshold you set. Runs unprivileged, with no root and no CAP_NET_RAW. | 0.8 |
| `/features/udp-monitoring` | `pages/features-udp.md` | UDP monitoring — WhatPing | Monitor DNS, NTP and STUN services by sending a real request and requiring a real reply. There is no generic UDP port check, and this page explains why not. | 0.8 |
| `/features/grpc-monitoring` | `pages/features-grpc.md` | gRPC health check monitoring — WhatPing | Call the standard grpc.health.v1.Health/Check and require SERVING. A port check on a gRPC service tells you the listener is up, not that the service is. | 0.8 |
| `/features/smtp-imap-monitoring` | `pages/features-mail.md` | SMTP and IMAP monitoring — WhatPing | Read the mail server greeting and complete a STARTTLS handshake. This is where an expired certificate on port 587 surfaces, and a TCP check never will. | 0.8 |
| `/features/api` | `pages/features-api.md` | Uptime monitoring API — WhatPing | A REST API for monitors, incidents, results and channels. Bearer keys, read/write scopes, cursor pagination and Idempotency-Key, with an OpenAPI 3.1 spec. Free. | 0.9 |
| `/features/alerting` | `pages/features-alerting.md` | Alerting — WhatPing | Email, webhook, ntfy and Telegram. Reminders while an incident is still open, and a second opinion on whether the target is really unreachable. | 0.8 |
| `/how-it-works` | `pages/how-it-works.md` | How WhatPing works — architecture | A stateless Rust prober, a Convex backend that owns all state, and a dead man's switch on the prober itself. Restart-safe and idempotent by design. | 0.7 |
| `/pricing` | `pages/pricing.md` | Pricing — WhatPing | Free while in beta. No card, no trial timer, no seat pricing. 20 monitors per workspace. Paid tiers do not exist yet, and this page says so plainly. | 0.8 |
| `/blog` | `pages/blog.md` | Blog — WhatPing | Daily updates and monitoring insights from the WhatPing team. | 0.8 |
| `/blog/first-post` | `blog/first-post.md` | Why We Started WhatPing — WhatPing Blog | A look at the outages standard health checks can't predict, and why we decided to build WhatPing. | 0.7 |
| `/blog/best-uptime-monitoring-tools` | `blog/best-uptime-monitoring-tools.md` | Best Uptime Monitoring Tools for Startups and Small Teams (2026) | A field-tested technical guide comparing the best uptime monitoring tools for startups and small teams in 2026. | 0.7 |
| `/blog/server-uptime-monitoring` | `blog/server-uptime-monitoring.md` | Server Uptime Monitoring: Best Practices for Linux, Windows, and Cloud VMs (2026 Guide) | A comprehensive technical guide to server uptime monitoring across Linux, Windows Server, and Cloud VMs (AWS EC2, GCP, Azure). Learn agentless probing, systemd and Task Scheduler heartbeat scripts, TCP/ICMP configuration, firewall setup, and failure troubleshooting. | 0.7 |
| `/vs/uptime-kuma` | `pages/vs-uptime-kuma.md` | WhatPing vs Uptime Kuma — an honest comparison | Uptime Kuma is self-hosted, unlimited and has status pages. WhatPing is hosted, and monitors domain expiry, DNS and SPF. Where each one wins. | 0.8 |
| `/vs/better-stack` | `pages/vs-better-stack.md` | WhatPing vs Better Stack — an honest comparison | Better Stack has multi-region probing, on-call and status pages. WhatPing is free and monitors email authentication. What each does that the other does not. | 0.8 |
| `/roadmap` | `pages/roadmap.md` | Roadmap — WhatPing | What is designed but not built: status pages, maintenance windows, incident acknowledgement, tags. Marked as planned, not shipped. | 0.5 |
| `/changelog` | `pages/changelog.md` | Changelog — WhatPing | Dated record of what shipped, including the bugs found and fixed along the way. | 0.5 |
| `/security` | `pages/security.md` | Security — WhatPing | SSRF defences on every target, credentials never echoed in errors, alert destinations stored redacted, and a 7-day retention window on raw check results. | 0.6 |
| `/about` | `pages/about.md` | About — WhatPing | Built by one developer to solve a specific problem: the outages that never fail a health check. What it is, and what it deliberately is not. | 0.5 |
| `/contact` | `pages/contact.md` | Contact — WhatPing | Email, or open an issue. No sales team, no demo booking, no chat widget. | 0.4 |
| `/legal/privacy` | `pages/legal-privacy.md` | Privacy — WhatPing | What WhatPing stores, for how long, and who it is shared with. | 0.3 |
| `/legal/terms` | `pages/legal-terms.md` | Terms — WhatPing | Beta terms. No SLA, no warranty, and an explicit statement of what that means. | 0.3 |

## Docs

Sidebar groups in this order. `/docs` is the group-less index.

**Getting started**

| Route | Content file | Title | Description |
|---|---|---|---|
| `/docs` | `docs/index.md` | Documentation — WhatPing | How to monitor an endpoint, a cron job, a certificate, a domain, a DNS record or your email authentication, and how alerting behaves. |
| `/docs/quickstart` | `docs/quickstart.md` | Quickstart — WhatPing docs | Create an account, add your first monitor, attach an alert channel, and confirm it fires. About five minutes. |
| `/docs/concepts` | `docs/concepts.md` | Concepts — WhatPing docs | Monitors, checks, the failure threshold, incidents, and why a monitor sits in `pending` before it goes down. |

**Monitor types**

| Route | Content file | Title |
|---|---|---|
| `/docs/monitors/http` | `docs/monitors-http.md` | HTTP monitors — WhatPing docs |
| `/docs/monitors/tcp` | `docs/monitors-tcp.md` | TCP monitors — WhatPing docs |
| `/docs/monitors/heartbeat` | `docs/monitors-heartbeat.md` | Heartbeat monitors — WhatPing docs |
| `/docs/monitors/ssl` | `docs/monitors-ssl.md` | Certificate monitors — WhatPing docs |
| `/docs/monitors/domain` | `docs/monitors-domain.md` | Domain expiry monitors — WhatPing docs |
| `/docs/monitors/dns` | `docs/monitors-dns.md` | DNS monitors — WhatPing docs |
| `/docs/monitors/email-auth` | `docs/monitors-email-auth.md` | Email authentication monitors — WhatPing docs |
| `/docs/monitors/icmp` | `docs/monitors-icmp.md` | ICMP monitors — WhatPing docs |
| `/docs/monitors/udp` | `docs/monitors-udp.md` | UDP monitors — WhatPing docs |
| `/docs/monitors/grpc` | `docs/monitors-grpc.md` | gRPC monitors — WhatPing docs |
| `/docs/monitors/mail` | `docs/monitors-mail.md` | SMTP and IMAP monitors — WhatPing docs |

**Alerting**

| Route | Content file | Title |
|---|---|---|
| `/docs/alerting/channels` | `docs/alerting-channels.md` | Alert channels — WhatPing docs |
| `/docs/alerting/re-alert` | `docs/alerting-re-alert.md` | Reminders while still down — WhatPing docs |
| `/docs/alerting/second-opinion` | `docs/alerting-second-opinion.md` | External second opinion — WhatPing docs |

**Reference**

| Route | Content file | Title |
|---|---|---|
| `/docs/api` | `docs/api.md` | API reference — WhatPing docs |
| `/docs/webhook-payload` | `docs/webhook-payload.md` | Webhook payload — WhatPing docs |
| `/docs/heartbeat-api` | `docs/heartbeat-api.md` | Heartbeat ping endpoint — WhatPing docs |
| `/docs/limits` | `docs/limits.md` | Limits and defaults — WhatPing docs |
| `/docs/security` | `docs/security.md` | Security model — WhatPing docs |
| `/docs/troubleshooting` | `docs/troubleshooting.md` | Troubleshooting — WhatPing docs |
| `/docs/faq` | `docs/faq.md` | FAQ — WhatPing docs |

## Redirects

The first three go in `apps/web/public/_redirects` — a static export cannot use `redirects()`
from `next.config`. See `00-BRIEF.md`.

| From | To | Code |
|---|---|---|
| `/talk-to-us` | `/contact` | 308 |
| `/docs/monitors` | `/docs` | 308 |
| `/vs` | `/vs/uptime-kuma` | 308 |

`www.whatping.com/*` → `whatping.com/*` is a **Cloudflare redirect rule on the zone**, not a
`_redirects` entry — `_redirects` only sees requests that already reached the Pages project.
