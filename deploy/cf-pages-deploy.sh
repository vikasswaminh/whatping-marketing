#!/usr/bin/env bash
# Mint a scoped Cloudflare Pages token and deploy the marketing site.
#
# The account's master token can ONLY mint tokens — its scope is "Account API Tokens Write"
# and nothing else — so this indirection is required, not defensive. The master token is used
# on the workstation and never written to disk or sent to the VM; only the scoped value is.
#
#     CF_MASTER_TOKEN=... CF_ACCOUNT_ID=... bash deploy/80-cf-pages.sh
#
# ATTACH_DOMAINS=1 also binds whatping.com and www. That step touches a zone carrying live
# mail, so it prints the MX/SPF/DMARC records before and after and fails loudly on a change.
set -euo pipefail

: "${CF_MASTER_TOKEN:?CF_MASTER_TOKEN must be set}"
: "${CF_ACCOUNT_ID:?CF_ACCOUNT_ID must be set}"
PROJECT="${PROJECT:-whatping-marketing}"
ZONE_NAME="${ZONE_NAME:-whatping.com}"
ATTACH_DOMAINS="${ATTACH_DOMAINS:-0}"
API=https://api.cloudflare.com/client/v4

say() { printf '==> %s\n' "$*"; }

# --- 1. mint -------------------------------------------------------------------
# Permission groups are looked up by name rather than hardcoded: the IDs are stable but a
# wrong hardcoded ID fails as a confusing authorization error much later.
say "looking up permission groups"
PG_JSON=$(curl -sS "${API}/accounts/${CF_ACCOUNT_ID}/tokens/permission_groups?per_page=200" \
  -H "Authorization: Bearer ${CF_MASTER_TOKEN}")

pg_id() {
  echo "$PG_JSON" | python3 -c "
import json, sys
want = sys.argv[1]
d = json.load(sys.stdin)
if not d.get('success'):
    sys.exit(f'permission group lookup failed: {d.get(\"errors\")}')
hits = [g for g in d['result'] if g['name'] == want]
if not hits:
    sys.exit(f'no permission group named {want!r}')
print(hits[0]['id'])
" "$1"
}

PG_PAGES=$(pg_id "Pages Write")
PG_DNS=$(pg_id "DNS Write")
PG_ZONE=$(pg_id "Zone Read")
PG_REDIR=$(pg_id "Dynamic URL Redirects Write")
echo "    Pages Write=${PG_PAGES:0:8}… DNS Write=${PG_DNS:0:8}… Zone Read=${PG_ZONE:0:8}… Redirects=${PG_REDIR:0:8}…"

