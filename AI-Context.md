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
- Step 2+ (new dialect op set + frontend emitter + lowering + end-to-end binary): pending.

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
1. Execute Step 2 from `HINTZ_MLIR_PLAN.md`:
   - Define minimal op set in `StandaloneOps.td` for frontend mapping.
   - Add dialect parser/printer tests for each new op.
   - Gate: `ninja check-standalone`.
2. Execute Step 3:
   - Add `hintzCompiler/src/mlir_emitter.py`.
   - Add CLI flag in `hintzCompiler/compiler.py` to emit hintz-MLIR text.
   - Add unit tests for emitter output.

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
