---
route: /blog/ssl-certificate-monitoring-catch-expiry-before-users
title: "SSL Certificate Monitoring: Catch Expiry Before Users Do (2026)"
description: "Learn how SSL/TLS certificate monitoring works in 2026: expiry thresholds, ACME renewal failures, alert design, chain gaps, and how to catch silent HTTPS outages before customers see them."
h1: "13 SSL Certificate Monitoring: How to Catch Expiry Before Users Do (2026)"
tags: ["performance-special", "ssl certificate monitoring", "tls certificate", "expiry threshold", "acme renewal"]
keywords: ["ssl certificate monitoring", "tls certificate", "expiry threshold", "acme renewal", "https outage"]
pubDate: 2026-09-04
---

*Last updated: September 3, 2026*  
*Author: WhatPing Engineering Team*  
*Versions referenced: WhatPing Beta, Let’s Encrypt / ACME (2026), TLS 1.2–1.3 (RFC 8446), X.509 / PKIX practice, Uptime Kuma v1.23.x defaults*

---

## Executive Summary

An expired TLS certificate is one of the most embarrassing outages in production. The server is often still running. DNS still resolves. ICMP still replies. Your homepage monitor may keep returning 200 OK on HTTP—or your HTTPS check only fails after browsers and API clients already refuse the handshake. By then, customers see a scary interstitial, mobile apps throw certificate errors, payment webhooks stall, and support fills with screenshots of “Your connection is not private.”

SSL certificate monitoring means continuously reading the live certificate a hostname presents, tracking days remaining until expiry, and alerting early enough that renewal is routine work—not an incident. In 2026, that usually means a scheduled check (often daily) against port 443, a warning threshold matched to your renewal process (14 / 30 / 45–90 days), and alerts that fire when the certificate is already invalid or when remaining lifetime drops below your threshold.

This guide is an operations playbook for catching <a href="/blog/prevent-ssl-certificate-expiry-downtime/" class="theme-backlink">certificate expiry</a> before users do: how certificate monitors work, which thresholds fit ACME vs manual renewals, how to design alerts people trust, what certificate monitors do not catch (chain gaps, revocation, hostname mismatch), and how to wire certificate checks into a broader reliability stack with HTTP, domain expiry, DNS, and mail-path monitoring.

<div class="callout callout--note">
  <span class="callout__label">WhatPing note (honest)</span>
  WhatPing includes a dedicated certificate monitor that reads the live TLS certificate for a bare hostname on port 443 once a day by default, records issuer / expiry / days remaining, and fails when the cert is invalid or days remaining fall below your <code>cert_warn_days</code> threshold (default 30). It does not check OCSP/CRL revocation, full chain completeness, or non-443 ports. Pair it with an HTTP monitor when you need handshake/chain failures to surface as liveness incidents. Start at https://monitor.whatping.com/.
</div>

## Key Takeaways

- **<a href="/blog/prevent-ssl-certificate-expiry-downtime/" class="theme-backlink">Certificate expiry</a> is a calendar failure, not a crash.** The outage date is knowable weeks or months ahead.
- **HTTP 200 does not prove TLS health.** You need an explicit certificate or handshake assertion.
- **Thresholds must match renewal reality.** ACME automation, manual ops, and purchased certs need different warning windows.
- **Daily cadence is usually enough.** Certificates do not meaningfully change every minute.
- **Alert early, page late.** Treat “30 days remaining” as a ticket; treat “invalid / expired” as an incident.
- **ACME can fail silently.** DNS challenges, WAF rules, rate limits, and stuck renewers are common root causes.
- **Certificate monitors have blind spots.** Chain completeness, revocation, and hostname match often need companion checks.
- **Cover every public hostname.** Apex, www, API, admin, CDN <a href="/blog/uptime-monitoring-for-wordpress-shopify-webflow/" class="theme-backlink">custom domain</a>s, and any host customers can reach.
- **WhatPing’s default (30-day warn, daily check)** is a practical middle for teams that want expiry caught before users.



## 1. Problem Statement

Most teams discover certificate problems the hard way: a customer forwards a browser warning, an App Store review mentions TLS failures, or a partner’s webhook retries for hours. Certificates expire on a known date. The failure is that many stacks still treat that date like a surprise outage.

### Why certificate failures feel “sudden”

| What operators believe | What actually happens |
| :--- | :--- |
| “Let’s Encrypt renews automatically.” | Renewal jobs fail after DNS, WAF, or permission changes. |
| “The CDN handles certs.” | Custom hostnames, origin certs, or bypass paths still expire. |
| “Our <a class="theme-backlink" href="/blog/how-to-choose-an-uptime-monitoring-service-in-2026/">uptime tool</a> would catch it.” | Many tools only check HTTP status, not days remaining. |
| “Only the marketing site matters.” | API, admin, docs, and webhook endpoints fail first for real users. |

