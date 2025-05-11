# Hintz Compiler

A lightweight compiler for a C89-inspired language, supporting:
- Constants, variables, and types (`int`, `float`, `double`, `char`, `void`, `matrix`)
- Control flow: `if`, `while`, `do-while`, `return`
- Structs and array access
- Function calls and definitions (including `void`)
- `#include` support (planned)
- Symbol table and intermediate representation (IR) generation
- Command-line interface with custom `.hz` extension

---

## 🛠 Usage

### Run from source
```bash
python hintzcompiler/compiler.py path/to/file.hz
```

### Run as installed CLI
```bash
hintz file.hz -s out.hzir
```

---

## ⚙️ CLI Options

- `-s <file>`: Save IR dump to a file
- `-n`: Enable debug mode (dumps parse tree and symbol table)
- Input must have `.hz` extension

---

## 🧪 Run Unit Tests

```bash
python -m unittest discover -s tests
```

---

## 📦 Installation (Development Mode)

To install Hintz Compiler locally for development and enable the `hintz` command globally:

1. Clone the repository:
```bash
git clone https://github.com/kaakash29/HintzCompiler.git
cd HintzCompiler
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install in editable mode:
```bash
pip install -e .
```

You can now compile `.hz` files from anywhere:
```bash
hintz program.hz -s output.hzir -n
```

---

## 📁 Project Layout

```
HintzCompiler/
├── hintzcompiler/
│   ├── compiler.py        # CLI entry point
│   ├── src/
│   │   └── transformer.py # IR generation
│   └── __init__.py
├── grammar/
│   └── c89.lark           # Lark grammar
├── tests/
│   ├── test_basic.py
│   └── test_sample.hz
├── setup.py
├── pyproject.toml
└── README.md
```

---

## 📚 Docs

- [IR Format](docs/IR.md)
- [Symbol Table](docs/SymbolTable.md)

---

## 🧾 Example

### Sample `test_sample.hz` source

```c
struct Vec2 {
    int x;
    float y;
};

int main() {
    int a;
    struct Vec2 v;
    a = 42;
    v.x = a;
    return 0;
}
```

### Example IR Output

```
Program:
  declarations: [
    Function:
      return_type: int
      name: main
      params: [
      ]
      body:
        Block:
          statements: [
            Variable(name='a', type_spec='int')
            Variable(name='v', type_spec='Vec2')
            Assignment:
              target:
                Identifier(name='a')
              value:
                Literal(value=42)
            Assignment:
              target:
                FieldAccess(
                  base=Identifier(name='v'),
                  field='x'
                )
              value:
                Identifier(name='a')
            Return:
              value:
                Literal(value=0)
          ]
  ]
```

Generate this using:

```bash
hintz tests/test_sample.hz -n
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

