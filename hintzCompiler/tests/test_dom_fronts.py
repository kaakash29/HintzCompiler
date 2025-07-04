# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import Driver
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers


class TestDominanceFrontiers(unittest.TestCase):

    def test_domFronts_basic(self):
        code = """
        int main(int in) {
            int x;

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

        expected = """BB1 -> DF:[ ]
BB2 -> DF:[ BB3 ]
BB3 -> DF:[ ]
BB4 -> DF:[ BB3 ]"""

        cctx = Driver(code)
        bbg0 = cctx.bbgs[0]
        doms = Dominators(bbg0)
        domFs = DominanceFrontiers(doms)
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            domFs.dump()
            self.assertIn(expected.strip(), mock_stdout.getvalue().strip(), msg=f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||\n\nActual:||{mock_stdout.getvalue().strip()}||")



