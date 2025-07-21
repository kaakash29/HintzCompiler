# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.readWriteAnalyzer import ReadWriteAnalyzer
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
[2] Assignment(target=VarAccess(name='x1'), value=Literal(value=0.0)) -> 3
[3] If BinaryOp(op=Token('GT_OP', '>'), left=VarAccess(name='in'), right=Literal(value=5.0)) -> 5, 6
[4] IfJoin() -> 9
[5] Assignment(target=VarAccess(name='x2'), value=Literal(value=1.0)) -> 4
[6] Assignment(target=VarAccess(name='x4'), value=Literal(value=2.0)) -> 4
[7] Assignment(target=VarAccess(name='out1'), value=VarAccess(name='x3')) -> 8
[8] Return(value=VarAccess(name='out1')) ->
[9] Assignment(target=VarAccess(name='x3'), value=FunctionCall(name='phi', args=[VarAccess(name='x2'), VarAccess(name='x4')])) -> 7"""
       
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
[1] Assignment(target=VarAccess(name='x1'), value=Literal(value=0.0)) -> 5
[2] While BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x2'), right=Literal(value=5.0)) -> 3, 4
[3] Assignment(target=VarAccess(name='x3'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x2'), right=Literal(value=1.0))) -> 5
[4] Return(value=VarAccess(name='x2')) ->
[5] Assignment(target=VarAccess(name='x2'), value=FunctionCall(name='phi', args=[VarAccess(name='x1'), VarAccess(name='x3')])) -> 2"""

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
[1] Assignment(target=VarAccess(name='x1'), value=Literal(value=0.0)) -> 2
[2] Label(name='L1') -> 8
[3] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='x2'), right=Literal(value=5.0)) -> 5, 4
[4] IfJoin() -> 7
[5] Assignment(target=VarAccess(name='x3'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='x2'), right=Literal(value=1.0))) -> 6
[6] Goto(label='L1') -> 2
[7] Return(value=VarAccess(name='x2')) ->
[8] Assignment(target=VarAccess(name='x2'), value=FunctionCall(name='phi', args=[VarAccess(name='x1'), VarAccess(name='x3')])) -> 3"""
 
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

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
[0] Assignment(target=VarAccess(name='i'), value=Literal(value=24.0)) -> 1
[1] Assignment(target=VarAccess(name='j'), value=Literal(value=26.0)) -> 3
[2] DoWhile BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=VarAccess(name='j')) -> 3, 6
[3] DoJoin() -> 4
[4] Assignment(target=VarAccess(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 5
[5] Assignment(target=VarAccess(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 2
[6] Assignment(target=VarAccess(name='i'), value=Literal(value=112.0)) -> 7
[7] Assignment(target=VarAccess(name='j'), value=Literal(value=123.0)) -> 8
[8] Return(value=VarAccess(name='i')) ->"""

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
[0] Assignment(target=VarAccess(name='i1'), value=Literal(value=24.0)) -> 1
[1] Assignment(target=VarAccess(name='j1'), value=Literal(value=26.0)) -> 3
[2] DoWhile BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i3'), right=VarAccess(name='j3')) -> 3, 6
[3] DoJoin() -> 10
[4] Assignment(target=VarAccess(name='i3'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 5
[5] Assignment(target=VarAccess(name='j3'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 2
[6] Assignment(target=VarAccess(name='i4'), value=Literal(value=112.0)) -> 7
[7] Assignment(target=VarAccess(name='j4'), value=Literal(value=123.0)) -> 8
[8] Return(value=VarAccess(name='i4')) ->
[9] Assignment(target=VarAccess(name='i2'), value=FunctionCall(name='phi', args=[VarAccess(name='i1'), VarAccess(name='i3')])) -> 4
[10] Assignment(target=VarAccess(name='j2'), value=FunctionCall(name='phi', args=[VarAccess(name='j1'), VarAccess(name='j3')])) -> 9"""
 
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

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]

        origCfg = """Fcn : main
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
[0] Assignment(target=VarAccess(name='i1'), value=Literal(value=24.0)) -> 1
[1] Assignment(target=VarAccess(name='j1'), value=Literal(value=26.0)) -> 2
[2] Label(name='l1') -> 12
[3] Assignment(target=VarAccess(name='i3'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 4
[4] Assignment(target=VarAccess(name='j3'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 5
[5] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i3'), right=VarAccess(name='j3')) -> 7, 6
[6] IfJoin() -> 8
[7] Goto(label='l1') -> 2
[8] Assignment(target=VarAccess(name='i4'), value=Literal(value=112.0)) -> 9
[9] Assignment(target=VarAccess(name='j4'), value=Literal(value=123.0)) -> 10
[10] Return(value=Literal(value=0.0)) ->
[11] Assignment(target=VarAccess(name='i2'), value=FunctionCall(name='phi', args=[VarAccess(name='i1'), VarAccess(name='i3')])) -> 3
[12] Assignment(target=VarAccess(name='j2'), value=FunctionCall(name='phi', args=[VarAccess(name='j1'), VarAccess(name='j3')])) -> 11"""
 
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

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]
        origCfg = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes={})] -> 1
[1] [Variable(name='j', type_spec='int', attributes={})] -> 2
[2] Assignment(target=VarAccess(name='j'), value=Literal(value=0.0)) -> 3
[3] for(init; cond; update) -> 4
[4] Assignment(target=VarAccess(name='i'), value=Literal(value=0.0)) -> 5
[5] BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i'), right=Literal(value=10.0)) -> 6, 8
[6] Assignment(target=VarAccess(name='j'), value=VarAccess(name='i')) -> 7
[7] Assignment(target=VarAccess(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='i'), right=Literal(value=1.0))) -> 5
[8] Return(value=VarAccess(name='j')) ->"""

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
[0] [Variable(name='i', type_spec='int', attributes={})] -> 1
[1] [Variable(name='j', type_spec='int', attributes={})] -> 2
[2] Assignment(target=VarAccess(name='j1'), value=Literal(value=0.0)) -> 3
[3] for(init; cond; update) -> 4
[4] Assignment(target=VarAccess(name='i1'), value=Literal(value=0.0)) -> 10
[5] BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='i2'), right=Literal(value=10.0)) -> 6, 8
[6] Assignment(target=VarAccess(name='j3'), value=VarAccess(name='i2')) -> 7
[7] Assignment(target=VarAccess(name='i3'), value=BinaryOp(op=Token('ADD_OP', '+'), left=VarAccess(name='i2'), right=Literal(value=1.0))) -> 10
[8] Return(value=VarAccess(name='j2')) ->
[9] Assignment(target=VarAccess(name='i2'), value=FunctionCall(name='phi', args=[VarAccess(name='i1'), VarAccess(name='i3')])) -> 5
[10] Assignment(target=VarAccess(name='j2'), value=FunctionCall(name='phi', args=[VarAccess(name='j1'), VarAccess(name='j3')])) -> 9"""

        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_ssa_reaching_def(self):
        code = """
        int main() { 
            int j;
            if(j < 0) {
                j = 12;
            } else {
                j = 13;
            }
            return j;
        }"""
        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)

        expected = """DOMINANCE-FRONTIERS:
BB1 -> DF:[ ]
BB2 -> DF:[ BB3 ]
BB3 -> DF:[ ]
BB4 -> DF:[ BB3 ]
CFG:
Fcn : main
[0] [Variable(name='j', type_spec='int', attributes={})] -> 1
[1] If BinaryOp(op=Token('LT_OP', '<'), left=VarAccess(name='j'), right=Literal(value=0.0)) -> 3, 4
[2] IfJoin() -> 6
[3] Assignment(target=VarAccess(name='j1'), value=Literal(value=12.0)) -> 2
[4] Assignment(target=VarAccess(name='j3'), value=Literal(value=13.0)) -> 2
[5] Return(value=VarAccess(name='j2')) ->
[6] Assignment(target=VarAccess(name='j2'), value=FunctionCall(name='phi', args=[VarAccess(name='j1'), VarAccess(name='j3')])) -> 5"""

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"DOMINANCE-FRONTIERS:")
            domFs.dump()
            print(f"CFG:")
            cctx.cfgs[0].dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

        expectedReach = """ReachingDef for Use:VarAccess(name='j2') on Return(value=VarAccess(name='j2')) is:
 * Assignment(target=VarAccess(name='j2'), value=FunctionCall(name='phi', args=[VarAccess(name='j1'), VarAccess(name='j3')]))"""
        cfg0 = cctx.cfgs[0]
        drwa = ReadWriteAnalyzer(cfg0)
        readsOnLastStmt = drwa.get_reads(cfg0.nodes[-2].id)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(f"\nReachingDef for Use:{readsOnLastStmt[0].irVarAccessNode} on {readsOnLastStmt[0].irVarAccessNode.rootStmt()} is:\n * {readsOnLastStmt[0].irVarAccessNode._ssaReachingDef.rootStmt()} ")

            self.assertIn(expectedReach.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\nExpected:||{expectedReach.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")
