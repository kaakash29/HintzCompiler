# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import os
import sys
import argparse
from typing import List, cast
from lark import Lark, ParseTree
from dataclasses import dataclass
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.preprocessor import Preprocessor
from hintzCompiler.src.symbol_table import SymbolTable
from hintzCompiler.src.transformer import IRTransformer
from hintzCompiler.src.ir_nodes import Function, Program
from hintzCompiler.src.basic_blocks import BasicBlockGraph

from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.ssaConverter import SSAConverter
from hintzCompiler.src.ssaDCE import SSAAwareDeadCodeElimination
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers


##############################################################################################

@dataclass
class CompilationContext:
    _parseTree: ParseTree
    _ast: Program
    cfgs: List[ControlFlowGraph]
    bbgs: List[BasicBlockGraph]
    symbolTableGlobalScope: SymbolTable

##############################################################################################

"""
Parses the preprocessed-input program with Lark based grammar, and builds SymbolTables,
ControlFlowGraph and BasicBlocksGraphs for all functions in the input. Wraps all the info
into a CompilationContext object and returns it.
"""
def parseAndBuildCompilationContextFromInput(code):
    # Text to ParseTree
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar", "c89.lark")
    with open(grammar_path) as f:
        grammar = f.read()
    parser = Lark(grammar, parser="lalr", start="start")
    tree = parser.parse(code)

    # ParseTree to HintzAst
    transformer = IRTransformer()
    ir = transformer.transform(tree)

    # HintzAst to Cfgs/Bbgs
    allCfgs = []
    allBbgs = []
    for decl in ir.declarations:
        if isinstance(decl, Function):
            fcn = cast(Function, decl)
            cfg = ControlFlowGraph(fcn)
            bbg = BasicBlockGraph(cfg)
            allCfgs.append(cfg)
            allBbgs.append(bbg)

    compCtx = CompilationContext(_parseTree=tree, _ast=ir, cfgs=allCfgs, bbgs=allBbgs, symbolTableGlobalScope=transformer.symtab_manager.global_scope)
    return compCtx


"""
Handles the compilation of a simplified compilation unit.
Top level driver for a hypothetical compiler written in python
"""
def Driver(code: str):

    """FRONT-END"""

    compCtx = parseAndBuildCompilationContextFromInput(code)



    """MIDDLE-END"""

    # 1) cfg level optimizations ?
    for aCfg, aBfg in zip(compCtx.cfgs, compCtx.bbgs):

        doms  = Dominators(aBfg)
        domFs = DominanceFrontiers(doms)

        toSSA = SSAConverter(domFs)
        toSSA.doit()

        ssaDce = SSAAwareDeadCodeElimination(aCfg)
        ssaDce.doit()

        #ssaPe = SSAAwareDataFlowPeepholeEngine(aCfg)
        #ssaPe.doit()

    # may be we want :
    # 2) program level optimizations ?
    # 3) both (what are we trying to get to?)
    # 4) none (rely solely on the backend optimizations?)



    """BACK-END"""

    # may be lower to a well-supported ir MLIR/LLVM ir ?
    # toVM = convertToVM(compCtx)
    # toVM.doit()

    return compCtx

##############################################################################################

"""
Handles compilation of the provided input files, often includes some include directives.
"""
def compile(path: str) -> CompilationContext: #pragma: no cover
    if not path.endswith(".hz"):
        raise ValueError(f"❌ Only .hz files are supported: {path}")

    fullIncludePath = os.path.join(os.path.dirname(__file__), "..", "includes") 
    preprocessor = Preprocessor(include_paths=[fullIncludePath])
    code = preprocessor.preprocess(path)
    cctx = Driver(code)
    return cctx

##############################################################################################

"""
Main function for the Hintz Compiler
"""
def main(): #pragma: no cover

    parser = argparse.ArgumentParser(description="Hintz Compiler")
    parser.add_argument("-a", "--dumpAstToFile"     , action="store_true"   , help="Path to write IR output")
    parser.add_argument("-s", "--dumpSymbolTable"   , action="store_true"   , help="Dump symbol table for debugging")
    parser.add_argument("-p", "--dumpParseTree"     , action="store_true"   , help="Dump parse tree for debugging")
    parser.add_argument("-c", "--dumpCfgs"          , action="store_true"   , help="Dump control flow graph")
    parser.add_argument("source"                                            , help="Path to input .hz (hintz) source file")
    args = parser.parse_args()

    try:
        cctx = compile(args.source)

        parsetree   = cctx._parseTree;
        ir          = cctx._ast;
        cfgs        = cctx.cfgs 
        globalScope = cctx.symbolTableGlobalScope

        if args.dumpParseTree:
            print("\n=== PARSE-TREE ===\n")
            print(parsetree.pretty())
            
        if args.dumpAstToFile:
            print("\n=== AST-DUMP ===\n")
            ir.dump()

        if args.dumpSymbolTable:
            print("\n=== SYMBOL-TABLE ===\n")
            globalScope.dumpDownwards()

        if args.dumpCfgs:
            print(f"\n=== INITIAL CFG-DUMP ===\n")
            if len(ir.declarations) == 0 or not isinstance(ir.declarations[0], Function):
                raise ValueError("\n❌ CFG generation requires a function declaration.\n")
            
            for cfg in cfgs:
                print(cfg);
                cfg.to_graphviz(output_path=cfg._fcnName, view=False);

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print(f"\n❌ Compilation failed: {e}\n")
        sys.exit(1)

##############################################################################################

if __name__ == "__main__":
    main()
