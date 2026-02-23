# BEGINNER NOTE: This is a Python smoke test that checks Python bindings can parse/print the dialect.
# RUN: %python %s | FileCheck %s

# This smoke test validates that Python can register the dialect
# and parse/print a tiny module that uses one dialect op.
from mlir_standalone.ir import *
from mlir_standalone.dialects import builtin as builtin_d, standalone as standalone_d

with Context():
    standalone_d.register_dialect()
    module = Module.parse(
        """
    %0 = arith.constant 2 : i32
    %1 = standalone.foo %0 : i32
    """
    )
    # CHECK: %[[C:.*]] = arith.constant 2 : i32
    # CHECK: standalone.foo %[[C]] : i32
    print(str(module))