**Failure story A — “Homepage green, API red”**
`www.example.com` uses a CDN-managed certificate that auto-renews. `api.example.com` terminates TLS on an origin load balancer with certbot. A firewall change blocks the ACME HTTP-01 path. Certbot fails for three weeks. The marketing monitor stays green. Mobile clients start failing handshakes the morning the leaf expires. Revenue drops before on-call rings—because nobody watched days remaining on the API hostname.

**Failure story B — “We got the email… into spam”**
A CA sent renewal mail to `admin@` on a domain whose SPF/DMARC drifted months earlier. The notice never reached a human. The certificate expired on a Sunday. HTTP downtime paging still helped—but only after users were blocked. An earlier “21 days remaining” alert to Telegram would have made it a weekday ticket.

### Who feels the outage first

Certificate failures rarely hit every audience at once. Browser users see interstitial warnings. Native mobile apps often fail harder because they may pin certificates or use stricter TLS stacks. Server-to-server webhooks may retry quietly for hours before a partner emails you. SEO crawlers and payment processors can mark endpoints unhealthy while your marketing homepage still loads over a different certificate. That asymmetry is why “the site looks fine to me” is a useless incident response sentence during TLS expiry.

### The real problem

Certificate risk is not primarily cryptographic. It is operational continuity: inventory, ownership, renewal automation health, threshold design, and alert routing. SSL certificate monitoring converts a known future date into an actionable signal while there is still time to act. If your process only detects expiry after clients refuse the handshake, you do not have certificate monitoring—you have certificate forensics.

## 2. History

TLS certificate operations evolved in three eras.

**Era 1 — Manual, long-lived certificates.** Organizations bought 1–3 year certificates, installed them by hand, and tracked renewals in spreadsheets or calendars. Missed renewals were common, but the cadence was slow.

**Era 2 — Commercial SSL management and early monitors.** Hosted <a class="theme-backlink" href="/blog/best-uptime-monitoring-tools/">uptime products</a> added “SSL expiry” as a checkbox. Many implementations were shallow: warn at 7 days, email once, ignore automation health. Enterprise PKI teams built internal trackers disconnected from public uptime tooling.

**Era 3 — Short-lived certificates and ACME.** Let’s Encrypt normalized 90-day lifetimes and automated renewal. That reduced toil when automation worked—and increased outage frequency when it did not. A failed renewer now has weeks, not years, before production breaks.

By 2026, serious teams treat certificate monitoring as a first-class reliability control:
1. Inventory every public TLS hostname.
2. Observe the live presented certificate (not a spreadsheet).
3. Warn on remaining lifetime matched to process latency.
4. Verify renewal automation independently of hope.
5. Companion-check handshake/chain behavior for client-visible TLS health.

WhatPing’s certificate monitor sits in that model as a scheduled expiry check: daily by default, threshold-based, same incident and alert machinery as other monitor types—not a high-frequency probe pretending certificates flip every 30 seconds.

## 3. Definition

SSL certificate monitoring (more precisely, TLS <a href="/blog/prevent-ssl-certificate-expiry-downtime/" class="theme-backlink">certificate expiry</a> monitoring) is continuous observation of the X.509 certificate a service presents during a TLS handshake, to detect:
- Imminent expiry — days remaining below a warning threshold
- Current invalidity — certificate not valid at check time
- Operational metadata — issuer, expiry timestamp, and remaining lifetime

<div class="callout callout--note">
  <span class="callout__label">Definition box (citation-ready)</span>
  SSL/TLS certificate monitoring is a scheduled reliability check that connects to a hostname over TLS (commonly port 443), reads the live leaf certificate, computes days remaining until notAfter, and raises an alert when remaining lifetime falls below a policy threshold or the certificate is already invalid—so operators can renew before clients reject the handshake.
</div>

### Related terms

| Term | Meaning | Not the same as |
| :--- | :--- | :--- |
| **<a href="/blog/prevent-ssl-certificate-expiry-downtime/" class="theme-backlink">Certificate expiry</a> monitoring** | Days-remaining / validity checks | Full PKI posture management |
| **TLS handshake monitoring** | Can clients complete TLS now? | Calendar warning |
| **Certificate transparency monitoring** | Unexpected certs in CT logs | Expiry countdown |
| **Domain expiry monitoring** | Registry registration end date | TLS leaf end date |
| **<a href="/blog/monitor-ssl-certificate-renewal-lets-encrypt/" class="theme-backlink">ACME renewal</a> monitoring** | Did the renewer succeed? | Reading the presented cert |

## 4. Architecture

A practical SSL certificate monitoring architecture has five layers.

**4.1 Inventory layer**
Monitor every hostname that can break independently: apex and www, API and auth hosts, admin dashboards, docs/status microsites with <a href="/blog/uptime-monitoring-for-wordpress-shopify-webflow/" class="theme-backlink">custom domain</a>s, partner webhook receivers, and CDN <a href="/blog/uptime-monitoring-for-wordpress-shopify-webflow/" class="theme-backlink">custom domain</a>s. Prefer live discovery from load balancers, ingress TLS secrets, and CDN APIs over a wiki page that rots.

