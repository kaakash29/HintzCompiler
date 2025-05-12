import unittest
from hintzCompiler.compiler import compile_source  # You’ll implement this function

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
        print(ir.to_string())
        self.assertTrue("if" in str(ir))
