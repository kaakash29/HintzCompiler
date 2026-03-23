# Architecture Notes

This document provides a high-level map of the compiler’s main components.

## High-Level Modules

- `hintzCompiler/compiler.py`: CLI entrypoint and orchestration.
- `hintzCompiler/src/transformer.py`: AST construction and IR building.
- `hintzCompiler/src/ir_nodes.py`: IR node definitions.
- `hintzCompiler/src/cfg.py`: Control-flow graph construction and utilities.
- `hintzCompiler/src/basic_blocks.py`: Basic block graph construction.
- `hintzCompiler/src/ssaConverter.py`: SSA conversion logic.
- `hintzCompiler/src/ssaDCE.py`: SSA-aware dead code elimination.
- `hintzCompiler/src/readWriteAnalyzer.py`: Read/write analysis.
- `hintzCompiler/src/mlir_emitter.py`: Hintz MLIR emission.
- `hintzCompiler/hintz_web/app.py`: Web testbed UI.

## Common Data Flow

- Parsing and IR construction happen in the frontend.
- CFG/BBG and SSA utilities operate on the IR and its graph structure.
- MLIR emission is a separate step for lowering and external compilation.
