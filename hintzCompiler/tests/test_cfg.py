import unittest
from hintzCompiler.compiler import Driver
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.ir_nodes import Function
from io import StringIO
from unittest.mock import patch
from typing import cast

class TestCFG(unittest.TestCase):

    ## Simple singular control structures.

    def test_simple_empty_body(self):
        code = """
        int main() {
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        expected = """Fcn : main""";

        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_simple_straight_line(self):
        code = """
        int main() {
            int x;
            int i;

            x = i;
            i = x;
            x = i;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 3
[3] Assignment(target=Identifier(name='i'), value=Identifier(name='x')) -> 4
[4] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) ->""";

        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_simple_for(self):
        code = """
        int main() {
            int x;
            int i;

            for(i = 0; i < 5; i++) {
                x = i;
            }
            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] for(init; cond; update) -> 3
[3] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 4
[4] BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 5, 7
[5] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 6
[6] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='i'), is_postfix=True) -> 4
[7] Return(value=Identifier(name='x')) ->""";

        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_simple_switch(self):
        code = """
            int main() {
                int x;
                int i;

                switch(x) {
                case 1:
                    x = 1;
                    break;
                case 2:
                    x = 2;
                    break;
                default:
                    x = 99;
                    break;
                }

                return x;
            }"""
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        
        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] switch Identifier(name='x') -> 4, 6, 8
[3] SwitchJoin() -> 10
[4] Assignment(target=Identifier(name='x'), value=Literal(value=1.0)) -> 5
[5] Break() -> 3
[6] Assignment(target=Identifier(name='x'), value=Literal(value=2.0)) -> 7
[7] Break() -> 3
[8] Assignment(target=Identifier(name='x'), value=Literal(value=99.0)) -> 9
[9] Break() -> 3
[10] Return(value=Identifier(name='x')) ->""";

        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_simple_ifs(self):
        code = """
        int main() {
            int x;
            x = 1;
            if (x == 1) {
                x = 2;
            } else {
                x = 3;
            }
            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        # Check that there are expected number of nodes
        self.assertGreaterEqual(len(cfg.nodes), 5)

        # Optional: Assert branching from the if statement
        if_node = [n for n in cfg.nodes if type(n.stmt).__name__ == "If"]
        self.assertEqual(len(if_node), 1)
        self.assertEqual(len(if_node[0].successors), 2)  # then & else branches


        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] Assignment(target=Identifier(name='x'), value=Literal(value=1.0)) -> 2
[2] If BinaryOp(op=Token('EQ_OP', '=='), left=Identifier(name='x'), right=Literal(value=1.0)) -> 4, 5
[3] IfJoin() -> 6
[4] Assignment(target=Identifier(name='x'), value=Literal(value=2.0)) -> 3
[5] Assignment(target=Identifier(name='x'), value=Literal(value=3.0)) -> 3
[6] Return(value=Identifier(name='x')) ->""";
        
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_simple_if_no_else(self):
        code = """
        int main() {
            int x;
            x = 1;
            if (x == 1) {
                x = 2;
            }
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        # Check that there are expected number of nodes
        self.assertGreaterEqual(len(cfg.nodes), 5)

        # Optional: Assert branching from the if statement
        if_node = [n for n in cfg.nodes if type(n.stmt).__name__ == "If"]
        self.assertEqual(len(if_node), 1)
        self.assertEqual(len(if_node[0].successors), 2)  # then & else branches

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] Assignment(target=Identifier(name='x'), value=Literal(value=1.0)) -> 2
[2] If BinaryOp(op=Token('EQ_OP', '=='), left=Identifier(name='x'), right=Literal(value=1.0)) -> 4, 3
[3] IfJoin() ->
[4] Assignment(target=Identifier(name='x'), value=Literal(value=2.0)) -> 3""";

        #cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_simple_if_no_else_2(self):
        code = """
        int main() {
            int x;
            x = 1;
            if (x == 1) {
                x = 2;
            }
            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        if_node = [n for n in cfg.nodes if type(n.stmt).__name__ == "If"]
        self.assertEqual(len(if_node), 1)
        self.assertEqual(len(if_node[0].successors), 2)  # then & else branches


        expected = """
Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] Assignment(target=Identifier(name='x'), value=Literal(value=1.0)) -> 2
[2] If BinaryOp(op=Token('EQ_OP', '=='), left=Identifier(name='x'), right=Literal(value=1.0)) -> 4, 3
[3] IfJoin() -> 5
[4] Assignment(target=Identifier(name='x'), value=Literal(value=2.0)) -> 3
[5] Return(value=Identifier(name='x')) ->""";
        
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_simple_while_loop(self):
        code = """int main() {
            int i;
            i = 0;
            while(i < 10) {
                i = i + 1;
            }

            return i;
        }"""

        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] -> 1
[1] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 2
[2] While BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=10.0)) -> 3, 4
[3] Assignment(target=Identifier(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Identifier(name='i'), right=Literal(value=1.0))) -> 2
[4] Return(value=Identifier(name='i')) ->"""

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\
                          \nExpected:||{expected.strip()}||\
                          \nActual:||{mock_stdout.getvalue().strip()}||")

    def test_simple_do_while_loop(self):
        code = """int main() {
            int i;
            int j;
            i = 0;
            do {
                j = 0;
                i = i + 1;
                j = 1;
            } while (i < 10);

            return i;
        }"""

        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='j', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 4
