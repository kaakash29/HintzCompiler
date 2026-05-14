// BEGINNER NOTE: This TableGen file is a blueprint. MLIR generates C++ code from it during build.
//===- StandaloneOps.td - Standalone dialect ops -----------*- tablegen -*-===//
//
// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef STANDALONE_OPS
#define STANDALONE_OPS

include "Standalone/StandaloneTypes.td"
include "mlir/Interfaces/InferTypeOpInterface.td"
include "mlir/Interfaces/SideEffectInterfaces.td"

def Standalone_FooOp : Standalone_Op<"foo", [Pure,
                                             SameOperandsAndResultType]> {
    let summary = "Illustrates how to define an operation.";
    let description = [{
        The `hintz.foo` operation illustrates how to define a new
        operation in a dialect. It uses an operation trait to declare that it
        has no side effects.

        This operation takes an integer argument and returns an integer.

        Example:

        ```mlir
        %0 = arith.constant 2 : i32
        // Apply the foo operation to %0
        %1 = hintz.foo %0 : i32
        ```
    }];

    let arguments = (ins I32:$input);
    let results = (outs I32:$res);

    let assemblyFormat = [{
        $input attr-dict `:` type($input)
    }];
}

def Standalone_ConstOp : Standalone_Op<"const", [Pure]> {
    let summary = "Integer constant";
    let description = [{
        Produces an integer constant value.
    }];

    let arguments = (ins I64Attr:$value);
    let results = (outs I64:$result);

    let assemblyFormat = "$value attr-dict `:` type($result)";
}

def Standalone_AddOp : Standalone_Op<"add", [Pure, SameOperandsAndResultType]> {
    let summary = "Integer add";
    let description = [{
        Adds two integers.
    }];

    let arguments = (ins I64:$lhs, I64:$rhs);
    let results = (outs I64:$result);

    let assemblyFormat = "$lhs `,` $rhs attr-dict `:` type($lhs)";
}

def Standalone_AllocaOp : Standalone_Op<"alloca"> {
    let summary = "Allocate storage for one scalar variable slot";
    let description = [{
        Produces a stack slot that can hold a single integer value.
    }];

    let results = (outs AnyMemRef:$slot);

    let assemblyFormat = "attr-dict `:` type($slot)";
}

def Standalone_StoreOp : Standalone_Op<"store"> {
    let summary = "Store an integer into a scalar variable slot";
    let description = [{
        Writes an integer value into a slot produced by `hintz.alloca`.
    }];

    let arguments = (ins I64:$value, AnyMemRef:$slot);
    let results = (outs);

    let assemblyFormat = "$value `,` $slot attr-dict `:` type($value) `,` type($slot)";
}

def Standalone_LoadOp : Standalone_Op<"load"> {
    let summary = "Load an integer from a scalar variable slot";
    let description = [{
        Reads an integer value from a slot produced by `hintz.alloca`.
    }];

    let arguments = (ins AnyMemRef:$slot);
    let results = (outs I64:$result);

    let assemblyFormat = "$slot attr-dict `:` type($slot) `->` type($result)";
}

def Standalone_ReturnOp : Standalone_Op<"return", [Terminator]> {
    let summary = "Return from function";
    let description = [{
        Returns a single integer value from a function.
    }];

    let arguments = (ins I64:$value);
    let results = (outs);

    let assemblyFormat = "$value attr-dict `:` type($value)";
}

#endif // STANDALONE_OPS
