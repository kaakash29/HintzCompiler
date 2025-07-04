# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver

class TestSymbolTable(unittest.TestCase):

    def computeAndEmitSymbolTableForCode(self, code):
        cctx = Driver(code)
        cfgs = cctx.cfgs
        retStr = ""
        for cfg in cfgs:
            symT = cfg.fcn.symbolTable
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                print(f"\n")
                symT.dump()
            retStr +=  mock_stdout.getvalue()
        
        return retStr

    def test_symbol_table_multiple_fcns(self):
        code = """

        int G; 
        int main() {
            int x;
            x = 1;
            if (x < 5) {
                x = x + 1;
            }
            return x;
        }

        int foo(int a, int b) {
            int y;
            int xx;
            xx = 32;
            y = 23;
            return y;
        }"""

        expected = """Symbol Table [main]:
  x: <Symbol x: type=int, attrs={}>
  ↑ Parent scope:
  Symbol Table [global]:
    G: <Symbol G: type=int, attrs={}>
    main: <Symbol main: type=int, attrs={'params': []}>
    foo: <Symbol foo: type=int, attrs={'params': [Variable(name='a', type_spec='int', attributes={'isiovar': True}), Variable(name='b', type_spec='int', attributes={'isiovar': True})]}>


Symbol Table [foo]:
  y: <Symbol y: type=int, attrs={}>
  xx: <Symbol xx: type=int, attrs={}>
  a: <Symbol a: type=int, attrs={}>
  b: <Symbol b: type=int, attrs={}>
  ↑ Parent scope:
  Symbol Table [global]:
    G: <Symbol G: type=int, attrs={}>
    main: <Symbol main: type=int, attrs={'params': []}>
    foo: <Symbol foo: type=int, attrs={'params': [Variable(name='a', type_spec='int', attributes={'isiovar': True}), Variable(name='b', type_spec='int', attributes={'isiovar': True})]}>"""

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
            int xx;
            xx = 32;
            y = 23;
            return y;
        }"""

        expected = """Symbol Table:
  x: <Symbol x: type=int, attrs={}>
  main: <Symbol main: type=int, attrs={'params': []}>
  y: <Symbol y: type=int, attrs={}>
  foo: <Symbol foo: type=int, attrs={'params': [Variable(name='x', type_spec='int', attributes=None), Token('COMMA', ','), Variable(name='y', type_spec='int', attributes=None)]}>"""

        cctx = Driver(code)
        cfgMain = cctx.cfgs[1]
        fcnMain = cfgMain.fcn
        symT = fcnMain.symbolTable
        retStr = str(symT.lookup("xx"))  
        expected = """<Symbol xx: type=int, attrs={}>"""
        self.assertIn(expected.strip(), retStr, msg=f"\n\n[[-- FAILED --]]\n\nExpecting:||{expected.strip()}\nActual:||{retStr}||")


