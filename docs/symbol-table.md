# Symbol Table Format

## Overview

The symbol table keeps track of all declared identifiers (variables, structs, functions) within their lexical scopes.
It supports nested scopes and stores attributes for type checking and semantic analysis.

---

## Symbol Table Structure

```python
SymbolTable:
  symbols: Dict[str, Symbol]
  parent: SymbolTable | None
```

- Each function or compound block introduces a new scope.
- Lookups fall back to parent scopes if a symbol is not found.

---

## `Symbol`

```python
Symbol(
  name: str,
  type: str,               # "int", "float", "function", "struct", etc.
  attributes: dict         # additional metadata (e.g., fields, parameters)
)
```

---

## Example Symbol Table Output

```text
Symbol Table:
  Vec2: <Symbol Vec2: type=struct, attrs={'fields': {'x': 'int', 'y': 'float'}}>
  main: <Symbol main: type=int, attrs={'params': []}>
  x: <Symbol x: type=int, attrs={}>
```

---

## Struct Symbol Example

```python
Symbol(
  name='Vec2',
  type='struct',
  attributes={
    'fields': {
      'x': 'int',
      'y': 'float'
    }
  }
)
```

---

## Function Symbol Example

```python
Symbol(
  name='main',
  type='int',
  attributes={
    'params': []
  }
)
```

---

## Scope Nesting Example

```python
GlobalScope
├── Vec2
├── main
    └── LocalScope
        ├── x
        ├── y
```
