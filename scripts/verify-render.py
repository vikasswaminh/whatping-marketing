#!/usr/bin/env python3
"""Render checks against the live site, asserted on pixels.

`verify-contrast.py` proves the palette. This proves the cascade — which is a different
thing, and the difference is not academic: the primary CTA once reported 7.67:1 in the token
audit while rendering 2.14:1 on the page, because container rules like `.site-nav a` outrank
`.btn--primary` on specificity. Only a screenshot catches that.

Screenshots come from OllaGraph's /v1/screenshot. Element-scoped captures use its `selector`
parameter, so a contrast assertion is independent of viewport width and layout position —
the crop *is* the element.

    OLLAGRAPH_API_KEY=... python3 apps/marketing/scripts/verify-render.py
    BASE_URL=https://<hash>.whatping-marketing.pages.dev ... # check a deployment before cutover

PNG decoding is hand-rolled on purpose. This runs on a deploy host that should not accumulate
Python packages for a job this small.
"""
import json
import os
import pathlib
import struct
import sys
import time
import urllib.error
import urllib.request
import zlib
from collections import Counter

API = "https://api.ollagraph.com/v1/screenshot"
BASE = os.environ.get("BASE_URL", "https://whatping.com").rstrip("/")
KEY = os.environ.get("OLLAGRAPH_API_KEY", "")
OUT = pathlib.Path(os.environ.get("SHOTS_DIR", "/tmp/whatping-shots"))

# Full-page captures, kept for human review. Widths are the breakpoints the CSS actually
# switches on: mobile nav below 56rem, docs sidebar collapse below 58rem, TOC below 78rem.
PAGES = [
    ("home", "/", [(1440, 900), (768, 1024), (375, 812)]),
    ("docs-limits", "/docs/limits/", [(1440, 900), (375, 812)]),
    ("vs-uptime-kuma", "/vs/uptime-kuma/", [(1440, 900)]),
]

# Element-scoped contrast assertions. Each is a thing that has to stay legible, and each is
# a thing a stylesheet change could plausibly break without anyone noticing.
ELEMENTS = [
    ("/", ".site-header .btn--primary", 4.5, "header CTA"),
    ("/", ".hero .btn--primary", 4.5, "hero CTA on the dark band"),
    ("/", ".hero .btn--secondary", 4.5, "hero secondary CTA"),
    ("/", ".pill--down", 4.5, "DOWN pill"),
    ("/", ".pill--warn", 4.5, "WARN pill"),
    ("/", ".pill--up", 4.5, "UP pill"),
    ("/docs/limits/", ".docs-sidebar a[aria-current]", 4.5, "docs active link"),
]

TIMEOUT = 120


# --- capture ---------------------------------------------------------------------------


