import unittest
from hintzCompiler.compiler import compile_source  # You’ll implement this function
import unittest
from io import StringIO
from unittest.mock import patch


class TestCompiler(unittest.TestCase):

    def test_variable_assignment(self):
        code = """
        int main() {
            int x;
            x = 5;
        }
        """
        ir = compile_source(code)
        self.assertTrue(any(stmt for stmt in ir.declarations[0].body.statements if stmt.__class__.__name__ == "Assignment"))

    def test_function_call(self):
        code = """
        int add(int a, int b) {
            return a + b;
        }

        int main() {
            int result;
            result = add(1, 2);
        }
        """
        ir = compile_source(code)
        self.assertTrue(any("add" in str(stmt) for stmt in ir.declarations[1].body.statements))

    def test_array_access(self):
        code = """
        int main() {
            float m[3];
            m[0] = 10;
        }
        """
        ir = compile_source(code)
        self.assertTrue("ArrayAccess" in str(ir))

    def test_struct_field_access(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            v.x = 1;
        }
        """
        ir = compile_source(code)
        self.assertTrue("FieldAccess" in str(ir))

    def test_simple_if_stmt(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            v.x = 1;
            if(v.x == 1) {
                v.x = 0;
            } else {
                v.x = 29;
            }
        }
        """
        ir = compile_source(code)
        #print(ir.to_string())
        self.assertTrue("if" in str(ir))

    def test_simple_for_stmt(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            int i;

            for (i = 0; i < 5; i++) {
                v.x = v.x + 1;
            }
        }
        """
        ir = compile_source(code)
        #print(ir.to_string())
        self.assertTrue("For" in str(ir))


    def test_simple_while_stmt(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            int i;

            i = 0;
            while(i < 5) {
                v.x = v.x + 1;
                i = i + 1;
            }
        }
        """
        ir = compile_source(code)
        #print(ir.to_string())
        self.assertTrue("While" in str(ir))

    def test_simple_do_while_stmt(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            int i;

            i = 0;
            do {
                v.x = v.x + 1;
                i = i + 1;
            } while(i < 5);
        }
        """
        ir = compile_source(code)
        #print(ir.to_string())
        self.assertTrue("While" in str(ir))

    def test_simple_switch_stmt(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            int i;

            switch(v.x) {
                case 0:
                    i = 0;
                    break;
                case 1:
                    i = 1;
                    break;
                default:
                    i = -1;
                    break;
            }

        }
        """
        ir = compile_source(code)
        expected = """Switch:
              expr: FieldAccess(base=Identifier(name="Identifier(name='v')"), field='x')
              cases: [
                Case:
                  value:
                    Literal:
                      value: 0.0
                  body:
                    Block:
                      statements: [
                        Assignment:
                          target:
                            Identifier:
                              name: i
                          value:
                            Literal:
                              value: 0.0
                        Break:
                      ]"""
        self.maxDiff = None
        #ir.dump()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())


    def test_simple_got_label_stmt(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            int i;

            if(i < 12) {
                i = 0;
                goto label;
            } else {
                i = 1;
            }

            label:
                i = 2;
            
            return i;
        }
        """
        ir = compile_source(code)
        expected = """If:
              condition:
                BinaryOp:
                  op: <
                  left:
                    Identifier:
                      name: i
                  right:
                    Literal:
                      value: 12.0
              then_branch:
                Block:
                  statements: [
                    Assignment:
                      target:
                        Identifier:
                          name: i
                      value:
                        Literal:
                          value: 0.0
                    Goto:
                      label: label
                  ]
              else_branch:
                Block:
                  statements: [
                    Assignment:
                      target:
                        Identifier:
                          name: i
                      value:
                        Literal:
                          value: 1.0
                  ]
            Label:
              name: label
            Assignment:"""
        self.maxDiff = None
        #ir.dump()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected, mock_stdout.getvalue().strip())