**4.2 Scheduler layer**
Separate concerns:
- Liveness probes (HTTP/TCP every 20s–5m): “Is it up right now?”
- Expiry checks (daily): “Will it still be valid next month?”

Polling certificates every minute mostly returns identical answers and creates noise when transient network blips are misread as cert incidents.

**4.3 TLS reader layer**
The reader typically resolves the hostname, opens TCP to port 443, completes enough of the handshake to obtain the server certificate, parses issuer / notBefore / notAfter, and computes `days_remaining`. Many productized SSL monitors intentionally evaluate the leaf expiry—not the entire trust story for every client ecosystem.

**4.4 Policy engine**
Minimum useful policy:
- Fail if the certificate is not currently valid
- Fail if `days_remaining < warn_below`

**4.5 State, incidents, and alerts**
Treat certificate warnings like other monitor transitions: repeated failures open an incident, recovery closes it when the presented cert is healthy again, alerts go to channels humans actually see, and re-alerts matter for long-lived “21 days remaining” conditions people acknowledge and forget.

*WhatPing shape: certificate monitors are type `ssl` with bare hostname, `cert_warn_days` (1–365, default 30), `interval` (default 24h), `failures-before-down` (default 2), and optional `re-alert`—feeding the same state/incident/alert path as other monitors.*

## 5. Internal Working

**5.1 What a check actually measures**
A certificate monitor measures the certificate presented to that checker, on that port, for that hostname, at that moment. Results can differ from what a browser in another region receives, what an internal client sees on another VIP, or what your renewer thinks it deployed.

**5.2 Days remaining math**
`days_remaining = floor( (notAfter - now) / 1 day )`
Monitors compare that integer to `warn_below`. After a successful renewal and deploy, days remaining jumps upward and should clear the incident.

**5.3 “Invalid” vs “expiring soon”**
A check can fail because the cert is expired, not yet valid, unreadable/unreachable under product rules, or still valid but below threshold. “Expires in 12 days” is a process failure. “Certificate is not valid” is often already user-visible. Train responders to read that difference in the first 30 seconds.

**5.4 Failure thresholds and daily checks**
If you check once per day and require two consecutive failures before marking down, you may burn an extra day before alerting. For certificate monitors, many teams set `failures-before-down` to 1. WhatPing’s docs call this out: with a once-a-day check, waiting for a second failure costs a full day.

**5.5 What the check does not prove**
Leaf expiry does not prove intermediate chain completeness, OCSP/CRL status, hostname/SAN match in every product, identical certs on every edge, or healthy ACME jobs. Use companion HTTP monitors and renewer heartbeats for those gaps.

## 6. Components

**6.1 Hostname targets**
- Bare hostname for many SaaS monitors: `api.example.com`
- No scheme, path, or IP literal in strict implementations
- One monitor per distinct TLS termination you care about

**6.2 Threshold policy**

| Situation | Suggested warn-below | Why |
| :--- | :--- | :--- |
| **Automated ACME** | 14 days | Renew-at-~30d; 14d means automation likely failed twice |
| **Default / mixed ops** | 30 days | Common middle (WhatPing / Uptime Kuma style default) |
| **Manual renewal** | 45–60 days | Need calendar time for humans |
| **Purchase / third party** | 90 days | Procurement latency dominates |

**6.3 Check cadence**
Default 24 hours. Lower intervals rarely help pure expiry. During an active cutover, temporary faster checks can confirm deploy propagation.

**6.4 Alert channels**
Do not rely only on a shared inbox or email on a domain with broken SPF/DMARC. Prefer at least one non-email path (Telegram, ntfy, webhook into tickets) for expiry warnings.

**6.5 Companion monitors**
Pair certificate monitors with HTTP(S) for handshake/chain visibility, domain expiry for registry lapse, and a heartbeat on the renewer so automation death is visible before days-remaining collapses. Mail/STARTTLS checks cover submission ports that port-443 web monitors never see.

**6.6 Ownership**
Every certificate monitor needs a service name, team owner, runbook link, renewal method, and severity mapping (ticket vs page). Without ownership, alerts become archaeology.

## 7. Workflow

**Healthy path**
- Discover hostname from ingress/CDN/inventory.
- Create a certificate monitor with a threshold matched to renewal method.
- Attach alert channels used by the owning team.
- Baseline the first successful read (issuer, expiry, days remaining).
- On warn: open a ticket, verify renewer logs, fix automation or renew manually.
- On recover: confirm new notAfter from outside, close the incident, capture root cause.
- On expire/invalid: page immediately, deploy an emergency cert, then fix the process.

