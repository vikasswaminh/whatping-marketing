# whatping-marketing

The marketing site and documentation for [whatping.com](https://whatping.com). Astro, static
output, deployed to Cloudflare Pages.

Split out of `whatping-monitoring-core-code` so that **daily SEO and copy work cannot touch
the product**. Before the split, a content tweak and a probe-worker change landed in the same
repo, shared a history and a deploy path, and were indistinguishable in `git log`. Full
history came across with `git subtree split`, so `git log` on any page still reaches its
original commit.

```
src/                  the Astro site — pages, layouts, components, content collections
content-source/       the authored content package (see below)
scripts/              verification: routes, contrast, render, API examples, OG image
deploy/               Cloudflare Pages deploy and post-deploy render checks
public/openapi.json   vendored from the core repo — see "The one thing this repo does not own"
```

## Content lives in two places, deliberately

`content-source/` is the authored package — `00-BRIEF`, `01-BRAND`, `02-SITEMAP`, `CLAIMS`,
and a `.md` mirror of every page. `src/content/` is what Astro builds. They are kept parallel
on purpose: `02-SITEMAP.md` is authoritative for routes and meta descriptions, and `CLAIMS.md`
is the record of which marketing statements have evidence behind them.

**Edit both.** They are not generated from each other, and nothing enforces the parallel — a
change to one and not the other is how the site starts claiming something the record does not
support.

`01-BRAND.md` carries the do-not-claim list and the voice rules, including the greps to run
before shipping. Read it before writing copy.

## The one thing this repo does not own

`public/openapi.json` is **generated in the core repo** from `convex/api/routes.ts` — the API
contract belongs to the backend, so the spec is generated where the routes are defined and
vendored here as a committed artifact.

`scripts/verify-api-examples.py` validates every documented `curl` example against that
vendored spec rather than against the backend source, which is what lets this repo stand
alone. If the API changes, the core repo regenerates the spec and it is re-vendored here.

A stale copy is the **core repo's** drift check to catch: it compares its freshly generated
spec against the live `https://whatping.com/openapi.json`.

## Working on it

```bash
bun install
bun run dev          # localhost:3001
bun run build        # -> dist/, 49 routes + /og/ + 404
bun run verify       # routes, contrast and API examples
```

`bun run verify` needs no network and no credentials. The two that do:

```bash
OLLAGRAPH_API_KEY=... python3 scripts/verify-render.py   # pixel-level, against the live site
python3 scripts/build-og.py                              # regenerates public/og.png via Playwright
```

## Verification, and why each one exists

| Script | Catches |
|---|---|
| `verify-routes.py` | A route that 404s in production but works in dev; a broken internal link; **a docs page missing from `DOCS_NAV`** — five pages once shipped built, linked, and absent from the sidebar, which also silently killed their prev/next |
| `verify-contrast.py` | A token pair below WCAG AA, in both surface sets |
| `verify-render.py` | What the tokens cannot: the *cascade*. A primary CTA once measured 7.67:1 in the token audit while rendering 2.14:1, because container rules like `.site-nav a` outrank `.btn--primary`. It also compares the live CSS hash against `dist/`, because a deploy that uploads nothing can otherwise report success |
| `verify-api-examples.py` | A documented `curl` body the API would reject with a 422 |

Each has been made to fail deliberately before being trusted. A guard that has never gone red
is not yet a guard.

## Deploy

Cloudflare Pages. `deploy/cf-pages-deploy.sh` mints a scoped token, deploys, and revokes it on
exit — the account's master token can only mint tokens and never leaves the workstation.

Do **not** run wrangler under Bun's runtime (`bunx --bun`): it prints its banner, uploads
nothing, and exits 0, leaving the previous deployment live while every downstream check
reports success. The script uses plain `bunx` and reads the deployment ID back afterwards.
