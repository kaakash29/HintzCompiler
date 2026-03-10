// BEGINNER NOTE: This file contains hand-written C++ implementation code for the dialect.
// Generated code is included via .inc files, but this file controls how pieces are wired together.

//===- StandaloneDialect.cpp - Standalone dialect ---------------*- C++ -*-===//
//
// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "Standalone/StandaloneDialect.h"
#include "Standalone/StandaloneOps.h"
#include "Standalone/StandaloneTypes.h"

using namespace mlir;
using namespace mlir::hintz;

#include "Standalone/StandaloneOpsDialect.cpp.inc"

//===----------------------------------------------------------------------===//
// Standalone dialect.
//===----------------------------------------------------------------------===//

// Called once when the dialect is loaded.
// It registers all operation classes and custom types for this dialect.
void StandaloneDialect::initialize() {
  addOperations<
#define GET_OP_LIST
#include "Standalone/StandaloneOps.cpp.inc"
      >();
  registerTypes();
}
