from tests.assert_utils import assertContains
# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import unittest
from io import StringIO
from unittest.mock import patch
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.compiler import parseAndBuildCompilationContextFromInput
from hintzCompiler.src.basic_blocks import *
from hintzCompiler.src.readWriteAnalyzer import ReadWriteAnalyzer

class TestReadWriteAnalyzer(unittest.TestCase):

    def rwaAsStr(self, code):
        cctx = parseAndBuildCompilationContextFromInput(code)
        cfg = cctx.cfgs[0]
        rwa = ReadWriteAnalyzer(cfg)
        rwaAsStr = ""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            rwa.dump()
        rwaAsStr = mock_stdout.getvalue().strip()
        return rwaAsStr

    #@unittest.skip("Tmp")
    def test_rwa_basic(self):
        code = """
        int main() {
            int a;
            int b;
            int c;

            c = a;
            a = b;
            b = c;
        }
        """

        expected = """
[0] reads: None, writes: None
[1] reads: None, writes: None
[2] reads: None, writes: None
[3] reads: [a], writes: [c]
[4] reads: [b], writes: [a]
[5] reads: [c], writes: [b]"""

        rwaS = self.rwaAsStr(code)
        assertContains(rwaS, expected)


    #@unittest.skip("Tmp")
    def test_rwa_structs(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            v.x = 1;
        } 
        """

        expected = """
[0] reads: None, writes: None
[1] reads: None, writes: [v->x]
"""

        rwaS = self.rwaAsStr(code)
        assertContains(rwaS, expected)


    def test_rwa_structs_2(self):
        code = """
        struct Vec2 {
            int x;
        };

        int main() {
            struct Vec2 v;
            int y;
            y = v.x;
        } 
        """

        expected = """
[0] reads: None, writes: None
[1] reads: None, writes: None
[2] reads: [v->x], writes: [y]"""

        rwaS = self.rwaAsStr(code)
        assertContains(rwaS, expected)

    def test_rwa_matrix(self):
        code = """
        int main() {
            int v[10];
            int i;
            int y;
            for(i=0;i<5;i++){
                v[i] = i;
            }
            v[0] = 0;
            y = v[5];
        } 
        """

        expected = """[0] reads: None, writes: None
[1] reads: None, writes: None
[2] reads: None, writes: None
[3] reads: None, writes: None
[4] reads: None, writes: [i]
[5] reads: [i], writes: None
[6] reads: [i], writes: [v->UNKWN]
[7] reads: [i], writes: None
[8] reads: None, writes: [v->0.0]
[9] reads: [v->5.0], writes: [y]"""

        rwaS = self.rwaAsStr(code)
        assertContains(rwaS, expected)


    def test_rwa_struct_matrix(self):
        code = """
        struct Vec2 {
            int x[3];
        };

        int main() {
            struct Vec2 v;
            int i;
            int y;

            for(i=0;i<5;i++){
                v.x[0] = i;
            }
            v.x[5] = 0;
            y = v.x[5];
        } 
        """

        expected = """[0] reads: None, writes: None
[1] reads: None, writes: None
[2] reads: None, writes: None
[3] reads: None, writes: None
[4] reads: None, writes: [i]
[5] reads: [i], writes: None
[6] reads: [i], writes: [v->x->0.0]
[7] reads: [i], writes: None
[8] reads: None, writes: [v->x->5.0]
[9] reads: [v->x->5.0], writes: [y]"""

        rwaS = self.rwaAsStr(code)
        assertContains(rwaS, expected)

    def test_rwa_phi_expr(self):
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

        expected = """[0] reads: None, writes: None
[1] reads: None, writes: None
[2] reads: None, writes: None
[3] reads: [in], writes: None
[4] reads: None, writes: None
[5] reads: None, writes: [v1]
[6] reads: None, writes: [v2]
[7] reads: [v1][v2], writes: [v3]
[8] reads: None, writes: None"""

        rwaS = self.rwaAsStr(code)
        assertContains(rwaS, expected)

"""
The readWriteAnalyzer is only covered 86% and there is a lot of scope for writing unit tests for the RWA
especially related to memory exprs appearing at different places in the CFG like if conditions, 
while checks, for init etc.
"""
