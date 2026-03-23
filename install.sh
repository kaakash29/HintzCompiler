#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./install.sh [--location PATH]

Installs the Hintz compiler into the selected location.

Options:
  --location PATH  Installation root (default: ~/.local)
  -h, --help       Show this help text
EOF
}

fail() {
  echo "install.sh: $*" >&2
  exit 1
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LOCATION="${HOME}/.local"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location)
      shift
      [[ $# -gt 0 ]] || fail "--location requires a path"
      LOCATION="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
  shift
done

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi
[[ -n "${PYTHON_BIN}" ]] || fail "python3 is required but was not found on PATH"
[[ -x "${PYTHON_BIN}" ]] || fail "python executable was not found at PYTHON_BIN=${PYTHON_BIN}"
"${PYTHON_BIN}" -c "import lark" >/dev/null 2>&1 || fail "the selected python does not have the 'lark' dependency installed"

CLANG_BIN="${CLANG:-}"
if [[ -n "${CLANG_BIN}" ]]; then
  [[ -x "${CLANG_BIN}" ]] || fail "clang was not found at CLANG=${CLANG_BIN}"
else
  CLANG_BIN="$(command -v clang || true)"
  [[ -n "${CLANG_BIN}" ]] || fail "clang is required for native executable generation but was not found on PATH"
fi

HINTZ_OPT_SRC="${SCRIPT_DIR}/tools/hintz-opt"
if [[ ! -x "${HINTZ_OPT_SRC}" ]]; then
  HINTZ_OPT_SRC="${SCRIPT_DIR}/hintz-mlir-dialect/build/bin/hintz-opt"
fi
[[ -x "${HINTZ_OPT_SRC}" ]] || fail "hintz-opt was not found; build hintz-mlir-dialect first"

[[ -x "${SCRIPT_DIR}/tools/mlir-opt" ]] || fail "tools/mlir-opt is missing or not executable"
[[ -x "${SCRIPT_DIR}/tools/mlir-translate" ]] || fail "tools/mlir-translate is missing or not executable"

BIN_DIR="${LOCATION}/bin"
LIB_DIR="${LOCATION}/lib"
PKG_DIR="${LIB_DIR}/hintzCompiler"
INCLUDES_DIR="${LIB_DIR}/hintzlib"
TOOLS_DIR="${LIB_DIR}/tools"

mkdir -p "${BIN_DIR}" "${LIB_DIR}" "${TOOLS_DIR}"
rm -rf "${PKG_DIR}" "${INCLUDES_DIR}"

cp -R "${SCRIPT_DIR}/hintzCompiler" "${PKG_DIR}"
cp -R "${SCRIPT_DIR}/hintzlib" "${INCLUDES_DIR}"
cp "${SCRIPT_DIR}/tools/mlir-opt" "${TOOLS_DIR}/mlir-opt"
cp "${SCRIPT_DIR}/tools/mlir-translate" "${TOOLS_DIR}/mlir-translate"
cp "${HINTZ_OPT_SRC}" "${TOOLS_DIR}/hintz-opt"

cat > "${BIN_DIR}/hintz" <<EOF
#!/usr/bin/env bash
set -euo pipefail
INSTALL_ROOT="\$(cd -- "\$(dirname -- "\${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="\${INSTALL_ROOT}/lib\${PYTHONPATH:+:\${PYTHONPATH}}"
exec "${PYTHON_BIN}" -m hintzCompiler.compiler "\$@"
EOF
chmod +x "${BIN_DIR}/hintz"

echo "Installed Hintz to ${LOCATION}"
echo "Using host clang at ${CLANG_BIN}"
