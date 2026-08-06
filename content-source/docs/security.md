---
route: "/docs/security"
title: "Security model — WhatPing docs"
description: "What WhatPing validates on every target, what it redacts, what it stores, and why each defence exists."
h1: "Security model"
---

## Why this is specific

A monitoring service fetches URLs you supply, from inside its own network, and stores
credentials you give it. That is a server-side request forgery engine and a secret store with a
friendly interface on top. The defences are worth describing precisely.

## Target validation

Every target is validated when you save it, not when it is fetched.

**Scheme allowlist.** `http` and `https` only. `file://`, `ftp://`, `gopher://` and
`javascript:` are rejected.

**No credentials in URLs.** `https://user:pass@example.com/` is refused — those credentials
would be transmitted to the target on every check, and stored in your monitor configuration.

**Private-network targets refused by default**, covering:

| Category | Range |
|---|---|
| Loopback | `127.0.0.0/8`, `::1` |
| "This network" | `0.0.0.0/8` |
| RFC1918 | `10/8`, `172.16/12`, `192.168/16` |
| Link-local, incl. cloud metadata | `169.254.0.0/16`, `fe80::/10` |
| CGNAT | `100.64.0.0/10` |
| IETF protocol assignments | `192.0.0.0/24` |
| Benchmarking | `198.18.0.0/15` |
| Multicast and reserved | `224.0.0.0/4` and above |
| IPv6 unique-local | `fc00::/7` |

IPv4-mapped IPv6 addresses are unwrapped and re-checked, so `::ffff:10.0.0.1` cannot bypass the
IPv4 rules. Hostnames ending `.local`, `.localhost`, `.internal` or `.home.arpa`, plus
`localhost` and `metadata.google.internal`, are refused by name.

A deployment can opt in to private targets deliberately — a self-hosted instance monitoring its
own LAN — but it is off unless explicitly enabled.

**Stricter rules for intelligence monitors.** Certificate, domain, DNS and email-auth targets
must be bare domain names: no scheme, no port, no path, no IP literals. Those targets are passed
to a third-party API rather than fetched directly, so the surface is narrowed further.

## Secrets

**Alert destinations are credentials.** A Slack webhook URL grants posting rights. An ntfy topic
URL grants publishing rights. A Telegram bot token grants control of the bot.

They are stored whole — delivery needs them — and **always displayed redacted**:

| Channel | Displayed as | Why |
|---|---|---|
| Webhook | `https://hooks.slack.com/…` | Path contains the secret |
| ntfy | `https://ntfy.sh/…` | The topic name *is* the secret |
| Telegram | Chat ID only | Token never shown, not even a prefix |
| Email | First two characters + domain | Enough to identify, not to harvest |

Telegram is the strictest deliberately: a token prefix is enough to correlate a leaked token
across sources, so there is no "last four characters" convenience.

**Error text is sanitised before storage.** Failure messages are scanned for credential-shaped
fragments — `authorization:`, `Bearer …`, `api_key=` — and those are replaced before anything is
written. Messages are also length-bounded, so a hostile target cannot use an error string as a
storage channel.

**Telegram failures report the status code only.** Never the response body, because the Telegram
API echoes the request URL — which contains the bot token — back in its errors.

## Heartbeat tokens

Stored hashed, like an API key. The plaintext is shown once at creation and cannot be recovered,
only rotated.

The ping endpoint returns a uniform, detail-free response: `200 {"ok":true}` or `404
{"ok":false}`. A 404 does not distinguish malformed from unknown, so the endpoint cannot be used
to enumerate monitors.

## Isolation

Monitors, channels and members belong to a workspace. A monitor in one workspace cannot be
attached to a channel in another, and this is enforced at the API layer — not hidden in the
interface.

## Alerting cannot corrupt monitoring

Notifications are dispatched after monitor state is committed, and delivery failures are
recorded rather than raised. A webhook returning 500 forever, an SMTP server refusing
connections, or a revoked Telegram token cannot change what a monitor believes.

## Authentication

Email and password, or a one-time code by email. Passwords require at least 8 characters with
upper case, lower case and a digit. Email verification is mandatory. Repeated failed sign-ins
are locked out.

There is no SSO, no SAML, and Google sign-in is not enabled.

## Data retention

| Data | Kept |
|---|---|
| Check results | 7 days, then deleted |
| Incidents | Until the monitor is deleted |
| Delivery ledger | Until the incident is deleted |
| Monitor configuration | Until you delete it |

Response bodies are never stored. Keyword matching happens in memory; only the pass/fail result
is kept.

## What is not claimed

No SOC 2, no ISO 27001, no penetration test, no compliance certification. The defences above are
real and implemented; an audit is a different thing and is not being implied.

## Reporting

Email rather than a public issue — see [contact](/contact).

## Related

- [Security overview](/security)
- [Limits](/docs/limits)
- [Alert channels](/docs/alerting/channels)
