---
route: "/changelog"
title: "Changelog — WhatPing"
description: "Dated record of what shipped, including the bugs found and fixed along the way."
h1: "Changelog"
---

## Intro

What shipped, and — where it is instructive — what was broken and how it was found. A
changelog that only lists features is a marketing page with dates on it.

Entries are newest first. **Build note for the implementing agent:** seed this page from
`git log --date=short --pretty='%ad %h %s'` and keep the format below. Do not backfill dates
you cannot verify from history.

---

## 3 August 2026

**External second opinion on HTTP incidents**
When an incident opens on an HTTP monitor, an independent network is asked whether it can reach
the target, and the incident is labelled `agreed`, `disagreed` or `unavailable`. It never
delays the alert — confirming an unreachable target can take 30 seconds, so the alert goes
first and the verdict follows. Verdicts annotate rather than suppress.
[Docs](/docs/alerting/second-opinion)

**Reminders while an incident is still open**
Off by default; 5 minutes to 24 hours when enabled. Reminders carry the elapsed time and the
second-opinion verdict. The delivery ledger gained an attempt column so a reminder is not
deduplicated as a replay of the original alert.
[Docs](/docs/alerting/re-alert)

**Fixed: a domain that does not exist was reporting as up**
DNS lookups report a nonexistent name as an HTTP 200 success with an error nested inside the
record set. A DNS monitor with no expected value fell through both guards and called a dead
domain healthy. Found by live verification, not by unit tests — the stubs were as wrong as the
code.

**Fixed: DNS monitors ignored the configured record type**
CNAME, NS and AAAA monitors were silently checking the default record set instead. MX and TXT
happened to work by coincidence.

**Fixed: a new monitor type could freeze the probe worker**
Adding the intelligence monitor types made the worker reject its entire configuration
response, so it kept serving a stale snapshot and looked healthy from outside. The worker's own
heartbeat monitor was the only thing that caught it, about ten minutes in. Unknown monitor
types now degrade instead of failing the parse.

**Four new monitor types** — certificate expiry, domain registration expiry, DNS record
assertions, and SPF/DMARC monitoring.
[Docs](/docs)

**Accepted status ranges and redirect depth**
`200-299,301` style expressions, and redirect following from 0 to 10. A `204` API or a
redirecting site was previously unmonitorable.

**Fixed: uptime queries would have started failing at scale**
The uptime calculation read every result in the window against a hard document ceiling. A
20-second monitor would have crossed it at roughly 3.8 days of history. It looked fine only
because no monitor had run that long yet.

---

## 2 August 2026

**Deploy from git on the VM**, with dependency and Rust versions pinned, so a deploy rebuilds
only what changed.

**First release** — HTTP, TCP and heartbeat monitors; incidents with a configurable failure
threshold; email, webhook, ntfy and Telegram alert channels; uptime percentages; and a Rust
probe worker with its own heartbeat monitor.
