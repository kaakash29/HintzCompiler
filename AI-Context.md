# AI Context: HintzCompiler + Hintz MLIR Dialect

## Purpose
This file is a durable handoff context for future Codex sessions so work can continue without re-discovery.

## Repo Layout
- `hintzCompiler/`: Python frontend (parser, IR, CFG, SSA, analyses, web testbed).
- `hintz-mlir-dialect/`: Out-of-tree MLIR dialect project (currently based on standalone template, partially renamed to Hintz).
- `HINTZ_MLIR_PLAN.md`: Stepwise implementation plan with test gates and completion status.

## Current Progress Snapshot
- Step 0 in `HINTZ_MLIR_PLAN.md`: done.
- Step 1 (dialect naming/layout consistency): done and test-verified.
- Steps 2–6: partial. Integer constants, addition and scalar local storage lower
  through MLIR to working native executables; broader language support remains.

## Local Build Verification (2026-09-18)
- Updated checkout to remote revision `dbc0086`.
- LLVM/MLIR 19.1.1 SDK extracted into ignored `tools/llvm/`; Python dependencies
  and editable CLI installed in `.venv/`.
- `scripts/setup-dev.sh` bootstraps the pinned Python environment and LLVM SDK;
  `--local-llvm` forces a repository-local SDK, `--llvm-prefix` selects an existing SDK.
- `scripts/build-mlir.sh` builds the dialect and creates tool wrappers.
- `scripts/hintz` selects the local Python environment and tools without activation.
- `scripts/check.sh` runs all required gates and rejects skipped Python tests.
- Python suite: 103 passed, including native and installed-CLI integration tests.
- Dialect suite: 8 passed; optional MLIR Python-binding test unsupported because
  those bindings are disabled (not required by the native pipeline).
- `samples/scalar_pipeline.hz` compiles through every stage and exits with 42.
- See `docs/building.md` for reproducible setup and remaining backend work.
- `.github/workflows/build.yml` bootstraps a fresh Ubuntu 24.04 checkout, repeats
  setup, and runs the same required gates. Dependencies are pinned in `dev/`.
- Verified setup, repeated setup and all required gates in a separate fresh Git
  clone with no existing venv, SDK or build outputs (2026-09-18). GitHub-hosted CI
  has been added but has not yet run remotely.
- Older machine-specific commands below are historical; use the build guide.

## Verified Baseline Commands
- Frontend unit tests:
  - `cd /home/aakash/WORK/HintzCompiler`
  - `PYTHONPATH=hintzCompiler pytest -q hintzCompiler/tests`
- Dialect tool build:
  - `cd /home/aakash/WORK/HintzCompiler/hintz-mlir-dialect/build`
  - `ninja hintz-opt`
- Dialect visibility:
  - `./bin/hintz-opt --show-dialects < /dev/null`
  - Expected to include: `hintz`
- Dialect regression tests:
  - `cd /home/aakash/WORK/HintzCompiler/hintz-mlir-dialect/build`
  - `ninja check-standalone`
  - Note: in restricted sandboxes this may need elevated permissions due to Python multiprocessing semaphore behavior in `llvm-lit`.

## Web Testbed Status (`hintzCompiler/hintz_web`)
- Added random sample loader:
  - Endpoint: `GET /random-sample`
  - Source: extracts `code = """..."""` and `code = '''...'''` snippets from `hintzCompiler/tests/test_*.py`.
  - UI button in `templates/index.html`: `🎲 Random Sample`.
- Added Read/Write analysis action:
  - UI button: `Show R/W`.
  - Action key: `rwa`.
  - Uses `ReadWriteAnalyzer` output and renders in textual output pane.
- Button styling improved:
  - Uniform size and consistent appearance in `.actions` row.

## Files Introduced Recently
- `HINTZ_MLIR_PLAN.md` (implementation plan with gated steps).
- `AI-Context.md` (this file).
- `hintzCompiler/tests/test_web_samples.py` (web sample + endpoint + R/W action tests).
- `hintz-mlir-dialect/python/mlir_standalone/dialects/hintz.py` (python dialect binding module).

## Important Naming State (Do Not Regress)
- Tool binary: `hintz-opt`.
- Textual dialect namespace: `hintz` (e.g., `hintz.foo`).
- Some paths/class names still contain `Standalone` (template ancestry) but semantic behavior is now Hintz-oriented.
- Backward-compatibility shim exists:
  - `python/mlir_standalone/dialects/standalone.py` re-exports `hintz`.

## Fish Shell Convenience (User Environment)
User has fish aliases configured in `~/.config/fish/config.fish`:
- `hintz-mlir-build` -> builds `hintz-opt`.
- `hintz-tests` -> runs frontend unit tests.
- Homebrew shellenv loaded in fish.

## What to Do Next (Recommended)
1. Extend the partial stages in `HINTZ_MLIR_PLAN.md` together: dialect operations,
   frontend emission, lowering and executable integration tests.
2. Implement control flow/SSA joins, function calls/parameters, additional
   operators and type/ABI handling beyond the current straight-line i64 subset.
3. Keep both the Python and dialect test gates passing; do not mark partial
   stages complete solely because the minimal end-to-end pipeline works.

## Working Rules From User
- Do not push commits automatically; user controls pushes.
- Keep plan/test-gated workflow:
  - implement step,
  - add/adjust tests,
  - run tests,
  - only then mark step done in `HINTZ_MLIR_PLAN.md`.

## Quick Session Restart Checklist
1. `cd /home/aakash/WORK/HintzCompiler`
2. Run frontend tests.
3. Build `hintz-opt`.
4. Run `hintz-opt --show-dialects`.
5. Open `HINTZ_MLIR_PLAN.md` and continue from first `[ ]` step.
