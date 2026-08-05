# Brand, positioning and the do-not-claim list

## What WhatPing is

Uptime monitoring that also watches the things that take you down **without ever failing a
health check**: your TLS certificate, your domain registration, your DNS records, and your
email authentication.

## The wedge

Uptime Kuma pings your site. Better Stack pings it from more places and charges you for it.
Neither one tells you that your domain registration lapses in nine days. Neither notices when
your SPF record breaks and your own alert emails stop being delivered.

Every one of those failures returns HTTP 200 right up until the moment it doesn't.

WhatPing treats "is the site reachable" as the *starting* question, not the whole product.

## Positioning statement

> For developers and small teams who run their own infrastructure, WhatPing is uptime
> monitoring that watches the certificate, the domain, the DNS and the SPF record alongside
> the health check — because those are the outages a health check cannot predict.

## The second differentiator, framed honestly

When a check fails, WhatPing asks a network that isn't ours whether it agrees, and labels the
incident accordingly:

- `confirmed unreachable from a second network`
- `reachable externally — may be local to our probe`

**Call this a second network. Never call it multi-region, global, or a probe fleet.** It is
one independent network path, and it is genuinely useful, and it is not what Better Stack
sells. Overstating it invites precisely the comparison we lose. The honest version is also
the more interesting one: most tools tell you something is down without ever asking whether
the problem is their own vantage point.

---

## Visual system

Implemented in `apps/marketing/src/styles/tokens.css`. Three tiers — brand, surfaces, semantic
— and nothing outside that file states a colour. The one exception is the `theme-color` meta
tag and the favicon data-URI in `Base.astro`, which cannot read CSS variables.

**The design language is capacity.so's**, extracted from their compiled CSS rather than
eyeballed. A cream page with full-bleed black bands, orange brand, soft shadows, 10px radii.

```
--brand-orange        #ff8205     --brand-beige-light   #fffaeb
--brand-orange-light  #ffaf00     --brand-beige-medium  #fff0c3
--brand-orange-dark   #fa500f     --brand-beige-dark    #e9e2cb
--brand-yellow        #ffd800     --brand-red           #e10500

light   canvas #fffaeb · card #fcfbf8 · text #252525 · hairline #ebebeb
dark    canvas #0a0a0a · card #1c1c1c · text #fafafa · hairline #27272a
radius  0.625rem base, ±2/4px derived, pill for buttons
shadow  0 1px 3px #0000001a, 0 2px 4px -1px #0000001a  (md)
```

**Dark is a section treatment, not a colour scheme.** `.band--dark` remaps the same semantic
names, so the hero and the closing CTA are black bands inside a cream page and every component
inside them works unchanged. `.surface--terminal` does the same for the alert-stream block.

**Type: Instrument Serif for h1/h2, Geist for body, Geist Mono for data.** Display tracking is
flat at −0.05em with 1.08 leading, matching the reference rather than the size-scaled ramp the
previous system used.

**Accent has two forms, and this is load-bearing.** `#ff8205` on cream is 2.2:1 — it fails AA
as text, and even `#fa500f` only reaches 3.2:1. So `--accent` fills buttons (with a near-black
label at 7.7:1) and `--accent-text` `#cd3c04` is the only orange that words are ever set in.
Same reasoning for the status colours: brand hue kept, lightness solved to 4.75:1.

**Status is always a labelled pill, never bare coloured text.** With orange as the brand, a red
word on an orange-accented page stops carrying information. `DOWN` does the work; the colour
reinforces it. This is the mitigation for a collision that was accepted deliberately — on a
monitoring product, orange chrome and amber warnings occupy the same visual register.

*Exception, deliberate:* a **value or an error string that sits beside its own pill** may take
the status colour — `21 days` next to `WARN`, `connection refused` next to `DOWN`. The pill has
already named the state, so the colour is reinforcing a label the reader has, not standing in
for one they do not. The rule is about colour carrying meaning *alone*; it never does here.
Bare status-coloured text with no pill in the same row is still out.

**Accessibility is asserted, not eyeballed.** `apps/marketing/scripts/verify-contrast.py`
resolves every pair in **both** surface sets and fails below WCAG AA. It caught eight failures
in the first pass of this palette, including every status pill.

