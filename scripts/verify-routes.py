#!/usr/bin/env python3
"""Every route in the content package must exist in dist/, and every docs page must be
reachable from the sidebar.

Under a static build a route missing from `getStaticPaths` works in dev and 404s in
production, so this compares the built output rather than the dev server. Also checks that
every internal link resolves.

The sidebar check exists because of a specific failure. Five docs pages — the API reference
and the four new protocol types — shipped built, linked from the docs index, and *absent from
`DOCS_NAV`*. That is worse than a 404: `Docs.astro` derives prev/next from the same list via
`findIndex`, so an unlisted page returns -1 and loses its sidebar entry, its prev/next and its
active-link highlight all at once. A reader arriving from search lands somewhere with no way
out, and nothing failed.

Checked in **both** directions, for the same reason `build-openapi.py` is: a sidebar entry
pointing at a page that does not exist is the mirror-image defect, and only the reverse pass
finds it.

    python3 scripts/verify-routes.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CONTENT = ROOT / "src/content"
SITE_TS = ROOT / "src/lib/site.ts"

FRONT_ROUTE = re.compile(r'^route:\s*"?([^"\n]+)"?', re.M)
LINK = re.compile(r"\]\((/[^)#\s]*)\)")
# DOCS_NAV entries only — `href: "..."` inside the exported array. Regex rather than a TS
# parse for the same reason build-openapi.py uses one: no toolchain on the deploy host.
NAV_HREF = re.compile(r'href:\s*"(/docs/[^"]*)"')


def norm(route: str) -> str:
    route = route.strip().rstrip("/")
    return route or "/"


def main() -> int:
    built = set()
    for f in DIST.rglob("index.html"):
        rel = f.parent.relative_to(DIST).as_posix()
        built.add(norm("/" + rel if rel != "." else "/"))

    # Static assets are legitimate link targets too — /openapi.json is linked from four
    # pages and is not a route. Without this the checker reports a working link as broken,
    # which trains people to ignore it.
    assets = {
        "/" + f.relative_to(DIST).as_posix()
        for f in DIST.rglob("*")
        if f.is_file() and f.name != "index.html"
    }

    expected = {"/"}  # index.astro, which has no content file
    docs_routes = set()
    links: list[tuple[str, str]] = []
    for f in CONTENT.rglob("*.mdx"):
        text = f.read_text(encoding="utf-8")
        m = FRONT_ROUTE.search(text)
        if not m:
            print(f"NO ROUTE: {f}")
            return 1
        route = norm(m.group(1))
        expected.add(route)
        if f.parent.name == "docs":
            docs_routes.add(route)
        links.extend((f.name, norm(href)) for href in LINK.findall(text))

    missing = sorted(expected - built)
    broken = sorted({(src, href) for src, href in links if href not in built | assets})

    print(f"expected routes : {len(expected)}")
    print(f"built pages     : {len(built)}")
    print(f"missing         : {missing or 'none'}")
    print(f"broken links    : {len(broken)}")
    for src, href in broken:
        print(f"  {src} -> {href}")

    # --- sidebar reachability, both directions ------------------------------------------
    nav = {norm(h) for h in NAV_HREF.findall(SITE_TS.read_text(encoding="utf-8"))}
    if not nav:
        print("\nDOCS_NAV: could not parse any hrefs out of site.ts — the regex has rotted")
        return 1

    # "/docs" is the index; it is reachable from the wordmark and the header, and it is
    # deliberately the group-less landing page rather than a sidebar item.
    orphans = sorted(docs_routes - nav - {"/docs"})
    dangling = sorted(nav - built)

    print(f"\ndocs pages      : {len(docs_routes)}")
    print(f"DOCS_NAV entries: {len(nav)}")
    print(f"orphans         : {orphans or 'none'}")
    for o in orphans:
        print(f"  built and linked, but absent from DOCS_NAV: {o}")
    print(f"dangling nav    : {dangling or 'none'}")
    for d in dangling:
        print(f"  in DOCS_NAV but not built: {d}")

    ok = not missing and not broken and not orphans and not dangling
    print("ROUTES:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
