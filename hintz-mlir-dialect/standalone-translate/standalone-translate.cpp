// BEGINNER NOTE: This tool entrypoint registers translation callbacks for conversion experiments.
//===- standalone-translate.cpp ---------------------------------*- C++ -*-===//
//
// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// This is a command line utility that translates a file from/to MLIR using one
// of the registered translations.
//
//===----------------------------------------------------------------------===//

#include "Standalone/StandaloneDialect.h"
#include "mlir/IR/DialectRegistry.h"
#include "mlir/IR/Operation.h"
#include "mlir/InitAllTranslations.h"
#include "mlir/Support/LogicalResult.h"
#include "mlir/Tools/mlir-translate/MlirTranslateMain.h"
#include "mlir/Tools/mlir-translate/Translation.h"
#include "llvm/Support/raw_ostream.h"

// This is the main entrypoint for the translation tool.
// It registers translation handlers and then runs mlir-translate.
int main(int argc, char **argv) {
  mlir::registerAllTranslations();

  // TODO: Register standalone translations here.
  // This callback is a placeholder translation body for demonstration.
  // It currently succeeds without changing output.
  mlir::TranslateFromMLIRRegistration withdescription(
      "option", "different from option",
      [](mlir::Operation *op, llvm::raw_ostream &output) {
        return mlir::LogicalResult::success();
      },
      [](mlir::DialectRegistry &a) {});

  return failed(
      mlir::mlirTranslateMain(argc, argv, "MLIR Translation Testing Tool"));
}
