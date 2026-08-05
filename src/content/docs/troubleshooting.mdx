---
route: "/docs/troubleshooting"
title: "Troubleshooting — WhatPing docs"
description: "Why a monitor sits in pending, why Telegram alerts never arrive, why one email for a two-hour outage, and other things people actually ask."
h1: "Troubleshooting"
---

## My monitor says `pending` and won't go up

`pending` means the state is not yet established. Two causes:

**It has never completed a check.** A monitor with a 60-second interval takes up to a minute
before its first result. Intelligence monitors — certificate, domain, DNS, email auth — are
evaluated on a schedule and can take up to about 15 minutes for the first check.

**It is failing but has not reached its threshold.** With the default threshold of 2, one
failure leaves the monitor in `pending`. Look at the last error on the monitor: it will tell you
what is failing. If it stays there, the monitor is alternating between success and failure —
which usually means a load balancer with one bad backend.

## I got one email for a two-hour outage

That is the default. Alerts fire on transitions: down, and recovered. Nothing in between.

Set **Re-alert every** on the monitor to repeat while the incident is open. See
[reminders](/docs/alerting/re-alert). It is off by default deliberately.

## My Telegram alerts never arrive

Almost always the same cause: **you have not messaged the bot**.

Telegram does not permit a bot to message a user who has never messaged it first. A fresh,
perfectly valid token fails with `403: bot can't initiate conversation with a user`.

Fix: open the bot in Telegram and press **Start**, or send it any message. For a group, add the
bot to the group and send a message there.

Then check the chat ID. `https://api.telegram.org/bot<TOKEN>/getUpdates` shows it. A group ID is
negative, usually starting `-100`; using a positive ID for a group silently delivers nowhere.

The delivery ledger will show the failure and its status code.

## My webhook alerts never arrive

Check the delivery ledger first — it records every attempt and the error.

`404` — wrong URL. Slack and Discord webhook URLs expire when the integration is removed.
`403` — the webhook was revoked; recreate it.
`timeout` — your receiver took longer than 10 seconds. Acknowledge with a 200 first and do the
work afterwards.

## Why does my private target say "external check unavailable"?

Because it is. The [second opinion](/docs/alerting/second-opinion) works by having an
independent network fetch your URL, and that network will not request a private address.

`unavailable` means "no information", not "there is a problem". Turn **Confirm externally** off
on private monitors to keep incidents clean.

## Why does my uptime only cover 7 days?

Raw check results are deleted after 7 days and there is no long-term rollup, so the available
windows are the last 24 hours and the last 7 days. Longer retention is on the
[roadmap](/roadmap).

If a window shows a shortened period, the monitor produced more results than a single query
reads and the figure covers the most recent portion — the interface says which period it
actually covered.

## My heartbeat monitor alerts even though the job ran

The job ran, but the ping did not arrive or did not arrive in time.

**Check where the ping is.** If it is in a `finally`, a `trap`, or an `if: always()` step, it
fires whether or not the job succeeded — which is the opposite of what you want, and separately
means a failing job looks healthy.

**Check the grace period.** A job that usually takes 2 minutes but occasionally takes 8 needs a
grace period that covers the 8.

**Check the ping actually left the machine.** `curl` without `-f` exits 0 on an HTTP error. Use
`curl -fsS --retry 3`.

**Check the URL.** A wrong token returns `404 {"ok":false}` — with `-f`, curl will fail loudly.

## I get alerts for a monitor that is clearly fine

**Threshold too low.** Raise **Failures before down** from 1 to 2 or 3 on a flaky network.

**Accepted status too narrow.** `200` alone fails a `204` health endpoint and any redirect. Use
a range: `200-299`, or `200-299,301`.

**Redirects not followed.** With max redirects at 0, a site that redirects `/` to `/en/` returns
`301` and fails unless `301` is in your accepted set. Either accept it, or set max redirects to
follow.

**Keyword no longer on the page.** A copy change removes the marker and the assertion starts
failing on a working page. Pick a marker unlikely to change — an element, not a sentence.

If the second opinion says `disagreed`, the target was reachable from another network when yours
was not. That is a genuine finding: look at routing, DNS and firewalls between the probe and
your service.

## My certificate monitor says down but the certificate is valid

It is warning, not reporting expiry. `certificate expires in 12 days` means days remaining is
below your **Warn below** threshold. That is the monitor doing its job.

Raise or lower the threshold to match how long a renewal actually takes you.

## My domain monitor says "registry returned no expiry date"

The registry for that TLD does not publish a machine-readable expiry date. Some ccTLDs withhold
it entirely.

Nothing can be done in the product — WhatPing reports what the registry returned rather than
guessing. For those TLDs, a calendar reminder is the honest alternative.

## My DNS monitor fails but the record looks right

**Substring matching.** The expected value must appear inside a returned record. Watch for
trailing dots: an NS record comes back as `pat.ns.cloudflare.com.` — matching `cloudflare.com`
works, matching `cloudflare.com.` also works, matching `cloudflare` works. Matching
`ns.cloudflare.com,` with a stray comma does not.

**Record type.** The monitor checks exactly the type you selected. If you expect an IP and
selected `CNAME`, you will get "no CNAME records found" even though the name resolves fine.

**`Domain does not exist`** means the name has no records at all, which usually means a typo in
the monitor or a zone that has genuinely gone.

## I can't add a monitor — 20 is the limit

The cap is 20 per workspace. Delete one you no longer need, or create a second workspace. The
cap will rise; see the [roadmap](/roadmap).

## Still stuck

[Contact](/contact) — with the monitor name and what you expected to happen.
