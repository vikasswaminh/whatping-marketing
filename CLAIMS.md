# Claims audit

Every factual claim made anywhere in this content package, with the file that proves it. Paths
are relative to the repository root.

**If you change the product, change this table, then change the content.** A claim that has
drifted from the code is worse than no claim, because it will be believed.

## Monitor types

| Claim | Source |
|---|---|
| Seven types: http, tcp, push, ssl, domain, dns, email-auth | `packages/backend/convex/schema.ts` — `monitorType` |
| Certificate, domain, DNS and email-auth are evaluated on a schedule, not by the prober | `packages/backend/convex/crons.ts`, `monitorIntel.ts` |
| Probed types default to 60 s; intelligence types default to 24 h | `utils/monitorTarget.ts` — `defaultIntervalSec`, `defaultIntelIntervalSec` |

## Bounds and defaults

| Claim | Source |
|---|---|
| 20 monitors per workspace | `utils/monitorTarget.ts` — `maxPerWorkspace: 20` |
| Interval 20 s – 24 h, default 60 s | `minIntervalSec`, `maxIntervalSec`, `defaultIntervalSec` |
| Timeout 1 – 60 s, default 10 s | `minTimeoutMs`, `maxTimeoutMs`, `defaultTimeoutMs` |
| Failures before down 1 – 10, default 2 | `minDownThreshold`, `maxDownThreshold`, `defaultDownThreshold` |
| Re-alert 5 – 1440 minutes, 0 = off, off by default | `minRepeatEveryMin`, `maxRepeatEveryMin`, `validateRepeatEvery` |
| Keyword up to 200 characters | `maxKeywordLength` |
| Body read capped at 256 KB | `maxBodyBytes: 262_144` |
| Max redirects 0 – 10, default 0 | `validateMaxRedirects`, `normalizeConfig` |
| URL up to 2048 characters | `validateHttpUrl` |
| Port 1 – 65535 | `validateTcpTarget` |
| Heartbeat interval 1 minute – 7 days, default 1 hour | `minPushIntervalSec`, `maxPushIntervalSec`, `normalizeConfig` |
| Heartbeat grace default 5 minutes | `normalizeConfig` — `validateGrace(a.pushGraceSec ?? 300)` |
| Warning threshold 1 – 365 days, default 30 | `validateWarnDays`, `normalizeConfig` |
| DNS record types A, AAAA, MX, TXT, CNAME, NS; default A | `DNS_RECORD_TYPES`, `validateDnsRecordType` |
| Monitor name up to 80 characters | `maxNameLength` |
| Stored error text up to 200 characters | `maxErrorLength`, `sanitizeError` |
| Ping token up to 128 characters | `packages/backend/convex/http.ts` |

## Behaviour

| Claim | Source |
|---|---|
| Accepted status supports codes and inclusive ranges, e.g. `200-299,301` | `validateAcceptedStatus`, `statusAccepted`; `services/monitor-worker/src/models.rs` |
| Exactly one incident per outage | `monitorEngine.ts` — `applyFailure` checks for an existing open incident |
| Recovery is a single success | `monitorEngine.ts` — `applySuccess` |
| Failure counter resets on success | `monitorEngine.ts` — `consecutiveFailures: 0` |
| Results are idempotent by producer-generated ID | `monitorEngine.ts` — `applyCheckResult` duplicate check on `resultId` |
| Alerts dispatched after state is committed; failures recorded not thrown | `monitorNotify.ts` — `dispatch`, `recordDelivery` |
| Reminder clock advances before the send | `monitorNotify.ts` — `repeatDue` patches before scheduling |
| Reminders carry elapsed time and the external verdict | `monitorNotify.ts` — `buildPayload`, `secondOpinion` |
| Heartbeat deadlines evaluated in the backend, not the prober | `packages/backend/convex/monitorPush.ts`, `crons.ts` |
| A never-pinged heartbeat is measured from creation | `monitorPush.ts` |
| Unknown monitor types degrade rather than failing the prober's config parse | `services/monitor-worker/src/models.rs` — hand-written `Deserialize` |
| Prober concurrency is bounded by a semaphore | `services/monitor-worker/src/main.rs` — `Semaphore` |
| Check results retained 7 days | `packages/backend/convex/monitorRetention.ts` — `RETENTION_DAYS = 7` |
| Uptime windows are 24 hours and 7 days | `packages/backend/convex/monitors.ts` — `uptime` |
| No uptime figure is shown when there is no data | `monitors.ts` — `pct: null` when `rows.length === 0` |

## Second opinion

| Claim | Source |
|---|---|
| Verdicts: pending, agreed, disagreed, unavailable, skipped | `schema.ts` — `externalVerdict` |
| Runs on HTTP monitors with a URL; on by default | `monitorConfirm.ts` — `confirmableUrl`; `monitors.ts` — `confirmExternally ?? true` |
| Scheduled alongside the alert, never in front of it | `monitorEngine.ts` — both `runAfter(0)` calls |
| Success, including an empty body, maps to `disagreed` | `monitorConfirm.ts` — `classify(null)` |
| 5xx / navigation timeout maps to `agreed` | `monitorConfirm.ts` — `classify` |
| A private target maps to `unavailable` | `monitorConfirm.ts` — 400 + "not allowed" |
| Auth failure, rate limit and our own timeout fail open to `unavailable` | `monitorConfirm.ts` — fallthrough |
| A missing API key records `skipped`, not agreement | `monitorConfirm.ts` — `verify` |
| An unreachable public target takes the external fetch up to 30 s | Observed live: `Timed out navigating to … after 30s` |

## Alerting

