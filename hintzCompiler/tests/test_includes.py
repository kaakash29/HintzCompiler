# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import os
import unittest
from typing import cast
from hintzCompiler.compiler import Driver
from hintzCompiler.preprocessor import Preprocessor
from hintzCompiler.src.ir_nodes import Function, Block

class TestCompiler(unittest.TestCase):
    def test_include_simplest(self):
 
        # Now preprocess the file
        fullIncludePath = os.path.join(os.path.dirname(__file__), "..", "..", "includes")
        preprocessor = Preprocessor(include_paths=[fullIncludePath])

        # Write the source file that uses the include
        test_file_path = "tests/temp_test.hz"
        with open(test_file_path, "w") as f:
            f.write("""
            #include "utils.hz"
            int main() {
                int x;
                x = 5;
            }
            """)

        code = preprocessor.preprocess(test_file_path)
        cctx = Driver(code)

        prog = cctx.ast
        mainF = cast(Function, prog.declarations[1])
        block = cast(Block, mainF.body)

        self.assertTrue(any(stmt.__class__.__name__ == "Assignment" for stmt in block.statements)
        )


