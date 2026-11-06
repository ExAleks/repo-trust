# Security Policy

## What this project does

`repo-trust` is an agent skill: markdown instructions plus YAML templates
that tell an AI coding agent how to add CI, license, security policy and
GitHub protections to a repository. It is not executed directly — the agent
reads it and acts. It also ships a small test suite and a CI workflow for
this repository itself.

## Supported versions

Supported: the `main` branch and the latest `v*` tag.

## What is in scope

- Malicious or deceptive instructions embedded in `SKILL.md`, the
  reference files or the templates — anything that makes the skill
  exfiltrate credentials, damage repositories, or bypass the safeguards
  it documents (token persistence, force-push, `--admin` merges).
- Template workflows that grant more permissions than their job needs, or
  that run untrusted input without sandboxing.
- Path traversal through the placeholders (`{{...}}`) or template copying.
- Committed secrets in this repository.

## What is out of scope

- The user's own agent mishandling a token the skill told it not to
  persist — the skill's rules are instructions, and the agent or the user
  can violate them; report agent-side issues to the agent's vendor.
- Vulnerabilities in GitHub Actions, Dependabot or the `gh` CLI.
- Repositories processed by the skill — their security is their own.

## How to report

Do not open a public issue. Use the private channel:

1. GitHub → **Security** tab → **Report a vulnerability**
   (Private vulnerability reporting).
2. Include: the file and line, the agent you were using, what the agent
   did, and the impact you assess.

Acknowledged within 7 days, fix aimed within 30 days. No bug bounty; credit
in the fix description offered if wanted.
