# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.compiler import Driver
from hintzCompiler.src.cfg import *
from hintzCompiler.src.StmtBuilderFacade import HintzStatementBuilder

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

        nodeAsTest = "i = 12;";
        newNode = HintzStatementBuilder().parse_statement(nodeAsTest)

        newCfgNode = CFGNode(id=cfg.stmt_id, stmt=newNode)
        cfg.stmt_id += 1

        #insert after 0
        nodeBefore = cfg.nodes[0]
        
        for succNode in nodeBefore.successors:
            newCfgNode.add_successor(succNode)

        nodeBefore.successors = [newCfgNode]
        newCfgNode.add_predecessor(nodeBefore)
        cfg.nodes.append(newCfgNode)
     
        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[1] Assignment(target=Identifier(name='i'), value=Literal(value=23.0)) ->
[2] Assignment(target=Identifier(name='i'), value=Literal(value=12.0)) -> 1"""

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

        #delete node 1 
        nodeToDelete = cfg.nodes[1]

        for predNode in nodeToDelete.predecessors:
            predNode.successors = nodeToDelete.successors

        for succNode in nodeToDelete.successors:
            succNode.predecessors = nodeToDelete.predecessors

        cfg.nodes.remove(nodeToDelete)

        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")
