from dataclasses import dataclass, field
from typing import Dict, Optional, Any

@dataclass
class Symbol:
    name: str
    type: str
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<Symbol {self.name}: type={self.type}, attrs={self.attributes}>"

class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent

    def dump(self, indent=0):
        pad = "  " * indent
        print(f"{pad}Symbol Table:")
        for name, sym in self.symbols.items():
            print(f"{pad}  {name}: {sym}")
        if self.parent:
            print(f"{pad}  ↑ Parent scope:")
            self.parent.dump(indent + 1)

    def define(self, symbol: Symbol):
        if symbol.name in self.symbols:
            raise RuntimeError(f"Symbol '{symbol.name}' already declared.")
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name) or (self.parent.lookup(name) if self.parent else None)

    def __repr__(self):
        return "\n".join(f"{name}: {sym}" for name, sym in self.symbols.items())

class ScopedSymbolTableManager:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope

    def push_scope(self):
        self.current_scope = SymbolTable(parent=self.current_scope)

    def pop_scope(self):
        if self.current_scope.parent is None:
            raise RuntimeError("Can't pop the global scope.")
        self.current_scope = self.current_scope.parent