[3] DoWhile BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=10.0)) -> 4, 7
[4] Assignment(target=Identifier(name='j'), value=Literal(value=0.0)) -> 5
[5] Assignment(target=Identifier(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Identifier(name='i'), right=Literal(value=1.0))) -> 6
[6] Assignment(target=Identifier(name='j'), value=Literal(value=1.0)) -> 3
[7] Return(value=Identifier(name='i')) ->"""

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\
                          \nExpected:||{expected.strip()}||\
                          \nActual:||{mock_stdout.getvalue().strip()}||")


    ## Nesting control structures inside IF/ELSE.

    def test_for_in_if(self):
        code = """
        int main() {
            int x;
            int i;

            x = 1;
            if (x == 1) {
                x = 2;
                for(i = 0; i < 5; i++) {
                    x = i;
                }
                x = 5;
            } else {
                x = 10;
            }
            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        # Check that there are expected number of nodes
        self.assertGreaterEqual(len(cfg.nodes), 5)

        # Optional: Assert branching from the if statement
        if_node = [n for n in cfg.nodes if type(n.stmt).__name__ == "If"]
        self.assertEqual(len(if_node), 1)
        self.assertEqual(len(if_node[0].successors), 2)  # then & else branches

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=Identifier(name='x'), value=Literal(value=1.0)) -> 3
[3] If BinaryOp(op=Token('EQ_OP', '=='), left=Identifier(name='x'), right=Literal(value=1.0)) -> 5, 12
[4] IfJoin() -> 13
[5] Assignment(target=Identifier(name='x'), value=Literal(value=2.0)) -> 6
[6] for(init; cond; update) -> 7
[7] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 8
[8] BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 9, 11
[9] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 10
[10] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='i'), is_postfix=True) -> 8
[11] Assignment(target=Identifier(name='x'), value=Literal(value=5.0)) -> 4
[12] Assignment(target=Identifier(name='x'), value=Literal(value=10.0)) -> 4
[13] Return(value=Identifier(name='x')) ->""";

        # Optional: Print to visually confirm
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")
 
    def test_for_in_else(self):
        code = """
        int main() {
            int x;
            int i;

            x = 1;
            if (x == 1) {
                x = 2;
            } else {
                x = 3;
                for(i = 0; i < 5; i++) {
                    x = i;
                }
                x = 5;
            }
            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        # Check that there are expected number of nodes
        self.assertGreaterEqual(len(cfg.nodes), 5)

        # Optional: Assert branching from the if statement
        if_node = [n for n in cfg.nodes if type(n.stmt).__name__ == "If"]
        self.assertEqual(len(if_node), 1)
        self.assertEqual(len(if_node[0].successors), 2)  # then & else branches

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=Identifier(name='x'), value=Literal(value=1.0)) -> 3
[3] If BinaryOp(op=Token('EQ_OP', '=='), left=Identifier(name='x'), right=Literal(value=1.0)) -> 5, 6
[4] IfJoin() -> 13
[5] Assignment(target=Identifier(name='x'), value=Literal(value=2.0)) -> 4
[6] Assignment(target=Identifier(name='x'), value=Literal(value=3.0)) -> 7
[7] for(init; cond; update) -> 8
[8] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 9
[9] BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 10, 12
[10] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 11
[11] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='i'), is_postfix=True) -> 9
[12] Assignment(target=Identifier(name='x'), value=Literal(value=5.0)) -> 4
[13] Return(value=Identifier(name='x')) ->""";

        # Optional: Print to visually confirm
        # cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    #NOTE: @unittest.skip("Skipping this test for now")
    def test_if_in_if(self):
        code = """
        int main() {
            int x;
            int i;
            int j;

            if(i < 5) {
                x = i;
                if(j < 10) {
                    x = j;
                }
            }

            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='j', type_spec='int', attributes=None)] -> 3
