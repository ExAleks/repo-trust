# LICENSE, SECURITY.md, Dependabot, secrets

## LICENSE

- Ask the user which license they want when none exists. Propose MIT as a
  default for small tools; note the practical difference in one line
  (permissive vs share-alike), do not lecture.
- Copyright line: `Copyright (c) YEAR OWNER`. The owner name comes from git
  identity (`git config user.name`), the year from the first commit
  (`git log --reverse --format=%ad --date=format:%Y | head -1`) or the
  current year for new repos.
- If a LICENSE file exists, never modify or replace it.

## SECURITY.md

The scope section is what separates a real policy from boilerplate. Fill it
from the actual attack surface, found by reading the code:

| The code does… | In scope |
|---|---|
| Network requests | TLS verification bypass, SSRF, credential leakage to logs |
| Renders user input | XSS, injection, unescaped output in templates |
| Writes files | path traversal, unsafe deserialization |
| Runs subprocesses | command injection via arguments or filenames |
| Reads `.env`/tokens | secret exposure in logs, artifacts, error messages |
| Ships binaries | artifact tampering, unsigned updates |
| Touches money/auth | idempotency, race conditions, privilege checks |

Structure (see `templates/SECURITY.md`):

1. **What the project does** — two or three sentences a stranger needs.
2. **Supported versions** — the default branch and the latest tag.
3. **In scope / out of scope** — the table above, filled with real items.
   Out of scope must honestly include dependency vulnerabilities (report
   them upstream) and social engineering.
4. **How to report** — private channel. GitHub Security Advisories
   (Security tab → Report a vulnerability) is the default; a security email
   is the alternative. State explicitly: *do not open a public issue*.
   Give response timelines only if the maintainer actually intends to keep
   them (7 days acknowledge / 30 days fix is a common default).
5. **Artifact verification** if the project ships builds — where to
   download them and that they come from the CI run attached to the tag.

Write it in the repository's language (match README.md). Keep it under a
page; a policy nobody reads protects nobody.

## Dependabot

One `updates` entry per ecosystem actually present. Enable only what
exists — a Dependabot entry for a nonexistent ecosystem is noise:

- `github-actions` — always, if `.github/workflows/` has files.
- `pip` — if `requirements.txt` or `pyproject.toml` with dependencies.
- `npm` — if `package.json` with dependencies (root directory `"/"`).
- `cargo`, `gomod`, `maven`, `nuget`, `gradle`, `docker`, `terraform` —
  by manifest presence.

Schedule `weekly`, reviewers empty (the owner is one person), no grouping
unless the project has many dependencies.

## Secrets check

Before adding anything, scan the tree for what should never be committed:

- `git grep -iE '(api[_-]?key|secret|token|password|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)'`
- look for `.env` files, `*.pem`, `*.key`, `*.keystore`, `*.jks`, connection
  strings in config files, and tokens embedded in remote URLs
  (`git remote get-url origin` — `https://user:TOKEN@github.com` means a
  leaked credential in `.git/config` history of clones).
- large binaries (`git ls-files | xargs -I{} du -k {}` or equivalent) —
  not secrets, but worth reporting: a 50 MB executable in git history is a
  trust negative and cannot be removed without rewriting history.

If a real secret is found: stop, tell the user it must be considered
compromised and rotated, and only then continue with the trust work.
Do not commit a `.gitignore` fix and call it done — the secret is already
in history.

## .gitignore

Add one only if missing. Languages' standard ignore sets, plus for any
project that handles credentials: `.env`, `.env.*`, `*.key`, `*.pem`,
session files, databases. Do not "fix" an existing `.gitignore` unless the
user asks.
