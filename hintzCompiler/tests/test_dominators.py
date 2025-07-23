# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import buildCompilationContext
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.basic_blocks import *


class TestDominators(unittest.TestCase):

    def computeAndEmitDomTree(self, code):
        cctx = buildCompilationContext(code)
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
[0] Declaration: [Variable(name='a', type_spec='int', attributes={})] -> 1
[1] Declaration: [Variable(name='b', type_spec='int', attributes={})] -> 2
[2] Declaration: [Variable(name='c', type_spec='int', attributes={})] -> 3
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

SIMPLE-DOM-RELS:
BB1 -> DOMS:[ BB1 ]
BB2 -> DOMS:[ BB1 BB2 ]
BB3 -> DOMS:[ BB1 BB2 BB3 ]
BB4 -> DOMS:[ BB1 BB2 BB4 ]
BB5 -> DOMS:[ BB1 BB5 ]
BB6 -> DOMS:[ BB1 BB6 ]"""

        domTreeAsStr = self.computeAndEmitDomTree(code)
        strippedActual = domTreeAsStr.replace(" ", "")
        strippedExpected = expected.replace(" ", "")
        self.assertIn(strippedExpected, strippedActual, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}||\nActual:||{domTreeAsStr}||")

    def test_complicated_if_else(self):
        code = """
        int main(int in) {
           int x;
           int out;

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
[0] Declaration: [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Declaration: [Variable(name='out', type_spec='int', attributes={})] -> 2
[2] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='in'), right=Literal(value=0.0)) -> 4, 3
[3] IfJoin() -> 6
[4] Assignment(target=VarAccess(name='x'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 5
[5] Goto(label='skipIf') -> 11
[6] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 7
[7] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 9, 10
[8] IfJoin() -> 11
[9] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 8
[10] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 8
[11] Label(name='skipIf') -> 12
[12] Assignment(target=VarAccess(name='out'), value=VarAccess(name='x')) -> 13
[13] Return(value=VarAccess(name='out')) ->


BB-GRAPH:
BB1: Nodes: [0, 1, 2]  -> BB2, BB4
BB2: Nodes: [4, 5]  -> BB3
BB3: Nodes: [11, 12, 13]  ->
BB4: Nodes: [3, 6, 7]  -> BB5, BB7
BB5: Nodes: [9]  -> BB6
BB6: Nodes: [8]  -> BB3
BB7: Nodes: [10]  -> BB6

DOM-TREE:
1
  2
  3
  4
    5
    6
    7"""
        domTreeAsStr = self.computeAndEmitDomTree(code)
        strippedActual = domTreeAsStr.replace(" ", "")
        strippedExpected = expected.replace(" ", "")
        self.assertIn(strippedExpected, strippedActual, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}||\nActual:||{domTreeAsStr}||")

    def test_dominates_relationships(self):

        code = """
        int main() {
            int l;                    
            double dl;              
            l = 12;                 
            l = l + 1;              
            if (l < 12) {           
                l = 12;             
            } else {                
                l = 24;             
            }                       
            return l;               
        }
        """

        cctx = buildCompilationContext(code)
        bbgs = cctx.bbgs
        doms = Dominators(bbgs[0])
        self.assertTrue(doms.dominates(3, 4))
        self.assertTrue(doms.dominates(0, 8))
        self.assertFalse(doms.dominates(6, 8))


    def test_complicated_if_else(self):
        code = """
        int main() {
            int i;
            int j;

            j = 0;
            for(i = 0; i < 10; i = i + 1) {
                j = i;
            }

            return j;
        }"""

        expected = """CFG:
Fcn : main
[0] Declaration: [Variable(name='i', type_spec='int', attributes={})] -> 1
[1] Declaration: [Variable(name='j', type_spec='int', attributes={})] -> 2
[2] Assignment(target=VarAccess(name='j'), value=Literal(value=0.0)) -> 3
[3] for(init; cond; update) -> 4
[4] Assignment(target=VarAccess(name='i'), value=Literal(value=0.0)) -> 5
[5] BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=Literal(value=10.0)) -> 6, 8
[6] Assignment(target=VarAccess(name='j'), value=VarAccess(name='i')) -> 7
[7] Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='i'), right=Literal(value=1.0))) -> 5
[8] Return(value=VarAccess(name='j')) ->


BB-GRAPH:
BB1: Nodes: [0, 1, 2, 3, 4]  -> BB2
BB2: Nodes: [5]  -> BB3, BB4
BB3: Nodes: [6, 7]  -> BB2
BB4: Nodes: [8]  ->

DOM-TREE:
1
  2
    3
    4

SIMPLE-DOM-RELS:
BB1 -> DOMS:[ BB1 ]
BB2 -> DOMS:[ BB1 BB2 ]
BB3 -> DOMS:[ BB1 BB2 BB3 ]
BB4 -> DOMS:[ BB1 BB2 BB4 ]"""

        domTreeAsStr = self.computeAndEmitDomTree(code)
        strippedActual = domTreeAsStr.replace(" ", "")
        strippedExpected = expected.replace(" ", "")
        self.assertIn(strippedExpected, strippedActual, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}||\nActual:||{domTreeAsStr}||")




