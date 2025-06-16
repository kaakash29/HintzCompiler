# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver
from hintzCompiler.src.basic_blocks import BasicBlockGraph

class TestBasicBlockGraph(unittest.TestCase):

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
[1] Assignment(target=Identifier(name='x'), value=Literal(value=1.0)) -> 2
[2] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='x'), right=Literal(value=5.0)) -> 4, 3
[3] IfJoin() -> 5
[4] Assignment(target=Identifier(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Identifier(name='x'), right=Literal(value=1.0))) -> 3
[5] Return(value=Identifier(name='x')) ->


DFS:[0, 1, 2, 4, 3, 5]

BB-GRAPH:
BB1: Nodes: [0, 1, 2]  -> BB2, BB3
BB2: Nodes: [4]  -> BB3
BB3: Nodes: [3, 5]  ->"""

        cctx = Driver(code)
        cfgs = cctx.cfgs
        bbg  = BasicBlockGraph()
        dcfg = cfgs[0]
        self.assertTrue(dcfg is not None)
        bbg.build_basic_blocks_from_cfg(cfgs[0])
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"\nCFG:\n{dcfg}")
            print(f"\nDFS:{dcfg.get_dfs_traversal_order()}")
            print(f"\nBB-GRAPH:")
            for block in bbg.blocks:
                print(block)

            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{mock_stdout.getvalue().strip()}||")

if __name__ == "__main__":
    unittest.main()

