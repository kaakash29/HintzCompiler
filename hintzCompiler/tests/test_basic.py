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

        expected = """statements: [
            [Variable(name='result', type_spec='int', attributes=None)]
            Assignment:
              target:
                Identifier:
                  name: result
              value: FunctionCall(name='add', args=[Literal(value=1.0), Literal(value=2.0)])
          ]"""

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_array_access(self):
        code = """
        int main() {
            float m[3];
            m[0] = 10;
        }
        """

        expected = """Program:
  declarations: [
    Function:
      return_type: int
      name: main
      params: [
      ]
      body:
        Block:
          statements: [
            [Variable(name='m', type_spec='float', attributes={'dimensions': [3]})]
            Assignment:
              target: ArrayAccess(base=Identifier(name="Identifier(name='m')"), index=Literal(value=0.0))
              value:
                Literal:
                  value: 10.0
          ]
  ]"""

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")



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

        expected = """statements: [
            [Variable(name='v', type_spec='Vec2', attributes=None)]
            Assignment:
              target: FieldAccess(base=Identifier(name="Identifier(name='v')"), field='x')
              value:
                Literal:
                  value: 1.0
          ]"""

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")



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
        expected = """If:
              condition:
                BinaryOp:
                  op: ==
                  left: FieldAccess(base=Identifier(name="Identifier(name='v')"), field='x')
                  right:
                    Literal:
                      value: 1.0
              then_branch:
                Block:
                  statements: [
                    Assignment:
                      target: FieldAccess(base=Identifier(name="Identifier(name='v')"), field='x')
                      value:
                        Literal:
                          value: 0.0""";

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")



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

        expected = """For:
              init:
                Assignment:
                  target:
                    Identifier:
                      name: i
                  value:
                    Literal:
                      value: 0.0
              condition:
                BinaryOp:
                  op: <
                  left:
                    Identifier:
                      name: i
                  right:
                    Literal:
                      value: 5.0
              update:
                UnaryOp:
                  op: ++
                  operand:
                    Identifier:
                      name: i
                  is_postfix: True
              body:"""

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


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
        expected = """While:
              condition:
                BinaryOp:
                  op: <
                  left:
                    Identifier:
                      name: i
                  right:
                    Literal:
                      value: 5.0"""
        
        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")




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

        expected = """DoWhile:
              body:
                Block:
                  statements: [
                    Assignment:
                      target: FieldAccess(base=Identifier(name="Identifier(name='v')"), field='x')
                      value:
                        BinaryOp:
                          op: +
                          left: FieldAccess(base=Identifier(name="Identifier(name='v')"), field='x')
                          right:
                            Literal:
                              value: 1.0"""

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")



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
        ir = compile_source(code)
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

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_for_with_no_init(self):
        code = """
int main() {
   int i;
   int j;
   i = 0;
   
   for(;i < 12; i++) {
      j = i;
   }
   
   return i;
}"""

        expected = """
            For:
              init: None
              condition:
                BinaryOp:
                  op: <
                  left:
                    Identifier:
                      name: i
                  right:
                    Literal:
                      value: 12.0
              update:
                UnaryOp:
                  op: ++
                  operand:
                    Identifier:
                      name: i
                  is_postfix: True
              body:"""

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


    def test_void_void_function(self):
        code = """
        void foo() {
            return;
        }

        int main() {
            foo();
            return;
        }
        """

        expected = """Function:
      return_type: int
      name: main
      params: [
      ]
      body:
        Block:
          statements: [
            FunctionCall(name='foo', args=[])
            Return:
              value: None
          ]
  ]"""

        ir = compile_source(code)
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")
