// BEGINNER NOTE: This MLIR test file is input for automated checks of dialect behavior and tooling.
// RUN: hintz-opt %s | hintz-opt | FileCheck %s

module {
    // CHECK-LABEL: func @bar()
    func.func @bar() {
        %0 = arith.constant 1 : i32
        // CHECK: %{{.*}} = hintz.foo %{{.*}} : i32
        %res = hintz.foo %0 : i32
        return
    }

    // CHECK-LABEL: func @hintz_types(%arg0: !hintz.custom<"10">)
    func.func @hintz_types(%arg0: !hintz.custom<"10">) {
        return
    }
}
