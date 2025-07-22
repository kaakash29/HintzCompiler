from dataclasses import is_dataclass, fields
from typing import Callable, Iterator
from hintzCompiler.src.ir_nodes import IRNode  # Adjust import paths if needed

class IRNodeIterator:
    def __init__(self, root: IRNode, predicate: Callable[[IRNode], bool]):
        self.root = root
        self.predicate = predicate

    def __iter__(self) -> Iterator[IRNode]:
        yield from self._visit(self.root)

    def _visit(self, node: IRNode) -> Iterator[IRNode]:

        if self.predicate(node):
            yield node

        elif isinstance(node, list):
            for item in node:
                if isinstance(item, IRNode):
                    yield from self._visit(item)

        elif is_dataclass(node):
            for f in fields(node):
                
                if f.name.startswith("_"):
                    continue

                attr = getattr(node, f.name)
                if isinstance(attr, IRNode) or isinstance(attr, list):
                    yield from self._visit(attr)

