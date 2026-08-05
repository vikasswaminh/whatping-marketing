---
route: "/docs/webhook-payload"
title: "Webhook payload — WhatPing docs"
description: "The full JSON schema WhatPing posts to a webhook channel, with real examples for opened, reminder and resolved events."
h1: "Webhook payload"
---

## Request

`POST` to your URL, `content-type: application/json`, 10-second timeout. Any non-2xx response is
recorded as a failed delivery; the incident and the monitor are unaffected.

## Schema

```jsonc
{
  "event": "opened" | "resolved",
  "status": "down" | "up",
  "attempt": 0,                    // 0 = transition alert, 1..n = reminder
  "monitor": {
    "id": "string",
    "name": "string",
    "type": "http" | "tcp" | "push" | "ssl" | "domain" | "dns" | "email-auth",
    "target": "string"             // URL, host:port, ping cadence, or domain
  },
  "incident": {
    "id": "string",
    "openedAt": 1754212345678,     // epoch milliseconds
    "resolvedAt": null,            // epoch milliseconds, or null while open
    "reason": "string",
    "durationMs": null,            // set on resolved, null while open
    "externalCheck": null          // "pending" | "agreed" | "disagreed"
                                   // | "unavailable" | "skipped" | null
  },
  "text": "string",
  "content": "string"              // identical to text — Discord compatibility
}
```

`text` and `content` are the same string. Slack renders `text`, Discord renders `content`, and
having both is what makes one endpoint work for either without configuration.

## Example — incident opened

```json
{
  "event": "opened",
  "status": "down",
  "attempt": 0,
  "monitor": {
    "id": "m97aqc31pvs1hhfvj5x9j4p5018bsct1",
    "name": "api",
    "type": "http",
    "target": "https://api.example.com/health"
  },
  "incident": {
    "id": "i97bm5dm7mzyvt92npa0n724918brspd",
    "openedAt": 1754212345678,
    "resolvedAt": null,
    "reason": "connect failed: Connection refused (os error 111)",
    "durationMs": null,
    "externalCheck": "pending"
  },
  "text": "🔴 DOWN — api (https://api.example.com/health): connect failed: Connection refused (os error 111)",
  "content": "🔴 DOWN — api (https://api.example.com/health): connect failed: Connection refused (os error 111)"
}
```

`externalCheck` is `"pending"` here because the [second
opinion](/docs/alerting/second-opinion) has not finished when the first alert is sent. That is
expected.

## Example — reminder

```json
{
  "event": "opened",
  "status": "down",
  "attempt": 2,
  "monitor": {
    "id": "m97aqc31pvs1hhfvj5x9j4p5018bsct1",
    "name": "api",
    "type": "http",
    "target": "https://api.example.com/health"
  },
  "incident": {
    "id": "i97bm5dm7mzyvt92npa0n724918brspd",
    "openedAt": 1754212345678,
    "resolvedAt": null,
    "reason": "connect failed: Connection refused (os error 111)",
    "durationMs": null,
    "externalCheck": "agreed"
  },
  "text": "🔴 STILL DOWN (1h 5m) — api (https://api.example.com/health): connect failed: Connection refused (os error 111) · confirmed unreachable from a second network",
  "content": "🔴 STILL DOWN (1h 5m) — api (https://api.example.com/health): connect failed: Connection refused (os error 111) · confirmed unreachable from a second network"
}
```

Note `event` is still `"opened"` — the incident has not changed state. **`attempt` is what
distinguishes a reminder**, and it is the field to branch on.

## Example — resolved

```json
{
  "event": "resolved",
  "status": "up",
  "attempt": 0,
  "monitor": {
    "id": "m97aqc31pvs1hhfvj5x9j4p5018bsct1",
    "name": "api",
    "type": "http",
    "target": "https://api.example.com/health"
  },
  "incident": {
    "id": "i97bm5dm7mzyvt92npa0n724918brspd",
    "openedAt": 1754212345678,
    "resolvedAt": 1754216012345,
    "reason": "connect failed: Connection refused (os error 111)",
    "durationMs": 3666667,
    "externalCheck": "agreed"
  },
  "text": "🟢 RECOVERED — api (https://api.example.com/health) after 3667s",
  "content": "🟢 RECOVERED — api (https://api.example.com/health) after 3667s"
}
```

`reason` on a resolved incident is the reason it *opened*, retained for context.

## The `target` field by monitor type

| Type | Format | Example |
|---|---|---|
| `http` | full URL | `https://api.example.com/health` |
| `tcp` | `host:port` | `db.example.com:5432` |
| `push` | ping cadence | `push every 86400s` |
| `ssl`, `domain`, `dns`, `email-auth` | domain | `example.com` |

## Building a receiver

**Deduplicate on `incident.id` + `attempt`.** Together they are unique for a given
notification. WhatPing does not retry a delivery within the same attempt, but building on this
pair makes your receiver safe regardless.

**Branch on `attempt`, not `event`**, to distinguish a reminder from a first alert.

**Do not treat `externalCheck: "pending"` as a verdict.** It means the check has not finished.
Re-read the field on the next reminder if you need it.

**Timestamps are epoch milliseconds**, UTC.

Minimal receiver:

```python
from flask import Flask, request

app = Flask(__name__)

@app.post("/whatping")
def hook():
    p = request.get_json()
    key = (p["incident"]["id"], p["attempt"])
    if seen(key):
        return "", 200
    if p["status"] == "down":
        page_someone(p["text"], first=p["attempt"] == 0)
    else:
        resolve(p["incident"]["id"])
    return "", 200
```

## Related

- [Alert channels](/docs/alerting/channels)
- [Reminders](/docs/alerting/re-alert)
- [Second opinion](/docs/alerting/second-opinion)
