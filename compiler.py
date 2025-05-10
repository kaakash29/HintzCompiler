import sys
import argparse
from lark import Lark
from src.transformer import IRTransformer

def compile_source(code: str, debug=False):
    with open("grammar/c89.lark") as f:
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
    with open(path) as f:
        code = f.read()
    return compile_source(code, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hintz Compiler")
    parser.add_argument("source", help="Path to .hz source file")
    parser.add_argument("-s", "--save-ir", help="Path to write IR output")
    parser.add_argument("-n", "--debug", action="store_true", help="Dump parse tree and symbol table")

    args = parser.parse_args()

    try:
        ir = compile_file(args.source, debug=args.debug)

        if args.save_ir:
            with open(args.save_ir, "w") as f:
                f.write("=== IR DUMP ===\n")
                f.write(ir.to_string() if hasattr(ir, "to_string") else str(ir))
            print(f"✅ IR written to {args.save_ir}")
        else:
            print("=== IR DUMP ===")
            ir.dump()

    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        sys.exit(1)
