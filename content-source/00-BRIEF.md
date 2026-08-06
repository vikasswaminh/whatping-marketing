# Build brief — WhatPing marketing site + docs

> **Built and shipped.** The site is live at https://whatping.com, implemented in Astro at
> `apps/marketing/` and deployed to Cloudflare Pages by `deploy/80-cf-pages.sh`. This file is
> kept as the record of the decisions it describes; where it says "Next.js", the build used
> Astro instead, and the deployment section below is accurate.

You are building a marketing site with an embedded docs section. **All copy already exists**
in `pages/` and `docs/` in this directory. You should not need to write a sentence of prose;
if you find yourself inventing copy, something is missing — flag it rather than filling it in.

Read `01-BRAND.md` before you touch anything. It contains a do-not-claim list, and every item
on it is false today. Adding a plausible-sounding feature to a heading would make the site
lie.

---

## Where it goes

`apps/web/` — an existing Next.js 14 app-router workspace in this monorepo.

```
apps/web/
  src/app/page.tsx          current template hero — replace
  src/app/talk-to-us/       Cal.com embed — delete, replaced by /contact
  src/components/           header, footer, subscribe-form — rework
  vercel.json               template residue — see Deployment
```

Stack already present: Next 14 (app router), Tailwind, `@v1/ui` (shadcn), Geist + a local
`DepartureMono` font, `@v1/analytics` (OpenPanel). Dev server runs on port 3001
(`bun run dev` from `apps/web`).

Do not add a CMS, a component library, or a docs framework. The content is flat markdown and
the site is small.

---

## Content pipeline

Convert `pages/*.md` and `docs/*.md` into MDX under `apps/web/content/`:

```
apps/web/content/
  pages/home.mdx, features.mdx, pricing.mdx, ...
  docs/index.mdx, quickstart.mdx, monitors-http.mdx, ...
```

Every file has frontmatter:

```yaml
---
route: /features/domain-expiry-monitoring
title: Domain expiry monitoring — WhatPing      # <title> and og:title
description: ...                                 # meta description, 140–160 chars
h1: Your domain expires on a Sunday
---
```

Render with a catch-all route (`app/[[...slug]]/page.tsx`) that resolves `route` from
frontmatter, plus a dedicated `app/docs/[[...slug]]/page.tsx` if the docs layout needs its own
sidebar shell. `generateStaticParams` over the content directory.

**`generateStaticParams` must enumerate every route.** With `output: "export"` a route that is
not returned there simply does not exist in the build — there is no server to fall back on. A
missing entry is a 404 in production and nothing in development.

Keep copy out of components. A copy change must never require touching a `.tsx` file.

---

## Routes and navigation

Full route list with metadata is in `02-SITEMAP.md`. Two shells:

**Marketing shell** — header, footer, wide content.
Header: `Features` · `How it works` · `Pricing` · `Docs` · `Compare` (dropdown → the two `/vs/`
pages) · **Sign in** (button, → `https://monitor.whatping.com`).
Mobile: hamburger to a full-screen sheet.

**Docs shell** — persistent left sidebar (four groups, see `02-SITEMAP.md`), content column,
right-hand "on this page" list on ≥lg. Sidebar collapses to a `<details>` disclosure below md.

Footer, four columns:
- **Product** — Features, How it works, Pricing, Roadmap, Changelog
- **Monitor types** — the seven type pages under `/features/…` and `/docs/monitors/…`
- **Docs** — Quickstart, Concepts, Alerting, Webhook payload, Limits
- **Company** — About, Security, Contact, Privacy, Terms

Every page must be reachable from the header or footer. No orphans.

---

## Components to build

| Component | Used by | Notes |
|---|---|---|
| `Hero` | `/` | H1, sub, two CTAs, beta strip |
| `MonitorTypeGrid` | `/`, `/features` | 7 cards, icon + name + one line + link |
| `AlertSample` | `/`, `/features/alerting` | Monospace block rendering a literal alert string. Do not restyle the emoji away — it is what the alert actually contains |
| `ComparisonTable` | `/vs/*` | Three columns. Must render ✗ as ✗ |
| `LimitsTable` | feature + docs pages | Field, bounds, default |
| `CodeBlock` | docs | Copy button, no syntax-highlight dependency needed for the languages used (bash, json, yaml) |
| `Callout` | docs | `note` / `warning` / `gotcha` variants |
| `DocsSidebar`, `TableOfContents` | docs shell | |
| `RoadmapItem` | `/roadmap` | Status pill: `planned` / `designed` — never `coming soon` |

---

## SEO

- Title and description come from frontmatter. Do not template-append " | WhatPing" — the
  titles supplied already end correctly.
- `sitemap.xml` and `robots.txt` generated from the content directory.
- Canonical tag on every page.
- JSON-LD: `SoftwareApplication` on `/`, `FAQPage` on `/docs/faq`, `TechArticle` on the two
  `/vs/` pages.
- OG images: reuse `src/app/opengraph-image.png` initially. A per-page generator is a later
  pass, not this one.

---

## Deployment — Cloudflare Pages

