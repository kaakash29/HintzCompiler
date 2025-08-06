# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.ssaConverter import SSAConverter
from hintzCompiler.compiler import buildCompilationContext
from hintzCompiler.src.ssaDCE import SSAAwareDeadCodeElimination
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers


class TestSSADce(unittest.TestCase):

    def cfgToString(self, cfg:ControlFlowGraph) -> str:
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            return mock_stdout.getvalue().strip()

    def test_dce_basic(self):
        code = """
        int main(int in) {
            int x;
            int out;

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

        expected = """Fcn : main
[0] Declaration: [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Declaration: [Variable(name='out', type_spec='int', attributes={})] -> 3
[3] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 5, 6
[4] IfJoin() -> 9
[5] Assignment(target=VarAccess(name='x2'), value=Literal(value=1.0)) -> 4
[6] Assignment(target=VarAccess(name='x4'), value=Literal(value=2.0)) -> 4
[7] Assignment(target=VarAccess(name='out1'), value=VarAccess(name='x3')) -> 8
[8] Return(value=VarAccess(name='out1')) ->
[9] Assignment(target=VarAccess(name='x3'), value=FunctionCall(name='phi', args=[VarAccess(name='x2'), VarAccess(name='x4')])) -> 7"""

        cctx  = buildCompilationContext(code)

        bbg0  = cctx.bbgs[0]
        doms  = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)

        toSSA = SSAConverter(domFs)
        toSSA.doit()

        ssaDce = SSAAwareDeadCodeElimination(cctx.cfgs[0])
        ssaDce.doit()

        cfgStr = self.cfgToString(cctx.cfgs[0])
        self.assertIn(expected.strip(), cfgStr, msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{cfgStr}||")

    def test_dce_basic_make_ifs_empty(self):
        code = """
        int main(int in) {
            int x;
            int out;

            x = 0;
            if(in > 5) {
                x = 1;
            } else {
                x = 2;
            }

            out = 23;
            return out;
        }
        """

        cctx  = buildCompilationContext(code)

        expected = """Fcn : main
[0] Declaration: [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Declaration: [Variable(name='out', type_spec='int', attributes={})] -> 3
[3] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 4
[4] IfJoin() -> 7
[7] Assignment(target=VarAccess(name='out1'), value=Literal(value=23.0)) -> 8
[8] Return(value=VarAccess(name='out1')) ->"""

        bbg0  = cctx.bbgs[0]
        doms  = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)

        toSSA = SSAConverter(domFs)
        toSSA.doit()

        ssaDce = SSAAwareDeadCodeElimination(cctx.cfgs[0])
        ssaDce.doit()

        cfgStr = self.cfgToString(cctx.cfgs[0])
        self.assertIn(expected.strip(), cfgStr, msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{cfgStr}||")

