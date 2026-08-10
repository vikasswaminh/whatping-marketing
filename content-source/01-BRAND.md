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

Implemented in `src/styles/tokens.css`. Three tiers — signal, surfaces, semantic — and nothing
outside that file states a colour. The one exception is the `theme-color` meta tag and the
favicon data-URI in `Base.astro`, which cannot read CSS variables.

**The design language is an operator console.** Dark-first: the product is an instrument that
watches things, so the site is typeset as the readout it sells rather than as a brochure about
one. Near-black with a faint cyan cast, amber phosphor, hairlines instead of shadows, milled
2px corners instead of 10px software radii.

*This replaced a cream-and-orange palette extracted from capacity.so. That system was competent
and contrast-verified, and it was someone else's.*

```
--signal-amber        #ffb000     --console-void   #08090a
--signal-amber-bright #ffc94d     --console-bay    #0e1113
--signal-amber-deep   #9a4a00     --paper-stock    #e9e7e1
--signal-green        #35d67f     --signal-red     #ff5c4d

console  canvas #08090a · bay #0e1113 · text #f4f6f6 · hairline #1b2124
paper    canvas #e9e7e1 · card #f3f1ec · ink  #16181a · hairline #cfcabe
radius   2px, collapsing to 0 for panels; pill retained for status chips only
shadow   none on the console — the hairline carries elevation on near-black
texture  SVG grain at 3.8% over a 3px scan line, fixed to the viewport
```

**Docs are paper, and that is a material, not a second theme.** `.band--paper` remaps the same
semantic names, so the sidebar, prose, callouts and pills all work inside it unchanged. The
manual is a light surface inset into the machine, with console chrome above and below it — long
-form reference reading is a different job from being sold to.

**Type: Martian Mono for display and UI, IBM Plex Sans for body, Geist Mono for data.** Headings,
nav, buttons and section labels are instrument labelling, so they are set in the face that
labels instruments — Martian Mono at the top of its width axis (112.5%). Prose is not, because
mono at length is tiring, so body copy drops to Plex Sans. Display tracking is only −0.03em: a
mono's sidebearings are already even, and the aggressive tracking a serif needs would crowd it.
The eyebrow tier goes strongly *positive* (+0.18em), which is what makes a label read as
stencilled onto a panel rather than as small caps.

**Amber is the accent and WARN both, deliberately.** On a monitoring product the brand colour
being the attention colour is correct rather than confused. The mitigation is the pill rule
below, unchanged from the previous palette and still load-bearing.

**The two-form accent split collapses on the console and returns on paper.** Orange on cream was
2.2:1, which forced `--accent` (fill) and `--accent-text` (words) apart. Amber on `#08090a` is
10.88:1, so on the console they are one value. On paper amber measures **1.48:1** — verified by
deliberately reverting it — so `--accent-text` there is `--signal-amber-deep` `#9a4a00` at
5.06:1, and it is the only form words are ever set in on that surface.

**Status is always a labelled pill, never bare coloured text.** With amber as both the brand and
the warning, a bare coloured word stops carrying information. `DOWN` does the work; the colour
reinforces it.

*Exception, deliberate:* a **value or an error string that sits beside its own pill** may take
the status colour — `21 days` next to `WARN`, `connection refused` next to `DOWN`. The pill has
already named the state, so the colour is reinforcing a label the reader has, not standing in
for one they do not. The rule is about colour carrying meaning *alone*; it never does here.
Bare status-coloured text with no pill in the same row is still out.

**Accessibility is asserted, not eyeballed.** `scripts/verify-contrast.py` resolves every pair in
**both** surface sets — console and paper — and fails below WCAG AA. All 30 pairs passed on the
first run of this palette; the values were solved before they were written, not adjusted after.
Two of them have been deliberately broken and restored since, because a guard that has never
gone red is not yet a guard.

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
- SSO, SAML, or Google sign-in. **`AUTH_GOOGLE_ID` is not configured on the deployment** —
  sign-in is email + password, or a magic email code.
- Any uptime SLA, guarantee, or "99.9%" figure about WhatPing itself.
- Uptime history beyond **7 days** — raw results are purged at 7 days and there is no
  long-term rollup.
- Log collection, metrics, APM, tracing, synthetic browser tests, screenshots on error.
- Generic "is this UDP port open" checking. UDP monitors send a real request and require a
  real reply; silence is not evidence and must never be presented as if it were.
- Any customer count, company logo, testimonial, star rating, or "trusted by".
- Compliance claims: SOC 2, ISO 27001, GDPR-compliant, HIPAA.

### Grep before shipping

Word-boundary `\bSLAs?\b` and `\bSSO\b`, not the bare forms: unanchored `SLA` matches
**Slack**, which appears legitimately all over the webhook documentation, and that noise buries
the hits that matter. Tightening the pattern took the count from 71 to 50 without losing a
single real one.

```bash
grep -rniE -e 'unlimited|multi-?region|global (probe|network|location)' \
           -e 'status page|\bSLAs?\b|\bSSO\b|SAML|sign in with google' \
           -e 'pagerduty|opsgenie|\bSMS\b|99\.9|trusted by|soc ?2|iso ?27001' \
           src/content/ src/pages/ src/components/
```

**Separate `-e` patterns, with the continuations outside the quotes.** The previous form in
this file wrapped one long pattern with a backslash *inside* the single quotes, where a
backslash-newline is a literal backslash rather than a line continuation. grep exited with
`Trailing backslash` and matched nothing, so the check reported clean while testing zero
files. The corrected form returns 51 hits; the broken one returned 0.
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
- **Nothing is claimed that isn't tested.** Every monitor type was verified against a live
  target with a known-true answer before it shipped — a reachable host and a black-holed one
  for ICMP, a real resolver for UDP, a real MX for SMTP. The backend and prober suites run on
  every change. *Do not put a test count in copy:* it was wrong for two releases, and the
  sentence is stronger without it.

Each of those links to the docs page that explains it. That is the proof: the reader can check.
