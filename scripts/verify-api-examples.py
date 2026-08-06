#!/usr/bin/env python3
"""Every API example in the docs, checked against the published contract.

The docs carry a create snippet on all eleven monitor-type pages. An unknown field is a `422`
by design — the API rejects rather than ignores — so one wrong field name turns a documented
example into one that cannot work, and no other check notices: the page still builds, still
renders, and still links correctly.

**Source of truth is `public/openapi.json`**, generated in the core repo from
`convex/api/routes.ts` and vendored here. This repo deliberately does not read the backend
source — the marketing site is standalone, and the published spec is the contract a reader
actually gets. A stale spec is the core repo's drift check to catch, not this one's.

    python3 scripts/verify-api-examples.py

Three checks, all against `components.schemas.MonitorCreate`:

  1. every field name in every example exists in the schema
  2. every `type` value is in the documented enum
  3. every example carries the fields that type needs to actually work
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "src/content/docs"
SPEC = ROOT / "public/openapi.json"

# Fields each type needs beyond `name` and `type` to be a *usable* example rather than merely
# a valid one. The API would accept a `tcp` monitor with no port; a reader copying that would
# not end up with a working monitor.
REQUIRED = {
    "http": {"url"},
    "tcp": {"host", "port"},
    "push": {"push_expected_interval_sec"},
    "ssl": {"host"},
    "domain": {"host"},
    "dns": {"host", "dns_record_type"},
    "email-auth": {"host"},
    "icmp": {"host"},
    "udp": {"host", "port", "udp_payload"},
    "grpc": {"host", "port"},
    "smtp": {"host", "port"},
    "imap": {"host", "port"},
}


def main() -> int:
    if not SPEC.exists():
        print(f"{SPEC} is missing — it is what this validates against", file=sys.stderr)
        return 2

    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    try:
        create = spec["components"]["schemas"]["MonitorCreate"]
        fields = set(create["properties"])
        types = set(create["properties"]["type"]["enum"])
    except KeyError as e:
        print(
            f"the spec has no MonitorCreate request schema ({e}) — regenerate it in the core "
            f"repo with build-openapi.py and re-vendor it here",
            file=sys.stderr,
        )
        return 2

    # A truncated spec would make every example pass by having nothing to fail against.
    if len(fields) < 20 or len(types) < 10:
        print(f"spec looks truncated: {len(fields)} fields, {len(types)} types", file=sys.stderr)
        return 2

    print(f"spec fields : {len(fields)}")
    print(f"spec types  : {len(types)}\n")

    failures: list[str] = []
    checked = 0

    for path in sorted(DOCS.glob("monitors-*.mdx")):
        text = path.read_text(encoding="utf-8")
        block = re.search(r"## Create it with the API\n\n```bash\n(.*?)```", text, re.S)
        if not block:
            failures.append(f"{path.stem}: no 'Create it with the API' section")
            continue

        joined = block.group(1).replace("\\\n", " ")
        payload = re.search(r"-d '(\{.*?\})'\s*$", joined, re.S)
        if not payload:
            failures.append(f"{path.stem}: could not find a -d '<json>' body")
            continue

        try:
            body = json.loads(payload.group(1))
        except json.JSONDecodeError as e:
            failures.append(f"{path.stem}: the example is not valid JSON — {e}")
            continue

        checked += 1
        problems = []

        unknown = sorted(set(body) - fields)
        if unknown:
            problems.append(f"field(s) not in the spec {unknown} — the API would return 422")

        mtype = body.get("type")
        if mtype not in types:
            problems.append(f"type {mtype!r} is not in the documented enum")
        else:
            missing = sorted(REQUIRED.get(mtype, set()) - set(body))
            if missing:
                problems.append(f"missing field(s) for {mtype}: {missing}")

        if problems:
            failures.extend(f"{path.stem}: {p}" for p in problems)
            print(f"  BAD {path.stem:<24} {problems[0]}")
        else:
            print(f"  ok  {path.stem:<24} type={mtype:<10} {len(body)} fields")

    print(f"\nchecked {checked} examples")
    for f in failures:
        print(f"  FAIL: {f}")
    ok = not failures
    print("API_EXAMPLES:", "PASS" if ok else f"FAIL ({len(failures)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
