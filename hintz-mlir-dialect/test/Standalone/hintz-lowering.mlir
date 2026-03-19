// BEGINNER NOTE: This MLIR test file is input for automated checks of dialect behavior and tooling.
// RUN: hintz-opt %s --convert-hintz-to-arith-func | FileCheck %s

module {
  func.func @main() -> i64 {
    %0 = hintz.const 1 : i64
    %1 = hintz.const 2 : i64
    %2 = hintz.add %0, %1 : i64
    hintz.return %2 : i64
  }
}

// CHECK: func.func @main() -> i64 {
// CHECK: %[[C:.*]] = arith.constant 3 : i64
// CHECK: return %[[C]] : i64
// CHECK-NOT: hintz.
