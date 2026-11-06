# Dependabot PRs: verify and merge

Branch protection with required checks means Dependabot PRs now go through
CI like everything else. They also get stuck when a workflow file changed
incompatibly. This skill finishes what it started: service the PRs its own
protection gate affects.

## The check sequence

For a PR (number N) in `owner/repo`:

1. **State** — `gh pr view N --json state,mergeable,headRefOid,author`
   (or `GET /repos/{o}/{r}/pulls/{n}`). Proceed only if `state: open`.
   Author check: `app/login == "dependabot"` (or
   `dependabot[bot]`); a human PR gets normal review treatment, not this
   flow.
2. **Checks** — check-runs for `headRefOid`. Every run must be
   `status: completed, conclusion: success`. Pending → wait and re-poll
   (runs usually finish in 1–5 minutes; do not merge on pending).
3. **Mergeable** — `mergeable: true`. `null` means GitHub is still
   computing it; `false` means a conflict.

## Green and mergeable

```
gh pr merge N --repo {owner}/{repo} --merge
```

`--merge` (merge commit) or `--squash` — match the repository's existing
history shape; for a solo repo with linear history prefer `--squash`.
Delete the branch after merge: `--delete-branch` (Dependabot prunes its own
branches anyway, but this is harmless).

After merging a **workflow-file** update (anything in `.github/`), check
that CI on the default branch still passes with the new action versions —
that is the one category where Dependabot can break the build it is
supposed to serve. If the default branch is now red, the fix is usually a
follow-up version bump or a workflow edit; report it, do not force-revert
blindly.

## Conflicted or red

Do not merge. Post the rebase request as a PR comment:

```
gh pr comment N --repo {owner}/{repo} --body "@dependabot rebase"
```

Dependabot recreates the PR against the new base and CI re-runs. This is
the documented, intended mechanism — never push commits into the
Dependabot branch manually.

If the same PR has been rebased and still fails twice, the update itself is
incompatible with the project. Close the PR with a note, and tell the user
what the incompatibility is (the failing check's log usually names it).

## Multi-PR situation

`gh pr list --author "app/dependabot" --state open --json number,title`
gets the queue. Process in order of risk: security fixes
(`bump ... from ... to ...` on a dependency with a known advisory) before
patch updates before major updates. Major version bumps of actions or
dependencies with breaking changes deserve a look at the diff, not a blind
merge.

## Safety line

Never `--admin` to bypass required checks, never merge a PR whose checks
failed, never force-push a Dependabot branch. The whole point of the
protection this skill installs is that these shortcuts stop existing.
