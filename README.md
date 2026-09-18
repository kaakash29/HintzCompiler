# Hintz Compiler

Hintz is a C89-inspired compiler project with a Python frontend and a custom MLIR dialect. The project focuses on a minimal, test-gated subset while the lowering pipeline expands.

## Docs Index

Start here:
- `docs/README.md`

Core docs:
- `docs/getting-started.md`
- `docs/web-testbed.md`
- `docs/cli.md`
- `docs/pipeline.md`
- `docs/architecture.md`
- `docs/ir.md`
- `docs/symbol-table.md`
- `docs/testing.md`

## Fresh checkout

On Ubuntu 24.04 / Linux Mint 22 (x86-64), from the repo root:

```bash
./scripts/setup-dev.sh
./scripts/check.sh
```

Setup creates a local Python environment and builds against LLVM/MLIR 19,
downloading a repository-local SDK if needed. No activation is required.
See [the build guide](docs/building.md) for host prerequisites, SDK selection,
repeatable setup and troubleshooting.

## Quick Start

Compile a Hintz program:

```bash
./scripts/hintz samples/scalar_pipeline.hz -o /tmp/hintz-scalar
/tmp/hintz-scalar
echo $?  # 42
```

## Web Testbed

The web testbed provides an interactive UI to inspect AST, CFG/BBG, dominators, SSA, and MLIR output.

Run it locally:

```bash
./hintzCompiler/hintz_web/run.sh
```

Open the UI at `http://127.0.0.1:5000`.

## License

This project is licensed under the [MIT License](LICENSE).
