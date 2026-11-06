# Batch mode: apply the trust work to many repositories

When the user says "add SECURITY.md to all my repos", "harden everything
public", or lists several repositories, switch to batch mode. This is the
same skill, run N times, with one set of extra rules.

## Before starting

1. **List the targets explicitly and get confirmation.** Build the list
   from `gh repo list --limit 200 --json name,visibility,isFork,pushedAt`
   (or `GET /users/{owner}/repos?per_page=100`), filter to what the user
   asked for, show the list, wait for a yes.
2. **Never include forks of other people's repositories** — the user does
   not control their branch protection or their settings, and pushing there
   pollutes the fork network. Skip with a note.
3. **Skip empty repositories** (no commits, or `pushedAt` at creation) —
   nothing to protect, and a CI workflow on an empty repo is noise.
4. **Archived repositories are read-only** — the API rejects pushes with
   `409`. Skip with a note.

## Per repository

Work in a shallow temp clone, never in the user's local copies:

```
git clone --depth 1 https://github.com/{owner}/{repo}.git "$TEMP/rt/{repo}"
```

Then run the normal Steps 1–5 (audit, files, local verification, commit,
push) for that repository, with two differences:

- **One repository = one commit.** All files for that repo go in a single
  conventional commit. Ten repos means ten commits, not thirty.
- **A failure in one repository does not stop the batch.** Record the error,
  continue with the next, report at the end. The only exception: a
  real committed secret found in a repo stops that repo's work (not the
  batch) and the finding goes into the report immediately.

## Branch protection in batch mode

Protection requires green CI on the default branch, which requires a push
and a wait. In batch mode this becomes the slow part. Two accepted shapes:

- **Two passes:** first pass adds files and pushes everywhere; poll each
  repo's check runs; second pass applies protection to the repos whose CI
  went green. Cleaner, and the report is accurate.
- **Defer protection:** add files everywhere, report CI status per repo,
  and let the user ask for protection on the green ones. Honest and fast.

Never enable protection speculatively before CI has run in that repo.

## The report

A table with one row per repository:

| Repo | Added | Commit | CI | Protection | Notes |
|---|---|---|---|---|---|
| alpha | ci.yml, SECURITY.md | `a1b2c3d` | success | on | — |
| beta | SECURITY.md | `e4f5a6b` | failure | skipped | unittest fails: import error |
| gamma | — | — | — | — | fork, skipped |
| delta | — | — | — | — | private, 403 plan limit |

"Failure" rows are the most valuable part of the report — they are exactly
the repositories whose CI just caught a real problem. Offer to fix them.

## Cleanup

Delete every temp clone when its repository is done. If the batch is
interrupted, the temp directory contains the only copies of uncommitted
work — say where it is before removing anything.
