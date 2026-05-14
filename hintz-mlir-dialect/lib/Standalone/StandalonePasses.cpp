// BEGINNER NOTE: This file contains hand-written C++ implementation code for the dialect.
// Generated code is included via .inc files, but this file controls how pieces are wired together.
//===- StandalonePasses.cpp - Standalone passes -----------------*- C++ -*-===//
//
// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
#include "mlir/Dialect/Arith/IR/Arith.h"
#include "mlir/Dialect/Func/IR/FuncOps.h"
#include "mlir/Dialect/MemRef/IR/MemRef.h"
#include "mlir/IR/DialectRegistry.h"
#include "mlir/IR/PatternMatch.h"
#include "mlir/Rewrite/FrozenRewritePatternSet.h"
#include "mlir/Support/LogicalResult.h"
#include "mlir/Transforms/GreedyPatternRewriteDriver.h"

#include "Standalone/StandaloneOps.h"
#include "Standalone/StandalonePasses.h"

namespace mlir::hintz {
#define GEN_PASS_DEF_STANDALONESWITCHBARFOO
#define GEN_PASS_DEF_STANDALONECONVERTHINTZTOARITHFUNC
#include "Standalone/StandalonePasses.h.inc"

namespace {
class StandaloneSwitchBarFooRewriter : public OpRewritePattern<func::FuncOp> {
public:
  using OpRewritePattern<func::FuncOp>::OpRewritePattern;
  // Looks for a function named "bar" and renames it to "foo".
  // Returns success only when a rename actually happened.
  LogicalResult matchAndRewrite(func::FuncOp op,
                                PatternRewriter &rewriter) const final {
    if (op.getSymName() == "bar") {
      rewriter.modifyOpInPlace(op, [&op]() { op.setSymName("foo"); });
      return success();
    }
    return failure();
  }
};

class StandaloneSwitchBarFoo
    : public impl::StandaloneSwitchBarFooBase<StandaloneSwitchBarFoo> {
public:
  using impl::StandaloneSwitchBarFooBase<
      StandaloneSwitchBarFoo>::StandaloneSwitchBarFooBase;
  // This is the pass body.
  // It applies the rewriter patterns to the current operation/module.
  void runOnOperation() final {
    RewritePatternSet patterns(&getContext());
    patterns.add<StandaloneSwitchBarFooRewriter>(&getContext());
    FrozenRewritePatternSet patternSet(std::move(patterns));
    if (failed(applyPatternsAndFoldGreedily(getOperation(), patternSet)))
      signalPassFailure();
  }
};

class HintzConstLowering : public OpRewritePattern<ConstOp> {
public:
  using OpRewritePattern<ConstOp>::OpRewritePattern;
  LogicalResult matchAndRewrite(ConstOp op,
                                PatternRewriter &rewriter) const final {
    rewriter.replaceOpWithNewOp<arith::ConstantOp>(op, op.getValueAttr());
    return success();
  }
};

class HintzAddLowering : public OpRewritePattern<AddOp> {
public:
  using OpRewritePattern<AddOp>::OpRewritePattern;
  LogicalResult matchAndRewrite(AddOp op,
                                PatternRewriter &rewriter) const final {
    rewriter.replaceOpWithNewOp<arith::AddIOp>(op, op.getLhs(), op.getRhs());
    return success();
  }
};

class HintzAllocaLowering : public OpRewritePattern<AllocaOp> {
public:
  using OpRewritePattern<AllocaOp>::OpRewritePattern;
  LogicalResult matchAndRewrite(AllocaOp op,
                                PatternRewriter &rewriter) const final {
    rewriter.replaceOpWithNewOp<memref::AllocaOp>(op, op.getSlot().getType());
    return success();
  }
};

class HintzStoreLowering : public OpRewritePattern<StoreOp> {
public:
  using OpRewritePattern<StoreOp>::OpRewritePattern;
  LogicalResult matchAndRewrite(StoreOp op,
                                PatternRewriter &rewriter) const final {
    rewriter.replaceOpWithNewOp<memref::StoreOp>(op, op.getValue(), op.getSlot(),
                                                 ValueRange{});
    return success();
  }
};

class HintzLoadLowering : public OpRewritePattern<LoadOp> {
public:
  using OpRewritePattern<LoadOp>::OpRewritePattern;
  LogicalResult matchAndRewrite(LoadOp op,
                                PatternRewriter &rewriter) const final {
    rewriter.replaceOpWithNewOp<memref::LoadOp>(op, op.getSlot(), ValueRange{});
    return success();
  }
};

class HintzReturnLowering : public OpRewritePattern<ReturnOp> {
public:
  using OpRewritePattern<ReturnOp>::OpRewritePattern;
  LogicalResult matchAndRewrite(ReturnOp op,
                                PatternRewriter &rewriter) const final {
    rewriter.replaceOpWithNewOp<func::ReturnOp>(op, op.getValue());
    return success();
  }
};

class StandaloneConvertHintzToArithFunc
    : public impl::StandaloneConvertHintzToArithFuncBase<
          StandaloneConvertHintzToArithFunc> {
public:
  using impl::StandaloneConvertHintzToArithFuncBase<
      StandaloneConvertHintzToArithFunc>::StandaloneConvertHintzToArithFuncBase;

  void getDependentDialects(DialectRegistry &registry) const override {
    registry.insert<arith::ArithDialect, func::FuncDialect,
                    memref::MemRefDialect>();
  }

  void runOnOperation() final {
    RewritePatternSet patterns(&getContext());
    patterns.add<HintzConstLowering, HintzAddLowering, HintzAllocaLowering,
                 HintzStoreLowering, HintzLoadLowering, HintzReturnLowering>(
        &getContext());
    FrozenRewritePatternSet patternSet(std::move(patterns));
    if (failed(applyPatternsAndFoldGreedily(getOperation(), patternSet)))
      signalPassFailure();
  }
};
} // namespace
} // namespace mlir::hintz
