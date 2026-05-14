# Hintz MLIR Integration Plan

## Goal

Build and stabilize this pipeline:

1. Hintz frontend IR (`hintzCompiler/src/ir_nodes.py`)
2. `->` custom Hintz MLIR dialect (`hintz.*`)
3. `->` lowered MLIR core/LLVM dialects
4. `->` LLVM IR
5. `->` native executable

This document is meant to be:

- accurate to the current repo state
- simple to follow
- explicit about what is already done vs what is still missing

---

## Current Reality

The repo has two different levels of completion:

- The Python frontend is substantial and healthy.
- The MLIR/LLVM backend is real, but only supports a minimal subset end-to-end.

Today, the project can:

- parse a meaningful C89-like subset into its own IR
- build CFGs and basic block graphs
- compute dominators and dominance frontiers
- convert IR to SSA
- run SSA-aware DCE
- emit Hintz MLIR for straight-line scalar local-variable programs using:
  - integer literals
  - assignments
  - variable reads
  - `+`
  - `return`
- lower that supported subset to `arith`/`func`/`memref`
- produce a native executable for the canonical tiny sample:
  - `int main() { return 1 + 2; }`
- produce a native executable for simple scalar-local programs such as:
  - `int x; x = 3; return x;`
  - `int x; int y; x = 1; y = x + 2; return y;`

Today, the project still cannot broadly:

- lower most arithmetic beyond `+`
- lower comparisons
- lower control flow (`if`, `while`, `for`, `switch`, `goto`)
- lower function calls
- compile real frontend samples end-to-end to binaries

---

## Status Legend

- `[x]` done and verified
- `[~]` partially done
- `[ ]` not started

---

## Verified Baseline

Current checked state in this repo:

- Frontend tests:
  - `cd /home/aakash/WORK/HintzCompiler`
  - `pytest -q hintzCompiler/tests`
  - Current result: `97 passed`
- Focused pipeline/install tests:
  - `pytest -q hintzCompiler/tests/test_mlir_pipeline.py hintzCompiler/tests/test_install_and_cli.py`
  - Current result: passing when required tools are available
- Focused SSA/DCE regression set:
  - `pytest -q hintzCompiler/tests/test_ssa_dce.py hintzCompiler/tests/test_to_ssa.py`
  - Current result: passing
- Minimal end-to-end native compile:
  - `int main() { return 1 + 2; }`
  - Produces an executable that exits with code `3`
- Straight-line scalar-local end-to-end native compile:
  - `int x; int y; x = 1; y = x + 2; return y;`
  - Produces an executable that exits with code `3`

Important note:

- `samples/exampleOfForLoop.hz` used to crash in SSA DCE due to recursive phi-cycle traversal.
- That frontend bug is now fixed.
- The sample still does not compile end-to-end through MLIR because backend coverage is still too limited.

---

## What Is Already Done

### Step 0: Baseline Validation
Status: `[x]`

Done:

- repo tests are passing
- dialect tool builds
- dialect is visible as `hintz`

Exit criteria: met.

---

### Step 1: Dialect Naming + Layout Consistency
Status: `[x]`

Done:

- textual dialect namespace is `hintz`
- tool name is `hintz-opt`
- dialect tests align with `hintz` naming

Caveat:

- some paths and class names still use `Standalone` because this started from the MLIR standalone template

Exit criteria: met.

---

### Step 2: Minimal Hintz Dialect Ops
Status: `[~]`

Goal of this step:

- define the smallest useful op set that can represent the current frontend subset

Implemented:

- `hintz.const`
- `hintz.add`
- `hintz.alloca`
- `hintz.store`
- `hintz.load`
- `hintz.return`

Verified by:

- dialect parser/printer tests
- lowering tests

Still missing:

- more arithmetic:
  - `-`
  - `*`
  - `/`
- comparisons
- any control-flow-related op set needed by the chosen lowering strategy
- call-related ops if frontend function calls are meant to lower soon

Exit criteria for this step:

- the dialect can represent the current supported straight-line scalar subset, not just the `return 1 + 2;` toy case
- this is now true for:
  - scalar local storage
  - assignments
  - variable reads
  - `+`
  - `return`

Recommended next scope:

1. comparisons
2. `- * /`
3. only then control flow / calls

---

### Step 3: Frontend Hintz IR -> Hintz MLIR Emitter
Status: `[~]`

Goal of this step:

- emit textual `hintz` MLIR from frontend IR

Implemented:

- CLI flag `--emit-mlir`
- emitter module exists
- deterministic emission for the supported straight-line subset

Currently supported by the emitter:

- integer literals
- scalar local assignments
- scalar local variable reads
- binary `+`
- value-returning `return`
- declarations are ignored

Currently not supported by the emitter:

- comparisons
- unary ops
- function calls
- `if`
- `while`
- `do while`
- `for`
- `switch`
- labels / gotos / breaks

Current reality:

- many frontend programs can parse and convert to CFG/SSA
- only a much smaller subset can emit MLIR

Exit criteria for this step:

- the emitter handles the same subset that Step 2 made representable in the dialect

Recommended next scope:

1. arithmetic and comparisons
2. structured control flow
3. calls if needed

---

### Step 4: Lowering Passes (Hintz Dialect -> Core MLIR)
Status: `[~]`

Goal of this step:

- lower `hintz.*` ops into downstream MLIR dialects suitable for LLVM lowering

Implemented:

