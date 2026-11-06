# GitHub API: protections, checks, verification

All calls use the same header set:

```
Authorization: Bearer $TOKEN
Accept: application/vnd.github+json
User-Agent: repo-trust
X-GitHub-Api-Version: 2022-11-28
```

Token sources, in order of preference: `gh auth token` (no secret handling
at all), an environment variable the user set, or a token the user pasted
(then remind them to revoke it after the session). Required scopes:
`repo` (protection, private repos) and `workflow` (pushing workflow files).
Without `workflow` scope, pushing a commit that adds `.github/workflows/*`
is rejected — the skill cannot do its job with a `repo`-only token.

## Where to find the contexts for required checks

Job `name:` values from the workflow, not the workflow's `name:`. Confirm
after the first run:

```
GET /repos/{owner}/{repo}/commits/{sha}/check-runs
```

`name` fields of each `check_runs` entry are the contexts to require.

## Wait for CI before protecting

Poll after pushing:

```
GET /repos/{owner}/{repo}/commits/{sha}/check-runs
```

Each run is `status: completed` with a `conclusion`. Only proceed to
protection when every conclusion is `success`. If a run fails, the correct
move is to fix the workflow, not to lower the bar.

## Branch protection

```
PUT /repos/{owner}/{repo}/branches/{branch}/protection
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["checks"]           // job names, see above
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

- `strict: true` — branches must be up to date before merging.
- `enforce_admins: false` — solo owners keep a merge hatchet for
  emergencies; recommend flipping it to `true` for teams.
- 200 on success. **403 "Upgrade to GitHub Pro or make this repository
  public"** — free-plan private repos cannot be protected. Report once,
  move on.
- 422 with a message about missing contexts — the context name does not
  match any check run. Re-fetch check runs and fix the names.

## Security features

```
PATCH /repos/{owner}/{repo}
{"security_and_analysis": {"secret_scanning": {"status": "enabled"},
                            "secret_scanning_push_protection": {"status": "enabled"},
                            "dependabot_security_updates": {"status": "enabled"}}}
```

Public repos: all three work. Private repos: `secret_scanning` returns
422 on free plans — same "report once" rule. `dependabot_security_updates`
generally works everywhere.

## Verification list for the report

After everything, verify each claim — the report contains only what was
actually checked:

| Claim | How verified |
|---|---|
| CI added and green | check-runs for the pushed SHA, conclusion `success` |
| Protection on | `GET .../branches/{branch}/protection` returns the settings |
| Secret scanning on | `GET /repos/{o}/{r}` → `security_and_analysis` statuses |
| Files committed | `git log --stat` for each SHA, only expected paths |
| User's work intact | `git status --porcelain` shows only their original dirt |
| No token left behind | `git remote get-url origin` clean; no token in any file |

Anything not verified gets the literal word "unverified", not silence.
