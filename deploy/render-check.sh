#!/usr/bin/env bash
# Render checks against the live marketing site.
#
# Run this after deploy/80-cf-pages.sh. It captures the pages at each breakpoint for human
# review and asserts contrast on the elements that have to stay legible — reading the
# rendered pixels, not the stylesheet.
#
# That distinction is the whole reason this exists: verify-contrast.py reported the primary
# CTA at 7.67:1 while the page rendered it at 2.14:1, because `.site-nav a` outranks
# `.btn--primary` on specificity. A token audit cannot see the cascade.
#
#     bash deploy/81-shots.sh
#     BASE_URL=https://<hash>.whatping-marketing.pages.dev bash deploy/81-shots.sh
#
# The second form checks a specific deployment before it is promoted, which also sidesteps
# the edge cache that serves the previous build on the apex for a minute or so after deploy.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SHOTS_DIR="${SHOTS_DIR:-/tmp/whatping-shots}"

# The key lives in the Convex deployment environment, not on disk.
if [ -z "${OLLAGRAPH_API_KEY:-}" ]; then
  NODE=/usr/bin/node
  CVX="${REPO}/node_modules/convex/bin/main.js"
  if [ ! -f "$CVX" ]; then
    echo "OLLAGRAPH_API_KEY is not set and the convex CLI is not available here" >&2
    exit 1
  fi
  OLLAGRAPH_API_KEY=$(cd "${REPO}/packages/backend" && "$NODE" "$CVX" env get OLLAGRAPH_API_KEY 2>/dev/null | tr -d '\r\n')
  export OLLAGRAPH_API_KEY
fi

: "${OLLAGRAPH_API_KEY:?could not resolve OLLAGRAPH_API_KEY}"

SHOTS_DIR="$SHOTS_DIR" python3 "${REPO}/scripts/verify-render.py"
STATUS=$?

echo
echo "screenshots in ${SHOTS_DIR}:"
ls -1 "${SHOTS_DIR}"/*.png 2>/dev/null | sed 's/^/  /' || echo "  none"

exit $STATUS