**When warned**
- Confirm whether ACME/auto-renew was expected.
- If yes, inspect renewer logs, timers, DNS-01/HTTP-01, WAF, and rate limits.
- If no, start manual/vendor renewal immediately.
- Verify the presented public cert matches the one you renewed.
- After deploy, re-check from outside your network before closing.

**Severity guide**

| Condition | Severity | Response |
| :--- | :--- | :--- |
| **≤ threshold** | Medium | Same-week ticket with owner |
| **≤ 7 days** | High | Same-day action, escalate |
| **Invalid / expired / clients failing** | Critical | Incident / page |

Do not page humans at day 30 if your culture will learn to ignore pages. Use medium-severity notifications early; reserve paging for imminent or active user impact.

## 8. Configuration

### 8.1 WhatPing certificate monitor
 
| Field | Range | Default |
| :--- | :--- | :--- |
| **Domain** | bare hostname | — |
| **Warn below** | 1–365 days | 30 days |
| **Interval** | 20s–24h | 24h |
| **Failures before down** | 1–10 | 2 |
| **Re-alert every** | 5m–24h, or off | off |

Product facts that matter:
- Domain is a bare hostname (`api.example.com`)
- Checks run on port 443
- Fails when cert is not valid or days remaining is below threshold
- Domain must resolve
- Does not check chain completeness, revocation, separate hostname assertion, or non-443 ports

**API example**

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "content-type: application/json" \
  -d '{
    "name": "example.com cert",
    "type": "ssl",
    "host": "example.com",
    "cert_warn_days": 30
  }'
