# Marketing CI — push-to-deploy

Push to **`main`** → GitHub Actions builds, verifies, and deploys the site to Cloudflare Pages
(`whatping.com` / `www`). Pull requests build + verify only. Nothing runs on the VM; the CF
**master token never leaves the workstation**.

## Pieces

| Piece | Where | What it does |
|---|---|---|
| [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) | repo | `build` job (all events) → `deploy` job (push-to-`main` only) |
| `production` GitHub Environment | repo settings | holds `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`, **restricted to the `main` branch** |
| [`deploy/mint-ci-token.sh`](./mint-ci-token.sh) | workstation | mints the **Pages-Write-only** CI token from the master token |
| [`deploy/cf-pages-deploy.sh`](./cf-pages-deploy.sh) | workstation | break-glass deploy + the **only** path for domains/DNS/redirect |

## Why it's safe

- The CI token is **`Pages Write` only** — it cannot touch DNS, other zones, or mint tokens. Worst
  case if it leaked: someone redeploys a Pages project until you rotate. Not the account.
- The token is an **environment secret on a `main`-only environment**. A PR-branch run — including a
  PR that edited `deploy.yml` to try to print the secret — is **denied the secret by GitHub**,
  because the run isn't on `main`. PRs therefore only ever `build`+`verify`.
- The **master token** (which *can* mint account-wide) is used only on the workstation, only for the
  one-time mint and for rare domain/redirect ops. It is never in CI and never on the VM.

**Recommended companion:** protect `main` (require PR review) so a workflow change can't merge
unreviewed. The environment already blocks PR-time exfil; branch protection blocks the merge path.

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

## Opt-in: auto-preview on PRs

Not enabled. It would require a Pages-write token readable in PR runs (a hostile PR-workflow edit
could then deface Pages until rotated). If you want it, add a second token in a non-restricted
secret and a preview `deploy` job keyed on `github.head_ref`. Ask and it'll be wired.

## Rollback

Disable/delete `deploy.yml` → back to manual `cf-pages-deploy.sh` (untouched, still works). Revoke
the CI token via the master token to fully unwind.
