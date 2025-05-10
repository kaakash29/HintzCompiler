# Hintz Compiler

A lightweight compiler for a C89-inspired language with support for:
- Constants and variables
- `int`, `float`, `double`, `char`, `void`, `matrix` types
- Control structures: `if`, `while`, `do-while`, `return`
- Structs and multidimensional arrays
- Function calls and definitions (including `void`)
- Modular compilation via `#include` support
- Intermediate representation (IR) and symbol table generation
- Unit testing support

---

## 🛠 Usage

### Compile a source file and dump IR:

```bash
python compiler.py path/to/file.c89