The marketing site is a **Cloudflare Pages** site. It is not on the VM, and it is not on
Vercel. `apps/app` stays where it is — the systemd unit behind the named tunnel on
`monitor.whatping.com` — and the two are unrelated at deploy time.

### Build as a static export

Every page in this package is static markdown. There is no reason for a server, and a static
export removes the entire question of runtime compatibility on Pages.

`apps/web/next.config.mjs`:

```js
/** @type {import('next').NextConfig} */
export default {
  output: "export",
  trailingSlash: true,          // directory-per-route, avoids redirect loops on Pages
  images: { unoptimized: true } // no Next image server in an export
};
```

Output lands in `apps/web/out/`.

### Delete `apps/web/vercel.json` before anything else

```json
{ "buildCommand": "cd ../../packages/backend && npx convex deploy --cmd ..." }
```

That is template residue and it runs **`convex deploy`**. If it were ever honoured by a build
pipeline it would push the backend as a side effect of building the marketing site. Remove the
file, do not adapt it.

### Strip the Convex client from `apps/web`

The template wraps the marketing site in a `ConvexClientProvider` and ships a `subscribe-form`
that calls a Convex action. The site in this package has no dynamic data and no newsletter —
the CTA is a link to `monitor.whatping.com`.

Remove:
- `src/app/convex-client-provider.tsx` and its use in `layout.tsx`
- `src/components/subscribe-form.tsx`
- `src/components/cal-embed.tsx` and `src/app/talk-to-us/` (replaced by `/contact`)
- from `package.json`: `convex`, `@convex-dev/auth`, `@convex-dev/polar`, `@calcom/embed-react`,
  `@v1/backend`

A marketing site that opens a websocket to your production backend on every visit is a cost and
an attack surface for no benefit.

### Build and deploy

```bash
bun install --frozen-lockfile
bun run build --filter=@v1/web
bunx wrangler pages deploy apps/web/out --project-name whatping-marketing --branch main
```

**Manual `wrangler` deploy is the recommendation, not a Git-connected build.** A Git-connected
Pages project needs read access to the repository — and this repository is the whole product:
backend, probe worker, deploy scripts. Granting a third-party build service read access to all
of it so it can render a marketing site is a poor trade. Deploying a prebuilt `out/` needs no
repository access at all.

If you would rather have Git-connected builds anyway, the settings are: root directory
`apps/web`, build command `bun run build --filter=@v1/web`, output directory `out`, and an
explicit Node or Bun version pin so the build does not drift.

The API token needs **Cloudflare Pages: Edit** on this account only. Do not reuse the master
token from `cf.txt`.

### Redirects

A static export cannot use `redirects()` from `next.config`. Put them in
`apps/web/public/_redirects`, which Pages reads:

```
/talk-to-us      /contact              308
/docs/monitors   /docs                 308
/vs              /vs/uptime-kuma       308
```

The `www` → apex redirect is a **Cloudflare redirect rule** on the zone, not a `_redirects`
entry — `_redirects` only applies to requests that already reached the Pages project.

### Security headers

There is no server to set them, so use `apps/web/public/_headers`:

```
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### Custom domain

Attach `whatping.com` and `www.whatping.com` as custom domains on the Pages project. The zone
is already on Cloudflare, so Cloudflare creates the records itself, including at the apex via
CNAME flattening.

**This removes a blocker I raised earlier.** `whatping.com`'s apex currently has no A record —
it publishes MX and TXT only, so it resolves for mail and nothing else. On the VM that would
have needed a record created by hand; with Pages, attaching the custom domain handles it.

Verify afterwards that the **MX and TXT records are still intact**. Those records are what make
your alert email deliverable, and email-authentication monitoring exists in this product
precisely because they get broken during unrelated DNS work.

### Cache

Pages invalidates its cache per deployment, so there is no purge step. If you add a zone-level
cache rule in front of it, that stops being true.

---

## Analytics

`@v1/analytics` (OpenPanel) is already wired into the template. Either configure it properly
or strip it. A tracker that loads and reports nowhere is worse than no tracker: it costs the
visitor a request and tells you nothing.

Cloudflare Web Analytics is the lower-friction option on Pages — one script tag, no cookie
banner, and it is on the same account as the deployment.

---

## Definition of done

1. Every route in `02-SITEMAP.md` exists in `apps/web/out/` after the build, and is linked from
   header or footer. Check the built output, not the dev server — a route missing from
   `generateStaticParams` works in dev and 404s in production.
2. Every internal link in the content resolves — no 404s.
3. The do-not-claim grep in `CLAIMS.md` returns only the deliberate negative statements.
4. Playwright headed pass **against the deployed `*.pages.dev` URL**, not localhost: header nav,
   docs sidebar, mobile breakpoint at 375px, the `_redirects` entries, and the `Sign in` button
   reaching `monitor.whatping.com`.
5. Lighthouse ≥ 95 on performance and accessibility for `/` and one docs page. The site is
   static markdown on a CDN; there is no excuse for less.
6. `dig whatping.com MX` and `dig whatping.com TXT` still return what they did before the
   custom domain was attached.
