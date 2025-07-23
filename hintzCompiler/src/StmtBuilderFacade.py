# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.
import os
from lark import Lark
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.cfg import ControlFlowGraph 
from hintzCompiler.src.transformer import IRTransformer

class HintzStatementBuilder:
    def __init__(self, cfg:ControlFlowGraph):
        grammar_path = os.path.join(os.path.dirname(__file__), "..", "grammar", "c89.lark")
        with open(grammar_path) as f:
            grammar = f.read()
        self.parser = Lark(grammar, start="stmt", parser="lalr", propagate_positions=True)
        self.transformer = IRTransformer()
        self.transformer.symtab_manager.current_scope = cfg.fcn.symbolTable
        self.transformer.decldFcnVars = cfg.fcn.declaredVarsList

    def parse_statement(self, code: str) -> IRNode:
        tree = self.parser.parse(code)
        return self.transformer.transform(tree)

