import unittest
from hintzCompiler.compiler import compile_source
from hintzCompiler.src.cfg import ControlFlowGraph
from io import StringIO
from unittest.mock import patch
import difflib


class TestCFG(unittest.TestCase):

    def test_simple_empty_body(self):
        code = """
        int main() {
        }
        """
        ir = compile_source(code)
        function = ir.declarations[0]
        cfg = ControlFlowGraph(function)
        expected = """Fcn : main""";

        # Optional: Print to visually confirm
        # cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())


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
        ir = compile_source(code)
        function = ir.declarations[0]
        cfg = ControlFlowGraph(function)
        expected = """Fcn : main
[0] [Variable(name='x', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='i', type_spec='int', attributes=None)] -> 2
[2] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) -> 3
[3] Assignment(target=Identifier(name='i'), value=Identifier(name='x')) -> 4
[4] Assignment(target=Identifier(name='x'), value=Identifier(name='i')) ->""";

        # Optional: Print to visually confirm
        #cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())

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
        ir = compile_source(code)
        function = ir.declarations[0]
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

        # Optional: Print to visually confirm
        # cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())

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
        ir = compile_source(code)
        function = ir.declarations[0]
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

        # Optional: Print to visually confirm
        #cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip())


    def test_if_stmt_simple_ifs(self):
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
        ir = compile_source(code)
        function = ir.declarations[0]
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
            self.assertIn(expected, mock_stdout.getvalue().strip())


    def test_if_stmt_if_then_for(self):
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
        ir = compile_source(code)
        function = ir.declarations[0]
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
        actual = "";
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            actual = mock_stdout.getvalue().strip();

        self.assertIn(expected, actual);
 


    @unittest.skip("Skipping till we lock other things down")
    def test_if_stmt_ifs_for(self):
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
        ir = compile_source(code)
        function = ir.declarations[0]
        cfg = ControlFlowGraph(function)

        # Check that there are expected number of nodes
        self.assertGreaterEqual(len(cfg.nodes), 5)

        # Optional: Assert branching from the if statement
        if_node = [n for n in cfg.nodes if type(n.stmt).__name__ == "If"]
        self.assertEqual(len(if_node), 1)
        self.assertEqual(len(if_node[0].successors), 2)  # then & else branches

        expected = """something""";

        # Optional: Print to visually confirm
        #cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())






if __name__ == '__main__':
    unittest.main()

