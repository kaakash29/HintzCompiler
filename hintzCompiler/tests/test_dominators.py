# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.basic_blocks import *


class TestDominators(unittest.TestCase):

    def computeAndEmitDomTree(self, code):
        cctx = Driver(code)
        bbgs = cctx.bbgs
        blks = bbgs[0].blocks
        doms = Dominators(blks)
        retn = ""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"\nCFG:\n{cctx.cfgs[0]}")
            print(f"\nBB-GRAPH:")
            for block in bbgs[0].blocks:
                print(block)
            print(f"\nDOM-TREE:")
            doms.dump()
        retn = mock_stdout.getvalue().strip()
        return retn 

    def test_dominators_basic(self):
        code = """
        int main() {
            int a;
            int b;
            int c;

            c = a;
            a = b;
            b = c;
        }
        """

        expected = """BB-GRAPH:
BB1: Nodes: [0, 1, 2, 3, 4, 5]  -> 

DOM-TREE:
1"""
        domTreeAsStr = self.computeAndEmitDomTree(code)
        self.assertIn(expected.strip(), domTreeAsStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}||\nActual:||{domTreeAsStr}||")


    def test_dominators_if_else(self):
        code = """
        int main() {
            int a;
            int b;
            int c;
            a = 0;
            b = 0;
            c = 0;
            if(a < b) {
                c = a;
                if(c > a) {
                    c = b;
                }
            } else {
                a = b;
            }
            b = c;
            return a + b + c;
        }
        """

        expected = """
CFG:
Fcn : main
[0] [Variable(name='a', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='b', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='c', type_spec='int', attributes=None)] -> 3
[3] Assignment(target=Identifier(name='a'), value=Literal(value=0.0)) -> 4
[4] Assignment(target=Identifier(name='b'), value=Literal(value=0.0)) -> 5
[5] Assignment(target=Identifier(name='c'), value=Literal(value=0.0)) -> 6
[6] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='a'), right=Identifier(name='b')) -> 8, 12
[7] IfJoin() -> 13
[8] Assignment(target=Identifier(name='c'), value=Identifier(name='a')) -> 9
[9] If BinaryOp(op=Token('GT_OP', '>'), left=Identifier(name='c'), right=Identifier(name='a')) -> 11, 10
[10] IfJoin() -> 7
[11] Assignment(target=Identifier(name='c'), value=Identifier(name='b')) -> 10
[12] Assignment(target=Identifier(name='a'), value=Identifier(name='b')) -> 7
[13] Assignment(target=Identifier(name='b'), value=Identifier(name='c')) -> 14
[14] Return(value=BinaryOp(op=Token('ADD_OP', '+'), left=BinaryOp(op=Token('ADD_OP', '+'), left=Identifier(name='a'), right=Identifier(name='b')), right=Identifier(name='c'))) ->


BB-GRAPH:
BB1: Nodes: [0, 1, 2, 3, 4, 5, 6]  -> BB2, BB6
BB2: Nodes: [8, 9]  -> BB3, BB4
BB3: Nodes: [11]  -> BB4
BB4: Nodes: [10]  -> BB5
BB5: Nodes: [7, 13, 14]  -> 
BB6: Nodes: [12]  -> BB5

DOM-TREE:
1
  2
    3
    4
  5
  6
"""
        domTreeAsStr = self.computeAndEmitDomTree(code)
        self.assertIn(expected.strip(), domTreeAsStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}||\nActual:||{domTreeAsStr}||")


