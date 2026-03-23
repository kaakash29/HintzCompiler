import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

import pytest

from hintzCompiler import __version__
from hintzCompiler.compiler import _default_hintz_opt_path, _find_tool


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SCRIPT = REPO_ROOT / "install.sh"


def _pipeline_ready() -> bool:
    hintz_opt = _find_tool("hintz-opt", None, "HINTZ_OPT", _default_hintz_opt_path())
    mlir_opt = _find_tool("mlir-opt", None, "MLIR_OPT")
    mlir_translate = _find_tool("mlir-translate", None, "MLIR_TRANSLATE")
    clang = _find_tool("clang", None, "CLANG")
    return all([hintz_opt, mlir_opt, mlir_translate, clang])


def _write_simple_program(path: Path) -> None:
    path.write_text(
        """
        int main() {
            return 1 + 2;
        }
        """,
        encoding="utf-8",
    )


def _run_install(location: Path, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
    cmd = ["/bin/bash", str(INSTALL_SCRIPT), "--location", str(location)]
    run_env = os.environ.copy() if env is None else env.copy()
    run_env.setdefault("PYTHON_BIN", sys.executable)
    return subprocess.run(
        cmd,
        check=False,
        cwd=str(REPO_ROOT),
        env=run_env,
        text=True,
        capture_output=True,
    )


def test_cli_version_flag():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "hintzCompiler.compiler", "--version"],
        check=False,
        text=True,
        capture_output=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == f"hintz {__version__}"


def test_cli_help_groups_main_options_first():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "hintzCompiler.compiler", "--help"],
        check=False,
        text=True,
        capture_output=True,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode == 0
    help_text = result.stdout
    assert "main options:" in help_text
    assert "pipeline options:" in help_text
    assert "tool overrides:" in help_text
    assert "debug options:" in help_text
    assert help_text.index("main options:") < help_text.index("pipeline options:")
    assert help_text.index("pipeline options:") < help_text.index("tool overrides:")
    assert help_text.index("tool overrides:") < help_text.index("debug options:")
    assert "-h, --help" in help_text
    assert "-v, --version" in help_text
    assert "-o OUT, --out OUT" in help_text


@pytest.mark.skipif(not _pipeline_ready(), reason="MLIR/LLVM tools not found")
def test_cli_defaults_to_simple_out_in_cwd(tmp_path):
    source_dir = tmp_path / "source"
    work_dir = tmp_path / "work"
    source_dir.mkdir()
    work_dir.mkdir()

    source = source_dir / "simple.hz"
    _write_simple_program(source)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    cmd = [sys.executable, "-m", "hintzCompiler.compiler", str(source)]
    result = subprocess.run(cmd, check=False, cwd=str(work_dir), env=env)

    exe_path = work_dir / "simple.out"
    assert result.returncode == 0
    assert exe_path.exists()
    run_result = subprocess.run([str(exe_path)], check=False)
    assert run_result.returncode == 3


def test_install_script_requires_clang(tmp_path):
    location = tmp_path / "install"
    env = os.environ.copy()
    env["CLANG"] = str(tmp_path / "missing-clang")

    result = _run_install(location, env=env)

    assert result.returncode != 0
    assert "clang" in result.stderr


def test_install_script_copies_runtime(tmp_path):
    location = tmp_path / "install"
    result = _run_install(location, env=os.environ.copy())

    assert result.returncode == 0, result.stderr
    assert (location / "bin" / "hintz").exists()
    assert (location / "lib" / "hintzCompiler" / "compiler.py").exists()
    assert (location / "lib" / "hintzlib").exists()
    assert (location / "lib" / "tools" / "hintz-opt").exists()
    assert (location / "lib" / "tools" / "mlir-opt").exists()
    assert (location / "lib" / "tools" / "mlir-translate").exists()


def test_installed_hintz_help_and_version(tmp_path):
    location = tmp_path / "install"
    install_result = _run_install(location, env=os.environ.copy())
    assert install_result.returncode == 0, install_result.stderr

    hintz_bin = location / "bin" / "hintz"

    help_result = subprocess.run(
        [str(hintz_bin), "--help"],
        check=False,
        text=True,
        capture_output=True,
    )
    version_result = subprocess.run(
        [str(hintz_bin), "--version"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert help_result.returncode == 0
    assert "Hintz Compiler" in help_result.stdout
    assert version_result.returncode == 0
    assert version_result.stdout.strip() == f"hintz {__version__}"


@pytest.mark.skipif(not _pipeline_ready(), reason="MLIR/LLVM tools not found")
def test_installed_hintz_builds_simple_out_in_cwd(tmp_path):
    location = tmp_path / "install"
    install_result = _run_install(location, env=os.environ.copy())
    assert install_result.returncode == 0, install_result.stderr

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    source = work_dir / "simple.hz"
    _write_simple_program(source)

    hintz_bin = location / "bin" / "hintz"
    build_result = subprocess.run([str(hintz_bin), str(source)], check=False, cwd=str(work_dir))

    exe_path = work_dir / "simple.out"
    assert build_result.returncode == 0
    assert exe_path.exists()
    run_result = subprocess.run([str(exe_path)], check=False)
    assert run_result.returncode == 3
