#!/usr/bin/env python3
"""Every route in the content package must exist in dist/.

Under a static build a route missing from `getStaticPaths` works in dev and 404s in
production, so this compares the built output rather than the dev server. Also checks that
every internal link resolves.

    python3 apps/marketing/scripts/verify-routes.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
DIST = ROOT / "apps/marketing/dist"
CONTENT = ROOT / "apps/marketing/src/content"

FRONT_ROUTE = re.compile(r'^route:\s*"?([^"\n]+)"?', re.M)
LINK = re.compile(r"\]\((/[^)#\s]*)\)")


def norm(route: str) -> str:
    route = route.strip().rstrip("/")
    return route or "/"


def main() -> int:
    built = set()
    for f in DIST.rglob("index.html"):
        rel = f.parent.relative_to(DIST).as_posix()
        built.add(norm("/" + rel if rel != "." else "/"))

    expected = {"/"}  # index.astro, which has no content file
    links: list[tuple[str, str]] = []
    for f in CONTENT.rglob("*.mdx"):
        text = f.read_text(encoding="utf-8")
        m = FRONT_ROUTE.search(text)
        if not m:
            print(f"NO ROUTE: {f}")
            return 1
        expected.add(norm(m.group(1)))
        links.extend((f.name, norm(href)) for href in LINK.findall(text))

    missing = sorted(expected - built)
    broken = sorted({(src, href) for src, href in links if href not in built})

    print(f"expected routes : {len(expected)}")
    print(f"built pages     : {len(built)}")
    print(f"missing         : {missing or 'none'}")
    print(f"broken links    : {len(broken)}")
    for src, href in broken:
        print(f"  {src} -> {href}")

    ok = not missing and not broken
    print("ROUTES:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
