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

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] [Variable(name='out', type_spec='int', attributes={})] -> 2
[2] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 3
[3] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 5, 6
[4] IfJoin() -> 7
[5] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 4
[6] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 4
[7] Assignment(target=VarAccess(name='out'), value=VarAccess(name='x')) -> 8
[8] Return(value=VarAccess(name='out')) ->"""

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
[1] [Variable(name='out', type_spec='int', attributes={})] -> 2
[2] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 3
[3] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 5, 6
[4] IfJoin() -> 9
[5] Assignment(target=VarAccess(name='x'), value=Literal(value=1.0)) -> 4
[6] Assignment(target=VarAccess(name='x'), value=Literal(value=2.0)) -> 4
[7] Assignment(target=VarAccess(name='out'), value=VarAccess(name='x')) -> 8
[8] Return(value=VarAccess(name='out')) ->
[9] Assignment(target=VarAccess(name='x'), value=FunctionCall(name='phi', args=[])) -> 7"""
       
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

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 2
[2] While BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x'), right=Literal(value=5.0)) -> 3, 4
[3] Assignment(target=VarAccess(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x'), right=Literal(value=1.0))) -> 2
[4] Return(value=VarAccess(name='x')) ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cctx.cfgs[0].dump()
            self.assertIn(origCfg.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{origCfg.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 5
[2] While BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x'), right=Literal(value=5.0)) -> 3, 4
[3] Assignment(target=VarAccess(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x'), right=Literal(value=1.0))) -> 5
[4] Return(value=VarAccess(name='x')) ->
[5] Assignment(target=VarAccess(name='x'), value=FunctionCall(name='phi', args=[])) -> 2"""

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

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 2
[2] Label(name='L1') -> 3
[3] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x'), right=Literal(value=5.0)) -> 5, 4
[4] IfJoin() -> 7
[5] Assignment(target=VarAccess(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x'), right=Literal(value=1.0))) -> 6
[6] Goto(label='L1') -> 2
[7] Return(value=VarAccess(name='x')) ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cctx.cfgs[0].dump()
            self.assertIn(origCfg.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{origCfg.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] [Variable(name='x', type_spec='int', attributes={})] -> 1
[1] Assignment(target=VarAccess(name='x'), value=Literal(value=0.0)) -> 2
[2] Label(name='L1') -> 8
[3] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x'), right=Literal(value=5.0)) -> 5, 4
[4] IfJoin() -> 7
[5] Assignment(target=VarAccess(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x'), right=Literal(value=1.0))) -> 6
[6] Goto(label='L1') -> 2
[7] Return(value=VarAccess(name='x')) ->
[8] Assignment(target=VarAccess(name='x'), value=FunctionCall(name='phi', args=[])) -> 3"""
 
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_do_while_needs_no_phis(self):
        code = """
        int main(int i, int j) {
        
        i = 24;
        do {
            i = -1;
            j = -1;
        } while(i < j);
        i = 112;
        j = 123;

        return i;

        }"""

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
[0] Assignment(target=VarAccess(name='i'), value=Literal(value=24.0)) -> 2
[1] DoWhile BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=VarAccess(name='j')) -> 2, 5
[2] DoJoin() -> 3
[3] Assignment(target=VarAccess(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 4
[4] Assignment(target=VarAccess(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 1
[5] Assignment(target=VarAccess(name='i'), value=Literal(value=112.0)) -> 6
[6] Assignment(target=VarAccess(name='j'), value=Literal(value=123.0)) -> 7
[7] Return(value=VarAccess(name='i')) ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cctx.cfgs[0].dump()
            self.assertIn(origCfg.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{origCfg.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

        # no phis inserted as there is no merging defs.
        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ ]
BB3 -> DF:[ ]
CFG:
Fcn : main
[0] Assignment(target=VarAccess(name='i'), value=Literal(value=24.0)) -> 2
[1] DoWhile BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=VarAccess(name='j')) -> 2, 5
[2] DoJoin() -> 3
[3] Assignment(target=VarAccess(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 4
[4] Assignment(target=VarAccess(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 1
[5] Assignment(target=VarAccess(name='i'), value=Literal(value=112.0)) -> 6
[6] Assignment(target=VarAccess(name='j'), value=Literal(value=123.0)) -> 7
[7] Return(value=VarAccess(name='i')) ->"""
 
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

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
[0] Assignment(target=VarAccess(name='i'), value=Literal(value=24.0)) -> 1
[1] Label(name='l1') -> 2
[2] Assignment(target=VarAccess(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 3
[3] Assignment(target=VarAccess(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 4
[4] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=VarAccess(name='j')) -> 6, 5
[5] IfJoin() -> 7
[6] Goto(label='l1') -> 1
[7] Assignment(target=VarAccess(name='i'), value=Literal(value=112.0)) -> 8
[8] Assignment(target=VarAccess(name='j'), value=Literal(value=123.0)) -> 9
[9] Return(value=Literal(value=0.0)) ->"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cctx.cfgs[0].dump()
            self.assertIn(origCfg.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{origCfg.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

        # no phis inserted as there is no merging defs.
        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB2 ]
BB3 -> DF:[ BB2 ]
BB4 -> DF:[ ]
CFG:
Fcn : main
[0] Assignment(target=VarAccess(name='i'), value=Literal(value=24.0)) -> 1
[1] Label(name='l1') -> 11
[2] Assignment(target=VarAccess(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 3
[3] Assignment(target=VarAccess(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 4
[4] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=VarAccess(name='j')) -> 6, 5
[5] IfJoin() -> 7
[6] Goto(label='l1') -> 1
[7] Assignment(target=VarAccess(name='i'), value=Literal(value=112.0)) -> 8
[8] Assignment(target=VarAccess(name='j'), value=Literal(value=123.0)) -> 9
[9] Return(value=Literal(value=0.0)) ->
[10] Assignment(target=VarAccess(name='i'), value=FunctionCall(name='phi', args=[])) -> 2
[11] Assignment(target=VarAccess(name='j'), value=FunctionCall(name='phi', args=[])) -> 10"""
 
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

