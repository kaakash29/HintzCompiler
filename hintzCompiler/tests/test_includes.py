import os
import unittest
from hintzCompiler.compiler import compile_source
from hintzCompiler.preprocessor import Preprocessor

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
        ir = compile_source(code)

        # Assert that there is an assignment statement in the body of main
        body_stmts = ir.declarations[1].body.statements  # index 1 assumes helper comes first
        self.assertTrue(
            any(stmt.__class__.__name__ == "Assignment" for stmt in body_stmts)
        )


