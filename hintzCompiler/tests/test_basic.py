# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import os
import unittest
from lark import Lark
from io import StringIO
from typing import cast
from unittest.mock import patch
from hintzCompiler.src.transformer import IRTransformer
from hintzCompiler.src.ir_nodes import Function, Block
from hintzCompiler.compiler import buildCompilationContext

class TestCompiler(unittest.TestCase):

    def test_simple_fcn_with_args(self):
        code = """
        int main(int a, int b) {
            int x;
        }
        """
        grammar_path = os.path.join(os.path.dirname(__file__),"..", "grammar", "c89.lark")
        with open(grammar_path) as f:
            grammar = f.read()
        parser = Lark(grammar, parser="lalr", start="start")
        tree = parser.parse(code)
        transformer = IRTransformer()
        ir = transformer.transform(tree)
        expected = """Program:
  declarations: [
    Function:
      return_type: int
      name: main
      params: [
        Variable:
          name: a
          type_spec: int
          attributes: {'isiovar': True}
        Variable:
          name: b
          type_spec: int
          attributes: {'isiovar': True}
      ]
      body:
        Block:
          statements: [
            [Variable(name='x', type_spec='int', attributes={})]
          ]"""
        self.assertIn(expected.strip(), ir.toString(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{ir.toString().strip()}||")

    def test_variable_assignment(self):
        code = """
        int main() {
            int x;
            x = 5;
        }
        """
        ir = buildCompilationContext(code)._ast
        fcn = cast(Function, ir.declarations[0])
        body = cast(Block, fcn.body)
        self.assertTrue(any(stmt for stmt in body.statements if stmt.__class__.__name__ == "Assignment"))

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
            [Variable(name='result', type_spec='int', attributes={})]
            Assignment:
              target:
                VarAccess:
                  name: result
              value:
                FunctionCall:
                  name: add
                  args: [
                    Literal:
                      value: 1.0
                    Literal:
                      value: 2.0
                  ]
          ]"""

        ir = buildCompilationContext(code)._ast
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

        expected = """Function:
      return_type: int
      name: main
      params: [
      ]
      body:
        Block:
          statements: [
            [Variable(name='m', type_spec='float', attributes={'dimensions': [3]})]
            Assignment:
              target:
                ArrayAccess:
                  base:
                    VarAccess:
                      name: m
                  index:
                    Literal:
                      value: 0.0
              value:
                Literal:
             """

        ir = buildCompilationContext(code)._ast
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

        expected = """Assignment:
              target:
                FieldAccess:
                  base:
                    VarAccess:
                      name: v
                  field: x
              value:
                Literal:
                  value: 1.0"""

        ir = buildCompilationContext(code)._ast
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
                  left:
                    FieldAccess:
                      base:
                        VarAccess:
                          name: v
                      field: x
                  right:
                    Literal:
                      value: 1.0
              then_branch:
                Block:
                  statements: [
                    Assignment:
                      target:
                        FieldAccess:
                          base:
                            VarAccess:
                              name: v
                          field: x
                      value:
                        Literal:
                          value: 0.0
                  ]
              else_branch:
                Block:
                  statements: [
                    Assignment:
                      target:
                        FieldAccess:
                          base:
                            VarAccess:
                              name: v
                          field: x
                      value:
                        Literal:
                          value: 29.0
                  ]
          ]""";

        ir = buildCompilationContext(code)._ast
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
                    VarAccess:
                      name: i
                  value:
                    Literal:
                      value: 0.0
              condition:
                BinaryOp:
                  op: <
                  left:
                    VarAccess:
                      name: i
                  right:
                    Literal:
                      value: 5.0
              update:
                UnaryOp:
                  op: ++
                  operand:
                    VarAccess:
                      name: i
                  is_postfix: True
              body:"""

        ir = buildCompilationContext(code)._ast
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
                    VarAccess:
                      name: i
                  right:
                    Literal:
                      value: 5.0"""
        
        ir = buildCompilationContext(code)._ast
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
                      target:
                        FieldAccess:
                          base:
                            VarAccess:
                              name: v
                          field: x
                      value:
                        BinaryOp:
                          op: +
                          left:
                            FieldAccess:
                              base:
                                VarAccess:
                                  name: v
                              field: x
                          right:
                            Literal:
                              value: 1.0
                    Assignment:
                      target:
                        VarAccess:
                          name: i
                      value:
                        BinaryOp:
                          op: +
                          left:
                            VarAccess:
                              name: i
                          right:
                            Literal:
                              value: 1.0
                  ]"""

        ir = buildCompilationContext(code)._ast
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
        expected = """            Switch:
              expr:
                FieldAccess:
                  base:
                    VarAccess:
                      name: v
                  field: x
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
                            VarAccess:
                              name: i
                          value:
                            Literal:
                              value: 0.0
                        Break:
                      ]
                Case:
                  value:
                    Literal:
                      value: 1.0
                  body:
                    Block:
                      statements: [
                        Assignment:
                          target:
                            VarAccess:
                              name: i
                          value:
                            Literal:
                              value: 1.0
                        Break:
                      ]
                Case:
                  value: None
                  body:
                    Block:
                      statements: [
                        Assignment:
                          target:
                            VarAccess:
                              name: i
                          value:
                            UnaryOp:
                              op: -
                              operand:
                                Literal:
                                  value: 1.0
                              is_postfix: False
                        Break:
                      ]"""
        ir = buildCompilationContext(code)._ast
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")


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
                    VarAccess:
                      name: i
                  right:
                    Literal:
                      value: 12.0
              then_branch:
                Block:
                  statements: [
                    Assignment:
                      target:
                        VarAccess:
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
                        VarAccess:
                          name: i
                      value:
                        Literal:
                          value: 1.0
                  ]
            Label:
              name: label
            Assignment:"""

        ir = buildCompilationContext(code)._ast
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
                    VarAccess:
                      name: i
                  right:
                    Literal:
                      value: 12.0
              update:
                UnaryOp:
                  op: ++
                  operand:
                    VarAccess:
                      name: i
                  is_postfix: True
              body:"""

        ir = buildCompilationContext(code)._ast
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

        expected = """    Function:
      return_type: int
      name: main
      params: [
      ]
      body:
        Block:
          statements: [
            FunctionCall:
              name: foo
              args: [
              ]
            Return:
              value: None
          ]"""

        ir = buildCompilationContext(code)._ast
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")

    def test_phi_expr(self):
        code = """
        int main(int in) {
            int v1;
            int v2;
            int v3;
            if(in < 0) {
                v1 = 0;
            } else {
                v2 = 1;
            }
            v3 = phi(v1, v2);
            return;
        }
        """
        expected = """Assignment:
              target:
                VarAccess:
                  name: v3
              value:
                FunctionCall:
                  name: phi
                  args: [
                    VarAccess:
                      name: v1
                    VarAccess:
                      name: v2
                  ]"""

        ir = buildCompilationContext(code)._ast
        self.maxDiff = None
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            ir.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")
