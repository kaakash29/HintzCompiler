# Getting Started

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

Emit Hintz MLIR for a sample program:

```bash
hintz --emit-mlir samples/exampleOfForLoop.hz
```

End-to-end binary (minimal example):

```bash
cat > /tmp/hintz_simple.hz <<'EOFSAMPLE'
int main() {
    return 1 + 2;
}
EOFSAMPLE

hintz \
  --emit-hintz-mlir --emit-lowered-mlir --emit-llvm --emit-exe \
  /tmp/hintz_simple.hz

/tmp/hintz_simple
echo $?
```

Expected exit code: `3`
