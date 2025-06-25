# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver

class TestBasicBlockGraph(unittest.TestCase):

    def computeAndEmitSymbolTableForCode(self, code):
        cctx = Driver(code)
        symT = cctx.symbol_table

        retStr = ""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            symT.dump()
        retStr =  mock_stdout.getvalue().strip()
        return retStr

    def test_symbol_table_multiple_fcns(self):
        code = """
        int main() {
            int x;
            x = 1;
            if (x < 5) {
                x = x + 1;
            }
            return x;
        }

        int foo(int x, int y) {
            int y;
            {
                int xx;
                xx = 32;
            }
            y = 23;
            return y;
        }"""

        expected = """Symbol Table:
  x: <Symbol x: type=int, attrs={}>
  main: <Symbol main: type=int, attrs={'params': []}>
  y: <Symbol y: type=int, attrs={}>
  xx: <Symbol xx: type=int, attrs={}>
  foo: <Symbol foo: type=int, attrs={'params': [Variable(name='x', type_spec='int', attributes=None), Token('COMMA', ','), Variable(name='y', type_spec='int', attributes=None)]}>"""

        retStr = self.computeAndEmitSymbolTableForCode(code)
        self.assertIn(expected.strip(), retStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{retStr}||")

    def test_basic_blocks_for_simple_lookup(self):
        code = """
        int main() {
            int x;
            x = 1;
            if (x < 5) {
                x = x + 1;
            }
            return x;
        }

        int foo(int x, int y) {
            int y;
            {
                int xx;
                xx = 32;
            }
            y = 23;
            return y;
        }"""

        expected = """Symbol Table:
  x: <Symbol x: type=int, attrs={}>
  main: <Symbol main: type=int, attrs={'params': []}>
  y: <Symbol y: type=int, attrs={}>
  foo: <Symbol foo: type=int, attrs={'params': [Variable(name='x', type_spec='int', attributes=None), Token('COMMA', ','), Variable(name='y', type_spec='int', attributes=None)]}>"""

        cctx = Driver(code)
        symT = cctx.symbol_table
        retStr = str(symT.lookup("xx"))  
        expected = """<Symbol xx: type=int, attrs={}>"""
        self.assertIn(expected.strip(), retStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{retStr}||")


