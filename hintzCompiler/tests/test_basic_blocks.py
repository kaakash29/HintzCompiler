# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver
from hintzCompiler.src.basic_blocks import BasicBlockGraph

class TestBasicBlockGraph(unittest.TestCase):

    def computeAndEmitBBGForCode(self, code):
        cctx = Driver(code)
        cfgs = cctx.cfgs
        dcfg = cfgs[0]
        bbg  = BasicBlockGraph(dcfg)
        bbgStr = "";
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"\nCFG:\n{dcfg}")
            print(f"\nDFS:{dcfg.get_dfs_traversal_order()}")
            print(f"\nBB-GRAPH:")
            for block in bbg.blocks:
                print(block)
            bbgStr = mock_stdout.getvalue().strip()

        return bbgStr


    #@unittest.skip("Aakash Skipping this test for now")
    def test_basic_blocks_for_simple_if(self):
        code = """
        int main() {
            int x;
            x = 1;
            if (x < 5) {
                x = x + 1;
            }
            return x;
        }"""

        expected = """CFG:
Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 2
[2] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x'), right=Literal(value=5.0)) -> 4, 3
[3] IfJoin() -> 5
[4] Assignment(target=VarAccess(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x'), right=Literal(value=1.0))) -> 3
[5] Return(value=VarAccess(name='x')) ->


DFS:[0, 1, 2, 4, 3, 5]

BB-GRAPH:
BB1: Nodes: [0, 1, 2]  -> BB2, BB3
BB2: Nodes: [4]  -> BB3
BB3: Nodes: [3, 5]  ->"""

        bbgAsStr = self.computeAndEmitBBGForCode(code)
        self.assertIn(expected.strip(), bbgAsStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{bbgAsStr}||")


    def test_basic_blocks_straightline_code(self):
        code = """
        int main() {
            int x;
            x = 1;
            x = 2;
            x = 3;
            return x;
        }"""

        expected = """CFG:
Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 2
[2] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 3
[3] Assignment(target=VarAccess(name='x'), value=Literal(value=3.0)) -> 4
[4] Return(value=VarAccess(name='x')) ->


DFS:[0, 1, 2, 3, 4]

BB-GRAPH:
BB1: Nodes: [0, 1, 2, 3, 4]  ->"""

        bbgAsStr = self.computeAndEmitBBGForCode(code)
        self.assertIn(expected.strip(), bbgAsStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{bbgAsStr}||")


    def test_basic_blocks_whileloop(self):
        code = """
        int main() {
            int i;
            int k;

            i = 0;
            k = 0;
            while(i < 12) {
                k = 1;
                i = i + 1;
                k = 2;
            }

            return k;
        }"""

        expected = """CFG:
Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='k', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=VarAccess(name='i'), value=Literal(value=0.0)) -> 3
[3] Assignment(target=VarAccess(name='k'), value=Literal(value=0.0)) -> 4
[4] While BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=Literal(value=12.0)) -> 5, 8
[5] Assignment(target=VarAccess(name='k'), value=Literal(value=1.0)) -> 6
[6] Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='i'), right=Literal(value=1.0))) -> 7
[7] Assignment(target=VarAccess(name='k'), value=Literal(value=2.0)) -> 4
[8] Return(value=VarAccess(name='k')) ->


DFS:[0, 1, 2, 3, 4, 5, 6, 7, 8]

BB-GRAPH:
BB1: Nodes: [0, 1, 2, 3]  -> BB2
BB2: Nodes: [4]  -> BB3, BB4
BB3: Nodes: [5, 6, 7]  -> BB2
BB4: Nodes: [8]  ->"""
        bbgAsStr = self.computeAndEmitBBGForCode(code)
        self.assertIn(expected.strip(), bbgAsStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{bbgAsStr}||")

    def test_basic_block_for_loop(self):
        code = """
        int main() {
            int i;
            int k;

            k = 0;
            k = 12;

            for(i = 0; i < 25; i++) {
                k = i - 1;
                k = k + 7;
            }

            return k;
        }
        """

        expected = """CFG:
Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='k', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=VarAccess(name='k'), value=Literal(value=0.0)) -> 3
[3] Assignment(target=VarAccess(name='k'), value=Literal(value=12.0)) -> 4
[4] for(init; cond; update) -> 5
[5] Assignment(target=VarAccess(name='i'), value=Literal(value=0.0)) -> 6
[6] BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=Literal(value=25.0)) -> 7, 10
[7] Assignment(target=VarAccess(name='k'), value=BinaryOp(op=Token('SUB_OP', '-'), left=VarAccess(name='i'), right=Literal(value=1.0))) -> 8
[8] Assignment(target=VarAccess(name='k'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='k'), right=Literal(value=7.0))) -> 9
[9] UnaryOp(op=Token('INCREMENT', '++'), operand=VarAccess(name='i'), is_postfix=True) -> 6
[10] Return(value=VarAccess(name='k')) ->


DFS:[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

BB-GRAPH:
BB1: Nodes: [0, 1, 2, 3, 4, 5]  -> BB2
BB2: Nodes: [6]  -> BB3, BB4
BB3: Nodes: [7, 8, 9]  -> BB2
BB4: Nodes: [10]  ->"""
        bbgAsStr = self.computeAndEmitBBGForCode(code)
        self.assertIn(expected.strip(), bbgAsStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{bbgAsStr}||")

    def test_basic_blocks_conditional_jump(self):
        code = """
        int main() {
        
        int i;
        int j;
        int k;

        j = 0;
        k = 0;
        i = 0;
        l1:
            k = k + 1;
            i = i * 3;
            j = j + (k - i);

        if(k < 12) {
            goto l1;
        }

        i = j;
        k = j;

        return j;

        }"""

        expected = """CFG:
Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='j', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='k', type_spec='int', attributes=None)] -> 3
[3] Assignment(target=VarAccess(name='j'), value=Literal(value=0.0)) -> 4
[4] Assignment(target=VarAccess(name='k'), value=Literal(value=0.0)) -> 5
[5] Assignment(target=VarAccess(name='i'), value=Literal(value=0.0)) -> 6
[6] Label(name='l1') -> 7
[7] Assignment(target=VarAccess(name='k'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='k'), right=Literal(value=1.0))) -> 8
[8] Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('MUL_OP', '*'), left=VarAccess(name='i'), right=Literal(value=3.0))) -> 9
[9] Assignment(target=VarAccess(name='j'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='j'), right=Token('LPAR', '('))) -> 10
[10] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='k'), right=Literal(value=12.0)) -> 12, 11
[11] IfJoin() -> 13
[12] Goto(label='l1') -> 11, 6
[13] Assignment(target=VarAccess(name='i'), value=VarAccess(name='j')) -> 14
[14] Assignment(target=VarAccess(name='k'), value=VarAccess(name='j')) -> 15
[15] Return(value=VarAccess(name='j')) ->


DFS:[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 11, 13, 14, 15]

BB-GRAPH:
BB1: Nodes: [0, 1, 2, 3, 4, 5]  -> BB2
BB2: Nodes: [6, 7, 8, 9, 10]  -> BB3, BB4
BB3: Nodes: [12]  -> BB4, BB2
BB4: Nodes: [11, 13, 14, 15]  ->"""

        bbgAsStr = self.computeAndEmitBBGForCode(code)
        self.assertIn(expected.strip(), bbgAsStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{bbgAsStr}||")