| Claim | Source |
|---|---|
| Four channels: webhook, email, ntfy, Telegram | `schema.ts` — `channelConfig` |
| Webhook body carries `text` and `content` aliases | `monitorNotify.ts` — `sendWebhook` |
| Webhook timeout 10 seconds | `monitorNotify.ts` — `WEBHOOK_TIMEOUT_MS` |
| ntfy sets Title, Priority and Tags from the incident | `monitorNotify.ts` — `sendNtfy` |
| Telegram failures report status only, never the body | `monitorNotify.ts` — `sendTelegram` |
| Every delivery attempt is recorded | `monitorNotify.ts` — `recordDelivery` |
| `attempt` is 0 for the transition alert, 1..n for reminders | `monitorNotify.ts` — `buildPayload`, `repeatDue` |
| Payload field list and types | `monitorNotify.ts` — `IncidentPayload` |

## Heartbeat endpoint

| Claim | Source |
|---|---|
| `/monitor/ping/<token>`, GET and POST | `packages/backend/convex/http.ts` |
| Responses are `200 {"ok":true}` / `404 {"ok":false}` | `http.ts` — `pingHandler` |
| Response is uniform so monitors cannot be enumerated | `http.ts` — comment and implementation |
| Token stored hashed, shown once | `monitors.ts` — `create`, `sha256Hex`, `pushTokenHash` |

## Security

| Claim | Source |
|---|---|
| Private ranges refused: loopback, 0/8, RFC1918, link-local, CGNAT, 192.0.0.0/24, 198.18/15, multicast | `utils/monitorTarget.ts` — `isPrivateIpv4` |
| IPv6: `::1`, `fc00::/7`, `fe80::/10`, IPv4-mapped unwrapped | `isPrivateIpv6` |
| Internal suffixes refused: `.local`, `.localhost`, `.internal`, `.home.arpa` | `PRIVATE_HOST_SUFFIXES`, `isPrivateHost` |
| `http`/`https` schemes only | `validateHttpUrl` |
| URLs with embedded credentials rejected | `validateHttpUrl` |
| Intelligence targets must be bare domains, no IP literals | `validateIntelDomain` |
| Channel configs displayed redacted; Telegram token never partially shown | `redactChannelConfig` and its tests |
| Error text sanitised for credential fragments and length-bounded | `sanitizeError` |
| Password: 8+ chars, upper, lower, digit; email verification required | `packages/backend/convex/auth.ts` |
| Google sign-in is **not** enabled | `convex env list` on the deployment — no `AUTH_GOOGLE_ID` |

## Proof claims used in marketing copy

| Claim | Source |
|---|---|
| 187 backend tests | `bun x vitest run` in `packages/backend` |
| 22 prober tests | `cargo test` in `services/monitor-worker` |
| The heartbeat caught a prober regression within ~10 minutes | Commit `9d58d51` and the session that produced it |
| A DNS error envelope once made a dead domain read as up | Commit `ca8dad4` |
| DNS monitors ignored the configured record type | Commit `5cd993b` |
| The uptime query would have failed at ~3.8 days of 20 s history | Commit `805d9f3`; Convex 16,384-document read ceiling |

<Callout>
Test counts change. Either re-run the suites before publishing and update them here, or replace
the sentence with one that does not carry a number.
</Callout>

## Deliberate negative statements

These sentences contain do-not-claim keywords **on purpose**. They are the only permitted hits
in the sweep below.

| Page | Statement |
|---|---|
| `/`, `/features`, `/pricing`, `/how-it-works`, `/docs/faq` | one probe location; not multi-region |
| `/features`, `/pricing`, `/roadmap`, `/vs/*`, `/docs/limits`, `/docs/faq` | no status pages |
| `/features`, `/roadmap`, `/vs/*`, `/docs/limits` | no maintenance windows, acknowledgement, tags, on-call |
| `/features/alerting`, `/vs/better-stack`, `/docs/faq`, `/docs/limits` | no SMS, phone, PagerDuty, Opsgenie |
| `/pricing`, `/legal/terms`, `/vs/better-stack`, `/docs/faq` | no SLA |
| `/security`, `/docs/security` | no SOC 2, ISO 27001, penetration test |
| `/docs/security` | no SSO, no SAML, Google sign-in not enabled |
| `/vs/uptime-kuma` | "unlimited monitors" — describing Uptime Kuma, not WhatPing |
| `/docs/faq`, `/pricing`, `/docs/limits` | 7-day retention, 20-monitor cap |
| `/`, `/features/certificate-monitoring` | "mobile apps fail silently" — the reader's apps breaking, not a WhatPing app |
| `/features/domain-expiry-monitoring` | "your SSO" — the reader's SSO going down with the domain |
| `/features/domain-expiry-monitoring`, `/vs/uptime-kuma`, `/docs/faq` | "self-hosted" — describing Uptime Kuma |
| `/docs/alerting/channels` | "self-hosted ntfy" — the reader's ntfy server |

**Verified clean:** the sweep was run against this package and every hit maps to a row above.
The tone sweep returned nothing.

## The sweep

```bash
grep -rniE 'unlimited|multi-?region|global (probe|network|location)|status page|\bSLA\b|\bSSO\b|SAML|sign in with google|pagerduty|opsgenie|\bSMS\b|99\.9|trusted by|soc ?2|iso ?27001|mobile app|self-host' \
  apps/marketing/src/content/
```

Every hit must map to a row in the table above. If it does not, delete the sentence — do not
soften it.

Second sweep, for tone:

```bash
grep -rniE 'seamless|effortless|peace of mind|worry-free|blazing|enterprise-grade|game.chang|revolutionar|!' \
  apps/marketing/src/content/
```

Expected result: nothing, except exclamation marks inside quoted code or literal alert text.
