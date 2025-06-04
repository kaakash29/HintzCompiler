import unittest
from hintzCompiler.compiler import compile_source
from hintzCompiler.src.cfg import ControlFlowGraph
from io import StringIO
from unittest.mock import patch

class TestCFG(unittest.TestCase):
    
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

    @unittest.skip("Skipping till we lock other things down")
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


        expected = """something""";
        
        cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())


    @unittest.skip("Skipping till we lock other things down")
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

        expected = """something""";

        # Optional: Print to visually confirm
        cfg.dump()
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cfg.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())


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

