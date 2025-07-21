# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from typing import Set, Dict, cast
from ordered_set import OrderedSet
from hintzCompiler.src.ir_nodes import *
from dataclasses import dataclass, field

##############################################################################################

@dataclass
class MemAccess:

    def toStr(self) -> str:
        return ""

@dataclass
class MemAccessStructField(MemAccess):
    fieldName:str

    def toStr(self):
        retVal = f"{self.fieldName}"
        return retVal

@dataclass 
class MemAccessArrayElem(MemAccess):
    linearizedElemIndex:int

    def toStr(self):
        retVal = f"{self.linearizedElemIndex}" if self.linearizedElemIndex >= 0 else "UNKWN"
        return retVal

@dataclass
class MemAccessVariable(MemAccess):
    varname:str
    _var:Variable = field(repr=False)

    def toStr(self):
        return self.varname

@dataclass
class ReadOcc:
    baseVar: Variable
    memAccessPath: List[MemAccess]
    irVarAccessNode: VarAccess

    def toStr(self):
        ret = "["
        for i, axs in enumerate(self.memAccessPath):
            ret += axs.toStr()
            if i < len(self.memAccessPath) - 1:
                ret += "->"
        ret += "]"
        return ret


@dataclass
class WriteOcc:
    baseVar: Variable
    memAccessPath: List[MemAccess]
    irVarAccessNode: VarAccess

    def toStr(self):
        ret = "["
        for i, axs in enumerate(self.memAccessPath):
            ret += axs.toStr()
            if i < len(self.memAccessPath) - 1:
                ret += "->"
        ret += "]"
        return ret


##########################################################################################################################


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
        while not isinstance(smMemE, VarAccess):

            if isinstance(smMemE, FieldAccess):
                memAccessPattern.append(MemAccessStructField(smMemE.field))
                base = smMemE.base
                smMemE = base

            elif isinstance(smMemE, ArrayAccess):
                if  isinstance(smMemE.index, Literal):
                    memAccessPattern.append(MemAccessArrayElem(smMemE.index.value)) #pyright: ignore
                else:
                    memAccessPattern.append(MemAccessArrayElem(-1))

                base = smMemE.base
                smMemE = base

            elif isinstance(smMemE, FunctionCall):
                break

            else:
                print(f"Unknown memory access type: {smMemE}")
                break

        if isinstance(smMemE, VarAccess):
            if smMemE._var is None:
                RuntimeError("Ran into a Variable Access where the variable is UNKNOWN")
            assert(smMemE._var is not None)
            memAccessPattern.append(MemAccessVariable(varname=smMemE.name, _var=smMemE._var))
        else:
            memAccessPattern = []
        
        memAccessPattern.reverse();
        return smMemE, memAccessPattern

    def _get_reads_and_writes(self, stmt: IRNode) -> Dict[str, List[str]]:
        reads = []
        writes = []

        def visit(node, memOccPath):

            if isinstance(node, VarAccess):
                assert(node._var is not None)
                memOccPath.append(MemAccessVariable(node.name, _var=node._var))
                memOccPath.reverse()
                readO = ReadOcc(node._var, memOccPath, node)
                reads.append(readO)

            elif isinstance(node, Assignment):
                if isinstance(node.target, (VarAccess, FieldAccess, ArrayAccess)):
                    simplifiedAccess, writeMemOccPath = self._simplifyMemoryAccess(node.target)
                    if isinstance(simplifiedAccess, VarAccess):
                        assert(simplifiedAccess._var is not None)
                        writeO = WriteOcc(simplifiedAccess._var, writeMemOccPath, simplifiedAccess)
                        writes.append(writeO)
                visit(node.value, [])

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

            elif isinstance(node, While):
                visit(node.condition, [])

            elif isinstance(node, DoWhile):
                visit(node.condition, [])

            elif isinstance(node, For):
                pass

            elif isinstance(node, Switch):
                visit(node.expr, [])

            elif isinstance(node, Return):
                if node.value:
                    visit(node.value, [])

            elif isinstance(node, (Goto, Label, Break)):
                pass

            elif isinstance(node, ArrayAccess):
                if  isinstance(node.index, Literal):
                    memOccPath.append(MemAccessArrayElem(node.index.value)) #pyright: ignore
                else:
                    memOccPath.append(MemAccessArrayElem(-1))
                visit(node.base, memOccPath)
                visit(node.index, [])

            elif isinstance(node, FieldAccess):
                memOccPath.append(MemAccessStructField(node.field))
                visit(node.base, memOccPath)

        visit(stmt, [])
        return {'reads': reads, 'writes': writes}

    def get_reads(self, node_id: int) -> Set[ReadOcc]:
        return self.analysis.get(node_id, {}).get('reads', set())

    def get_writes(self, node_id: int) -> Set[WriteOcc]:
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
