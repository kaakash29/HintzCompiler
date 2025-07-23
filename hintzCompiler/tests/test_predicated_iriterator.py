# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from typing import cast
from io import StringIO
from unittest.mock import patch
from hintzCompiler.compiler import buildCompilationContext
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.PredicatedIRNodeIterator import *

class TestCFG(unittest.TestCase):

    def test_simple_varaccess(self):
        code = """
        int main() {
            int i;
            int j;

            j = 12;
            i = 23 + j;

            return i;

        }
        """
        comp = buildCompilationContext(code)
        ir = comp._ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        expected = """* 1. VarAccess(name='j') at Assignment(target=VarAccess(name='j'), value=Literal(value=12.0))
* 2. VarAccess(name='i') at Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Literal(value=23.0), right=VarAccess(name='j')))
* 3. VarAccess(name='j') at Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Literal(value=23.0), right=VarAccess(name='j')))
* 4. VarAccess(name='i') at Return(value=VarAccess(name='i'))"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            i = 0
            for varAccess in IRNodeIterator(cfg.fcn, lambda n: isinstance(n, VarAccess)):
                i = i + 1
                print(f"* {i}. {varAccess} at {varAccess.rootStmt()}");

            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")



    def test_simple_assignment(self):
        code = """
        int main() {
            int i;
            int j;

            j = 12;
            i = 23 + j;

            return i;

        }
        """
        comp = buildCompilationContext(code)
        ir = comp._ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        expected = """* 1. Assignment(target=VarAccess(name='j'), value=Literal(value=12.0))
* 2. Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Literal(value=23.0), right=VarAccess(name='j')))"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            i = 0
            for varAccess in IRNodeIterator(cfg.fcn, lambda n: isinstance(n, Assignment)):
                i = i + 1
                print(f"* {i}. {varAccess}");

            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


            
