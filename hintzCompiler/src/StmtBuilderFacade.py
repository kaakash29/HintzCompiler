from lark import Lark
from hintzCompiler.src.transformer import IRTransformer
from hintzCompiler.src.ir_nodes import IRNode

class HintzStatementBuilder:
    def __init__(self):
        grammar_path = "../hintzCompiler/grammar/c89.lark"
        with open(grammar_path) as f:
            grammar = f.read()
        self.parser = Lark(grammar, start="stmt", parser="lalr", propagate_positions=True)
        self.transformer = IRTransformer()

    def parse_statement(self, code: str) -> IRNode:
        tree = self.parser.parse(code)
        return self.transformer.transform(tree)

