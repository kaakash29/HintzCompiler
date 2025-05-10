import sys
from lark import Lark
from src.transformer import IRTransformer

def compile_source(code: str, dump_tree=False):
    """Compile code from a string. Returns IR."""
    with open("grammar/c89.lark") as f:
        grammar = f.read()

    parser = Lark(grammar, parser="lalr", start="start")
    tree = parser.parse(code)

    if dump_tree:
        print("=== PARSE TREE ===")
        print(tree.pretty())

    transformer = IRTransformer()
    ir = transformer.transform(tree)

    if dump_tree:
        print("\n=== SYMBOL TABLE ===")
        transformer.get_global_symbol_table().dump()  # Optional if you attach it

    return ir

def compile_file(path: str, dump_tree=False):
    with open(path) as f:
        code = f.read()
    return compile_source(code, dump_tree=dump_tree)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source-file.c89> [--dump-tree]")
        sys.exit(1)

    path = sys.argv[1]
    dump_tree = "--dump-tree" in sys.argv

    try:
        ir = compile_file(path, dump_tree=dump_tree)
        
        print("=== IR DUMP ===")
        ir.dump()
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        sys.exit(1)
