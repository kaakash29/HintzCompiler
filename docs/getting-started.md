# Getting Started

From a fresh clone on Ubuntu 24.04 / Linux Mint 22 (x86-64):

```bash
./scripts/setup-dev.sh
./scripts/check.sh
./scripts/hintz samples/scalar_pipeline.hz --out /tmp/hintz-scalar
/tmp/hintz-scalar
echo $?  # 42
```

No environment activation is required. See [Building](building.md) for host
prerequisites, SDK selection, repeatable setup and troubleshooting.

To inspect Hintz MLIR without compiling an executable:

```bash
./scripts/hintz --emit-mlir samples/scalar_pipeline.hz
```

The backend currently supports straight-line integer programs; the frontend has
broader language support. See [Pipeline](pipeline.md) for the compilation stages.
