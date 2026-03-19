# Hintz Compiler

Hintz is a C89‑inspired compiler project with a Python frontend and a custom MLIR dialect. The current pipeline is intentionally minimal and focuses on a small, test‑gated subset to keep progress measurable.

Current MLIR support (minimal subset)
- Hintz dialect ops: `hintz.const`, `hintz.add`, `hintz.return`
- Emitter: CFG‑based and emits `i64` everywhere
- Lowering: `hintz.*` -> `arith`/`func` -> LLVM dialect -> LLVM IR -> native binary

---

## Quick Start

### Emit Hintz MLIR
```bash
python -m hintzCompiler.compiler --emit-mlir samples/exampleOfForLoop.hz
```

### End‑to‑end binary (minimal example)
```bash
cat > /tmp/hintz_simple.hz <<'EOFSAMPLE'
int main() {
    return 1 + 2;
}
EOFSAMPLE

python -m hintzCompiler.compiler \
  --emit-hintz-mlir --emit-lowered-mlir --emit-llvm --emit-exe \
  /tmp/hintz_simple.hz

/tmp/hintz_simple
echo $?
```
Expected exit code: `3`

---

## Pipeline Overview

Textual flow
```
Hintz source (.hz)
  -> Hintz IR (Python)
  -> Hintz MLIR (hintz.*)
  -> arith/func MLIR
  -> LLVM dialect MLIR
  -> LLVM IR (.ll)
  -> native executable
```

Command flow
```
python -m hintzCompiler.compiler --emit-hintz-mlir
  -> hintz-opt --convert-hintz-to-arith-func
  -> mlir-opt --convert-arith-to-llvm --convert-func-to-llvm --reconcile-unrealized-casts
  -> mlir-translate --mlir-to-llvmir
  -> clang
```

---

## CLI

Primary entrypoint:
```bash
python -m hintzCompiler.compiler <file.hz> [options]
```

Key options:
- `--emit-mlir`: print Hintz MLIR to stdout
- `--emit-hintz-mlir`: write `<base>.hintz.mlir`
- `--emit-lowered-mlir`: write `<base>.lowered.mlir`
- `--emit-llvm`: write `<base>.ll`
- `--emit-exe`: build native executable at `<base>`
- `--out <path>`: base output path (default: source path without extension)
- Tool overrides:
  - `--hintz-opt`, `--mlir-opt`, `--mlir-translate`, `--clang`

Example with explicit tool paths:
```bash
python -m hintzCompiler.compiler \
  --emit-exe \
  --mlir-opt /path/to/mlir-opt \
  --mlir-translate /path/to/mlir-translate \
  --clang /path/to/clang \
  /tmp/hintz_simple.hz
```

---

## External Tool Dependencies

To produce executables, the compiler shells out to the following tools:

- `hintz-opt` (built from `hintz-mlir-dialect/`)
- `mlir-opt` (from LLVM/MLIR)
- `mlir-translate` (from LLVM/MLIR)
- `clang` (system or LLVM build)

Tool discovery order
1. CLI flag (e.g. `--mlir-opt /path/to/mlir-opt`)
2. Environment variable (e.g. `MLIR_OPT`)
3. Repo‑local `tools/` directory (e.g. `tools/mlir-opt`)
4. PATH (via `which`)

Recommended layout for bundling tools
```
HintzCompiler/
└── tools/
    ├── hintz-opt
    ├── mlir-opt
    ├── mlir-translate
    └── clang
```

---

## Tests

Run all frontend tests:
```bash
PYTHONPATH=hintzCompiler pytest -q hintzCompiler/tests
```

Pipeline integration test:
- Located at `hintzCompiler/tests/test_mlir_pipeline.py`
- Skips automatically if MLIR/LLVM tools are missing

---

## Project Layout (Key Parts)

```
HintzCompiler/
├── hintzCompiler/
│   ├── compiler.py
│   ├── src/
│   │   ├── ir_nodes.py
│   │   ├── cfg.py
│   │   ├── mlir_emitter.py
│   │   └── ...
│   └── tests/
├── hintz-mlir-dialect/
│   ├── include/Standalone/
│   ├── lib/Standalone/
│   ├── test/Standalone/
│   └── build/ (out of tree)
├── samples/
├── HINTZ_MLIR_PLAN.md
└── AI-Context.md
```

---

## Known Limitations (Current)

- MLIR emitter only supports:
  - integer constants
  - binary add (`+`)
  - return
- Variables, control flow, and function calls are not yet lowered to MLIR.

---

## License

This project is licensed under the [MIT License](LICENSE).
