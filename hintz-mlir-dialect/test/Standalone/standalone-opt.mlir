// BEGINNER NOTE: This MLIR test file is input for automated checks of dialect behavior and tooling.
// RUN: standalone-opt --show-dialects | FileCheck %s
// CHECK: Available Dialects:
// CHECK-SAME: standalone
