import sys
import argparse
from lark import Lark, ParseTree
from typing import Optional, List, cast
from hintzCompiler.src.transformer import IRTransformer
from hintzCompiler.preprocessor import Preprocessor
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.ir_nodes import Function, Program
from hintzCompiler.src.symbol_table import SymbolTable
from dataclasses import dataclass
import os


@dataclass
class CompilationContext:
    parseTree: ParseTree
    symbol_table: SymbolTable
    ast: Program
    cfgs: Optional[ List[ControlFlowGraph] ]

"""
Handles the compilation of a simplified compilation unit.
Top level driver for a hypothetical compiler written in python
"""
def Driver(code: str):

    """FRONT-END"""
    # Parse text to ParseTree
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar", "c89.lark")
    with open(grammar_path) as f:
        grammar = f.read()
    parser = Lark(grammar, parser="lalr", start="start")
    tree = parser.parse(code)

    # ParseTree to HintzAst
    transformer = IRTransformer()
    ir = transformer.transform(tree)
    symb_tab = transformer.get_global_symbol_table() 

    # HintzAst to HintzCfgs
    allCfgs = []
    for decl in ir.declarations:
        if isinstance(decl, Function):
            cfg = ControlFlowGraph(cast(Function, decl))
            allCfgs.append(cfg)

    """MIDDLE-END"""

    # may be we want :
    #
    # 1) program level optimizations ?
    # 2) cfg level optimizations ?
    # 3) both (what are we trying to get to?)
    # 4) none (rely solely on the backend optimizations?)

    """BACK-END"""
    # may be lower to a well-supported ir MLIR/LLVM ir ?

    compCtx = CompilationContext(parseTree=tree, symbol_table=symb_tab, ast=ir, cfgs=allCfgs)
    return compCtx

"""
Handles compilation of the provided input files, often includes some include directives.
"""
def processInput(path: str) -> CompilationContext:
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
def main():

    parser = argparse.ArgumentParser(description="Hintz Compiler")
    parser.add_argument("source", help="Path to .hz source file")
    parser.add_argument("-s", "--save-ir", help="Path to write IR output")
    parser.add_argument("-n", "--debug", action="store_true", help="Dump parse tree and symbol table")
    parser.add_argument("--cfg", help="Dump control flow graph HTML", action="store_true")
    args = parser.parse_args()

    try:
        cctx = processInput(args.source)

        parsetree   = cctx.parseTree;
        ir          = cctx.ast;
        symbolTable = cctx.symbol_table;
        cfgs        = cctx.cfgs 

        if args.debug:
            print("=== PARSE TREE ===")
            print(parsetree.pretty())
            print("=== SYMBOL TABLE ===")
            symbolTable.dump()
            
        if args.save_ir:
            with open(args.save_ir, "w") as f:
                f.write("=== IR DUMP ===\n")
                f.write(ir.toString())
                print(f"✅ IR written to {args.save_ir}")
        else:
            print("=== IR DUMP ===")
            ir.dump()

        if args.cfg:
            if len(ir.declarations) == 0 or not isinstance(ir.declarations[0], Function):
                raise ValueError("❌ CFG generation requires a function declaration.")

            for cfg in cfgs:
                print(cfg);
                cfg.to_graphviz(output_path=cfg._fcnName, view=False);

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print(f"❌ Compilation failed: {e}")
        sys.exit(1)

##############################################################################################

if __name__ == "__main__":
    main()
