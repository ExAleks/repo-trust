# repo-trust

**A skill that makes a GitHub repository trustworthy with verifiable signals —
for any AI coding agent, any language.**

A repository is trustworthy when a stranger can check four things in under a
minute: the license, the CI status, the security policy, and that the default
branch cannot be force-pushed. Not stars, not badges — things you can click
and verify.

This skill walks an agent through adding exactly those artifacts:

| Artifact | What it gives |
|---|---|
| CI workflow | green checks that test something real, not `echo` |
| `LICENSE` | clear terms for strangers |
| `SECURITY.md` | scope filled from the actual attack surface, private reporting channel |
| `dependabot.yml` | dependency and action updates tracked |
| Branch protection | default branch cannot be force-pushed or deleted |
| Secret scanning + push protection | leaked keys blocked before they land |
| Release workflow *(optional)* | tag → build → `SHA256SUMS.txt` → GitHub Release |

It also services what it installs: Dependabot PRs are verified against CI and
merged green-only, and the whole flow can run in batch mode across every
public repository you own.

## Design principles

1. **Verifiable, not declarable.** Every step ends with something a stranger
   can check. The final report contains only verified facts; anything
   unverified is labeled as such.
2. **CI must test something real.** A workflow that only runs `echo` is fake
   trust. The skill reads the project's entry points first, then writes CI
   that exercises them.
3. **Never breaks existing work.** In a dirty working tree, the skill commits
   only the files it created, by explicit path. Your uncommitted edits stay
   untouched.
4. **Green before gates.** Branch protection is enabled only after the pushed
   SHA has green check runs — otherwise you lock yourself out of your own
   branch.
5. **No secrets persisted.** Works through `gh auth token` when available; a
   pasted token is used once and never written to `.git/config`, a file, or
   the report.

## Install

The skill is a plain folder (`skills/repo-trust/`) with a `SKILL.md`, so it
works with any agent that loads skills from a directory. Pick your agent:

### Claude Code

```bash
git clone https://github.com/ExAleks/repo-trust.git
mkdir -p ~/.claude/skills
cp -r repo-trust/skills/repo-trust ~/.claude/skills/
```

Project-local instead of global: copy the same folder into your repo's
`.claude/skills/`. Invoke with `/repo-trust` or by asking "make this repo
trustworthy".

As a plugin (namespaced):

```
/plugin marketplace add ExAleks/repo-trust
```

### Codex / Codex CLI

```bash
git clone https://github.com/ExAleks/repo-trust.git
mkdir -p ~/.codex/skills
cp -r repo-trust/skills/repo-trust ~/.codex/skills/
```

Or paste the contents of `skills/repo-trust/SKILL.md` into your
`AGENTS.md` / `~/.codex/AGENTS.md` — it is plain markdown and reads fine
inline, losing only the reference files (inline their content when you need
them).

### Cursor

```bash
git clone https://github.com/ExAleks/repo-trust.git
mkdir -p ~/.cursor/skills
cp -r repo-trust/skills/repo-trust ~/.cursor/skills/
```

Project-local: `.cursor/skills/` inside the repository. In a Cursor rules
file (`.cursorrules` or `.cursor/rules/*.mdc`), reference the skill:

```
When asked to make this repository trustworthy, add CI, or harden the repo,
follow the instructions in skills/repo-trust/SKILL.md.
```

### OpenCode

```bash
git clone https://github.com/ExAleks/repo-trust.git
mkdir -p ~/.config/opencode/skills
cp -r repo-trust/skills/repo-trust ~/.config/opencode/skills/
```

Skills are auto-discovered from that directory — no config change needed.

### GitHub Copilot (instructions file)

Copilot has no skill folder; the skill works as chat instructions. Paste the
full text of `skills/repo-trust/SKILL.md` into your custom instructions
(`.github/copilot-instructions.md` for a repository, or the editor's
custom-instructions setting), and copy the `references/` and `templates/`
files into the repo at `.github/repo-trust/` (adjust the paths mentioned in
the pasted text accordingly).

### Any other agent

If your agent reads a skills/markdown folder (Grok, Windsurf's rules, a
custom harness), copy `skills/repo-trust/` wherever that agent looks. If it
only takes a single prompt, paste `SKILL.md` and copy `templates/` into the
project — the reference files are optional deep-dives, the main flow lives
in `SKILL.md`.

## What it looks like in use

```
you:    повысь доверие к этому репозиторию

agent:  Audit: python project, requirements.txt, no CI, no SECURITY.md,
        no LICENSE, working tree clean, default branch main.
        Plan: ci.yml (pip + compileall + unittest), SECURITY.md scoped
        to network egress and token handling, LICENSE MIT, dependabot.
        Confirm?

you:    да

agent:  [writes files, runs the same checks locally — all green]
        [commits only the four files it created]
        [pushes]
        [waits for check runs: checks — success]
        [enables branch protection, secret scanning, push protection]

        | Artifact        | Commit    | CI      | Protection |
        |-----------------|-----------|---------|------------|
        | ci.yml          | a1b2c3d   | success | required   |
        | SECURITY.md     | a1b2c3d   | —       | —          |
        | LICENSE         | a1b2c3d   | —       | —          |
        | dependabot.yml  | a1b2c3d   | —       | alerts on  |
```

## Batch mode

```
you:    add SECURITY.md and CI to all my public repositories

agent:  Found 13 public repositories, 2 are forks (skipped), 1 archived
        (skipped). 10 targets. Confirm?
```

One commit per repository, a failure in one repo never stops the batch,
protection applied in a second pass only to repos whose CI went green. The
report shows every repository with its status.

## Repository layout

```
skills/repo-trust/
├── SKILL.md                 the method: 8 steps + aftercare + batch
├── references/
│   ├── ci.md                CI rules, real-check discovery, local-vs-CI gaps
│   ├── gh-cli.md            gh CLI equivalents for every operation
│   ├── github-api.md        raw API calls, payloads, verification list
│   ├── policy-files.md      SECURITY.md scoping table, Dependabot, secrets scan
│   ├── dependabot-prs.md    PR verification flow, rebase protocol
│   └── batch.md             multi-repository rules
└── templates/
    ├── ci-python.yml        pip + compileall + unittest
    ├── ci-node.yml          install + typecheck/test/build (scripts that exist)
    ├── ci-rust.yml          fmt + check -D warnings + test
    ├── ci-static-web.yml    local-asset existence check for HTML
    ├── ci-release.yml       tag → build → SHA256SUMS → Release
    ├── dependabot.yml       5 ecosystems, keep only what exists
    ├── SECURITY.md          scoped-policy skeleton
    └── LICENSE-MIT
```

## Contributing

Run the checks first: `python -m unittest discover -s tests` and the CI
workflow does the same on every push. A PR that turns the repo's own checks
red is doing the opposite of what this skill teaches.

## License

MIT — see [LICENSE](LICENSE).
