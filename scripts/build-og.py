#!/usr/bin/env python3
"""Render /og/ to public/og.png at exactly 1200x630.

The card is an Astro page (`src/pages/og.astro`) rather than a drawn asset, so it is built
from the same tokens as the site and cannot drift from the palette.

Capture is **local**, against `astro preview`, not against the deployed site. OllaGraph's
screenshot API cannot reach localhost, so using it here would need the image to be deployed
before it could be generated — deploy, capture, commit, deploy again. A local browser closes
that loop.

    python3 scripts/build-og.py            # builds and previews for you
    OG_URL=http://localhost:3001/og/ python3 ... build-og.py   # against a preview already up

Requires playwright: `pip install playwright && playwright install chromium`. If it is not
available the script says so and exits non-zero rather than leaving a stale PNG in place and
reporting success.
"""
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

APP = pathlib.Path(__file__).resolve().parents[1]
OUT = APP / "public/og.png"
URL = os.environ.get("OG_URL", "http://localhost:3001/og/")
WIDTH, HEIGHT = 1200, 630


def preview_is_up(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as res:
            return res.status == 200
    except (urllib.error.URLError, OSError):
        return False


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "playwright is not installed.\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    started = None
    if not preview_is_up(URL):
        print(f"no preview at {URL} — starting one")
        # `astro preview` serves dist/, so the build must already exist.
        if not (APP / "dist/og/index.html").exists():
            print("dist/og/index.html is missing — run the build first", file=sys.stderr)
            return 2
        started = subprocess.Popen(
            ["bunx", "astro", "preview", "--port", "3001"],
            cwd=APP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(40):
            if preview_is_up(URL):
                break
            time.sleep(0.5)
        else:
            started.terminate()
            print(f"preview never came up at {URL}", file=sys.stderr)
            return 1

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            # deviceScaleFactor 2 would produce a 2400x1260 file; the OG spec wants the
            # declared dimensions to match the actual ones, and og:image:width says 1200.
            page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
            page.goto(URL, wait_until="networkidle")
            # Webfonts decide the layout of every line here; capturing before they land
            # produces a card set in the fallback serif.
            page.wait_for_function("document.fonts.ready.then(() => true)")
            page.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT})
            browser.close()
    finally:
        if started:
            started.terminate()

    size = OUT.stat().st_size
    # A card that failed to render is a flat rectangle, and a flat 1200x630 PNG compresses
    # to a couple of kilobytes. Anything real is far larger.
    if size < 8_000:
        print(f"og.png is only {size} bytes — it probably rendered blank", file=sys.stderr)
        return 1

    print(f"wrote {OUT.relative_to(APP.parents[1])} ({size // 1024} KB, {WIDTH}x{HEIGHT})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
