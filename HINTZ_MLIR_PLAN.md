# Hintz MLIR Integration Plan

## Goal
Build a reliable pipeline:
1. Hintz frontend IR (`hintzCompiler/src/ir_nodes.py`)
2. -> custom MLIR dialect (`hintz.*`)
3. -> lowered MLIR core/LLVM dialect
4. -> LLVM IR
5. -> native binary

This plan is test-gated. Each step has required tests. A step is marked done only when its tests pass.

---

## Current Baseline (Measured)
- `hintz-mlir-dialect/build && ninja hintz-opt`: passes
- `hintz-opt --show-dialects < /dev/null`: shows `hintz`
- `PYTHONPATH=hintzCompiler pytest -q hintzCompiler/tests`: `87 passed`

## Status Legend
- `[ ]` not started
- `[~]` in progress
- `[x]` completed and verified by tests

---

## Step 0: Baseline Validation
Status: `[x]`

### What this step covers
- Confirm existing repo health before new implementation work.

### Tests/Gates
- `cd hintz-mlir-dialect/build && ninja hintz-opt`
- `hintz-mlir-dialect/build/bin/hintz-opt --show-dialects < /dev/null`
- `cd /home/aakash/WORK/HintzCompiler && PYTHONPATH=hintzCompiler pytest -q hintzCompiler/tests`

---

## Step 1: Dialect Naming + Layout Consistency
Status: `[x]`

### What this step covers
- Make naming consistent across source/tests/tooling so developers do not mix `standalone` vs `hintz`.
- Keep current behavior intact while cleaning interfaces.

### Planned code areas
- `hintz-mlir-dialect/include/Standalone/*.td`
- `hintz-mlir-dialect/lib/Standalone/*`
- `hintz-mlir-dialect/python/*`
- `hintz-mlir-dialect/test/*`

### Required tests
- Add/adjust dialect smoke tests:
  - `hintz-mlir-dialect/test/Standalone/standalone-opt.mlir` (or renamed equivalent)
  - verify checks expect `hintz` textual dialect
- Run:
  - `cd hintz-mlir-dialect/build && ninja hintz-opt check-standalone`

### Exit criteria
- No broken references due to naming mismatch.
- Dialect tests pass with `hintz` namespace expectations.

### Verification run
- `cd hintz-mlir-dialect/build && ninja check-standalone` -> passed (`7/7` tests)
- `hintz-mlir-dialect/build/bin/hintz-opt --show-dialects < /dev/null` -> includes `hintz`
- `cd /home/aakash/WORK/HintzCompiler && PYTHONPATH=hintzCompiler pytest -q hintzCompiler/tests` -> `81 passed`

---

## Step 2: Define Minimal Hintz Dialect Ops for Frontend Mapping
Status: `[~]`

### What this step covers
- Add the smallest useful op set to represent current Hintz IR subset.
- Initial scope:
  - constants
  - variable load/store model
  - arithmetic (`+`, `-`, `*`, `/`)
  - comparison
  - return

### Planned code areas
- `hintz-mlir-dialect/include/Standalone/StandaloneOps.td`
- `hintz-mlir-dialect/lib/Standalone/StandaloneOps.cpp`
- optional type updates in `StandaloneTypes.td`

### Required tests
- New MLIR parser/printer tests in `hintz-mlir-dialect/test/Standalone/*.mlir`
- Validate operation roundtrip (`hintz-opt input | hintz-opt`)
- Run:
  - `cd hintz-mlir-dialect/build && ninja hintz-opt check-standalone`

### Exit criteria
- New ops parse/print and verify correctly.
- Test files demonstrate valid IR examples for each new op.

### Progress notes
- Added ops: `hintz.const`, `hintz.add`, `hintz.return`.
- Added test: `hintz-mlir-dialect/test/Standalone/hintz-ops.mlir`.
- `ninja check-standalone` passes (run outside sandbox due to multiprocessing semaphore permissions).
- Not yet implemented: `load`, `store`, `cmp`, other arithmetic.

---

## Step 3: Hintz IR -> Hintz MLIR Emitter in Frontend Repo
Status: `[~]`

### What this step covers
- Implement emitter from Python Hintz IR nodes to textual `hintz` MLIR module.
- Start with single-function integer programs.

### Planned code areas
- New module: `hintzCompiler/src/mlir_emitter.py`
- CLI wiring in `hintzCompiler/compiler.py` (e.g., `--emit-mlir`)

### Required unit tests
- New tests under `hintzCompiler/tests/`:
  - `test_mlir_emitter_basic.py`
  - `test_mlir_emitter_control_flow.py` (initial minimal if/while subset)
