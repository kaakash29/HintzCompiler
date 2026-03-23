# CLI Reference

Primary entrypoint:

```bash
hintz <file.hz> [options]
```

## Options

- `--emit-mlir`: print Hintz MLIR to stdout
- `--emit-hintz-mlir`: write `<base>.hintz.mlir`
- `--emit-lowered-mlir`: write `<base>.lowered.mlir`
- `--emit-llvm`: write `<base>.ll`
- `--emit-exe`: build native executable at `<base>`
- `--out <path>`: base output path (default: source path without extension)

### Tool overrides

- `--hintz-opt`
- `--mlir-opt`
- `--mlir-translate`
- `--clang`

## Tool Discovery Order

1. CLI flag (e.g. `--mlir-opt /path/to/mlir-opt`)
2. Environment variable (e.g. `MLIR_OPT`)
3. Repo-local `tools/` directory (e.g. `tools/mlir-opt`)
4. PATH (via `which`)
