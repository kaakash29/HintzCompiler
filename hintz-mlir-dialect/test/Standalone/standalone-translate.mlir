// BEGINNER NOTE: This MLIR test file is input for automated checks of dialect behavior and tooling.
// RUN: standalone-translate --help | FileCheck %s
// CHECK: --deserialize-spirv
// CHECK: --import-llvm
// CHECK: --mlir-to-llvmir
// CHECK: --serialize-spirv
