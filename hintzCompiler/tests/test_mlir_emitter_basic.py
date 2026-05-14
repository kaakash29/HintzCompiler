from tests.assert_utils import assertContains

from hintzCompiler.compiler import parseAndBuildCompilationContextFromInput
from hintzCompiler.src.mlir_emitter import emit_mlir


def test_emit_mlir_const_add_return():
    code = """
    int main() {
        return 40 + 2;
    }
    """
    cctx = parseAndBuildCompilationContextFromInput(code)
    mlir = emit_mlir(cctx)
    expected = """
    module {
        func.func @main() -> i64 {
            %0 = hintz.const 40 : i64
            %1 = hintz.const 2 : i64
            %2 = hintz.add %0, %1 : i64
            hintz.return %2 : i64
        }
    }
    """
    assertContains(mlir, expected)


def test_emit_mlir_return_literal():
    code = """
    int main() {
        return 7;
    }
    """
    cctx = parseAndBuildCompilationContextFromInput(code)
    mlir = emit_mlir(cctx)
    expected = """
    module {
        func.func @main() -> i64 {
            %0 = hintz.const 7 : i64
            hintz.return %0 : i64
        }
    }
    """
    assertContains(mlir, expected)


def test_emit_mlir_ignores_declarations():
    code = """
    int main() {
        int x;
        return 3 + 4;
    }
    """
    cctx = parseAndBuildCompilationContextFromInput(code)
    mlir = emit_mlir(cctx)
    expected = """
    module {
        func.func @main() -> i64 {
            %0 = hintz.const 3 : i64
            %1 = hintz.const 4 : i64
            %2 = hintz.add %0, %1 : i64
            hintz.return %2 : i64
        }
    }
    """
    assertContains(mlir, expected)


def test_emit_mlir_scalar_assignment_and_return():
    code = """
    int main() {
        int x;
        x = 3;
        return x;
    }
    """
    cctx = parseAndBuildCompilationContextFromInput(code)
    mlir = emit_mlir(cctx)
    expected = """
    module {
        func.func @main() -> i64 {
            %0 = hintz.const 3 : i64
            %1 = hintz.alloca : memref<i64>
            hintz.store %0, %1 : i64, memref<i64>
            %2 = hintz.load %1 : memref<i64> -> i64
            hintz.return %2 : i64
        }
    }
    """
    assertContains(mlir, expected)


def test_emit_mlir_scalar_variable_chain():
    code = """
    int main() {
        int x;
        int y;
        x = 1;
        y = x + 2;
        return y;
    }
    """
    cctx = parseAndBuildCompilationContextFromInput(code)
    mlir = emit_mlir(cctx)
    expected = """
    module {
        func.func @main() -> i64 {
            %0 = hintz.const 1 : i64
            %1 = hintz.alloca : memref<i64>
            hintz.store %0, %1 : i64, memref<i64>
            %2 = hintz.load %1 : memref<i64> -> i64
            %3 = hintz.const 2 : i64
            %4 = hintz.add %2, %3 : i64
            %5 = hintz.alloca : memref<i64>
            hintz.store %4, %5 : i64, memref<i64>
            %6 = hintz.load %5 : memref<i64> -> i64
            hintz.return %6 : i64
        }
    }
    """
    assertContains(mlir, expected)
