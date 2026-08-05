#!/usr/bin/env python3
"""WCAG contrast audit over the OKLCH token pairs.

A derived ramp is exactly where contrast quietly fails: every step looks fine next to its
neighbour, and the fourth text level against the raised surface is 3.9:1. This resolves the
OKLCH values in `tokens.css` to sRGB and asserts the pairs that actually get rendered.

    python3 apps/marketing/scripts/verify-contrast.py
"""
import math
import pathlib
import re
import sys

TOKENS = pathlib.Path(__file__).resolve().parents[1] / "src/styles/tokens.css"

# (foreground, background, required ratio, what it is)
# 4.5 for body text, 3.0 for large text (>=24px or >=18.66px bold) and UI boundaries.
PAIRS = [
    ("--text-primary", "--surface-canvas", 4.5, "body on canvas"),
    ("--text-primary", "--surface-raised", 4.5, "body on card"),
    ("--text-primary", "--surface-overlay", 4.5, "body on overlay"),
    ("--text-secondary", "--surface-canvas", 4.5, "lede on canvas"),
    ("--text-secondary", "--surface-raised", 4.5, "lede on card"),
    ("--text-tertiary", "--surface-canvas", 4.5, "supporting on canvas"),
    ("--text-tertiary", "--surface-raised", 4.5, "supporting on card"),
    # Quaternary is eyebrows and captions only — uppercase mono at 12px, which is
    # small text, so it is held to 4.5 as well rather than excused as "large".
    ("--text-quaternary", "--surface-canvas", 4.5, "eyebrow on canvas"),
    ("--text-quaternary", "--surface-raised", 4.5, "eyebrow on card"),
    ("--accent", "--surface-canvas", 4.5, "accent link on canvas"),
    ("--accent", "--surface-raised", 4.5, "accent link on card"),
    ("--accent-ink", "--accent", 4.5, "button label on accent"),
    ("--status-down", "--surface-canvas", 4.5, "down text on canvas"),
    ("--status-down", "--surface-raised", 4.5, "down text on card"),
    ("--status-warn", "--surface-canvas", 4.5, "warn text on canvas"),
    ("--status-warn", "--surface-raised", 4.5, "warn text on card"),
    ("--hairline-strong", "--surface-canvas", 1.4, "visible hairline"),
]


def parse_tokens(css: str) -> dict[str, tuple[float, float, float]]:
    """Pull `--name: oklch(L C H)` declarations, resolving the few var()/calc() forms used."""
    consts = {
        "--h": 220.0,
        "--c-surface": 0.006,
        "--c-text": 0.008,
        "--contrast": 1.0,
    }
    out: dict[str, tuple[float, float, float]] = {}

    def num(tok: str) -> float | None:
        tok = tok.strip()
        if tok in consts:
            return consts[tok]
        m = re.fullmatch(r"var\((--[a-z-]+)\)", tok)
        if m:
            return consts.get(m.group(1))
        m = re.fullmatch(r"calc\(([\d.]+)\s*([*/])\s*var\((--[a-z-]+)\)\)", tok)
        if m:
            base, op, ref = float(m.group(1)), m.group(2), consts.get(m.group(3))
            if ref is None:
                return None
            return base * ref if op == "*" else base / ref
        try:
            return float(tok)
        except ValueError:
            return None

    def split_args(body: str) -> list[str]:
        """Split on spaces, but not inside parentheses — calc(0.145 / var(--contrast))
        contains both a space and a nested paren, which a plain regex mangles."""
        parts, depth, cur = [], 0, ""
        for ch in body:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch.isspace() and depth == 0:
                if cur:
                    parts.append(cur)
                    cur = ""
                continue
            cur += ch
        if cur:
            parts.append(cur)
        return parts

    # Balanced match for the whole oklch(...) call, including nested calc()/var().
    for m in re.finditer(r"(--[a-z-]+):\s*oklch\(", css):
        name = m.group(1)
        i, depth = m.end(), 1
        while i < len(css) and depth:
            if css[i] == "(":
                depth += 1
            elif css[i] == ")":
                depth -= 1
            i += 1
        body = css[m.end() : i - 1]
        parts = split_args(body)
        if len(parts) != 3:
            continue
        vals = [num(p) for p in parts]
        if any(v is None for v in vals):
            continue
        out[name] = (vals[0], vals[1], vals[2])  # type: ignore[misc]
    return out


def oklch_to_srgb(L: float, C: float, H: float) -> tuple[float, float, float]:
    h = math.radians(H)
    a, b = C * math.cos(h), C * math.sin(h)

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3

    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def gamma(u: float) -> float:
        u = max(0.0, min(1.0, u))
        return 1.055 * (u ** (1 / 2.4)) - 0.055 if u > 0.0031308 else 12.92 * u

    return gamma(r), gamma(g), gamma(bl)


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: tuple[float, float, float], bg: tuple[float, float, float]) -> float:
    a, b = relative_luminance(fg), relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def hexof(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(c * 255):02x}" for c in rgb)


def main() -> int:
    tokens = parse_tokens(TOKENS.read_text(encoding="utf-8"))
    print(f"resolved {len(tokens)} oklch tokens\n")

    failures = 0
    for fg_name, bg_name, need, label in PAIRS:
        if fg_name not in tokens or bg_name not in tokens:
            print(f"  MISSING  {fg_name} / {bg_name}")
            failures += 1
            continue
        fg = oklch_to_srgb(*tokens[fg_name])
        bg = oklch_to_srgb(*tokens[bg_name])
        r = ratio(fg, bg)
        ok = r >= need
        if not ok:
            failures += 1
        print(
            f"  {'ok ' if ok else 'BAD'} {label:<26} {r:5.2f}:1  (need {need})"
            f"  {hexof(fg)} on {hexof(bg)}"
        )

    print()
    print("CONTRAST:", "PASS" if failures == 0 else f"FAIL ({failures})")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