```

Unknown fields return 422 naming the field.

**Worked config (ACME API host)**
- **Domain:** `api.example.com`
- **Warn below:** 14 days
- **Interval:** 24 hours
- **Failures before down:** 1
- **Re-alert every:** 24 hours

Rationale: renew-at-~30 days is expected; warning at 14 means automation has likely failed more than once. Failure threshold 1 avoids losing a day.

### 8.2 Threshold selection
Ask: How long would it take us to fix this if automation had already stopped working? Set `warn_below` larger than that worst-case human latency—not equal to your happy-path renewer schedule.

### 8.3 Pairing
For each critical hostname: certificate monitor + HTTP monitor; optionally renewer heartbeat and DNS assertion.

### 8.4 Alert text examples

```text
🔴 DOWN — api-cert (api.example.com): certificate expires in 12 days
🔴 DOWN — api-cert (api.example.com): certificate is not valid
```

Monitor detail:
```text
<a href="/blog/monitor-ssl-certificate-renewal-lets-encrypt/" class="theme-backlink">Let's Encrypt</a> R3 · expires Sep 20 16:23:22 2026 GMT · 12 days remaining
```

## 9. Examples

**Example 1 — Startup with Let’s Encrypt on Kubernetes**
cert-manager issues 90-day certs and renews around 30 days remaining. Configure a WhatPing SSL monitor on `api.startup.com` with warn at 14 days and failures=1. Add an HTTP monitor on `/healthz` and a daily heartbeat that verifies the Certificate Ready condition. When HTTP-01 breaks after an ingress change, days remaining decays; at 14 days Telegram fires; the team fixes challenge routing before users see a browser warning.

**Example 2 — B2B SaaS with vendor-supplied process**
Annual cert purchase needs two approvers. Warn at 90 days on `app.clientportal.com`. Day-90 opens a procurement ticket; day-30 re-alert escalates if the new cert is not deployed. Renewal becomes a project, not a panic.

**Example 3 — Marketing on CDN, API on origin**
CDN manages the edge cert for `<a href="/blog/monitor-https-certificate-expiry-apex-www-api/" class="theme-backlink">www`; origin ALB uses a separate cert for `api`. Monitoring only `www` is the classic miss. Create separate certificate</a> monitors for both hostnames, plus DNS monitors to catch cutover mistakes.

**Example 4 — “Green expiry, red clients”**
Leaf dates look fine, but one node omitted the intermediate. A pure days-remaining monitor can stay green while strict clients fail TLS. Keep an HTTP monitor on the same host. Expiry monitoring is necessary, not sufficient.

**Example 5 — Agency multi-domain inventory**
An agency manages dozens of client hostnames across mixed CDNs and registrars. The workable pattern is API-provisioned certificate monitors with client IDs in the monitor name, a default 30-day warning, and webhooks that open tickets in the agency PSA. Certificate monitoring becomes a productized ops control instead of tribal memory about which client renews where.

## 10. Performance

Certificate monitoring performance is about signal quality per unit cost, not microseconds.

### Why daily is efficient
A 90-day cert changes slowly. Twenty-four hourly checks usually return the same days-remaining bucket. Excess frequency mostly increases false classification of transient network errors.

### Cost model

| Approach | Pros | Cons |
| :--- | :--- | :--- |
| **Daily hosted SSL monitors** | Cheap, low noise, external truth | Not instant during cutovers |
| **Only CA emails** | Free | Misses wrong-host deploys; inbox dependent |
| **Only ACME logs** | Good for automation health | Misses what is publicly presented |
| **Custom cron + openssl** | Tailored | Becomes an unowned shadow product |

### WhatPing planning context
WhatPing beta: free, 20 monitors per workspace, certificate checks default daily, 7 days raw history, one primary <a href="/blog/multi-region-uptime-monitoring-location-impacts-reliability/" class="theme-backlink">probe location</a>. Spend budget on distinct hostnames, not duplicate minute-level SSL polls of the same leaf. A single external reader is not a global edge census.

## 11. Security

Certificate monitoring is a security-adjacent reliability control.

**What it protects**
HTTPS client trust expectations, brand conversion (browser warnings destroy funnels), API/mobile ecosystem trust, and fewer emergency change windows.

**What it does not replace**
CT monitoring for unexpected issuance, HSTS, key management, revocation strategy, and application authn/WAF. An in-date certificate can still be compromised.

**Safe practices**
Use least-privilege API keys for monitor automation, prefer HMAC-verified webhooks, never put private keys into monitoring tools, and remember that if warnings only travel by email, SPF/DMARC integrity becomes part of your certificate safety net.

## 12. Troubleshooting

**Alert: expires in N days, but cert-manager says Ready**
Public traffic may hit a different certificate than the one renewed. Compare the live leaf serial/notAfter from outside to the in-cluster secret. Check all listeners (ingress, LB, CDN). Fix the path still serving the old leaf.

**Users report errors, certificate monitor green**
Likely incomplete chain, hostname mismatch, revocation/client policy, or a regional edge serving different material. Rely on HTTP/TLS errors and client telemetry—not days-remaining alone.

**<a href="/blog/monitor-ssl-certificate-renewal-lets-encrypt/" class="theme-backlink">ACME renewal</a>s fail repeatedly**
Inspect HTTP-01 reachability, DNS-01 permissions/propagation, rate limits, clock skew, WAF rules against the ACME user-agent, and disabled renewers after migrations. The SSL monitor proves time is running out; it does not fix ACME.

**Mass alert cliff after a migration**
Many certs issued the same day will warn together. Bundle tickets by owner, stagger re-issue schedules going forward, and avoid permanent threshold exceptions without an end date.

**Daily check delayed by failures-before-down = 2**
For 24h certificate checks, set `failures-before-down` to 1 unless you have a specific noise reason not to. Also remember: apex names that do not resolve cannot be certificate-monitored; monitor the subdomain that actually serves TLS.

## 13. Best Practices

- **Monitor the live presented certificate, not a spreadsheet of intended dates.**
  Spreadsheets track what you meant to deploy. Certificate monitors read what the internet actually receives on that hostname today. After cutovers, CDN changes, or partial rollouts, those two often diverge. Always trust the live leaf over the wiki.
- **One monitor per customer-facing TLS hostname that can break independently.**
  `www`, `api`, `admin`, `docs`, and webhook hosts can expire on different schedules and terminators. One homepage check will not save an API that terminates TLS elsewhere. Inventory every public hostname customers or partners can hit.
- **Match thresholds to renewal latency, not vendor marketing defaults blindly.**
  A 7-day warning is useless if procurement takes three weeks. Set `warn_below` larger than your worst-case human fix time. Defaults are starting points, not policy.
- **Use 14 days for healthy ACME, 30 as a general default, 45–90 for human/vendor processes.**
  ACME usually renews around day 30; warning at 14 means automation likely failed more than once. Manual renewals need calendar room. Vendor-purchased certs need ~90 days for approvals and shipping.
- **Prefer daily cadence for expiry; save high-frequency checks for liveness.**
  Certificates do not meaningfully change every minute. Daily checks catch calendar risk with low noise. Keep 20s–5m probes for “is it up right now,” not for days-remaining math.
- **Set failure threshold to 1 for daily certificate monitors.**
  If you check once per day and require two failures, you can lose a full extra day before alerting. For expiry, one confirmed bad read is enough. Reserve multi-failure thresholds for flaky high-frequency probes.
- **Send warnings where humans respond—not only to email.**
  Shared inboxes and broken SPF/DMARC bury CA and monitor mail. Route warnings to Telegram, ntfy, Slack, or ticket webhooks the owning team actually watches. Email can be backup, not the only path.
- **Enable re-alerts for long-lived warning states.**
  A “21 days remaining” alert acknowledged on Monday can be forgotten by Friday. Daily re-alerts keep open expiry risk visible until the presented cert recovers. Without re-alerts, soft warnings die in chat history.
- **Pair with HTTP monitors for handshake/chain visibility.**
  Days-remaining can look fine while clients fail on incomplete chains or hostname mismatch. An HTTP/TLS check on the same host catches client-visible breakage expiry monitors miss. Use both.
- **Heartbeat your renewer so automation death is visible early.**
  cert-manager, certbot, and ACME cron jobs can stop without the leaf immediately expiring. A heartbeat or Ready-condition check surfaces “automation is dead” before days remaining collapses. Do not wait for the calendar cliff.
- **Include API and webhook hosts, not just marketing sites.**
  Mobile apps and partner webhooks often fail first—and harder—than browsers on the marketing site. Revenue and integrations break on `api.` and callback hosts. Monitor those as first-class targets.
- **Document owners and runbooks on every monitor.**
  An alert without an owner becomes archaeology. Attach service name, team, renewal method, and a short runbook link. Ownership turns warnings into tickets instead of ignored noise.
- **Verify after renewal from outside your network.**
  Internal `openssl` against a pod or VIP can show the new cert while the public edge still serves the old leaf. Confirm `notAfter` from an external checker before closing the incident. Outside truth closes the loop.

## 14. Common Mistakes

- **Assuming ACME means you never think about certs again.**
  Let’s Encrypt reduces toil only while HTTP-01/DNS-01, timers, and permissions keep working. WAF rules, DNS changes, and rate limits break renewers quietly. Automation without a safety net is hope, not monitoring.
- **Monitoring only the homepage while APIs expire.**
  CDN-managed `www` can stay green while origin `api` dies. Customers and mobile clients hit the API path first. Homepage-only coverage is the classic silent outage pattern.
- **Relying on CA email alone.**
  Renewal mail goes to outdated contacts, spam folders, or domains with broken SPF/DMARC. It also does not prove the presented public cert was updated. Treat CA email as optional noise, not your primary control.
- **Warning at 7 days for manual renewals—too late.**
  Manual and vendor renewals need human calendars, approvals, and deploy windows. Seven days leaves no room for weekends, holidays, or stuck tickets. By then you are already in incident mode.
- **Paging at 30 days and training teams to ignore pages.**
  If every distant calendar reminder pages on-call, people mute the channel. Use tickets for early warnings and reserve pages for invalid/expired or ≤7-day risk. Severity discipline keeps alerts trusted.
- **Checking every minute for pure expiry.**
  Minute-level SSL polls rarely change the days-remaining answer and amplify transient network blips into fake cert incidents. They waste probe budget better spent on distinct hostnames. Daily is enough for calendar risk.
- **Ignoring non-443 TLS (mail, custom ports).**
  Web certificate monitors usually read port 443 only. Mail submission, LDAPS, and custom TLS listeners can expire independently. Cover those with the right check type—or accept that gap explicitly.
- **Trusting only internal openssl checks.**
  Inside the VPC you may see a different VIP, secret, or sidecar than public users. Internal green does not equal edge green. Always include an external reader for customer-facing hosts.
- **Forgetting CDN <a href="/blog/uptime-monitoring-for-wordpress-shopify-webflow/" class="theme-backlink">custom domain</a>s.**
  Custom hostnames on CDNs and API gateways have their own cert lifecycle. Origin renewal does not automatically fix the edge name. Inventory every <a href="/blog/uptime-monitoring-for-wordpress-shopify-webflow/" class="theme-backlink">custom domain</a> in the CDN/API console.
- **No owner on the alert.**
  Unowned monitors create “someone should fix this” loops until expiry day. Every certificate monitor needs a named team and escalation path. No owner means no response.
- **No companion HTTP monitor for chain/hostname issues.**
  Expiry-only monitoring misses incomplete intermediates and SAN mismatches. Clients fail while days-remaining still looks healthy. Pair HTTP/TLS checks wherever strict clients matter.
- **Failures-before-down = 2 on daily checks, adding a day of blindness.**
  Two consecutive daily failures can delay the first alert by ~24 hours. On a shrinking certificate clock, that day matters. Set `failures-before-down` to 1 for daily SSL monitors unless you have a specific noise reason not to.

## 15. Alternatives

| Approach | Best when | Watch-outs |
| :--- | :--- | :--- |
| **CA / registrar email** | Tiny single-host setups | Spam, wrong contacts, no presented-cert proof |
| **ACME / cert-manager health only** | Kubernetes-native estates | Can be green while public edge serves old leaf |
| **Self-hosted tools (e.g., Uptime Kuma)** | You want full control | You also own uptime of the monitor |
| **Large observability suites** | Already standardized there | Cost/complexity; SSL may be a buried checkbox |
| **Custom cron + openssl + Slack** | Very custom policy | Becomes an unowned product unless heartbeated |
| **Hosted agentless cert monitors** | External truth + low ops | Respect product limits (443 focus, no deep revocation/chain) |

For most small engineering teams: ACME as primary, hosted certificate monitors as safety net, HTTP monitors as client-visibility backup.

## 16. Comparison Tables

### Detection methods vs failure modes

| Failure mode | CA email | ACME dashboard | Daily SSL monitor | HTTP monitor |
| :--- | :--- | :--- | :--- | :--- |
| **Leaf approaching expiry** | Partial | Partial | Strong | Late |
| **Leaf already expired** | Late/none | Maybe | Strong | Strong |
| **Wrong host renewed** | Weak | Weak | Strong (if monitored) | Strong |
| **Incomplete chain** | No | No | Weak/No | Strong |
| **Mail cert on 587 expired** | No | No | No (443-only) | No |
| **Domain registration lapsed** | No | No | No | Yes (as downtime) |

### WhatPing certificate monitor vs HTTP-only uptime

| Capability | HTTP-only uptime | WhatPing certificate monitor |
| :--- | :--- | :--- |
| **Detects days remaining** | Usually no | Yes |
| **Alert before user-visible expiry** | Weak | Strong |
| **Detects expired cert after the fact** | Often yes | Yes |
| **Default cadence** | 1–5 minutes typical | Daily (appropriate) |
| **Chain completeness** | Sometimes via TLS errors | Not directly |
| **Same alert channels as other silent failures** | Depends | Yes |

## 17. Enterprise Deployment

Enterprise certificate monitoring fails when it is a shared mailbox plus a quarterly spreadsheet.

**Operating model**
- Platform team provides standards, API automation, and alert routing patterns
- Service teams own hostname inventory and renewal runbooks
- Security / PKI owns issuance policy and exceptions
- Incident command owns severity for expiry vs invalid

**Policy pack (example)**
- Every public hostname has an external certificate monitor.
- ACME services warn at 14 days; non-ACME at 60–90 days.
- Invalid/expired is always high severity by customer impact.
- No production hostname relies solely on CA email.
- Renewals require post-deploy external verification.
- Diff weekly: cloud inventory vs monitors configured. Missing monitor = defect.

**Alert routing**
- Threshold warnings → team ticket queue
- ≤7 days remaining → escalate
- Invalid/expired → primary on-call
- Daily re-alerts until resolved

A simple SaaS certificate monitor is excellent for public leaf expiry truth. Enterprises still need internal PKI tooling, CT monitoring, and possibly multi-region edge verification. Use WhatPing-style monitors as the external expiry safety net—not as the entire PKI platform.

## 18. Cloud Deployment

Cloud makes renewals easier and creates new ways to watch the wrong certificate.

### Common patterns

| Pattern | Monitor |
| :--- | :--- |
| **CDN / edge cert** | Edge hostname(s) |
| **ALB/NLB + ACM** | Public LB hostnames / aliases |
| **Ingress + cert-manager** | Ingress hosts |
| **API Gateway <a href="/blog/uptime-monitoring-for-wordpress-shopify-webflow/" class="theme-backlink">custom domain</a>s** | <a href="/blog/uptime-monitoring-for-wordpress-shopify-webflow/" class="theme-backlink">Custom domain</a> names |

### Cloud-specific failure modes
Renewed cert not attached to the right listener; DNS still pointing at an old distribution; blue/green presenting different certs; “issued” ≠ “associated.”

### Deploy checklist
- Issue/renew the certificate.
- Attach it to all required listeners/distributions.
- Confirm DNS targets the intended terminator.
- Externally read leaf notAfter and confirm HTTP is green before closing the ticket.

### Using WhatPing in cloud estates
Provision SSL monitors via API from Terraform/CI for each public hostname. Default `cert_warn_days=30`, override to 14 for ACME hosts. Webhook into chat or tickets. Keep HTTP monitors on the same hosts and add domain expiry monitors for the registered domains. Prioritize production public hostnames inside workspace limits.

Setup: https://monitor.whatping.com/ · Docs: https://www.whatping.com/docs/monitors/ssl/

*Private-only certs need in-network checks; hosted internet checkers cannot see them without exposure.*

## 19. FAQs

**1) What is SSL certificate monitoring?**
SSL certificate monitoring continuously checks the live TLS certificate a hostname presents—usually on port 443. It tracks days remaining until expiry and alerts when the cert is invalid or below your warning threshold. That gives you time to renew before browsers, apps, and APIs fail the handshake. It is a calendar safety net, not a replacement for full TLS security testing.

**2) How early should I get SSL expiry alerts?**
Match the warning window to how slow your renewal process really is. Use about 14 days for healthy ACME automation, 30 days as a solid default, and 45–60 days for manual ops. Choose ~90 days when purchasing or third parties are involved. Warn early enough for tickets; page only when expiry is imminent or already user-visible.

**3) Why didn’t my uptime tool warn me before expiry?**
Many uptime setups only check HTTP status or basic reachability. They notice certificate problems only after the handshake already fails for clients. Dedicated certificate monitors alert on days remaining, not just “site down.” Without that, expiry looks sudden even though the date was knowable weeks earlier.

**4) Is daily SSL checking enough?**
Yes for expiry risk—certificates do not meaningfully change every minute. Keep high-frequency HTTP/TCP checks for liveness, and use daily certificate checks for calendar risk. During cutovers, temporary faster checks can confirm the new leaf is live. For daily monitors, set `failures-before-down` to 1 so you do not lose an extra day.

**5) Does Let’s Encrypt auto-renewal mean I can skip monitoring?**
No. ACME renewers fail after DNS, WAF, permission, and rate-limit changes—often silently. Certificate monitoring catches “automation stopped working” while you still have days left. Treat ACME as the primary control and external expiry checks as the safety net. Skipping monitoring means customers may find the outage first.

**6) What’s the difference between certificate monitoring and domain expiry monitoring?**
Certificate monitoring tracks the TLS leaf’s notAfter date—the end of the HTTPS certificate. Domain expiry monitoring tracks the domain registration end date at the registrar. Either can take you offline, and they fail independently. You need both if you want to avoid “HTTPS looks fine until the domain or cert dies.”

**7) Can SSL certificate monitors detect every TLS problem?**
No. Basic expiry monitors may miss incomplete chains, revocation, hostname mismatches, or non-443 services like mail. Pair them with HTTP/TLS checks where those risks matter. Expiry monitoring answers “how long until this leaf dies,” not “will every client trust this path.” Use companion monitors for the gaps.

**8) How do I monitor SSL certificates with WhatPing?**
Create a certificate monitor per bare hostname, set `cert_warn_days` (default 30), and keep the daily interval. Attach alert channels people actually see, and optionally provision via API with `type: "ssl"`. Pair each critical host with an HTTP monitor for handshake/chain visibility. Details: Certificate monitors.

## 20. References

- WhatPing certificate monitors: https://www.whatping.com/docs/monitors/ssl/
- WhatPing features: https://www.whatping.com/features/
- WhatPing concepts: https://www.whatping.com/docs/concepts/
- WhatPing API: https://www.whatping.com/docs/api/
- WhatPing limits: https://www.whatping.com/docs/limits/
- WhatPing app / CTA: https://monitor.whatping.com/
- WhatPing site: https://www.whatping.com/
- TLS 1.3: RFC 8446
- Related blog: <a class="theme-backlink" href="/blog/best-uptime-monitoring-tools-for-startups/">Best uptime monitoring tools for startups (2026)</a>
- Internal linking targets: <a class="theme-backlink" href="/blog/hidden-causes-website-downtime-ping-tests-never-catch/">hidden causes beyond ping</a>; <a class="theme-backlink" href="/blog/how-uptime-monitoring-actually-works/">how uptime monitoring works</a>; domain expiry; DNS monitoring

## 21. Conclusion

<a href="/blog/prevent-ssl-certificate-expiry-downtime/" class="theme-backlink">Certificate expiry</a> is not mysterious. It is a dated event teams either observe early or discover through customers. Keep renewal automation as the primary control. Read the live certificate from outside your assumptions. Warn on a threshold that matches how slow your humans and vendors actually are. Page on invalid/expired or imminent user impact—not on every distant calendar reminder. Pair expiry monitors with HTTP checks, renewer heartbeats, and domain/DNS integrity monitors so “HTTPS looks fine” means more than “one path returned a status code.”

SSL certificate monitoring will not replace PKI strategy or CT monitoring. It will catch the common, preventable outage where everything is “up” until the calendar runs out.

Next step: add certificate monitors for every public hostname at https://monitor.whatping.com/, start with a 30-day warning (or 14 for ACME), set failures-before-down to 1 on daily checks, and verify alert delivery before the next renewal cliff.

<div class="related-guides-box">
  <div class="related-guides-header">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F9B900" stroke-width="2">
      <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
    </svg>
    <h3>Related Guides</h3>
  </div>
  <p>Learn more about <a href="/blog/how-uptime-monitoring-actually-works/">how uptime monitoring works</a> or explore <a href="/blog/hidden-causes-website-downtime-ping-tests-never-catch/">hidden causes of downtime</a> to catch every blind spot.</p>
  <a href="https://monitor.whatping.com" class="related-cta-btn">Start Free with WhatPing →</a>
</div>

### Related SSL Monitoring Guides

* <a href="/blog/monitor-ssl-certificate-renewal-lets-encrypt/" class="theme-backlink">How to Monitor SSL Certificate Renewal Without Missing Let's Encrypt Cycles</a>
* <a href="/blog/monitor-https-certificate-expiry-apex-www-api/" class="theme-backlink">Monitor HTTPS Certificate Expiry Across Apex, www, and API Hostnames</a>
* <a href="/blog/expired-ssl-certificate-alerts-detect-escalate-recover/" class="theme-backlink">Expired SSL Certificate Alerts</a>
* <a href="/blog/hidden-causes-website-downtime-ping-tests-never-catch/" class="theme-backlink">Hidden Causes of Website Downtime</a>
* <a href="/blog/website-uptime-monitoring-guide-2026/" class="theme-backlink">Website Uptime Monitoring Guide 2026</a>

