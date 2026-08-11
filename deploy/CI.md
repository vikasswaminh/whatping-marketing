# Marketing CI — push-to-deploy

Push to **`main`** → a **self-hosted runner on the production VM** builds, verifies, and deploys the
site to Cloudflare Pages (`whatping.com` / `www`). No `pull_request` trigger. The CF **master token
never leaves the workstation**.

## Pieces

| Piece | Where | What it does |
|---|---|---|
| [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) | repo | `build` job → `deploy` job, both on the self-hosted runner; **push to `main` only** |
| self-hosted runner `nh-4c8g-318` | VM `10.1.30.29`, user `ghrunner` | executes the jobs; systemd service `actions-runner` |
| `production` GitHub Environment | repo settings | holds `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`, **restricted to the `main` branch** |
| [`deploy/mint-ci-token.sh`](./mint-ci-token.sh) | workstation | mints the **Pages-Write-only** CI token from the master token |
| [`deploy/cf-pages-deploy.sh`](./cf-pages-deploy.sh) | workstation | break-glass deploy + the **only** path for domains/DNS/redirect |

## Why it's safe

- **No `pull_request` trigger.** A self-hosted runner runs workflow code on the box, so we never let
  an unmerged PR execute on the production host. Only pushes to `main` (already-merged, trusted code)
  run. The people who can push to `main` (you + the write-collaborator) are the same people who
  already have root on this VM — so the runner grants no new access.
- The runner runs as the **non-root `ghrunner` user** (no sudo, no extra groups), so a build cannot
  read root-owned production files (Convex data, the monitor stack) by default.
- The CI token is **`Pages Write` only** — it cannot touch DNS, other zones, or mint tokens. Worst
  case if it leaked: someone redeploys a Pages project until you rotate. Not the account.
- The token is an **environment secret on a `main`-only environment**, referenced solely by the
  `deploy` job — belt-and-braces with the no-PR-trigger rule.
- The **master token** (which *can* mint account-wide) is used only on the workstation, only for the
  one-time mint and for rare domain/redirect ops. It is never in CI and never on the VM.

**Recommended companion:** protect `main` (require PR review) so a workflow change can't merge
unreviewed — the only remaining way to change what the prod runner executes.

## The runner (VM ops)

Registered on `10.1.30.29` (`nh-4c8g-318`) as `ghrunner`, run by systemd:

```bash
ssh root@10.1.30.29 'systemctl status actions-runner'     # health
ssh root@10.1.30.29 'systemctl restart actions-runner'    # restart
ssh root@10.1.30.29 'journalctl -u actions-runner -n 50'  # logs

# Re-register (e.g. after a repo move) or remove:
ssh root@10.1.30.29 "su - ghrunner -c 'cd /opt/actions-runner && ./config.sh remove --token <REMOVE_TOKEN>'"
#   REMOVE_TOKEN: gh api -X POST repos/vikasswaminh/whatping-marketing/actions/runners/remove-token --jq .token
```

A build needs `node`+`npm`+`python3` on the box (present) and pulls `bun` per-run via `setup-bun`.

## First-time setup (workstation, once)

```bash
# 1. Source the master token + account id from the gitignored creds file (never commit/echo it).
#    (cf.txt lives in the core repo: convex-ready-template-main/cf.txt)
export CF_MASTER_TOKEN=...   CF_ACCOUNT_ID=...

# 2. Mint the Pages-only CI token. Prints TOKEN_ID=… and TOKEN=… (value) on stdout.
out=$(bash deploy/mint-ci-token.sh)
echo "$out" | grep '^TOKEN_ID='          # record this id for rotation/revocation

# 3. Create the main-only environment and store the secrets (piped, never pasted).
R=vikasswaminh/whatping-marketing
gh api -X PUT "repos/$R/environments/production" \
  -f 'deployment_branch_policy[protected_branches]=false' \
  -f 'deployment_branch_policy[custom_branch_policies]=true'
gh api -X POST "repos/$R/environments/production/deployment-branch-policies" -f name=main
echo "$out" | sed -n 's/^TOKEN=//p' | gh secret set CLOUDFLARE_API_TOKEN --env production -R "$R"
printf '%s' "$CF_ACCOUNT_ID"            | gh secret set CLOUDFLARE_ACCOUNT_ID --env production -R "$R"
```

## Rotating the CI token

```bash
export CF_MASTER_TOKEN=...  CF_ACCOUNT_ID=...
out=$(bash deploy/mint-ci-token.sh)                       # mint a fresh one
echo "$out" | sed -n 's/^TOKEN=//p' | gh secret set CLOUDFLARE_API_TOKEN --env production \
  -R vikasswaminh/whatping-marketing
# then revoke the OLD token by its recorded id:
curl -sS -X DELETE "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/tokens/<OLD_ID>" \
  -H "Authorization: Bearer $CF_MASTER_TOKEN"
```

## What stays manual (by design)

- **Previews:** `DEPLOY_BRANCH=my-branch bash deploy/cf-pages-deploy.sh` → a `*.pages.dev` URL.
- **Domain attach / DNS / apex→www redirect:** `ATTACH_DOMAINS=1 bash deploy/cf-pages-deploy.sh`.
  Kept off CI: it needs a broader token and touches a zone carrying **live mail** (it diffs
  MX/SPF/DMARC and aborts on any change).

## PR validation / previews

There is no `pull_request` trigger (it would run unmerged code on the prod runner). Validate a change
before pushing to `main` from the workstation: `bun run build && bun run verify`, or preview it live
with `DEPLOY_BRANCH=my-branch bash deploy/cf-pages-deploy.sh` → a `*.pages.dev` URL.

## Rollback

Disable/delete `deploy.yml` → back to manual `cf-pages-deploy.sh` (untouched, still works). Revoke
the CI token via the master token to fully unwind.
