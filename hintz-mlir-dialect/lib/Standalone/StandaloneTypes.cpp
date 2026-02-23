// BEGINNER NOTE: This file contains hand-written C++ implementation code for the dialect.
// Generated code is included via .inc files, but this file controls how pieces are wired together.
//===- StandaloneTypes.cpp - Standalone dialect types -----------*- C++ -*-===//
//
// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "Standalone/StandaloneTypes.h"

#include "Standalone/StandaloneDialect.h"
#include "mlir/IR/Builders.h"
#include "mlir/IR/DialectImplementation.h"
#include "llvm/ADT/TypeSwitch.h"

using namespace mlir::hintz;

#define GET_TYPEDEF_CLASSES
#include "Standalone/StandaloneOpsTypes.cpp.inc"

// Called during dialect initialization.
// It registers every custom type declared for this dialect.
void StandaloneDialect::registerTypes() {
  addTypes<
#define GET_TYPEDEF_LIST
#include "Standalone/StandaloneOpsTypes.cpp.inc"
      >();
}