- Assertions:
  - emitted text contains expected `hintz.*` ops
  - deterministic output for fixed input
- Run:
  - `cd /home/aakash/WORK/HintzCompiler && PYTHONPATH=hintzCompiler pytest -q hintzCompiler/tests`

### Exit criteria
- Frontend can emit valid, parseable hintz-MLIR text for the supported subset.

### Progress notes
- CFG-based MLIR emitter added (`hintzCompiler/src/mlir_emitter.py`).
- CLI flag `--emit-mlir` added in `hintzCompiler/compiler.py`.
- Tests added in `hintzCompiler/tests/test_mlir_emitter_basic.py`.
- `PYTHONPATH=hintzCompiler pytest -q hintzCompiler/tests` -> `87 passed`.
- Not yet supported: variables, control flow, function calls, non-`+` ops.

---

## Step 4: Lowering Passes (Hintz Dialect -> Core MLIR Dialects)
Status: `[~]`

### What this step covers
- Implement conversion passes from `hintz` ops to `arith`/`func`/`cf` (and `scf` if needed).
- Keep lowering staged and test each rewrite pattern.

### Planned code areas
- `hintz-mlir-dialect/include/Standalone/StandalonePasses.td`
- `hintz-mlir-dialect/lib/Standalone/StandalonePasses.cpp`
- pass registration in `standalone-opt/standalone-opt.cpp`

### Required tests
- New pass tests in `hintz-mlir-dialect/test/Standalone/*.mlir`:
  - input with `hintz.*`
  - `RUN: hintz-opt ... --convert-hintz-to-... | FileCheck`
- Run:
  - `cd hintz-mlir-dialect/build && ninja check-standalone`

### Exit criteria
- Supported `hintz` ops are fully eliminated after lowering pipeline.
- Resulting IR uses only intended downstream dialects.

### Progress notes
- Added pass `--convert-hintz-to-arith-func` lowering:
  - `hintz.const` -> `arith.constant`
  - `hintz.add` -> `arith.addi`
  - `hintz.return` -> `func.return`
- Added test: `hintz-mlir-dialect/test/Standalone/hintz-lowering.mlir`.
- `ninja check-standalone` passes (run outside sandbox due to multiprocessing semaphore permissions).
- Not yet implemented: lowering for variables, control flow, comparisons, calls.

---

## Step 5: End-to-End Compile to Binary
Status: `[~]`

### What this step covers
- Wire complete script/commands:
  - emit hintz-MLIR
  - lower with `hintz-opt` and/or `mlir-opt`
  - translate to LLVM IR (`mlir-translate`)
  - compile with `clang`

### Planned code areas
- New script: `scripts/hintz_to_bin.sh`
- optional helper docs update in `README.md`

### Required tests
- Add integration test input program(s) in `samples/`
- Add pytest integration test:
  - `hintzCompiler/tests/test_mlir_e2e_binary.py`
  - compile and assert executable exit code/output

### Exit criteria
- One canonical sample compiles and runs end-to-end in local dev environment.

### Progress notes
- Pipeline wired in `hintzCompiler/compiler.py` with:
  - `--emit-hintz-mlir`, `--emit-lowered-mlir`, `--emit-llvm`, `--emit-exe`
  - tool discovery with `tools/` fallback
- Added integration test: `hintzCompiler/tests/test_mlir_pipeline.py` (skips if tools missing).
- Minimal sample (`return 1 + 2;`) compiles to binary and returns exit code `3`.
- Not yet working for real samples with variables/control flow (emitter lacks `load/store`).

---

## Step 6: Expand Feature Coverage + Regression Suite
Status: `[ ]`

### What this step covers
- Broaden support for more IR nodes (if/while/for/calls).
- Lock behavior with regression tests to avoid breakage.

### Required tests
- Add targeted emitter and lowering tests per new IR node family.
- Maintain:
  - `pytest` suite green
  - `check-standalone` green

### Exit criteria
- Every newly supported IR node has:
  - emitter test
  - lowering test
  - at least one end-to-end scenario if semantically meaningful

---

## Execution Rules for This Plan
- Only mark a step `[x]` after all listed tests for that step pass.
- If a test fails, keep step as `[~]` or `[ ]` and log the blocker.
- Prefer small, reviewable commits per step (no large mixed changes).

---

## Known Blockers / Gaps
- No `hintz.load` / `hintz.store` yet, so variables cannot be emitted or lowered.
- No control flow ops (if/while/for) in the dialect or emitter yet.
- No comparison ops or non-`+` arithmetic ops.
- End-to-end pipeline currently only works for constant `return` or `return a + b` where `a/b` are literals.
