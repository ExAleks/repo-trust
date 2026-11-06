# GitHub CLI: the preferred way to talk to GitHub

Check `gh --version` and `gh auth status` first. If `gh auth status` reports
a logged-in account, use `gh` for everything and skip PAT handling entirely
— `gh auth token` supplies credentials without a secret ever being pasted,
stored or echoed.

If `gh` is not installed or not authenticated: fall back to raw API calls
with a token (`references/github-api.md`), and suggest `gh auth login` as
the better long-term setup. Never run `gh auth login` yourself — it is
interactive and belongs to the user.

## Equivalents: gh vs raw API

| Task | gh command |
|---|---|
| Repo metadata | `gh api repos/{owner}/{repo}` |
| List check runs for a SHA | `gh api repos/{o}/{r}/commits/{sha}/check-runs` |
| Branch protection | `gh api repos/{o}/{r}/branches/{branch}/protection -X PUT --input body.json` |
| Secret scanning / push protection | `gh repo edit {o}/{r} --enable-secret-scanning --enable-push-protection` |
| Dependabot alerts | `gh api repos/{o}/{r}/dependabot/alerts` |
| Run a workflow | `gh workflow run ci.yml --ref {branch}` |
| Watch a run | `gh run watch {run-id} --exit-status` |
| List runs | `gh run list --repo {o}/{r} --limit 5` |
| List secrets | `gh secret list --repo {o}/{r}` |
| Merge a PR | `gh pr merge {n} --repo {o}/{r} --merge` |
| View a PR | `gh pr view {n} --repo {o}/{r} --json state,mergeable,headRefOid` |
| Comment on a PR | `gh pr comment {n} --repo {o}/{r} --body "..."` |
| Create a release | `gh release create {tag} --target {branch} dist/*` |

Body payloads for `--input` are written to a temp file as JSON, then
deleted. Never pass secrets inline where they land in shell history.

## Notes

- `gh` output defaults to nice tables; add `--json` or `-t` templates when
  the output will be parsed programmatically.
- On Windows, quote paths with spaces; `gh` is a normal executable, no
  PowerShell execution-policy issues.
- `gh auth token` prints the token — pipe it straight into the consumer,
  never into a variable that gets echoed or written:
  `git push "https://x-access-token:$(gh auth token)@github.com/..." BRANCH`.
- gh respects the `GH_TOKEN`/`GITHUB_TOKEN` env vars — if the user has one
  set, `gh` works without `gh auth login`.