---

## Voice

Plain, specific, technical. Assume the reader has run a server, read a stack trace, and been
paged at 3am.

**Do:**
- Use real numbers: "20 seconds to 24 hours", not "flexible intervals".
- Show the literal output: the actual alert string, the actual error text, the actual JSON.
- Name the failure mode before the feature. The reader recognises the problem first.
- State limitations in the same breath as the feature. It is what makes the rest believable.

**Don't:**
- "Seamless", "effortless", "peace of mind", "worry-free", "blazing fast", "enterprise-grade",
  "powerful", "robust", "simply", "just".
- Exclamation marks.
- Fake urgency, fake scarcity, fake social proof.
- Rhetorical questions as headings ("Tired of downtime?").

**Tone test:** would someone who reads the source code find any sentence embarrassing? If yes,
cut it.

---

## Terminology — use these exact words

| Use | Not |
|---|---|
| monitor | check (as a noun for the thing you configure) |
| check / check result | ping (except for heartbeat monitors, where "ping" is correct) |
| incident | outage event, alert (an alert is the message; the incident is the state) |
| heartbeat monitor | push monitor (internal name), dead man's switch (use once, as a gloss) |
| second opinion | multi-location, multi-region, global check |
| workspace | team, org, account |
| down / up / pending | offline, online, unknown |
| reminder | re-notification, escalation (escalation implies on-call routing, which does not exist) |

Product name is **WhatPing**, one word, capital W and P. The app lives at
`monitor.whatping.com`. The marketing site is `whatping.com`.

---

## Do-not-claim list

Every item below is **false today**. It must not appear as a feature, a heading, a table tick,
or an implication — anywhere except a deliberate negative statement on `/roadmap` or a `/vs/`
page.

- Multi-region, multi-location, or global probe locations. **There is one probe location.**
- Unlimited monitors. The cap is **20 per workspace**.
- Status pages, public or private.
- Maintenance windows.
- Incident acknowledgement, on-call scheduling, escalation policies, rotations.
- Tags, grouping, or folders.
- SMS, phone calls, PagerDuty, Opsgenie, Slack app (the webhook works with Slack; there is no
  Slack app), Discord app (same), Microsoft Teams.
- A mobile app.
- A public REST API for creating or managing monitors. The only public HTTP surface is the
  heartbeat ping endpoint; webhooks are outbound.
- SSO, SAML, or Google sign-in. **`AUTH_GOOGLE_ID` is not configured on the deployment** —
  sign-in is email + password, or a magic email code.
- Any uptime SLA, guarantee, or "99.9%" figure about WhatPing itself.
- Uptime history beyond **7 days** — raw results are purged at 7 days and there is no
  long-term rollup.
- Log collection, metrics, APM, tracing, synthetic browser tests, screenshots on error.
- Any customer count, company logo, testimonial, star rating, or "trusted by".
- Compliance claims: SOC 2, ISO 27001, GDPR-compliant, HIPAA.

### Grep before shipping

```bash
grep -rniE 'unlimited|multi-?region|global (probe|network|location)|status page|SLA|SSO|SAML|\
sign in with google|pagerduty|opsgenie|\bSMS\b|99\.9|trusted by|soc ?2|iso ?27001' \
  apps/marketing/src/content/
```

Every hit must be a deliberate negative statement. If you cannot point at the sentence that
makes it negative, delete it.

---

## Honest substitutes for social proof

The product has no users to quote yet. Do not invent any. These are true and stronger:

- **It monitors its own prober.** A heartbeat monitor watches the probe worker, so if the
  worker dies the system reports it rather than going quiet. This caught a real regression
  where a config-parsing bug froze the worker on a stale snapshot.
- **Alert failures never alter monitor state.** A broken webhook is recorded in a delivery
  ledger and cannot corrupt what the monitor believes.
- **Every check result is idempotent.** Results carry a producer-generated ID, so a retry
  after a network blip cannot open a second incident or double-page you.
- **Nothing is claimed that isn't tested.** 187 backend tests and 22 worker tests, and every
  monitor type was verified against a live target with a known-true answer before shipping.

Each of those links to the docs page that explains it. That is the proof: the reader can check.
