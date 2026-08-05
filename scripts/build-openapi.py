#!/usr/bin/env python3
"""Generate the OpenAPI 3.1 document from the live route table.

Paths, methods and scopes are read out of `convex/api/routes.ts` rather than transcribed,
so a route added to the API cannot quietly go undocumented. Descriptions live here, because
prose belongs with prose — but if the two disagree about which routes exist, this fails.

    python3 apps/marketing/scripts/build-openapi.py            # writes public/openapi.json
    python3 apps/marketing/scripts/build-openapi.py --check    # fails if it would change
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
ROUTES = ROOT / "packages/backend/convex/api/routes.ts"
OUT = ROOT / "apps/marketing/public/openapi.json"
SERVER = "https://api.whatping.com"

# path -> method -> (summary, description)
DOCS = {
    "/v1/me": {"GET": ("Current key", "The key's scope, its workspace, and usage against the monitor limit.")},
    "/v1/monitors": {
        "GET": ("List monitors", "Filter by `type`, `state` or `enabled`. Cursor paginated."),
        "POST": ("Create a monitor", "Validated by the same code the dashboard uses. Send `Idempotency-Key` to make retries safe. A `push` monitor returns `push_token` exactly once."),
    },
    "/v1/monitors/{id}": {
        "GET": ("Get a monitor", "A monitor in another workspace returns 404, not 403."),
        "PATCH": ("Update a monitor", "Partial. `type` is immutable. The whole target is re-validated, so a partial edit cannot bypass a rule."),
        "DELETE": ("Delete a monitor", "Removes its incidents and channel attachments. Check history is purged in the background."),
    },
    "/v1/monitors/{id}/pause": {"POST": ("Pause a monitor", "Clears failure accounting and resolves any open incident, so resuming does not alert from stale counters.")},
    "/v1/monitors/{id}/resume": {"POST": ("Resume a monitor", "The monitor returns to `pending` until its next check.")},
    "/v1/monitors/{id}/rotate-token": {"POST": ("Rotate a heartbeat token", "Invalidates the previous token immediately. The new one is returned once.")},
    "/v1/monitors/{id}/results": {"GET": ("List check results", "Newest first. `since` is epoch milliseconds. Results are retained 7 days.")},
    "/v1/monitors/{id}/channels": {"GET": ("List attached channels", "Channel IDs attached to this monitor.")},
    "/v1/monitors/{id}/channels/{channelId}": {
        "PUT": ("Attach a channel", "Idempotent."),
        "DELETE": ("Detach a channel", "Idempotent."),
    },
    "/v1/incidents": {"GET": ("List incidents", "Filter by `status` (open, resolved) and `monitor_id`.")},
    "/v1/channels": {"GET": ("List alert channels", "Destinations are redacted. The API cannot read back a stored credential.")},
}


def parse_routes() -> list[tuple[str, str, str]]:
    """(method, pattern, scope) from the route table, including the mapped pairs."""
    src = ROUTES.read_text(encoding="utf-8")
    found: list[tuple[str, str, str]] = []

    for m in re.finditer(
        r'method:\s*"(\w+)",\s*\n\s*pattern:\s*"([^"]+)",\s*\n\s*scope:\s*"(\w+)"', src
    ):
        found.append((m.group(1), m.group(2), m.group(3)))

    # Mapped pairs. Two shapes are in use and both have to be handled:
    #   ["pause", "resume"].map(verb => ({ method: "POST", pattern: `.../${verb}` }))
    #   ["PUT", "DELETE"].map(method => ({ method, pattern: "..." }))
    # The second uses shorthand property syntax. An earlier version of this regex required
    # `method:` and silently skipped it, so the generated spec was missing two real routes —
    # which is exactly what the reverse check below now refuses to let happen again.
    for m in re.finditer(
        r"\.\.\.\(\[([^\]]+)\] as const\)\.map<Route>\(\((\w+)\) => \(\{(.{0,500}?)scope:\s*\"(\w+)\"",
        src,
        re.S,
    ):
        values = [v.strip().strip('"') for v in m.group(1).split(",") if v.strip()]
        var, body, scope = m.group(2), m.group(3), m.group(4)

        pattern_match = re.search(r"pattern:\s*[`\"]([^`\"]+)[`\"]", body)
        if not pattern_match:
            continue
        pattern = pattern_match.group(1)

        literal_method = re.search(r"method:\s*\"(\w+)\"", body)
        shorthand = re.search(r"\bmethod\s*,", body)

        for value in values:
            if literal_method:
                method = literal_method.group(1)
            elif shorthand and var == "method":
                method = value
            else:
                continue
            found.append((method.upper(), pattern.replace(f"${{{var}}}", value), scope))
    return found


def build(routes) -> dict:
    error = {
        "type": "object",
        "properties": {
            "error": {
                "type": "object",
                "required": ["code", "message"],
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "field": {"type": "string"},
                },
            }
        },
    }

    paths: dict[str, dict] = {}
    undocumented: list[str] = []

    for method, pattern, scope in sorted(routes, key=lambda r: (r[1], r[0])):
        doc = DOCS.get(pattern, {}).get(method)
        if not doc:
            undocumented.append(f"{method} {pattern}")
            continue
        summary, description = doc

        params = [
            {
                "name": name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
            }
            for name in re.findall(r"\{(\w+)\}", pattern)
        ]
        if method == "GET" and pattern in ("/v1/monitors", "/v1/incidents", "/v1/monitors/{id}/results"):
            params += [
                {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25}},
                {"name": "cursor", "in": "query", "schema": {"type": "string"}},
            ]

        operation = {
            "summary": summary,
            "description": f"{description}\n\nRequires a `{scope}` key.",
            "operationId": re.sub(r"\W+", "_", f"{method.lower()}{pattern}").strip("_"),
            "security": [{"bearerAuth": []}],
            "responses": {
                "200": {"description": "Success"},
                "401": {"description": "Missing, unknown, revoked or expired key", "content": {"application/json": {"schema": error}}},
                "403": {"description": "The key lacks the required scope", "content": {"application/json": {"schema": error}}},
                "404": {"description": "Not found, or not in this workspace", "content": {"application/json": {"schema": error}}},
                "422": {"description": "Validation failed", "content": {"application/json": {"schema": error}}},
                "429": {"description": "Rate limited; see `retry-after`", "content": {"application/json": {"schema": error}}},
            },
        }
        if params:
            operation["parameters"] = params
        if method == "POST" and pattern == "/v1/monitors":
            operation["responses"]["201"] = {"description": "Created"}
            operation["responses"]["409"] = {"description": "Idempotency-Key reused with a different body", "content": {"application/json": {"schema": error}}}
            del operation["responses"]["200"]
        if method == "DELETE" and pattern == "/v1/monitors/{id}":
            operation["responses"]["204"] = {"description": "Deleted"}
            del operation["responses"]["200"]

        paths.setdefault(pattern, {})[method.lower()] = operation

    if undocumented:
        print("Routes exist with no description in this script:", file=sys.stderr)
        for r in undocumented:
            print(f"  {r}", file=sys.stderr)
        sys.exit(1)

    # The reverse check, which matters more: a spec that advertises an endpoint the API does
    # not serve sends every reader down a dead end. The first version of this script only
    # checked one direction and silently shipped a spec missing two real routes.
    described = {(method, pattern) for pattern, methods in DOCS.items() for method in methods}
    real = {(method, pattern) for method, pattern, _ in routes}
    phantom = sorted(f"{m} {p}" for m, p in described - real)
    if phantom:
        print("Described here but not present in the route table:", file=sys.stderr)
        for r in phantom:
            print(f"  {r}", file=sys.stderr)
        sys.exit(1)

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "WhatPing API",
            "version": "1.0.0",
            "description": (
                "Provision monitors and read their state.\n\n"
                "Writes are validated by the same code the dashboard uses, so the API accepts "
                "exactly what the interface accepts and nothing more."
            ),
        },
        "servers": [{"url": SERVER}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "A workspace API key, `sk_…`. Scoped read or write.",
                }
            }
        },
        "security": [{"bearerAuth": []}],
        "paths": paths,
    }


def main() -> int:
    routes = parse_routes()
    if len(routes) < 10:
        print(f"only parsed {len(routes)} routes — the route table format probably changed", file=sys.stderr)
        return 1

    spec = build(routes)
    rendered = json.dumps(spec, indent=2) + "\n"

    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != rendered:
            print("openapi.json is out of date — run build-openapi.py", file=sys.stderr)
            return 1
        print(f"OPENAPI: PASS ({len(routes)} routes)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(routes)} routes, {len(spec['paths'])} paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
