#!/usr/bin/env bash
# Full required gates: never silently skip native pipeline integration tests.
set -euo pipefail
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
fail() { echo "check: $*" >&2; exit 1; }
export PATH="${REPO_ROOT}/tools:${REPO_ROOT}/.venv/bin:${PATH}"
export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/hintzCompiler"
export PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
export HINTZ_OPT="${REPO_ROOT}/hintz-mlir-dialect/build/bin/hintz-opt"
export MLIR_OPT="${REPO_ROOT}/tools/mlir-opt"
export MLIR_TRANSLATE="${REPO_ROOT}/tools/mlir-translate"
export CLANG="${REPO_ROOT}/tools/clang"
[[ -x "$PYTHON_BIN" && -x "${REPO_ROOT}/.venv/bin/lit" ]] || fail 'run ./scripts/setup-dev.sh first'
for tool in "$HINTZ_OPT" "$MLIR_OPT" "$MLIR_TRANSLATE" "$CLANG"; do
  [[ -x "$tool" ]] || fail "missing required tool: $tool; run ./scripts/setup-dev.sh"
  "$tool" --version >/dev/null || fail "cannot run $tool; rerun setup and check host shared libraries"
done
command -v dot >/dev/null || fail 'Graphviz dot is required; install graphviz'

results="${REPO_ROOT}/tools/check-results"
mkdir -p "$results"
# Rebuild first, so edits to the dialect cannot be tested against stale binaries.
cmake --build hintz-mlir-dialect/build -j "${BUILD_JOBS:-2}"
"$PYTHON_BIN" -m pytest -q hintzCompiler/tests --junitxml="$results/pytest.xml"
"$PYTHON_BIN" - "$results/pytest.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
cases = list(root.iter("testcase"))
if not cases or any(case.find("skipped") is not None for case in cases):
    raise SystemExit("Required Python tests were missing or skipped; the full pipeline gate failed.")
PY
"${REPO_ROOT}/.venv/bin/lit" -sv hintz-mlir-dialect/build/test -o "$results/lit.json"
"$PYTHON_BIN" - "$results/lit.json" <<'PY'
import json
import sys
from pathlib import Path
results = json.loads(Path(sys.argv[1]).read_text())["tests"]
passed = 0
for test in results:
    if test["code"] == "PASS":
        passed += 1
    elif test["code"] == "UNSUPPORTED" and test["name"].endswith("python/smoketest.py"):
        print("Optional MLIR Python bindings: disabled (not needed for the native pipeline).")
    else:
        raise SystemExit(f"Unexpected dialect test result: {test['name']}: {test['code']}")
if not passed:
    raise SystemExit("No dialect tests ran.")
PY

"${REPO_ROOT}/scripts/hintz" --emit-hintz-mlir --emit-lowered-mlir \
  --emit-llvm --emit-exe --out "$results/scalar" samples/scalar_pipeline.hz
"$PYTHON_BIN" - "$results/scalar" <<'PY'
import subprocess
import sys
from pathlib import Path
binary = Path(sys.argv[1])
for suffix in (".hintz.mlir", ".lowered.mlir", ".llvm.mlir", ".ll", ""):
    artifact = Path(str(binary) + suffix)
    if not artifact.is_file() or not artifact.stat().st_size:
        raise SystemExit(f"Missing or empty pipeline artifact: {artifact}")
code = subprocess.run([str(binary)], check=False).returncode
if code != 42:
    raise SystemExit(f"Native executable returned {code}; expected 42")
print("End-to-end native executable returned 42.")
PY
printf '\nAll required checks passed. Reports and pipeline artifacts: %s\n' "$results"
