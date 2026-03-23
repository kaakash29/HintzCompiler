# Web Testbed

The web testbed is a lightweight Flask UI that lets you explore compiler internals in real time.

## Run Locally

```bash
./hintzCompiler/hintz_web/run.sh
```

Open the UI at `http://127.0.0.1:5000`.

## What It Does

- Loads sample Hintz programs from `hintzCompiler/tests` and provides a “Random Sample” button.
- Parses input into a cached compilation context (hash-keyed) to speed up repeated actions.
- Produces textual outputs for AST, R/W analysis, SSA, and MLIR.
- Uses Graphviz `dot` to render CFG/BBG/Dominator graphs into `hintzCompiler/hintz_web/static/cfg.svg`.

## Actions

- `Show AST`: Prints the parsed AST.
- `Show R/W`: Runs read/write analysis on the first function.
- `Show CFG`: Renders the control-flow graph.
- `Show BBG`: Renders the basic block graph.
- `Show DOM`: Renders the dominator tree.
- `Run toSSA`: Converts to SSA and dumps the CFG.
- `Run ssaDCE`: Runs SSA-aware DCE and dumps the CFG.
- `Show MLIR`: Emits Hintz MLIR for the input.

## Dependencies

- Python package: `flask`
- System tool: `dot` (Graphviz)
