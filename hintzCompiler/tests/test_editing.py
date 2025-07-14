# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.compiler import Driver
from hintzCompiler.src.cfg import *
from hintzCompiler.src.StmtBuilderFacade import HintzStatementBuilder
from hintzCompiler.src.EditCfg import EditCfg

class TestEditingCFG(unittest.TestCase):

    # we need cfg editing APIs for what is being done here.

    def test_insert_simple_assignment(self):
        code = """
        int main() {
            int i;
            i = 23;
        }
        """
        ir = Driver(code)
        cfg = ir.cfgs[0]

        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='i'), value=Literal(value=23.0)) ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


        nodeAsText = "i = 12;";
        newAstNode = HintzStatementBuilder(cfg).parse_statement(nodeAsText)
        newCfgNode = CFGNode(id=cfg.stmt_id, stmt=newAstNode)
        EditCfg.addNodeAfter(cfg, 0, newCfgNode)

        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes={})] -> 2
[1] Assignment(target=VarAccess(name='i'), value=Literal(value=23.0)) ->
[2] Assignment(target=VarAccess(name='i'), value=Literal(value=12.0)) -> 1"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_simple_removal(self):
        code = """
        int main() {
            int i;
            i = 23;
        }
        """
        ir = Driver(code)
        cfg = ir.cfgs[0]
        EditCfg.deleteNode(cfg, 1)
        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes={})] ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")
