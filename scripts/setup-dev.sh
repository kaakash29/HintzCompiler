#!/usr/bin/env bash
# No sudo or system mutations: everything installed here stays in the checkout.
set -euo pipefail
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
fail() { echo "setup-dev: $*" >&2; exit 1; }
usage() {
  cat <<'HELP'
Usage: ./scripts/setup-dev.sh [--local-llvm | --llvm-prefix PATH]

Default: reuse /usr/lib/llvm-19 if installed, otherwise extract the pinned
Ubuntu 24.04 amd64 toolchain into tools/llvm (no sudo required).
--local-llvm        Always use the repository-local, pinned SDK.
--llvm-prefix PATH  Use an existing LLVM/MLIR 19 SDK.

Prerequisites: Python 3.10+ with venv, C/C++ compiler, CMake 3.20+, Ninja,
Graphviz, and network access for first-time dependency downloads.
Set PYTHON_BIN to select Python and BUILD_JOBS to control parallelism (default 2).
HELP
}
mode=auto
sdk_prefix=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --local-llvm)
      [[ "$mode" == auto ]] || fail 'choose only one LLVM option'
      mode=local; shift ;;
    --llvm-prefix)
      [[ "$mode" == auto && $# -ge 2 ]] || fail '--llvm-prefix requires a path and cannot be combined with --local-llvm'
      mode=external; sdk_prefix="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "unknown option: $1 (see --help)" ;;
  esac
done

for tool in cmake ninja cc c++ dot; do
  command -v "$tool" >/dev/null || fail "missing $tool; on Ubuntu install: sudo apt-get install build-essential cmake ninja-build graphviz python3-venv"
done
PYTHON_BIN="${PYTHON_BIN:-python3}"
command -v "$PYTHON_BIN" >/dev/null || fail "Python not found: $PYTHON_BIN"
"$PYTHON_BIN" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ is required"'
if [[ ! -x "${REPO_ROOT}/.venv/bin/python" ]]; then
  "$PYTHON_BIN" -m venv "${REPO_ROOT}/.venv" || fail 'could not create .venv; install python3-venv for your Python version'
fi
# Keep pip's cache local too; no dependency on a writable home directory.
export PIP_CACHE_DIR="${REPO_ROOT}/tools/pip-cache"
"${REPO_ROOT}/.venv/bin/python" -m pip install -r "${REPO_ROOT}/dev/requirements.txt"
"${REPO_ROOT}/.venv/bin/python" -m pip install --no-build-isolation --no-deps -e "${REPO_ROOT}[dev]"

if [[ "$mode" == auto ]]; then
  if [[ -f /usr/lib/llvm-19/lib/cmake/mlir/MLIRConfig.cmake && -x /usr/lib/llvm-19/bin/clang ]]; then
    sdk_prefix=/usr/lib/llvm-19
  else
    mode=local
  fi
fi
if [[ "$mode" == local ]]; then
  for tool in apt-get dpkg-deb dpkg; do
    command -v "$tool" >/dev/null || fail "local SDK download requires $tool; use --llvm-prefix for an existing SDK"
  done
  # These are Ubuntu noble packages, not a portable binary distribution.
  source /etc/os-release
  [[ "${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}" == noble ]] || fail 'local SDK download supports Ubuntu 24.04 / Mint 22; use --llvm-prefix on other systems'
  [[ "$(dpkg --print-architecture)" == amd64 ]] || fail 'local SDK download supports amd64; use --llvm-prefix for another architecture'
  "${REPO_ROOT}/.venv/bin/python" "${REPO_ROOT}/scripts/fetch-llvm.py"
  sdk_prefix="${REPO_ROOT}/tools/llvm/usr/lib/llvm-19"
fi
LLVM_PREFIX="$sdk_prefix" PYTHON_BIN="${REPO_ROOT}/.venv/bin/python" \
  LIT_BIN="${REPO_ROOT}/.venv/bin/lit" bash "${REPO_ROOT}/scripts/build-mlir.sh"
printf '\nSetup complete. Run ./scripts/check.sh, or ./scripts/hintz samples/scalar_pipeline.hz -o /tmp/hintz-scalar\n'
