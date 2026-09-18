#!/usr/bin/env bash
# Build against an installed LLVM/MLIR 19 SDK (or extracted distro packages).
set -euo pipefail
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${LLVM_PREFIX:-}" ]]; then
  LLVM_PREFIX="${REPO_ROOT}/tools/llvm/usr/lib/llvm-19"
  if [[ ! -d "$LLVM_PREFIX" ]]; then
    LLVM_PREFIX=/usr/lib/llvm-19
  fi
fi
fail() { echo "build-mlir: $*" >&2; exit 1; }
[[ -d "$LLVM_PREFIX" ]] || fail "SDK directory does not exist: $LLVM_PREFIX; run scripts/setup-dev.sh"
LLVM_PREFIX="$(cd -- "${LLVM_PREFIX}" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-${REPO_ROOT}/.venv/bin/python}"
LIT_BIN="${LIT_BIN:-${REPO_ROOT}/.venv/bin/lit}"
for config in mlir/MLIRConfig.cmake llvm/LLVMConfig.cmake; do
  [[ -f "${LLVM_PREFIX}/lib/cmake/${config}" ]] || fail "missing ${config}; install LLVM and MLIR development packages"
done
[[ -x "$PYTHON_BIN" && -x "$LIT_BIN" ]] || fail 'missing Python/lit; run scripts/setup-dev.sh'
for tool in llvm-config mlir-opt mlir-translate clang FileCheck; do
  binary="${LLVM_PREFIX}/bin/${tool}"
  [[ -x "$binary" ]] || fail "missing SDK executable: $binary"
  version="$("$binary" --version)" || fail "cannot run $binary; check missing host shared libraries with ldd"
  [[ "$version" =~ (^|[[:space:]])19\. ]] || fail "$tool must be version 19: $version"
done

cmake -G Ninja -S "${REPO_ROOT}/hintz-mlir-dialect" \
  -B "${REPO_ROOT}/hintz-mlir-dialect/build" \
  -DMLIR_DIR="${LLVM_PREFIX}/lib/cmake/mlir" \
  -DLLVM_DIR="${LLVM_PREFIX}/lib/cmake/llvm" \
  -DLLVM_EXTERNAL_LIT="${LIT_BIN}" \
  -DMLIR_ENABLE_BINDINGS_PYTHON=OFF \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "${REPO_ROOT}/hintz-mlir-dialect/build" -j "${BUILD_JOBS:-2}"

# Wrappers retain the original executable's location, preserving SDK library
# discovery even when install.sh copies these wrappers to an installation.
"${PYTHON_BIN}" - "${REPO_ROOT}" "${LLVM_PREFIX}" <<'PY'
import shlex
import sys
from pathlib import Path

root, prefix = map(Path, sys.argv[1:])
(root / "tools").mkdir(exist_ok=True)
for name in ("mlir-opt", "mlir-translate", "clang"):
    binary = prefix / "bin" / name
    if not binary.is_file():
        raise SystemExit(f"Missing tool: {binary}")
    wrapper = root / "tools" / name
    wrapper.write_text("#!/bin/sh\nexec " + shlex.quote(str(binary)) + ' "$@"\n')
    wrapper.chmod(0o755)
PY
