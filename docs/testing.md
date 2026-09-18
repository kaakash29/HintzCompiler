# Testing

After `./scripts/setup-dev.sh`, run the full required gates:

```bash
./scripts/check.sh
```

This builds current dialect sources, runs Python and dialect tests, verifies
native compilation (including the installed CLI), and checks a sample executable
returns 42. Missing tools or skipped Python tests cause failure. The optional
MLIR Python-binding smoke test is explicitly disabled for this SDK configuration.
Reports and pipeline artifacts are written to `tools/check-results/`.

For frontend-only development, this narrower command remains available:

```bash
.venv/bin/python -m pytest -q hintzCompiler/tests
```

Some integration tests skip without the native toolchain; this is not equivalent
to the full verification command. See [Building](building.md) for setup details.
