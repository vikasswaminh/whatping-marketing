#!/usr/bin/env bash
# Mint a LONG-LIVED, Pages-only Cloudflare token for CI (GitHub Actions).
#
# This is the reproducible way to produce (and later rotate) the CLOUDFLARE_API_TOKEN that
# lives in the repo's `production` GitHub Environment. Unlike deploy/cf-pages-deploy.sh this
# token must PERSIST — so there is deliberately no revoke trap — and it is scoped to *only*
# "Pages Write". It cannot touch DNS, other zones, or mint further tokens, so if the CI secret
# ever leaked the blast radius is "redeploy a Pages project", not the account.
#
# The account master token can ONLY mint tokens ("Account API Tokens Write") — that is why it
# is needed here and nowhere else. It is used on the WORKSTATION only; it never goes to CI or
# the VM. Source it from convex-ready-template-main/cf.txt (gitignored) and run:
#
#     CF_MASTER_TOKEN=... CF_ACCOUNT_ID=... bash deploy/mint-ci-token.sh
#
# The token VALUE is printed exactly once, on the last line, prefixed with `TOKEN=`. Pipe it
# straight into `gh secret set` — do not paste it into a file or a shell history.
set -euo pipefail

: "${CF_MASTER_TOKEN:?CF_MASTER_TOKEN must be set (workstation only; from cf.txt)}"
: "${CF_ACCOUNT_ID:?CF_ACCOUNT_ID must be set}"
TOKEN_NAME="${TOKEN_NAME:-whatping-marketing-ci}"
API=https://api.cloudflare.com/client/v4

say() { printf '==> %s\n' "$*" >&2; }   # progress on stderr so stdout carries only TOKEN=

# --- 1. resolve the "Pages Write" permission group by name (ids are stable but opaque) -------
say "looking up 'Pages Write' permission group"
PG_JSON=$(curl -sS "${API}/accounts/${CF_ACCOUNT_ID}/tokens/permission_groups?per_page=200" \
  -H "Authorization: Bearer ${CF_MASTER_TOKEN}")

PG_PAGES=$(echo "$PG_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('success'):
    sys.exit(f'permission group lookup failed: {d.get(\"errors\")}')
hits = [g for g in d['result'] if g['name'] == 'Pages Write']
if not hits:
    sys.exit(\"no permission group named 'Pages Write'\")
print(hits[0]['id'])
")
say "Pages Write = ${PG_PAGES:0:8}…"

# --- 2. mint: a single account-scoped 'Pages Write' policy, nothing else ---------------------
say "minting '${TOKEN_NAME}' (Pages Write only, no expiry)"
BODY=$(python3 - "$CF_ACCOUNT_ID" "$TOKEN_NAME" "$PG_PAGES" <<'PY'
import json, sys
acct, name, pages = sys.argv[1:4]
res = f"com.cloudflare.api.account.{acct}"
print(json.dumps({
    "name": name,
    "policies": [
        {"effect": "allow", "permission_groups": [{"id": pages}], "resources": {res: "*"}},
    ],
}))
PY
)

MINTED=$(curl -sS -X POST "${API}/accounts/${CF_ACCOUNT_ID}/tokens" \
  -H "Authorization: Bearer ${CF_MASTER_TOKEN}" \
  -H "Content-Type: application/json" --data "$BODY" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('success'):
    sys.exit(f'mint failed: {d.get(\"errors\")}')
print(d['result']['id'], d['result']['value'], sep='\t')
")
TOKEN_ID=${MINTED%%$'\t'*}
VALUE=${MINTED#*$'\t'}
if [ -z "$TOKEN_ID" ] || [ -z "$VALUE" ]; then
  echo "mint returned an unusable response" >&2
  exit 1
fi

say "minted token id ${TOKEN_ID:0:8}… (record this id — you revoke by id when rotating)"
say "next: pipe the TOKEN= line into  gh secret set CLOUDFLARE_API_TOKEN --env production -R vikasswaminh/whatping-marketing"
# stdout: exactly the two machine-readable lines, value last.
echo "TOKEN_ID=${TOKEN_ID}"
echo "TOKEN=${VALUE}"
