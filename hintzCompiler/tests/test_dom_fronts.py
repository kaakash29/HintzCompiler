# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers


class TestDominanceFrontiers(unittest.TestCase):

    def test_domFronts_basic(self):
        code = """
        int main(int in) {
            int x;

            x = 0;
            if(in > 5) {
                x = 1;
            } else {
                x = 2;
            }

            out = x;
            return out;
        }
        """

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 2
[2] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 4, 5
[3] IfJoin() -> 6
[4] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 3
[5] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 3
[6] Assignment(target=VarAccess(name='out'), value=VarAccess(name='x')) -> 7
[7] Return(value=VarAccess(name='out')) ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cctx.cfgs[0].dump()
            self.assertIn(origCfg.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{origCfg.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB3 ]
BB3 -> DF:[ ]
BB4 -> DF:[ BB3 ]
CFG:
Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 2
[2] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 4, 5
[3] IfJoin() -> 8
[4] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 3
[5] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 3
[6] Assignment(target=VarAccess(name='out'), value=VarAccess(name='x')) -> 7
[7] Return(value=VarAccess(name='out')) ->
[8] Assignment(target=VarAccess(name='x'), value=FunctionCall(name='phi', args=[])) -> 6"""


       
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")
