// BEGINNER NOTE: This MLIR test file is input for automated checks of dialect behavior and tooling.
// RUN: hintz-opt %s | hintz-opt | FileCheck %s

module {
    // CHECK-LABEL: func.func @const_add_return() -> i64
    func.func @const_add_return() -> i64 {
        // CHECK: %[[C0:.*]] = hintz.const 40 : i64
        %c0 = hintz.const 40 : i64
        // CHECK: %[[C1:.*]] = hintz.const 2 : i64
        %c1 = hintz.const 2 : i64
        // CHECK: %[[SUM:.*]] = hintz.add %[[C0]], %[[C1]] : i64
        %sum = hintz.add %c0, %c1 : i64
        // CHECK: hintz.return %[[SUM]] : i64
        hintz.return %sum : i64
    }
}
