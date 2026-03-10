// BEGINNER NOTE: This MLIR test file is input for automated checks of dialect behavior and tooling.
// RUN: mlir-opt %s --load-dialect-plugin=%standalone_libs/StandalonePlugin%shlibext --pass-pipeline="builtin.module(hintz-switch-bar-foo)" | FileCheck %s

module {
  // CHECK-LABEL: func @foo()
  func.func @bar() {
    return
  }

  // CHECK-LABEL: func @hintz_types(%arg0: !hintz.custom<"10">)
  func.func @hintz_types(%arg0: !hintz.custom<"10">) {
    return
  }
}