[3] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 5, 4
[4] IfJoin() -> 9
[5] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 6
[6] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='j'), right=Literal(value=10.0)) -> 8, 7
[7] IfJoin() -> 4
[8] Assignment(target=Identifier(name='x'), value=Identifier(name='j')) -> 7
[9] Return(value=Identifier(name='x')) ->""";

        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_if_in_if_2(self):
        code = """
        int main() {
            int x;
            int i;
            int j;

            if(i < 5) {
                x = i;
                if(j < 10) {
                    x = j;
                } else {
                    x = j;
                }
            }

            return x;
        }
        """

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='j', type_spec='int', attributes=None)] -> 3
[3] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 5, 4
[4] IfJoin() -> 10
[5] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 6
[6] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='j'), right=Literal(value=10.0)) -> 8, 9
[7] IfJoin() -> 4
[8] Assignment(target=Identifier(name='x'), value=Identifier(name='j')) -> 7
[9] Assignment(target=Identifier(name='x'), value=Identifier(name='j')) -> 7
[10] Return(value=Identifier(name='x')) ->""";

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_switch_in_if(self):
        code = """
        int main() {
            int l;
            int out;

            if(l > 12) {

                switch(l) {
                    case 13:
                        out = 0;
                        break;
                    case 14:
                        out = 1;
                        break;
                    default:
                        out = 99;
                        break;
                }

            } else {
                out = 11;
            } 

            return out;
        }"""

        expected = """Fcn : main
[0] [Variable(name='l', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='out', type_spec='int', attributes=None)] -> 2
[2] If BinaryOp(op=Token('GT_OP', '>'), left=Identifier(name='l'), right=Literal(value=12.0)) -> 4, 12
[3] IfJoin() -> 13
[4] switch Identifier(name='l') -> 6, 8, 10
[5] SwitchJoin() -> 3
[6] Assignment(target=Identifier(name='out'), value=Literal(value=0.0)) -> 7
[7] Break() -> 5
[8] Assignment(target=Identifier(name='out'), value=Literal(value=1.0)) -> 9
[9] Break() -> 5
[10] Assignment(target=Identifier(name='out'), value=Literal(value=99.0)) -> 11
[11] Break() -> 5
[12] Assignment(target=Identifier(name='out'), value=Literal(value=11.0)) -> 3
[13] Return(value=Identifier(name='out')) ->"""
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\
                          \nExpected:||{expected.strip()}||\
                          \nActual:||{mock_stdout.getvalue().strip()}||")

    def test_while_in_if(self):
        code = """
        int main() {
            int x;
            int i;

            if(x < 0) {

                while(i < 20) {
                    x = i;
                    i = i + 1; 
                }

            }
        }
        """

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='x'), right=Literal(value=0.0)) -> 4, 3
[3] IfJoin() ->
[4] While BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=20.0)) -> 5, 3
[5] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 6
[6] Assignment(target=Identifier(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Identifier(name='i'), right=Literal(value=1.0))) -> 4"""

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\
                          \nExpected:||{expected.strip()}||\
                          \nActual:||{mock_stdout.getvalue().strip()}||")

    def test_do_while_in_if(self):
        code = """
        int main() {
            int x;
            int i;

            if(x < 0) {

                do {
                    x = i;
                    i = i + 1; 
                } while(i < 20);
    
            }

            return x;
        }
        """

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='x'), right=Literal(value=0.0)) -> 5, 3
[3] IfJoin() -> 7
[4] DoWhile BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=20.0)) -> 5, 3
[5] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 6
[6] Assignment(target=Identifier(name='i'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Identifier(name='i'), right=Literal(value=1.0))) -> 4
[7] Return(value=Identifier(name='x')) ->"""

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\
                          \nExpected:||{expected.strip()}||\
                          \nActual:||{mock_stdout.getvalue().strip()}||")

    ## Nesting control structures inside FOR-LOOPS.

    def test_for_in_for(self):
        code = """
        int main() {
            int x;
            int i;
            int j;

            for(i = 0; i < 5; i++) {
                x = i;
                for(j = 0; j < 10; j++) {
                    x = j;
                }
            }

            return x;
        }"""

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='j', type_spec='int', attributes=None)] -> 3
[3] for(init; cond; update) -> 4
[4] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 5
[5] BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 6, 13
[6] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 7
[7] for(init; cond; update) -> 8
[8] Assignment(target=Identifier(name='j'), value=Literal(value=0.0)) -> 9
[9] BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='j'), right=Literal(value=10.0)) -> 10, 12
[10] Assignment(target=Identifier(name='x'), value=Identifier(name='j')) -> 11
[11] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='j'), is_postfix=True) -> 9
[12] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='i'), is_postfix=True) -> 5
[13] Return(value=Identifier(name='x')) ->""";

        # Optional: Print to visually confirm
        # cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    #@unittest.skip("Skipping this test for now")
    def test_if_in_for(self):
        code = """
        int main() {
            int x;
            int i;
            int j;

            for(i = 0; i < 5; i++) {
                x = i;

                if(x == 12) {
                    x = 12;
                }

            }

            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='j', type_spec='int', attributes=None)] -> 3