- `hintz.const` -> `arith.constant`
- `hintz.add` -> `arith.addi`
- `hintz.alloca` -> `memref.alloca`
- `hintz.store` -> `memref.store`
- `hintz.load` -> `memref.load`
- `hintz.return` -> `func.return`

Still missing:

- lowering for other arithmetic ops
- lowering for comparisons
- lowering for control flow
- lowering for calls

Exit criteria for this step:

- all ops emitted by the frontend are fully eliminated by the lowering pipeline
- resulting IR is valid for the downstream `mlir-opt` / `mlir-translate` flow

Important dependency:

- Step 4 should grow in lockstep with Step 2 and Step 3
- do not add frontend-emitted ops without corresponding lowering coverage and tests

---

### Step 5: End-to-End Compile to Binary
Status: `[~]`

Goal of this step:

- make `hintz <file.hz>` work for a meaningful supported subset

What is already done:

- CLI supports:
  - `-h`, `--help`
  - `-v`, `--version`
  - `-o`, `--out`
- default no-flag compile path triggers executable generation
- default executable naming is `./<source>.out` in the caller's current working directory
- tool discovery supports:
  - CLI flags
  - environment variables
  - repo-local `tools/`
  - PATH
- minimal integration test for native executable exists and passes when tools are available
- straight-line scalar-local integration test exists and passes when tools are available

What is not done yet:

- end-to-end support for real sample programs
- broad coverage for loops / branches / calls
- a clearly documented supported source-language subset for backend compilation

Current practical meaning of Step 5:

- complete for the tiny canonical sample
- complete for a narrow straight-line scalar subset
- incomplete for the actual frontend language surface

Exit criteria for this step:

- at least a small but non-trivial supported subset compiles end-to-end reliably
- recommended minimum target:
  - local variables
  - assignments
  - `+ - * /`
  - comparisons
  - `if`
  - `while` or `for`
  - return

Recommended milestone sequence:

1. compile branching programs
2. compile loop programs
3. only then advertise sample-directory coverage

---

### Step 6: Linux Packaging + Installer
Status: `[~]`

This step was previously marked as not started. That is no longer accurate.

Already done:

- `install.sh` exists
- install location can be selected with `--location`
- installer checks for Python and `lark`
- installer checks for `clang`
- installer installs:
  - `hintzCompiler`
  - `hintzlib`
  - bundled tool binaries
- installer creates a `hintz` wrapper script
- install/CLI tests exist and pass

Still left:

- clarify and harden the tool distribution story
- decide what is officially bundled vs externally required
- document Linux install/runtime expectations more clearly
- verify installed workflow once broader backend coverage exists

Current recommendation:

- treat Step 6 as partially complete
- do not spend major effort polishing installation further until backend feature coverage is larger

Exit criteria for this step:

- a fresh Linux install can build the supported subset without manual path surgery
- install docs match reality

---

## Main Remaining Work

If reduced to the real critical path, the project mainly needs:

1. Add comparisons and more arithmetic to the Hintz dialect.
2. Expand the Python MLIR emitter to match that richer expression subset.
3. Add lowering for every newly emitted op.
4. Add structured control flow support.
5. Grow end-to-end tests one supported language feature at a time.
6. Keep docs aligned with the actual supported subset.

---

## Recommended Next Implementation Order

This is the simplest path that keeps the project testable and easy to reason about.

### Phase A: Variables

Status: `[x]`

Implemented:

- variable read/write MLIR model using:
  - `hintz.alloca`
  - `hintz.store`
  - `hintz.load`
- emitter support for:
  - `Assignment`
  - `VarAccess`
- lowering for that model to `memref`
- end-to-end native compile coverage for the narrow scalar-local subset

Add tests for:

- `int x; x = 3; return x;`
- `int x; int y; x = 1; y = x + 2; return y;`

Result:

- done and verified

### Phase B: More Expressions

Implement:

- `-`
- `*`
- `/`
- comparisons

Add tests for:

- arithmetic expression lowering
- comparison-return or comparison-driven control tests

### Phase C: Structured Control Flow

Implement:

- either direct control-flow ops in Hintz dialect, or a structured lowering strategy
- emitter support for:
  - `if`
  - one loop form first:
    - `while` recommended

Add tests for:

- simple `if/else`
- simple counting loop

### Phase D: Broader Coverage

Only after A-C are stable, decide whether to support:

- `for`
- `do while`
- `switch`
- labels / gotos
- function calls
- arrays / structs

These exist in the frontend, but they should not be treated as near-term backend requirements unless there is a clear roadmap for them.

---

## Testing Rules

For each new backend feature:

1. add or update dialect op tests
2. add or update lowering tests
3. add or update frontend emitter tests
4. add or update end-to-end tests
5. then mark progress in this document

Do not mark a step complete just because the code exists.
Mark it complete only when the intended feature subset is covered by tests and works through the pipeline.

---

## Known Constraints And Risks

- The frontend supports more constructs than the backend can lower.
- README-style examples can become misleading if they use unsupported samples.
- Step descriptions drift quickly unless updated after tests are added.
- The best way to avoid confusion is to define a narrow supported backend subset and keep all docs/examples inside that boundary.

---

## Definition Of Success

This plan should be considered successful when:

- the supported backend subset is explicitly defined
- that subset compiles from `.hz` source to working native executable
- the docs only advertise what is actually supported
- new features are added in small, test-gated increments
