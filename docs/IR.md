# Intermediate Representation (IR) Format

## Overview

The IR is a structured, tree-like representation of the parsed C89-inspired program.  
It serves as the foundation for semantic analysis, optimization, and eventual code generation.

---

## Top-Level IR Node

```python
Program:
  declarations: List[StructDef | Function | Variable]
```

---

## Node Types

### `Variable`

```python
Variable(
  name: str,
  type_spec: str,             # e.g., "int", "float", "Vec2"
  attributes: dict | None     # e.g., {'size': 3} for arrays
)
```

---

### `Function`

```python
Function(
  return_type: str,
  name: str,
  params: List[Variable],
  body: Block
)
```

---

### `Block`

```python
Block(
  statements: List[Variable | Assignment | FunctionCall | If | While | DoWhile | Return]
)
```

---

### `Assignment`

```python
Assignment(
  target: Identifier | FieldAccess | ArrayAccess,
  value: Expression
)
```

---

### `FunctionCall`

```python
FunctionCall(
  name: str,
  args: List[Expression]
)
```

---

### `BinaryOp`

```python
BinaryOp(
  op: str,         # e.g., "+", "-", "*", "==", etc.
  left: Expression,
  right: Expression
)
```

---

### `Identifier`, `Literal`

```python
Identifier(name: str)
Literal(value: int | float | str)
```

---

### `FieldAccess` and `ArrayAccess`

```python
FieldAccess(
  base: Expression,
  field: str
)

ArrayAccess(
  base: Expression,
  index: Expression
)
```

---

## Example IR Output

```text
Function:
  return_type: int
  name: main
  params: []
  body:
    Block:
      statements:
        Variable(name='x', type_spec='int')
        Assignment:
          target: Identifier(name='x')
          value: Literal(value=5.0)
```
