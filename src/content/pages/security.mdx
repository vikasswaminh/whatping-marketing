---
route: "/security"
title: "Security — WhatPing"
description: "SSRF defences on every target, credentials never echoed in errors, alert destinations stored redacted, and a 7-day retention window on raw check results."
h1: "Security"
---

## Why this page is specific

A monitoring service is a machine that fetches URLs you supply, from inside its own network,
and stores credentials you give it. That is a server-side request forgery engine and a secret
store wearing a friendly interface. So the defences are worth describing precisely rather than
asserting.

---

## Targets you can ask us to fetch

**Private-network targets are refused by default.** Every monitor target is checked against
loopback, RFC1918, link-local (including `169.254.169.254`, the cloud metadata address), CGNAT,
IETF protocol assignments, benchmarking ranges and multicast. IPv6 equivalents are covered:
`::1`, unique-local `fc00::/7`, link-local `fe80::/10`, and IPv4-mapped addresses are unwrapped
and re-checked so `::ffff:10.0.0.1` cannot slip through.

Hostname suffixes that are unambiguously internal — `.local`, `.localhost`, `.internal`,
`.home.arpa`, plus `localhost` and `metadata.google.internal` — are refused as well.

**Only `http` and `https` schemes.** `file://`, `ftp://`, `gopher://` and `javascript:` are
rejected at validation, not at fetch time.

**Credentials in a URL are rejected.** `https://user:pass@example.com/` is refused outright,
because those credentials would be transmitted to the target on every single check.

**Intelligence monitor targets are stricter still.** Certificate, domain, DNS and email-auth
monitors take a bare domain name — no scheme, no port, no path, no IP literals — because those
targets are passed to a third-party API rather than fetched directly.

---

## Secrets

**Alert destinations are treated as credentials**, because they are. A Slack webhook URL grants
posting rights to your channel. An ntfy topic URL grants publishing rights to your topic. A
Telegram bot token grants control of the bot.

They are stored whole and **returned to the interface redacted, always**:

| Channel | What you see |
|---|---|
| Webhook | `https://hooks.slack.com/…` — scheme and host only |
| ntfy | `https://ntfy.sh/…` — the topic name is the secret, so it is dropped entirely |
| Telegram | Chat ID visible; the bot token never partially shown |
| Email | First two characters and the domain |

Telegram is worth calling out: the token is never partially exposed. A prefix is enough to
correlate a token across a leak, so there is no "last four characters" convenience here.

**Error messages are sanitised before storage.** Failure text is scanned for
credential-shaped fragments — `authorization:`, `Bearer …`, `api_key=` — which are replaced
before the error is written anywhere. Failure text is also length-bounded, so a target cannot
use an error message as a storage channel.

**Telegram failures report the status code only**, never the response body, because the
Telegram API echoes the request URL — which contains the bot token — back in its errors.

**API keys are stored hashed**, the same way heartbeat tokens are. The plaintext `sk_…` is
shown once at creation and cannot be recovered afterwards, only rotated — a leaked key is
revoked, never "looked up".

Four different rejections — unknown key, revoked key, expired key, key whose workspace is gone
— return **one identical `401`**. Distinguishing them would turn the endpoint into an oracle
for probing which keys once existed.

**The API sends no CORS headers at all.** A key grants full access to its workspace, so a key
in browser JavaScript is a leaked key. Refusing browser requests outright is a stronger
position than documenting that you shouldn't. It also means channels cannot be created through
the API — only listed and attached — because creating one means handing over a credential, and
that belongs in one place with one audit trail.

Every API response goes through the same redaction as the interface. A destination cannot be
read back out through it.

---

## Alerting cannot corrupt monitoring

Notifications are dispatched only after monitor state is committed, and every delivery failure
is recorded rather than raised. A webhook returning 500 forever, an SMTP server refusing
connections, or a revoked Telegram token cannot change what a monitor believes about its
target.

---

## Data

**What is stored:** your account email, workspace and membership records, monitor
configuration, check results, incidents, alert channel configuration, and a delivery ledger.

**Check results are deleted after 7 days.** There is no long-term archive.

**Heartbeat tokens are stored hashed**, in the same way as an API key. The plaintext is shown
once at creation and cannot be recovered — only rotated.

**Passwords** must be at least 8 characters with upper case, lower case and a digit, and
repeated failed sign-ins are locked out. Email verification is mandatory.

---

## Infrastructure

Ingress runs through a Cloudflare named tunnel, so there are no inbound ports open on the host.
The probe worker authenticates to the backend with a shared token and holds no persistent
state.

---

## What this page does not claim

No SOC 2, no ISO 27001, no penetration test report, no compliance certification. WhatPing is a
beta product built by one developer. The defences above are real and you can read the code that
implements them; an audit is not the same thing and is not being implied.

## Reporting something

If you find a vulnerability, email it — see [contact](/contact) — rather than opening a public
issue. You will get a reply.

## Related

- [Security model in the docs](/docs/security)
- [Alert channels](/docs/alerting/channels)
