from dataclasses import dataclass
from typing import List, Optional, Union

class IRNode:
    def dump(self, indent=0):
        pad = '  ' * indent
        print(f"{pad}{self.__class__.__name__}:")
        for field in self.__dataclass_fields__:
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

@dataclass
class Program(IRNode):
    declarations: List[IRNode]

@dataclass
class Function(IRNode):
    return_type: str
    name: str
    params: List['Variable']
    body: IRNode

@dataclass
class Variable(IRNode):
    name: str
    type_spec: Optional[str]
    attributes: dict = None

@dataclass
class BinaryOp(IRNode):
    op: str
    left: IRNode
    right: IRNode

@dataclass
class UnaryOp(IRNode):
    op: str
    operand: IRNode

@dataclass
class Assignment(IRNode):
    target: IRNode
    value: IRNode

@dataclass
class If(IRNode):
    condition: IRNode
    then_branch: IRNode
    else_branch: Optional[IRNode] = None

@dataclass
class While(IRNode):
    condition: IRNode
    body: IRNode

@dataclass
class DoWhile(IRNode):
    body: IRNode
    condition: IRNode

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
class Identifier(IRNode):
    name: str

@dataclass
class FieldAccess:
    base: 'IRNode'  # e.g., Identifier('s')
    field: str      # e.g., 'f'

@dataclass
class ArrayAccess:
    base: 'IRNode'  # e.g., Identifier('m')
    index: 'IRNode' # e.g., Literal(2)

@dataclass
class FunctionCall:
    name: str
    args: list
