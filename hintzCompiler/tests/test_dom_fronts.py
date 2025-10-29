# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import parseAndBuildCompilationContextFromInput
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers


class TestDominanceFrontiers(unittest.TestCase):

    def test_domFronts_basic(self):
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

        cctx = parseAndBuildCompilationContextFromInput(code)
        bbg0 = cctx.bbgs[0]

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB3 ]
BB3 -> DF:[ ]
BB4 -> DF:[ BB3 ]
CFG:
Fcn : main
[0] Declaration: [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Declaration: [Variable(name='out', type_spec='int', attributes={})] -> 2
[2] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 3
[3] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 5, 6
[4] IfJoin() -> 7
[5] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 4
[6] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 4
[7] Assignment(target=VarAccess(name='out'), value=VarAccess(name='x')) -> 8
[8] Return(value=VarAccess(name='out')) ->"""
       
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_domFronts_while_simple(self):
        code = """
        int main(int in) {
            int x;

            x = 0;
            while(x < 5) {
                x = x + 1;
            }
            return x;
        }
        """

        cctx = parseAndBuildCompilationContextFromInput(code)
        bbg0 = cctx.bbgs[0]

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] Declaration: [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 2
[2] While BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x'), right=Literal(value=5.0)) -> 3, 4
[3] Assignment(target=VarAccess(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x'), right=Literal(value=1.0))) -> 2
[4] Return(value=VarAccess(name='x')) ->"""

        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_domFronts_while_simulated(self):
        code = """
        int main(int in) {
            int x;

            x = 0;
            L1:
            if(x < 5) {
                x = x + 1;
                goto L1;
            }
            return x;
        }
        """

        cctx = parseAndBuildCompilationContextFromInput(code)
        bbg0 = cctx.bbgs[0]

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] Declaration: [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 2
[2] Label(name='L1') -> 3
[3] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x'), right=Literal(value=5.0)) -> 5, 4
[4] IfJoin() -> 7
[5] Assignment(target=VarAccess(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x'), right=Literal(value=1.0))) -> 6
[6] Goto(label='L1') -> 2
[7] Return(value=VarAccess(name='x')) ->"""
 
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_do_while(self):
        code = """
        int main(int i, int j) {
        
        i = 24;
        j = 26;
        do {
            i = -1;
            j = -1;
        } while(i < j);
        i = 112;
        j = 123;

        return i;

        }"""

        cctx = parseAndBuildCompilationContextFromInput(code)
        bbg0 = cctx.bbgs[0]

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] Assignment(target=VarAccess(name='i'), value=Literal(value=24.0)) -> 1
[1] Assignment(target=VarAccess(name='j'), value=Literal(value=26.0)) -> 3
[2] DoWhile BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=VarAccess(name='j')) -> 3, 6
[3] DoJoin() -> 4
[4] Assignment(target=VarAccess(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 5
[5] Assignment(target=VarAccess(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 2
[6] Assignment(target=VarAccess(name='i'), value=Literal(value=112.0)) -> 7
[7] Assignment(target=VarAccess(name='j'), value=Literal(value=123.0)) -> 8
[8] Return(value=VarAccess(name='i')) ->"""
 
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_simulated_do_while_(self):
        code = """
        int main(int i, int j) {
        
        i = 24;
        j = 26;
        l1:
            i = -1;
            j = -1;

            if(i < j) {
                goto l1;
            }
            
            i = 112;
            j = 123;

            
            return 0;
        }"""

        cctx = parseAndBuildCompilationContextFromInput(code)
        bbg0 = cctx.bbgs[0]

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] Assignment(target=VarAccess(name='i'), value=Literal(value=24.0)) -> 1
[1] Assignment(target=VarAccess(name='j'), value=Literal(value=26.0)) -> 2
[2] Label(name='l1') -> 3
[3] Assignment(target=VarAccess(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 4
[4] Assignment(target=VarAccess(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 5
[5] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=VarAccess(name='j')) -> 7, 6
[6] IfJoin() -> 8
[7] Goto(label='l1') -> 2
[8] Assignment(target=VarAccess(name='i'), value=Literal(value=112.0)) -> 9
[9] Assignment(target=VarAccess(name='j'), value=Literal(value=123.0)) -> 10
[10] Return(value=Literal(value=0.0)) ->"""
 
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_dom_fronts_for_loop(self):
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

        cctx = parseAndBuildCompilationContextFromInput(code)
        bbg0 = cctx.bbgs[0]
        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] Declaration: [Variable(name='i', type_spec='int', attributes={})] -> 1
[1] Declaration: [Variable(name='j', type_spec='int', attributes={})] -> 2
[2] Assignment(target=VarAccess(name='j'), value=Literal(value=0.0)) -> 3
[3] for(init; cond; update) -> 4
[4] Assignment(target=VarAccess(name='i'), value=Literal(value=0.0)) -> 5
[5] BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=Literal(value=10.0)) -> 6, 8
[6] Assignment(target=VarAccess(name='j'), value=VarAccess(name='i')) -> 7
[7] Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='i'), right=Literal(value=1.0))) -> 5
[8] Return(value=VarAccess(name='j')) ->"""

        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


