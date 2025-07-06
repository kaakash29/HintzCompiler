from hintzCompiler.src.cfg import *
from hintzCompiler.src.ir_nodes import IRNode, Goto, Label, Block, Function, Return, If, While, DoWhile, For, Switch, Break, SwitchJoin, IfJoin, DoJoin 

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
        cfg.version += 1

    @staticmethod
    def deleteNode(cfg:ControlFlowGraph, nodeIndex:int):
        assert(0 <= nodeIndex < len(cfg.nodes))
        nodeToDelete = cfg.nodes[nodeIndex]
        
        for predNode in nodeToDelete.predecessors:
            predNode.successors = nodeToDelete.successors

        for succNode in nodeToDelete.successors:
            succNode.predecessors = nodeToDelete.predecessors
        
        cfg.nodes.remove(nodeToDelete)

