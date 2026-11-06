---
name: repo-trust
description: >-
  Raises trust in a GitHub repository with verifiable signals: CI that actually
  tests the project, LICENSE, a scoped SECURITY.md, Dependabot, branch
  protection, secret scanning and push protection. Use when the user says
  "make my repo trustworthy", "add CI", "harden this repo", "get it ready to
  publish", "make it look professional", "повысь доверие к репозиторию",
  "добавь CI и SECURITY.md", or before promoting, announcing or sharing a
  repository. Works for any local git repository with a GitHub remote, any
  language. Never breaks existing work: it commits only the files it created.
---

# repo-trust

Trust is earned with verifiable artifacts, not claims. A repository is
trustworthy when a stranger can check four things in under a minute: the
license, the CI status, the security policy, and that the default branch
cannot be force-pushed. This skill adds those artifacts to any repository
without touching work the user already has.

Reply in the user's language. Write files, commit messages and SECURITY.md in
the repository's own language (match README.md; default to English).

## Ground rules — read before anything else

1. **Never commit files you did not create.** If `git status --porcelain` is
   not empty, stage only your own files by explicit path. Say out loud what
   the user's dirty files are and that they stay untouched.
2. **CI must test something real.** A workflow that only runs `echo` is fake
   trust — worse than none, because it looks like a check that isn't one.
   Discover the project's actual entry points first (see `references/ci.md`).
3. **CI must be green before branch protection.** Enabling required status
   checks on a red or absent workflow locks the user out of their own branch.
4. **Tokens never persist.** Take credentials from `gh auth token`, an env
   var, or the user. Use them in one command. Never write a token into
   `.git/config`, a file, a commit, or the report.
5. **Private repos hit plan limits.** Branch protection and secret scanning
   return `403 Upgrade to GitHub Pro` on free accounts. Report that honestly
   once; do not retry, do not improvise workarounds.
6. **Verify locally before pushing.** Run the same checks locally that CI
   will run. If it fails locally it will fail publicly.

## Step 0 — Pick the credential path

Check `gh auth status`. If a GitHub account is logged in, use the `gh` CLI
for every API call in this skill (`references/gh-cli.md` has the
equivalents); `gh auth token` supplies credentials without handling a
secret at all. Only if `gh` is absent or unauthenticated fall back to raw
API calls with a token. Never run `gh auth login` yourself — it is
interactive and belongs to the user.

## Step 1 — Audit the repository

Collect, without changing anything:

- `git remote get-url origin`, default branch, `git status --porcelain`,
  last commit, is HEAD in sync with `origin/HEAD`.
- Language and structure: `package.json` scripts, `requirements.txt`,
  `pyproject.toml`, `Cargo.toml`, `go.mod`, `*.sh`, test directories,
  entry-point files.
- What already exists: `LICENSE`, `SECURITY.md`, `.github/workflows/*`,
  `.github/dependabot.yml`, `.gitignore`. Read the existing workflow — if one
  exists, fix or extend it instead of adding a duplicate.
- If an API token is available: repo metadata (public/private), open
  workflows, branch protection state.
- Scan the tree for committed secrets before adding anything
  (`references/policy-files.md`, "Secrets check").

Present the findings as a short table: what exists, what is missing, what
will be added.

## Step 2 — Propose the plan

One short list, then get a confirmation. Typically:

- `LICENSE` (if absent — ask which; MIT is a reasonable default to propose)
- `SECURITY.md` scoped to what the code actually does
- `.github/workflows/ci.yml` adapted to the real entry points
- `.github/dependabot.yml` for the ecosystems found
- after CI is green: branch protection, secret scanning, push protection,
  Dependabot alerts

Skip anything that already exists. Say why for each skip.

## Step 3 — Create the files

Templates live in `templates/`. Copy, then adapt — a template pasted
unmodified is another form of fake trust.

- `templates/ci-*.yml` — pick by language; see `references/ci.md` for the
  rules and how to make it test something real.
- `templates/ci-release.yml` — tag-driven release with checksums; only on
  request, build steps must be adapted.
- `templates/SECURITY.md` — fill the scope from the actual attack surface
  found in code; rules in `references/policy-files.md`. Prefer enabling
  **Private vulnerability reporting** on the repo in addition to Advisories
  — reporters get a private channel even if Advisories are not configured.
- `templates/LICENSE-MIT`, `templates/dependabot.yml`.
- Replace `{{DEFAULT_BRANCH}}` (and `{{PROJECT_NAME}}` in the release
  template) with real values.

## Step 4 — Verify locally

Run, in the repo, the exact commands CI will run: `python -m compileall`,
`node --check`, `tsc --noEmit`, `cargo check`, `shellcheck`, `npm test`,
whatever applies. On Windows note that `npm.ps1` is often blocked — use
`npm.cmd`. If the project has scripts that CI will execute, make sure the
executable bit is set (`git update-index --chmod=+x path`), or the Linux job
fails with `Permission denied`.

Fix what you find, then re-run. Only commit when green locally.

## Step 5 — Commit and push

- Stage only files you created, by path.
- Conventional commit messages; the body says what was added and why it is
  verifiable ("runs byte-compile and unittest on push/PR" — not "improves
  quality").
- Push. If the remote URL has no credentials, push once with the token in
  the URL: `git push https://x-access-token:$TOKEN@github.com/OWNER/REPO.git
  BRANCH`. Do not change the stored remote to contain the token.

## Step 6 — Protections, after CI is green

Poll the check runs for the pushed SHA until they complete. Only when the
conclusion is `success`:

1. Branch protection on the default branch — required status check contexts
   must match the exact job names in the workflow.
2. Secret scanning and push protection (public repos).
3. Dependabot alerts.

Exact API calls and payloads: `references/github-api.md`.

## Step 7 — Report

A table: file added or setting enabled, commit SHA or API status, and
verification (CI run URL, check conclusions). Anything skipped gets a reason:
"already present", "private repo, 403 from plan limits", "CI not green yet".
Remind the user to revoke any token they pasted into the chat.

## Aftercare: Dependabot PRs

The protection installed in Step 6 gates Dependabot's PRs through CI.
When the user mentions a Dependabot PR ("завис бот прислал PR", "check the
dependabot PR"), service it: verify the author is the bot, wait for
check-runs to complete, merge only green-and-mergeable, request a rebase
with `@dependabot rebase` for conflicted or red PRs. Never bypass required
checks. Full flow: `references/dependabot-prs.md`.

## Batch mode

When the user asks to apply this to many repositories at once ("all my
public repos", a list of names), switch to batch mode: explicit target list
with confirmation, shallow temp clones, one commit per repository, a
failure in one repo never stops the batch, protection only in a second
pass after CI is green. Full rules: `references/batch.md`.

## Releases (optional, on request)

When the user wants versioned releases with verifiable artifacts, add the
tag-driven release workflow (`templates/ci-release.yml`): pushing `v*`
builds the artifacts, computes `SHA256SUMS.txt` and attaches both to a
GitHub Release. This turns the artifact-verification promise in SECURITY.md
into something the user can actually check. Adapt the build steps to the
project's real build command — the template's build section is commented
out on purpose.

## What this skill deliberately does not do

- Stars, badges for badges' sake, or promotional README sections.
- Signing keys or GPG setup — that requires the user's manual action on
  GitHub; recommend it as a follow-up instead of pretending it is done.
- Anything to repositories the user did not point at.
