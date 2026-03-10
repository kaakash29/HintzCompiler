// BEGINNER NOTE: This file exposes a small Python extension module that registers the dialect in Python MLIR contexts.
//===- StandaloneExtension.cpp - Extension module -------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "Standalone-c/Dialects.h"
#include "mlir/Bindings/Python/PybindAdaptors.h"

using namespace mlir::python::adaptors;

// Python module entrypoint.
// Exposes helper functions so Python users can register/load the dialect.
PYBIND11_MODULE(_standaloneDialects, m) {
  //===--------------------------------------------------------------------===//
  // hintz dialect
  //===--------------------------------------------------------------------===//
  auto hintzM = m.def_submodule("hintz");

  // This function registers the dialect with a context, and optionally loads it.
  hintzM.def(
      "register_dialect",
      [](MlirContext context, bool load) {
        MlirDialectHandle handle = mlirGetDialectHandle__hintz__();
        mlirDialectHandleRegisterDialect(handle, context);
        if (load) {
          mlirDialectHandleLoadDialect(handle, context);
        }
      },
      py::arg("context") = py::none(), py::arg("load") = true);
}
