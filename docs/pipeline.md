# Pipeline Overview

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

## External Tool Dependencies

To produce executables, the compiler shells out to the following tools:

- `hintz-opt` (built from `hintz-mlir-dialect/`)
- `mlir-opt` (from LLVM/MLIR)
- `mlir-translate` (from LLVM/MLIR)
- `clang` (system or LLVM build)

Tool discovery order
1. CLI flag (e.g. `--mlir-opt /path/to/mlir-opt`)
2. Environment variable (e.g. `MLIR_OPT`)
3. Repo-local `tools/` directory (e.g. `tools/mlir-opt`)
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
