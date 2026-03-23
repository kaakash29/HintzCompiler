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

## Install

From the repo root:

```bash
pip install .
```

If you want graph output (CFG/BBG), install Graphviz system binaries:

```bash
sudo apt-get install graphviz
```

## Quick Start

Compile a Hintz program:

```bash
hintz example.hz -o example.out
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
