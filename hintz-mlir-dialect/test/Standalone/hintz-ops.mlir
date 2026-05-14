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

    // CHECK-LABEL: func.func @scalar_slot_roundtrip() -> i64
    func.func @scalar_slot_roundtrip() -> i64 {
        // CHECK: %[[SLOT:.*]] = hintz.alloca : memref<i64>
        %slot = hintz.alloca : memref<i64>
        // CHECK: %[[VALUE:.*]] = hintz.const 9 : i64
        %value = hintz.const 9 : i64
        // CHECK: hintz.store %[[VALUE]], %[[SLOT]] : i64, memref<i64>
        hintz.store %value, %slot : i64, memref<i64>
        // CHECK: %[[LOAD:.*]] = hintz.load %[[SLOT]] : memref<i64> -> i64
        %load = hintz.load %slot : memref<i64> -> i64
        // CHECK: hintz.return %[[LOAD]] : i64
        hintz.return %load : i64
    }
}
