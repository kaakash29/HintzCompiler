# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from hintzCompiler.src.cfg import *
from hintzCompiler.src.ir_nodes import *
from dataclasses import fields
class EditCfg:

    @staticmethod
    def addNodeAfter(cfg:ControlFlowGraph, nodeIndex:int, nodeToInsert:CFGNode):
        assert(0 <= nodeIndex < len(cfg.nodes))
        nodeBefore = cfg.nodes[nodeIndex] 
        for succNode in nodeBefore.successors:
            nodeToInsert.add_successor(succNode)

        nodeBefore.successors = [nodeToInsert]
        nodeToInsert.add_predecessor(nodeBefore)
        cfg.nodes.append(nodeToInsert)
        cfg.stmt_id += 1
        cfg._version += 1

    @staticmethod
    def deleteNode(cfg:ControlFlowGraph, nodeIndex:int):
        assert(0 <= nodeIndex < len(cfg.nodes))
        nodeToDelete = cfg.nodes[nodeIndex]
        
        for predNode in nodeToDelete.predecessors:
            predNode.successors = nodeToDelete.successors

        for succNode in nodeToDelete.successors:
            succNode.predecessors = nodeToDelete.predecessors
        
        cfg.nodes.remove(nodeToDelete)

    @staticmethod
    def addNodeBefore(cfg:ControlFlowGraph, nodeIndex:int, nodeToInsert:CFGNode):
        assert(0 <= nodeIndex < len(cfg.nodes))
        nodeAfter = cfg.nodes[nodeIndex]

        for predNode in nodeAfter.predecessors:
            predNode.successors = [nodeToInsert]
        
        nodeToInsert.predecessors = nodeAfter.predecessors
        nodeAfter.predecessors = [nodeToInsert]
        nodeToInsert.successors = [nodeAfter]
        cfg.nodes.append(nodeToInsert)
        cfg.stmt_id += 1
        cfg._version += 1

    @staticmethod
    def createNewLocalVar(cfg: ControlFlowGraph, varName: str, varType: str, varAttr: dict):
        # add to local symbol table
        # add to cfg declared vars
        # add a decl stmt for the variable -- we dont need to do this,
        #                                     only when the cfg needs emitting do we need the declaration,
        #                                     this prevents dirtying the cfg unnecessarily.

        newVarSymbol = Symbol(varName, varType, varAttr)
        cfg.symbol_table.define(newVarSymbol)
        newVar = Variable(varName, varType, varAttr, newVarSymbol)
        cfg.fcn.declaredVarsList.append(newVar)
        return newVar
    
    @staticmethod
    def swapIntoCfg(newIRNode: IRNode, oldIRNode: IRNode):
        newIRNode._parent = oldIRNode._parent
        assert(oldIRNode._parent is not None)
        for field in fields(oldIRNode._parent):
            pchild = getattr(oldIRNode._parent, field.name)
            if pchild == oldIRNode:
                setattr(oldIRNode._parent, field.name, newIRNode)
                oldIRNode._parent = None
                return True
        return False

    @staticmethod
    def addInputToPhi(newAccess : IRNode, phi: FunctionCall):
        phi.args.append(newAccess)
        newAccess._parent = phi
        


