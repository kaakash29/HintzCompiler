import os
import subprocess
import sys

import pytest

from hintzCompiler.compiler import _find_tool, _default_hintz_opt_path


def _have_pipeline_tools() -> bool:
    hintz_opt = _find_tool("hintz-opt", None, "HINTZ_OPT", _default_hintz_opt_path())
    mlir_opt = _find_tool("mlir-opt", None, "MLIR_OPT")
    mlir_translate = _find_tool("mlir-translate", None, "MLIR_TRANSLATE")
    clang = _find_tool("clang", None, "CLANG")
    return all([hintz_opt, mlir_opt, mlir_translate, clang])


@pytest.mark.skipif(not _have_pipeline_tools(), reason="MLIR/LLVM tools not found")
def test_mlir_pipeline_to_exe(tmp_path):
    source = tmp_path / "simple.hz"
    source.write_text(
        """
        int main() {
            return 1 + 2;
        }
        """,
        encoding="utf-8",
    )

    out_base = tmp_path / "simple"
    cmd = [
        sys.executable,
        "-m",
        "hintzCompiler.compiler",
        "--emit-exe",
        "--emit-llvm",
        "--emit-lowered-mlir",
        "--emit-hintz-mlir",
        "--out",
        str(out_base),
        str(source),
    ]
    subprocess.run(cmd, check=True)

    exe_path = str(out_base)
    assert os.path.exists(exe_path)

    result = subprocess.run([exe_path], check=False)
    assert result.returncode == 3
