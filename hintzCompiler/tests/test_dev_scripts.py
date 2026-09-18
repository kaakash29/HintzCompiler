"""Exercise bootstrap failure handling and the checkout-local launcher."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from hintzCompiler.compiler import _default_hintz_opt_path, _find_tool

ROOT = Path(__file__).resolve().parents[2]


def test_setup_rejects_conflicting_sdk_options():
    result = subprocess.run(
        [str(ROOT / "scripts/setup-dev.sh"), "--local-llvm", "--llvm-prefix", "/missing"],
        text=True, capture_output=True,
    )
    assert result.returncode != 0
    assert "choose only one" in result.stderr or "cannot be combined" in result.stderr


def test_check_rejects_missing_native_toolchain(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(ROOT / "scripts/check.sh", scripts / "check.sh")
    venv_bin = tmp_path / ".venv/bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "python").symlink_to(sys.executable)
    # This preflight must fail before even attempting to run lit or pytest.
    (venv_bin / "lit").symlink_to(sys.executable)
    result = subprocess.run([str(scripts / "check.sh")], text=True, capture_output=True)
    assert result.returncode != 0
    assert "missing required tool" in result.stderr
    assert "hintz-opt" in result.stderr


@pytest.mark.skipif(
    not (ROOT / ".venv/bin/python").exists()
    or not _find_tool("hintz-opt", None, "HINTZ_OPT", _default_hintz_opt_path()),
    reason="checkout bootstrap required",
)
def test_repo_launcher_compiles_from_another_directory(tmp_path):
    source = tmp_path / "source with spaces.hz"
    source.write_text("int main() { int x; x = 40; return x + 2; }")
    binary = tmp_path / "native program"
    env = os.environ.copy()
    # Prove that activation and inherited Python/tool overrides are unnecessary.
    for key in ("PYTHONPATH", "HINTZ_OPT", "MLIR_OPT", "MLIR_TRANSLATE", "CLANG"):
        env.pop(key, None)
    env["PATH"] = "/usr/bin:/bin"
    result = subprocess.run(
        [str(ROOT / "scripts/hintz"), str(source), "--out", str(binary)],
        cwd=tmp_path, env=env, text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert subprocess.run([str(binary)], check=False).returncode == 42