[3] for(init; cond; update) -> 4
[4] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 5
[5] BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 6, 11
[6] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 7
[7] If BinaryOp(op=Token('EQ_OP', '=='), left=Identifier(name='x'), right=Literal(value=12.0)) -> 9, 8
[8] IfJoin() -> 10
[9] Assignment(target=Identifier(name='x'), value=Literal(value=12.0)) -> 8
[10] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='i'), is_postfix=True) -> 5
[11] Return(value=Identifier(name='x')) ->""";

        # Optional: Print to visually confirm
        # cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_while_in_for(self):
        code = """
        int main() {
            int x;
            int i;
            int j;

            for(i = 0; i < 5; i++) {
                x = i;

                while(x < 22) {
                    j = 0;
                    x = x + 1;
                    j = 99;
                }

                x = j;
            }

            return x;
        }
        """
        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)

        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='j', type_spec='int', attributes=None)] -> 3
[3] for(init; cond; update) -> 4
[4] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 5
[5] BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Literal(value=5.0)) -> 6, 13
[6] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 7
[7] While BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='x'), right=Literal(value=22.0)) -> 8, 11
[8] Assignment(target=Identifier(name='j'), value=Literal(value=0.0)) -> 9
[9] Assignment(target=Identifier(name='x'), value=BinaryOp(op=Token('ADD_OP', '+'), left=Identifier(name='x'), right=Literal(value=1.0))) -> 10
[10] Assignment(target=Identifier(name='j'), value=Literal(value=99.0)) -> 7
[11] Assignment(target=Identifier(name='x'), value=Identifier(name='j')) -> 12
[12] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='i'), is_postfix=True) -> 5
[13] Return(value=Identifier(name='x')) ->""";

        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_do_for_without_init_cond_update(self):
        code = """
int main() {
   int i;
   int j;
   i = 0;
   
   for(;;) {
      j = i;
   }
   
   return i;
}"""

        expected = """Fcn : main
[0] [Variable(name='i', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='j', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=Identifier(name='i'), value=Literal(value=0.0)) -> 3
[3] for(init; cond; update) -> 3, 4, 5
[4] Assignment(target=Identifier(name='j'), value=Identifier(name='i')) -> 3
[5] Return(value=Identifier(name='i')) ->"""

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\
                          \nExpected:||{expected.strip()}||\
                          \nActual:||{mock_stdout.getvalue().strip()}||")


    def test_simple_goto_label(self):
        code = """
        int main(int i, int j) {

            if(i < j) {
                goto l1;
            }
            
            i = 112;
            j = 123;

        l1:
            i = -1;
            j = -1;
            
            return 0;
        }
        """

        expected = """Fcn : main
[0] If BinaryOp(op=Token('LT_OP', '<'), left=Identifier(name='i'), right=Identifier(name='j')) -> 2, 1
[1] IfJoin() -> 3
[2] Goto(label='l1') -> 1, 5
[3] Assignment(target=Identifier(name='i'), value=Literal(value=112.0)) -> 4
[4] Assignment(target=Identifier(name='j'), value=Literal(value=123.0)) -> 5
[5] Label(name='l1') -> 6
[6] Assignment(target=Identifier(name='i'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 7
[7] Assignment(target=Identifier(name='j'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 8
[8] Return(value=Literal(value=0.0)) ->"""

        ir = Driver(code).ast
        function = cast(Function, ir.declarations[0])
        cfg = ControlFlowGraph(function)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(),
                          msg=f"\n\n[[-- FAILED --]]\
                          \nExpected:||{expected.strip()}||\
                          \nActual:||{mock_stdout.getvalue().strip()}||")
