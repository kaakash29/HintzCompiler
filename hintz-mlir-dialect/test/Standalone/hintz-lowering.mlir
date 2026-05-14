// BEGINNER NOTE: This MLIR test file is input for automated checks of dialect behavior and tooling.
// RUN: hintz-opt %s --convert-hintz-to-arith-func | FileCheck %s

module {
  func.func @main() -> i64 {
    %0 = hintz.alloca : memref<i64>
    %1 = hintz.const 1 : i64
    hintz.store %1, %0 : i64, memref<i64>
    %2 = hintz.load %0 : memref<i64> -> i64
    %3 = hintz.const 2 : i64
    %4 = hintz.add %2, %3 : i64
    hintz.return %4 : i64
  }
}

// CHECK: func.func @main() -> i64 {
// CHECK: %[[SLOT:.*]] = memref.alloca() : memref<i64>
// CHECK: %[[ONE:.*]] = arith.constant 1 : i64
// CHECK: memref.store %[[ONE]], %[[SLOT]][] : memref<i64>
// CHECK: %[[LOAD:.*]] = memref.load %[[SLOT]][] : memref<i64>
// CHECK: %[[TWO:.*]] = arith.constant 2 : i64
// CHECK: %[[SUM:.*]] = arith.addi %[[LOAD]], %[[TWO]] : i64
// CHECK: return %[[SUM]] : i64
// CHECK-NOT: hintz.
