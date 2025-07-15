# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from lark import Token
from io import StringIO
from unittest.mock import patch
from dataclasses import dataclass
from typing import List, Optional, Union
from hintzCompiler.src.symbol_table import SymbolTable, Symbol
from dataclasses import dataclass, field

@dataclass(kw_only=True)
class IRNode:

    _parent: Optional["IRNode"] = field(default=None, repr=False)
    _cfgNodeId: int = field(default=-1, repr=False)
    _ssaIsPhi: bool = field(default=False, repr=False)

    def dump(self, indent=0):
        pad = '  ' * indent
        print(f"{pad}{self.__class__.__name__}:")
        for field in self.__dataclass_fields__:

            if field.startswith("_"):
                continue

            value = getattr(self, field)
            if isinstance(value, list):
                print(f"{pad}  {field}: [")
                for v in value:
                    if isinstance(v, IRNode):
                        v.dump(indent + 2)
                    else:
                        print(f"{pad}    {v}")
                print(f"{pad}  ]")
            elif isinstance(value, IRNode):
                print(f"{pad}  {field}:")
                value.dump(indent + 2)
            else:
                print(f"{pad}  {field}: {value}")

    def toString(self):
        retVal = ""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.dump()
            retVal = mock_stdout.getvalue().strip()
        return retVal;

    def rootStmt(self):
        higherLevel = self._parent
        if higherLevel is None : return self

        prev = None
        while higherLevel is not None:
            prev = higherLevel
            higherLevel = higherLevel._parent
        return prev

##################################################################################

@dataclass
class Program(IRNode):
    declarations: List[IRNode]

@dataclass
class Function(IRNode):
    return_type: str
    name: str
    params: List['Variable']
    body: IRNode
    symbolTable: SymbolTable
    declaredVarsList: List['Variable'] = field(repr=False)

@dataclass
class Variable(IRNode):
    name: str
    type_spec: Optional[str]
    attributes: dict = field(default_factory=dict)
    _symbol: Optional[Symbol] = field(default=None, repr=False)
    _ssaIsVersionOfAVar: bool = field(default=False, repr=False)
    _ssaVersions: List["Variable"] = field(default_factory=list, repr=False)
    _ssaUnversioned: Optional["Variable"] = field(default=None, repr=False)

@dataclass
class BinaryOp(IRNode):
    op: str
    left: IRNode
    right: IRNode

@dataclass
class UnaryOp(IRNode):
    op: Token
    operand: IRNode
    is_postfix: bool = False

@dataclass
class Assignment(IRNode):
    target: IRNode
    value: IRNode

@dataclass
class If(IRNode):
    condition: IRNode
    then_branch: IRNode
    else_branch: Optional[IRNode] = None

    def __str__(self):
        return f"If {self.condition}"

@dataclass
class While(IRNode):
    condition: IRNode
    body: IRNode

    def __str__(self):
        return f"While {self.condition}";

@dataclass
class DoWhile(IRNode):
    body: IRNode
    condition: IRNode

    def __str__(self):
        return f"DoWhile {self.condition}";

@dataclass
class Return(IRNode):
    value: Optional[IRNode]

@dataclass
class Block(IRNode):
    statements: List[IRNode]

@dataclass
class Call(IRNode):
    func: str
    args: List[IRNode]

@dataclass
class Literal(IRNode):
    value: Union[int, float, str]

@dataclass
class VarAccess(IRNode):
    name: str
    _var: Optional[Variable] = field(default=None, repr=False)
    _ssaReachingDef : Optional["VarAccess"] = field(default=None, repr=False)

@dataclass
class FieldAccess(IRNode):
    base: 'IRNode'  # e.g., Identifier('s')
    field: str      # e.g., 'f'

@dataclass
class ArrayAccess(IRNode):
    base: 'IRNode'  # e.g., Identifier('m')
    index: 'IRNode' # e.g., Literal(2)

@dataclass
class FunctionCall(IRNode):
    name: str
    args: list

@dataclass
class For(IRNode):
    init: Optional[IRNode]
    condition: Optional[IRNode]
    update: Optional[IRNode]
    body: IRNode

    def __str__(self):
        return "for(init; cond; update)"

@dataclass
class Goto(IRNode):
    label: str

@dataclass
class Label(IRNode):
    name: str

@dataclass
class Switch(IRNode):
    expr: IRNode
    cases: List["Case"]

    def __str__(self):
        return f"switch {self.expr}"

@dataclass
class Case(IRNode):
    value: Optional[IRNode]  # None for default
    body: Block

@dataclass
class Break(IRNode):
    pass

@dataclass
class SwitchJoin(IRNode):
    pass

@dataclass
class IfJoin(IRNode):
    pass

@dataclass
class DoJoin(IRNode):
    pass
