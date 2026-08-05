#!/usr/bin/env python3
"""Every API example in the docs, checked against the code that would receive it.

The docs carry a create snippet on all eleven monitor-type pages. An unknown field is a `422`
by design — `toInternal` in `convex/api/routes.ts` rejects rather than ignores — so one wrong
field name turns a documented example into one that cannot work, and no other check notices:
the page still builds, still renders, and still links correctly.

This is the static half of that verification. It reads the shipped markdown and the shipped
TypeScript and asserts they agree:

  1. every field name in every example exists in the `FIELDS` map
  2. every `type` value is a literal in `monitorType`
  3. every example carries the fields that type actually requires

It is not a substitute for POSTing them (`deploy/_docs-api-verify.sh` does that against a live
deployment), but it needs no credentials and no network, so it can run on every change.

    python3 apps/marketing/scripts/verify-api-examples.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
DOCS = ROOT / "apps/marketing/src/content/docs"
ROUTES = ROOT / "packages/backend/convex/api/routes.ts"
SCHEMA = ROOT / "packages/backend/convex/schema.ts"

# Fields every type needs beyond `name` and `type`, read from how the probes are configured.
# Kept short deliberately: this asserts the example is *usable*, not that it is exhaustive.
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
    fields = set(re.findall(r"^\s{2}([a-z_]+):\s*\"", ROUTES.read_text(encoding="utf-8"), re.M))

    # Scope to the monitorType union specifically. Matching v.literal across the whole file
    # pulls in monitorState, channelType and apiScope too — 27 literals instead of 12 — which
    # would let "webhook" or "pending" pass as a monitor type. A check that accepts anything
    # is worse than no check, because it reports PASS.
    block = re.search(r"export const monitorType = v\.union\((.*?)\n\);", SCHEMA.read_text(encoding="utf-8"), re.S)
    if not block:
        print("could not find the monitorType union in schema.ts", file=sys.stderr)
        return 2
    types = set(re.findall(r'v\.literal\("([a-z\-]+)"\)', block.group(1)))
    if not fields or not types:
        print("could not parse FIELDS or monitorType — the regexes have rotted", file=sys.stderr)
        return 2
    print(f"FIELDS in routes.ts : {len(fields)}")
    print(f"monitorType literals: {len(types)}\n")

    failures: list[str] = []
    checked = 0

    for path in sorted(DOCS.glob("monitors-*.mdx")):
        text = path.read_text(encoding="utf-8")
        block = re.search(r"## Create it with the API\n\n```bash\n(.*?)```", text, re.S)
        if not block:
            failures.append(f"{path.stem}: no 'Create it with the API' section")
            continue

        # Join the shell line-continuations, then lift the -d '<json>' payload.
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
            problems.append(f"unknown field(s) {unknown} — the API would return 422")

        mtype = body.get("type")
        if mtype not in types:
            problems.append(f"type {mtype!r} is not a monitorType literal")
        else:
            missing = sorted(REQUIRED.get(mtype, set()) - set(body))
            if missing:
                problems.append(f"missing required field(s) for {mtype}: {missing}")

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
