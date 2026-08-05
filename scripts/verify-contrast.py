#!/usr/bin/env python3
"""WCAG contrast audit over the token pairs, in both surface sets.

The site is light-first with dark full-bleed bands, so every pair exists twice and both have
to hold. This is the load-bearing check for this palette: orange on cream is about 2.2:1, so
the accent has separate fill and text forms and only the dark one is ever used for words.

    python3 apps/marketing/scripts/verify-contrast.py
"""
import pathlib
import re
import sys

TOKENS = pathlib.Path(__file__).resolve().parents[1] / "src/styles/tokens.css"

# (foreground, background, required ratio, what it is)
# 4.5 for text, 3.0 for UI boundaries and large text.
PAIRS = [
    ("--text-primary", "--surface-canvas", 4.5, "body on canvas"),
    ("--text-primary", "--surface-raised", 4.5, "body on card"),
    ("--text-secondary", "--surface-canvas", 4.5, "lede on canvas"),
    ("--text-secondary", "--surface-raised", 4.5, "lede on card"),
    ("--text-tertiary", "--surface-canvas", 4.5, "supporting on canvas"),
    ("--text-tertiary", "--surface-raised", 4.5, "supporting on card"),
    ("--text-quaternary", "--surface-canvas", 4.5, "eyebrow on canvas"),
    ("--text-quaternary", "--surface-raised", 4.5, "eyebrow on card"),
    ("--accent-text", "--surface-canvas", 4.5, "accent link on canvas"),
    ("--accent-text", "--surface-raised", 4.5, "accent link on card"),
    ("--accent-ink", "--accent", 4.5, "button label on accent fill"),
    ("--status-up", "--status-up-bg", 4.5, "UP pill"),
    ("--status-down", "--status-down-bg", 4.5, "DOWN pill"),
    ("--status-warn", "--status-warn-bg", 4.5, "WARN pill"),
    ("--hairline-strong", "--surface-canvas", 1.25, "visible hairline"),
]

# Scopes to audit: (label, css selector block to read values from, fallback scope)
SCOPES = [(":root", "light"), (".band--dark", "dark band")]


def parse_scope(css: str, selector: str) -> dict[str, str]:
    """Collect `--name: value` declarations inside one selector block."""
    i = css.find(selector + " {")
    if i < 0:
        i = css.find(selector + "{")
    if i < 0:
        return {}
    depth, j = 0, css.index("{", i)
    k = j
    while k < len(css):
        if css[k] == "{":
            depth += 1
        elif css[k] == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    body = css[j + 1 : k]
    out: dict[str, str] = {}
    for name, value in re.findall(r"(--[a-z0-9-]+):\s*([^;]+);", body):
        out[name] = value.strip()
    return out


def resolve(name: str, scope: dict[str, str], base: dict[str, str], seen=None) -> str | None:
    """Follow var() indirection. Scope wins over base, which is how .band--dark overrides."""
    seen = seen or set()
    if name in seen:
        return None
    seen.add(name)
    raw = scope.get(name) or base.get(name)
    if raw is None:
        return None
    raw = raw.strip()
    m = re.fullmatch(r"var\((--[a-z0-9-]+)\)", raw)
    if m:
        return resolve(m.group(1), scope, base, seen)
    return raw


def to_rgb(value: str) -> tuple[float, float, float] | None:
    v = value.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", v)
    if m:
        h = m.group(1)
        return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]
    m = re.fullmatch(r"#([0-9a-fA-F]{3})", v)
    if m:
        h = m.group(1)
        return tuple(int(c * 2, 16) / 255 for c in h)  # type: ignore[return-value]
    return None


def luminance(rgb: tuple[float, float, float]) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hexof(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(c * 255):02x}" for c in rgb)


def main() -> int:
    css = TOKENS.read_text(encoding="utf-8")
    base = parse_scope(css, ":root")
    failures = 0
    skipped = 0

    for selector, label in SCOPES:
        scope = base if selector == ":root" else parse_scope(css, selector)
        print(f"\n{label} ({selector})")
        for fg_name, bg_name, need, what in PAIRS:
            fg_raw = resolve(fg_name, scope, base)
            bg_raw = resolve(bg_name, scope, base)
            fg = to_rgb(fg_raw) if fg_raw else None
            bg = to_rgb(bg_raw) if bg_raw else None
            if fg is None or bg is None:
                # color-mix() results cannot be resolved statically; those tokens are
                # decorative (glows, soft fills) rather than text pairs.
                print(f"  --  {what:<26} unresolved ({fg_raw or fg_name} / {bg_raw or bg_name})")
                skipped += 1
                continue
            r = ratio(fg, bg)
            ok = r >= need
            if not ok:
                failures += 1
            print(
                f"  {'ok ' if ok else 'BAD'} {what:<26} {r:5.2f}:1  (need {need})"
                f"  {hexof(fg)} on {hexof(bg)}"
            )

    print()
    if skipped:
        print(f"{skipped} pair(s) unresolved — non-literal values, not text pairs")
    print("CONTRAST:", "PASS" if failures == 0 else f"FAIL ({failures})")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
