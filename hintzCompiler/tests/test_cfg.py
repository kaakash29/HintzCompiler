import unittest
from hintzCompiler.compiler import compile_source
from hintzCompiler.src.cfg import ControlFlowGraph
from io import StringIO
from unittest.mock import patch

class TestCFG(unittest.TestCase):
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
[0] [Variable(name='n', type_spec='int', attributes=None)] -> 1
[1] [Variable(name='cnt', type_spec='int', attributes=None)] -> 2
[2] [Variable(name='i', type_spec='int', attributes=None)] -> 3
[3] [Variable(name='retVal', type_spec='int', attributes=None)] -> 4
[4] Assignment(target=Identifier(name='n'), value=Literal(value=29.0)) -> 5
[5] Assignment(target=Identifier(name='cnt'), value=Literal(value=0.0)) -> 6
[6] if BinaryOp(op=Token('LE_OP', '<='), left=Identifier(name='n'), right=Literal(value=1.0)) -> 1, 1
[7] <hintzCompiler.src.ir_nodes.IRNode object at 0x7f7490676270> -> 2, 0
[8] Assignment(target=Identifier(name='retVal'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 7
[9] for(init; cond; update) -> 1, 0
[10] Assignment(target=Identifier(name='i'), value=Literal(value=1.0)) -> 1, 1
[11] BinaryOp(op=Token('LE_OP', '<='), left=Identifier(name='i'), right=Identifier(name='n')) -> 7
[12] if BinaryOp(op=Token('EQ_OP', '=='), left=BinaryOp(op=Token('MOD_OP', '%'), left=Identifier(name='n'), right=Identifier(name='i')), right=Literal(value=0.0)) -> 1, 5
[13] <hintzCompiler.src.ir_nodes.IRNode object at 0x7f749083e0d0> -> []
[14] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='cnt'), is_postfix=True) -> 1, 3
[15] UnaryOp(op=Token('INCREMENT', '++'), operand=Identifier(name='i'), is_postfix=True) -> 1, 1
[16] if BinaryOp(op=Token('GT_OP', '>'), left=Identifier(name='cnt'), right=Literal(value=2.0)) -> 1, 9
[17] <hintzCompiler.src.ir_nodes.IRNode object at 0x7f749083de50> -> []
[18] Assignment(target=Identifier(name='retVal'), value=UnaryOp(op=Token('SUB_OP', '-'), operand=Literal(value=1.0), is_postfix=False)) -> 1, 7
[19] Assignment(target=Identifier(name='retVal'), value=Literal(value=1.0)) -> 1, 7
[20] Return(value=Identifier(name='retVal')) -> []""";
        
        cfg.dump()
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

