import sys
import argparse
from lark import Lark
from hintzCompiler.src.transformer import IRTransformer
from hintzCompiler.preprocessor import Preprocessor
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.ir_nodes import Function
from typing import cast

import os


def compile_source(code: str, debug=False):

    grammar_path = os.path.join(os.path.dirname(__file__), "grammar", "c89.lark")
    with open(grammar_path) as f:
        grammar = f.read()

    parser = Lark(grammar, parser="lalr", start="start")
    
    tree = parser.parse(code)

    if debug:
        print("=== PARSE TREE ===")
        print(tree.pretty())

    transformer = IRTransformer()
    ir = transformer.transform(tree)

    if debug:
        print("=== SYMBOL TABLE ===")
        transformer.get_global_symbol_table().dump()

    return ir


def compile_file(path: str, debug=False):
    if not path.endswith(".hz"):
        raise ValueError(f"❌ Only .hz files are supported: {path}")
    fullIncludePath = os.path.join(os.path.dirname(__file__), "..", "includes") 
    preprocessor = Preprocessor(include_paths=[fullIncludePath])
    code = preprocessor.preprocess(path)
    return compile_source(code, debug=debug)


def main():
    parser = argparse.ArgumentParser(description="Hintz Compiler")
    parser.add_argument("source", help="Path to .hz source file")
    parser.add_argument("-s", "--save-ir", help="Path to write IR output")
    parser.add_argument("-n", "--debug", action="store_true", help="Dump parse tree and symbol table")
    parser.add_argument("--cfg", help="Dump control flow graph HTML", action="store_true")
    
    args = parser.parse_args()

    try:
        ir = compile_file(args.source, debug=args.debug)

        if args.save_ir:
            with open(args.save_ir, "w") as f:
                f.write("=== IR DUMP ===\n")
                f.write(ir.to_string())
            print(f"✅ IR written to {args.save_ir}")
        else:
            print("=== IR DUMP ===")
            ir.dump()

        if args.cfg:

            if len(ir.declarations) == 0 or not isinstance(ir.declarations[0], Function):
                raise ValueError("❌ CFG generation requires a function declaration.")

            for decl in ir.declarations:
                if isinstance(decl, Function):
                    cfg = ControlFlowGraph(cast(Function, decl))
                    cfg.dump();
                    print(cfg);
                    cfg.to_graphviz(output_path=cfg._fcnName, view=False);

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print(f"❌ Compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