say "minting '${PROJECT}-deploy'"
BODY=$(python3 - "$CF_ACCOUNT_ID" "${PROJECT}-deploy" "$PG_PAGES" "$PG_DNS" "$PG_ZONE" "$PG_REDIR" <<'PY'
import json, sys
acct, name, pages, dns, zone, redir = sys.argv[1:7]
res = f"com.cloudflare.api.account.{acct}"
print(json.dumps({
    "name": name,
    "policies": [
        {"effect": "allow", "permission_groups": [{"id": pages}], "resources": {res: "*"}},
        # DNS across every zone in the account, so attaching a custom domain needs no zone ID
        # up front. Read-only zone access is what lets us resolve the zone by name.
        {"effect": "allow",
         "permission_groups": [{"id": dns}, {"id": zone}, {"id": redir}],
         "resources": {res: {"com.cloudflare.api.account.zone.*": "*"}}},
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
# Both, tab-separated. Capturing the id HERE is the fix for a real leak: revocation used to
# find the token by name afterwards, listing ?per_page=100 with no pagination. This account
# has several hundred tokens, so the name was never on page 1, the lookup returned empty, and
# the revoke step was skipped in silence — leaving thirteen live Pages+DNS tokens behind
# before anyone noticed. The mint response already contains the id; asking twice was the bug.
print(d['result']['id'], d['result']['value'], sep='\t')
")
TOKEN_ID=${MINTED%%$'\t'*}
TOKEN=${MINTED#*$'\t'}
if [ -z "$TOKEN_ID" ] || [ -z "$TOKEN" ]; then
  echo "mint returned an unusable response" >&2
  exit 1
fi
echo "    minted ${TOKEN_ID:0:8}…"

# Revoke on any exit path, including a failure partway through. A deploy that dies after
# minting used to leak the credential too.
revoke() {
  curl -sS -X DELETE "${API}/accounts/${CF_ACCOUNT_ID}/tokens/${TOKEN_ID}" \
    -H "Authorization: Bearer ${CF_MASTER_TOKEN}" >/dev/null 2>&1 &&
    echo "==> revoked ${TOKEN_ID:0:8}…"
}
trap revoke EXIT

# --- 2. project ----------------------------------------------------------------
say "ensuring Pages project '${PROJECT}'"
EXISTS=$(curl -sS "${API}/accounts/${CF_ACCOUNT_ID}/pages/projects/${PROJECT}" \
  -H "Authorization: Bearer ${TOKEN}" |
  python3 -c "import json,sys; print(json.load(sys.stdin).get('success'))")

if [ "$EXISTS" != "True" ]; then
  curl -sS -X POST "${API}/accounts/${CF_ACCOUNT_ID}/pages/projects" \
    -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
    --data "{\"name\":\"${PROJECT}\",\"production_branch\":\"main\"}" |
    python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('success'):
    sys.exit(f'create failed: {d.get(\"errors\")}')
print('    created')
"
else
  echo "    already exists"
fi

# --- 3. deploy -----------------------------------------------------------------
say "deploying dist/"
export CLOUDFLARE_API_TOKEN="$TOKEN"
export CLOUDFLARE_ACCOUNT_ID="$CF_ACCOUNT_ID"
cd "$(dirname "$0")/.."
# NOT `bunx --bun`. Under Bun's runtime wrangler prints its banner, uploads nothing and exits
# 0 — a silent no-op that leaves the previous deployment live while every check downstream
# reports success. Node is what it expects.
bunx wrangler@4 pages deploy dist \
  --project-name "$PROJECT" --branch main --commit-dirty=true

# Trust the upload count, not the exit code. Wrangler has been observed to exit 0 having done
# nothing at all, which is exactly the failure this line exists to catch.
DEPLOYED=$(curl -sS "${API}/accounts/${CF_ACCOUNT_ID}/pages/projects/${PROJECT}/deployments?per_page=1" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('success') or not d['result']:
    sys.exit('could not read deployments')
r = d['result'][0]
print(r['id'][:8], r.get('latest_stage', {}).get('status'))
")
echo "    latest deployment: ${DEPLOYED}"

# --- 4. custom domains ---------------------------------------------------------
if [ "$ATTACH_DOMAINS" = "1" ]; then
  say "DNS before"
  BEFORE=$(dig +short MX "$ZONE_NAME" @1.1.1.1 | sort; dig +short TXT "$ZONE_NAME" @1.1.1.1; dig +short TXT "_dmarc.${ZONE_NAME}" @1.1.1.1)
  echo "$BEFORE" | sed 's/^/    /'

  say "resolving zone id for ${ZONE_NAME}"
  ZONE_ID=$(curl -sS "${API}/zones?name=${ZONE_NAME}" -H "Authorization: Bearer ${TOKEN}" |
    python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('success') or not d['result']:
    sys.exit(f'zone lookup failed: {d.get(\"errors\")}')
print(d['result'][0]['id'])
")
  echo "    ${ZONE_ID:0:8}…"

  for host in "$ZONE_NAME" "www.${ZONE_NAME}"; do
    say "attaching ${host}"
    curl -sS -X POST "${API}/accounts/${CF_ACCOUNT_ID}/pages/projects/${PROJECT}/domains" \
      -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
      --data "{\"name\":\"${host}\"}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('success'):
    print('    registered:', d['result']['name'], '-', d['result'].get('status'))
else:
    errs = d.get('errors', [])
    # 8000000-series 'already exists' is not a failure on a re-run.
    if any('already' in str(e.get('message', '')).lower() for e in errs):
        print('    already registered')
    else:
        sys.exit(f'attach failed: {errs}')
"

    # Registering the domain with the project does NOT create the DNS record — the dashboard
    # flow does that as a separate step, and the API does not. Without this the domain sits in
    # "initializing" forever and the name never resolves.
    #
    # A CNAME at the apex is legal here because Cloudflare flattens it at query time, which is
    # also why the MX and TXT records at the same name keep working.
    say "DNS record for ${host}"
    curl -sS -X POST "${API}/zones/${ZONE_ID}/dns_records" \
      -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
      --data "{\"type\":\"CNAME\",\"name\":\"${host}\",\"content\":\"${PROJECT}.pages.dev\",\"proxied\":true,\"comment\":\"Pages: ${PROJECT}\"}" |
      python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('success'):
    r = d['result']
    print('    created:', r['name'], '->', r['content'], '(proxied)' if r.get('proxied') else '')
else:
    errs = d.get('errors', [])
    if any(e.get('code') == 81057 or 'already exists' in str(e.get('message','')).lower() for e in errs):
        print('    record already exists')
    else:
        sys.exit(f'dns record failed: {errs}')
"
  done

  # Serving the same pages on two hostnames splits the SEO signal. The canonical tags already
  # point at the apex, but a redirect is the unambiguous version.
  say "www -> apex redirect rule"
  RULES=$(python3 -c "
import json
print(json.dumps({
    'rules': [{
        'action': 'redirect',
        'action_parameters': {'from_value': {
            'status_code': 308,
            'target_url': {'expression': 'concat(\"https://${ZONE_NAME}\", http.request.uri.path)'},
            'preserve_query_string': True,
        }},
        'expression': '(http.host eq \"www.${ZONE_NAME}\")',
        'description': 'www to apex',
        'enabled': True,
    }]
}))
")
  curl -sS -X PUT "${API}/zones/${ZONE_ID}/rulesets/phases/http_request_dynamic_redirect/entrypoint"     -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" --data "$RULES" |
    python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('success'):
    sys.exit(f'redirect rule failed: {d.get(\"errors\")}')
print('    308 www ->', sys.argv[1])
" "$ZONE_NAME"

  say "waiting for DNS to settle"
  sleep 20
  say "DNS after"
  AFTER=$(dig +short MX "$ZONE_NAME" @1.1.1.1 | sort; dig +short TXT "$ZONE_NAME" @1.1.1.1; dig +short TXT "_dmarc.${ZONE_NAME}" @1.1.1.1)
  echo "$AFTER" | sed 's/^/    /'

  if [ "$BEFORE" != "$AFTER" ]; then
    echo "MAIL RECORDS CHANGED — detach the custom domain and investigate" >&2
    exit 1
  fi
  echo "    mail records unchanged"
fi

# Revocation is the EXIT trap set at mint time — it runs on success, on failure, and on
# interrupt. Nothing to do here.
echo "PAGES_DONE"