def capture(path: str, *, width=1440, height=900, full_page=False, selector=None) -> bytes:
    body = {
        "url": f"{BASE}{path}",
        "width": width,
        "height": height,
        "full_page": full_page,
        "device_scale_factor": 2,
        "format": "png",
        "wait_until": "networkidle",
        "delay_ms": 800,
    }
    if selector:
        body["selector"] = selector

    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={
            "authorization": f"Bearer {KEY}",
            "content-type": "application/json",
            # Cloudflare sits in front of the API and rejects the default
            # `Python-urllib/3.x` signature with error 1010. Any named agent is accepted,
            # so this identifies itself honestly rather than impersonating a browser.
            "user-agent": "whatping-render-check/1.0 (+https://whatping.com)",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read()


# --- minimal PNG reader ----------------------------------------------------------------


def decode_png(data: bytes) -> tuple[int, int, list[tuple[int, int, int]]]:
    """8-bit RGB/RGBA, non-interlaced — which is all /v1/screenshot returns."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG (got %r)" % data[:16])

    pos, idat, width, height, channels = 8, bytearray(), 0, 0, 3
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        kind = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            if depth != 8 or interlace != 0 or colour not in (2, 6):
                raise ValueError(f"unsupported PNG: depth={depth} colour={colour}")
            channels = 3 if colour == 2 else 4
        elif kind == b"IDAT":
            idat += chunk
        elif kind == b"IEND":
            break
        pos += 12 + length

    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    pixels: list[tuple[int, int, int]] = []
    prev = bytearray(stride)
    at = 0
    for _ in range(height):
        filt = raw[at]
        line = bytearray(raw[at + 1 : at + 1 + stride])
        at += 1 + stride
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if filt == 1:
                line[i] = (line[i] + a) & 0xFF
            elif filt == 2:
                line[i] = (line[i] + b) & 0xFF
            elif filt == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 0xFF
            elif filt == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 0xFF
        for i in range(0, stride, channels):
            pixels.append((line[i], line[i + 1], line[i + 2]))
        prev = line
    return width, height, pixels


# --- colour ----------------------------------------------------------------------------


def luminance(rgb: tuple[int, int, int]) -> float:
    def lin(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hexof(rgb) -> str:
    return "#%02x%02x%02x" % rgb


def centre(pixels, width: int, height: int, fx=0.20, fy=0.25):
    """The middle of the element, excluding its edges.

    Necessary, not tidying: a pill button's bounding box includes the page background in its
    rounded corners, and a bordered button includes its own border. Both outnumber the text
    pixels, so a naive read of the whole crop reports the corner or the border as the
    foreground — which produced three confident false failures the first time this ran.
    """
    x0, x1 = int(width * fx), max(int(width * (1 - fx)), int(width * fx) + 1)
    y0, y1 = int(height * fy), max(int(height * (1 - fy)), int(height * fy) + 1)
    return [pixels[y * width + x] for y in range(y0, y1) for x in range(x0, x1)]


def foreground_background(pixels) -> tuple[tuple, tuple]:
    """Most common colour is the fill; the text is the most common colour far from it.

    Anti-aliasing produces a long tail of intermediate shades, so "far" is a contrast
    threshold rather than an exact match — the first candidate past 1.6:1 is the ink.
    """
    common = Counter(pixels).most_common(24)
    bg = common[0][0]
    for colour, _ in common[1:]:
        if contrast(colour, bg) >= 1.6:
            return colour, bg
    return common[1][0] if len(common) > 1 else bg, bg


# --- checks ----------------------------------------------------------------------------


def main() -> int:
    if not KEY:
        print("OLLAGRAPH_API_KEY is not set", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    print(f"base: {BASE}\nout:  {OUT}\n")

    print("full-page captures")
    for name, path, sizes in PAGES:
        for w, h in sizes:
            # Cache-bust: the apex serves the previous build from edge cache for up to a
            # minute after a deploy, which would silently check the wrong thing.
            bust = f"{'&' if '?' in path else '?'}render={int(time.time())}"
            try:
                png = capture(path + bust, width=w, height=h, full_page=(w == 1440))
            except urllib.error.HTTPError as e:
                failures.append(f"{name}@{w}: HTTP {e.code}")
                print(f"  BAD {name}@{w:<5} HTTP {e.code}")
                continue

            file = OUT / f"{name}-{w}.png"
            file.write_bytes(png)
            _, _, pixels = decode_png(png)
            dominant = Counter(pixels).most_common(1)[0][1] / len(pixels)
            # A blank or failed render is one flat colour. Anything real is far from that.
            blank = dominant > 0.97
            if blank:
                failures.append(f"{name}@{w}: looks blank ({dominant:.1%} one colour)")
            print(
                f"  {'BAD' if blank else 'ok '} {name}-{w}.png  "
                f"{len(png) // 1024}KB  dominant {dominant:.1%}"
            )

    print("\nelement contrast (this is the cascade check)")
    for path, selector, need, label in ELEMENTS:
        bust = f"{'&' if '?' in path else '?'}render={int(time.time())}"
        try:
            png = capture(path + bust, selector=selector)
        except urllib.error.HTTPError as e:
            failures.append(f"{label}: HTTP {e.code} for {selector}")
            print(f"  BAD {label:<28} HTTP {e.code}  ({selector})")
            continue

        w, h, pixels = decode_png(png)
        fg, bg = foreground_background(centre(pixels, w, h))
        r = contrast(fg, bg)
        ok = r >= need
        if not ok:
            failures.append(f"{label}: {r:.2f}:1 (need {need}) — {hexof(fg)} on {hexof(bg)}")
        print(
            f"  {'ok ' if ok else 'BAD'} {label:<28} {r:5.2f}:1  (need {need})  "
            f"{hexof(fg)} on {hexof(bg)}"
        )

    print()
    for f in failures:
        print(f"  FAIL: {f}")
    print("RENDER:", "PASS" if not failures else f"FAIL ({len(failures)})")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
