# CI workflows: make them test something real

The CI file is the core artifact of this skill. A stranger's first click is
on the green check; the second is on the workflow behind it. If the workflow
does nothing, trust collapses at the second click.

## Rules for every workflow

- Triggers: `push` to the default branch, `pull_request`, and
  `workflow_dispatch` so it can be run on demand.
- `permissions: contents: read` — least privilege by default. Only widen it
  when a job genuinely needs to write (releases, pages), and scope the
  widening to that job.
- `concurrency: group: ci-${{ github.ref }}, cancel-in-progress: true` —
  stops wasted runs on rapid pushes.
- `timeout-minutes` on every job. A hung job burns minutes and looks broken.
- Pin actions to a major version (`actions/checkout@v4`), and let Dependabot
  carry updates.
- Job names are status check contexts. If branch protection will require a
  check, the job's `name:` must match it exactly. Keep names short and
  stable (`checks`, `test`, `build`).

## Find the real entry points first

Read the project before writing the workflow. The right checks fall out of
the structure:

- Python: `requirements.txt`/`pyproject.toml` → `pip install`, then
  `python -m compileall -q .` plus `python -m unittest discover` or
  `pytest` if tests exist. If `main.py` exists, `py_compile` it explicitly.
- Node: `package.json` scripts → run `typecheck`, `test`, `build` only if
  the script exists in `package.json`; running a nonexistent script fails
  the job for no reason. For scriptless projects, `node --check *.js`.
- Rust: `cargo check` (fast) or `cargo test`; clippy if configured.
- Go: `go build ./...` and `go test ./...`.
- Shell: `shellcheck` via a Action, or `bash -n` as a minimum parse check.
- Web/HTML: verify local assets referenced by `src=`/`href=` exist in the
  repo — a 404 in production is a real bug CI can catch.
- Mixed or unknown: byte-compile/parse everything cheap, plus the project's
  own test command if it has one.

## Baseline template shape

```yaml
name: ci

on:
  push:
    branches: [{{DEFAULT_BRANCH}}]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  checks:
    name: checks
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      # ... language setup ...
      # ... real checks, each with a clear failure mode ...
```

Add a second `runs-on: windows-latest` job only when the project is
Windows-specific (`.ps1` scripts, Windows-only tooling) or its behavior
differs across platforms.

## Verify before pushing

Run locally the exact commands from the workflow steps. Common local-vs-CI
gaps that produce a red first run:

- **Executable bit**: scripts called as `./script.sh` on Linux fail with
  `Permission denied` if committed as `100644`. Fix with
  `git update-index --chmod=+x scripts/run.sh` (and commit that change
  before or together with the workflow).
- **CRLF**: harmless warnings, but a BOM in a shell script is fatal. Write
  workflow and script files as UTF-8 without BOM.
- **Pinned versions**: match the language version to what the project
  actually requires, not the newest available.
- **Missing test dependencies**: `pip install -r requirements.txt` must
  cover imports the tests use, or install them in the workflow explicitly.

## Existing workflow present

Read it. Then either:

- extend it (add a missing job, add `permissions`, add `concurrency`), or
- leave it alone and say so.

Never add a second workflow that duplicates jobs — duplicate checks confuse
the required-contexts configuration and the reader.
