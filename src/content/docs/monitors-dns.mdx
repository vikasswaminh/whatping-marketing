---
route: "/docs/monitors/dns"
title: "DNS monitors — WhatPing docs"
description: "Assert that an A, AAAA, MX, TXT, CNAME or NS record still contains the value it should."
h1: "DNS monitors"
---

## What it checks

Once a day, looks up one record type for a domain and asserts on the result.

The check fails when:

- the lookup itself failed — including the domain not existing
- no records of that type were found
- an expected value was configured and no record contains it

## Fields

| Field | Range | Default |
|---|---|---|
| Domain | bare hostname | — |
| Record type | A, AAAA, MX, TXT, CNAME, NS | A |
| Expected value | any substring, optional | none |
| Interval | 20 s – 24 h | 24 h |
| Failures before down | 1 – 10 | 2 |
| Re-alert every | 5 min – 24 h, or off | off |

Subdomains and underscore labels are supported, so `_dmarc.example.com` and
`_acme-challenge.example.com` both work.

## Create it with the API

```bash
curl -X POST https://api.whatping.com/v1/monitors \
  -H "Authorization: Bearer $KEY" \
  -H "content-type: application/json" \
  -d '{
    "name": "apex A record",
    "type": "dns",
    "host": "example.com",
    "dns_record_type": "A",
    "dns_expected": "203.0.113."
  }'
```

`dns_expected` matches by substring, so a partial value is usually the right assertion — it
survives a provider adding capacity, which an exact match does not.

Field names are snake_case and an unknown one is a `422` naming the field, never a silent
drop. Full reference: [API](/docs/api).

## Matching is by substring

The expected value must appear **somewhere in** at least one record of that type. This is
deliberate, and it is what makes the assertions durable:

| Record type | Records | Expected value that works |
|---|---|---|
| NS | `pat.ns.cloudflare.com.`, `dan.ns.cloudflare.com.` | `cloudflare.com` |
| MX | `9 route2.mx.cloudflare.net.`, `73 route3...` | `mx.cloudflare.net` |
| A | `104.21.5.7` | `104.21.` |
| TXT | `"v=spf1 include:_spf.example.com ~all"` | `v=spf1` |

Pinning the exact record means being paged every time your provider adds capacity or reorders
priorities. Matching the part that must not change is the assertion you actually meant.

## With no expected value

The monitor asserts only that records of that type exist. That catches deletion, and it catches
the whole zone disappearing.

## A nonexistent domain fails the check

Worth stating explicitly, because getting it wrong is a silent disaster: DNS lookups report a
name that does not exist as a *successful* lookup with an error nested inside the record set.

WhatPing treats that as a failed check:

```
🔴 DOWN — legacy-host (legacy.example.com): A lookup failed: Domain does not exist
```

An earlier build did not, and reported a deleted zone as healthy for about a day. It is now
covered by both a unit test and a live verification fixture.

## Failure messages

```
no A record contains "203.0.113.10"
no MX records found
A lookup failed: Domain does not exist
```

## What it does not check

- **Propagation across resolvers.** One authoritative answer, not a comparison across many
  public resolvers.
- **DNSSEC validity.**
- **TTL values.**
- **Record ordering or priority.** Substring matching is order-independent by design.

## Useful assertions

| Goal | Type | Expected value |
|---|---|---|
| Apex still points at our host | A | the IP prefix, e.g. `203.0.113.` |
| Mail still routes to our provider | MX | the provider's hostname fragment |
| Nameservers have not been changed | NS | your DNS provider's domain |
| A subdomain has not been left dangling | CNAME | the service it should point at |
| A verification record still exists | TXT | the verification prefix |

The NS one is worth having on every domain you care about. A nameserver change you did not make
is either a mistake or a compromise, and both are urgent.

## Worked example

```
Domain:               example.com
Record type:          NS
Expected value:       cloudflare.com
Interval:             24 hours
Failures before down: 1
```

## Related

- [Email auth monitors](/docs/monitors/email-auth) — SPF and DMARC specifically
- [Domain expiry monitors](/docs/monitors/domain)
- [Troubleshooting](/docs/troubleshooting)
