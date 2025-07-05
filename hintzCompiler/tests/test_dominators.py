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
        doms = Dominators(bbgs[0])
        retn = ""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"\nInput:\n{code}")
            print(f"\nCFG:\n{cctx.cfgs[0]}")
            print(f"\nBB-GRAPH:")
            for block in bbgs[0].blocks:
                print(block)
            print(f"\nDOM-TREE:")
            doms.dump()
            print(f"\nSIMPLE-DOM-RELS:")
            doms.dumpSimplifiedDomRels()

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

        expected = """CFG:
Fcn : main
[0] [Variable(name='a', type_spec='int', attributes={})] -> 1
[1] [Variable(name='b', type_spec='int', attributes={})] -> 2
[2] [Variable(name='c', type_spec='int', attributes={})] -> 3
[3] Assignment(target=VarAccess(name='a'), value=Literal(value=0.0)) -> 4
[4] Assignment(target=VarAccess(name='b'), value=Literal(value=0.0)) -> 5
[5] Assignment(target=VarAccess(name='c'), value=Literal(value=0.0)) -> 6
[6] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='a'), right=VarAccess(name='b')) -> 8, 12
[7] IfJoin() -> 13
[8] Assignment(target=VarAccess(name='c'), value=VarAccess(name='a')) -> 9
[9] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='c'), right=VarAccess(name='a')) -> 11, 10
[10] IfJoin() -> 7
[11] Assignment(target=VarAccess(name='c'), value=VarAccess(name='b')) -> 10
[12] Assignment(target=VarAccess(name='a'), value=VarAccess(name='b')) -> 7
[13] Assignment(target=VarAccess(name='b'), value=VarAccess(name='c')) -> 14
[14] Return(value=BinaryOp(op=Token('ADD_OP', '+'), left=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='a'), right=VarAccess(name='b')), right=VarAccess(name='c'))) ->


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
        strippedActual = domTreeAsStr.replace(" ", "")
        strippedExpected = expected.replace(" ", "")
        self.assertIn(strippedExpected, strippedActual, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}||\nActual:||{domTreeAsStr}||")

    def test_complicated_if_else(self):
        code = """
         int main(int in) {
            int x;


            if(in < 0) {
                x = -1;
                goto skipIf;
            }

            x = 0;
            
            if(in > 5) {
                x = 1;
            } else {
                x = 2;
            }

            skipIf:
                out = x;
                return out;
        }       
        """

        expected = """CFG:
Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='in'), right=Literal(value=0.0)) -> 3, 2
[2] IfJoin() -> 5
[3] Assignment(target=VarAccess(name='x'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 4
[4] Goto(label='skipIf') -> 2, 10
[5] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 6
[6] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 8, 9
[7] IfJoin() -> 10
[8] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 7
[9] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 7
[10] Label(name='skipIf') -> 11
[11] Assignment(target=VarAccess(name='out'), value=VarAccess(name='x')) -> 12
[12] Return(value=VarAccess(name='out')) ->


BB-GRAPH:
BB1: Nodes: [0, 1]  -> BB2, BB3
BB2: Nodes: [3, 4]  -> BB3, BB6
BB3: Nodes: [2, 5, 6]  -> BB4, BB7
BB4: Nodes: [8]  -> BB5
BB5: Nodes: [7]  -> BB6
BB6: Nodes: [10, 11, 12]  ->
BB7: Nodes: [9]  -> BB5

DOM-TREE:
1
  2
  3
    4
    5
    7
  6
"""
        domTreeAsStr = self.computeAndEmitDomTree(code)
        strippedActual = domTreeAsStr.replace(" ", "")
        strippedExpected = expected.replace(" ", "")
        self.assertIn(strippedExpected, strippedActual, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}||\nActual:||{domTreeAsStr}||")


