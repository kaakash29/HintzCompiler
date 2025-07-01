# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from typing import Set, Dict
from ordered_set import OrderedSet
from hintzCompiler.src.ir_nodes import *

@dataclass
class MemAccess:
    def toStr(self):
        retVal = ""
        for field in self.__dataclass_fields__:
            retVal += f"{getattr(self, field)}"
        return retVal

@dataclass
class MemAccessStructField(MemAccess):
    fieldName:str

@dataclass 
class MemAccessArrayElem(MemAccess):
    linearizedElemIndex:int

    def toStr(self):
        retVal = f"{self.linearizedElemIndex}" if self.linearizedElemIndex >= 0 else "UNKWN"
        return retVal

@dataclass
class MemAccessVariable(MemAccess):
    varname:str

@dataclass
class ReadOcc:
    baseVar:str
    memAccess:List

    def toStr(self):
        ret = "["

        for i, axs in enumerate(self.memAccess):
            ret += axs.toStr()
            if i < len(self.memAccess) - 1:
                ret += "->"
        ret += "]"
        return ret

    def __eq__(self, other):
        return isinstance(other, ReadOcc)\
           and self.baseVar == other.baseVar\
           and self.memAccess == other.memAccess

    def __hash__(self):
        return hash(self.toStr())

@dataclass
class WriteOcc:
    baseVar:str
    memAccess:List[MemAccess]
    def toStr(self):
        ret = "["

        for i, axs in enumerate(self.memAccess):
            ret += axs.toStr()
            if i < len(self.memAccess) - 1:
                ret += "->"
        ret += "]"
        return ret

    def __eq__(self, other):
        return isinstance(other, WriteOcc)\
           and self.baseVar == other.baseVar\
           and self.memAccess == other.memAccess

    def __hash__(self):
        return hash(self.toStr())

class ReadWriteAnalyzer:

    def __init__(self, cfg):
        self.cfg = cfg
        self.analysis = {}
        self._run()

    def _run(self):
        for node in self.cfg.nodes:
            self.analysis[node.id] = self._get_reads_and_writes(node.stmt)
    

    def _simplifyMemoryAccess(self, smMemE:IRNode):
        memAccessPattern = []
        base = None
        while not isinstance(smMemE, Identifier):

            if isinstance(smMemE, FieldAccess):
                memAccessPattern.append(MemAccessStructField(smMemE.field))
                base = smMemE.base
                smMemE = base

            if isinstance(smMemE, ArrayAccess):
                if  isinstance(smMemE.index, Literal):
                    memAccessPattern.append(MemAccessArrayElem(smMemE.index.value))
                else:
                    memAccessPattern.append(MemAccessArrayElem(-1))

                base = smMemE.base
                smMemE = base

            if isinstance(smMemE, FunctionCall):
                break
    
        #print(f"smMemE = {smMemE}")
        memAccessPattern.append(MemAccessVariable(varname=smMemE.name))
        memAccessPattern.reverse();
        return smMemE, memAccessPattern

    def _get_reads_and_writes(self, stmt: IRNode) -> Dict[str, Set[str]]:
        reads = OrderedSet([])
        writes = OrderedSet([])

        def visit(node, memOccPath):

            if isinstance(node, Identifier):
                memOccPath.append(MemAccessVariable(node.name))
                memOccPath.reverse()
                readO = ReadOcc(node.name, memOccPath)
                reads.add(readO)

            elif isinstance(node, Assignment):
                if isinstance(node.target, (Identifier, FieldAccess, ArrayAccess)):
                    simplifiedAccess, memOcc = self._simplifyMemoryAccess(node.target)
                    writeO = WriteOcc(simplifiedAccess.name, memOcc)
                    writes.add(writeO)
                visit(node.value, memOccPath)

            elif isinstance(node, BinaryOp):
                visit(node.left, [])
                visit(node.right, [])

            elif isinstance(node, UnaryOp):
                visit(node.operand, [])

            elif isinstance(node, FunctionCall):
                for arg in node.args:
                    if isinstance(arg, IRNode):
                        visit(arg, [])

            elif isinstance(node, If):
                visit(node.condition, [])
                visit_block(node.then_branch)
                if node.else_branch:
                    visit_block(node.else_branch)

            elif isinstance(node, While):
                visit(node.condition, []) #should a new memory be started here ?
                visit_block(node.body)

            elif isinstance(node, DoWhile):
                visit(node.condition, [])
                visit_block(node.body, [])

            elif isinstance(node, For):
                if node.init:
                    visit(node.init, [])
                if node.condition:
                    visit(node.condition, [])
                if node.update:
                    visit(node.update, [])
                visit_block(node.body)

            elif isinstance(node, Switch):
                visit(node.expr, [])
                for case in node.cases:
                    visit_block(case.body)

            elif isinstance(node, Case):
                visit_block(node.body)

            elif isinstance(node, Return):
                if node.value:
                    visit(node.value, [])

            elif isinstance(node, Block):
                visit_block(node)

            elif isinstance(node, (Goto, Label, Break)):
                pass

            elif isinstance(node, list): # what is this switch for ?
                for sub in node:
                    visit(sub, [])

            elif isinstance(node, ArrayAccess):
                if  isinstance(node.index, Literal):
                    memOccPath.append(MemAccessArrayElem(node.index.value))
                else:
                    memOccPath.append(MemAccessArrayElem(-1))
                visit(node.base, memOccPath)
                visit(node.index, [])

            elif isinstance(node, FieldAccess):
                memOccPath.append(MemAccessStructField(node.field))
                visit(node.base, memOccPath)

            elif isinstance(node, IRNode):
                for value in vars(node).values():
                    if isinstance(value, IRNode) or isinstance(value, list):
                        visit(value)

        def visit_block(block: Block):
            if block:
                for s in block.statements:
                    visit(s, [])

        visit(stmt, [])
        return {'reads': reads, 'writes': writes}

    def get_reads(self, node_id: int) -> Set[str]:
        return self.analysis.get(node_id, {}).get('reads', set())

    def get_writes(self, node_id: int) -> Set[str]:
        return self.analysis.get(node_id, {}).get('writes', set())

    def dump(self):
        for node_id, rw in self.analysis.items():
            reads = rw['reads']
            writes = rw['writes']
            readStr = ""
            writeStr = ""
            if len(reads) == 0: readStr += "None"
            for read in reads:
                readStr += f"{read.toStr()}";

            if len(writes) == 0: writeStr += "None"
            for write in writes:
                writeStr += f"{write.toStr()}"

            print(f"[{node_id}] reads: {readStr}, writes: {writeStr}")

