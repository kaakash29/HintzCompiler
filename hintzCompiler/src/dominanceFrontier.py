# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from typing import List
from ordered_set import OrderedSet
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.EditCfg import EditCfg
from hintzCompiler.src.cfg import ControlFlowGraph, CFGNode
from hintzCompiler.src.readWriteAnalyzer import ReadWriteAnalyzer
from hintzCompiler.src.StmtBuilderFacade import HintzStatementBuilder
from hintzCompiler.src.basic_blocks import BasicBlock, BasicBlockGraph


class DominanceFrontiers:

    #public:

    """
    A do-it-all constructor.
    """
    def __init__(self, dominators):
        self.doms   = dominators
        self.DFs    = {}
        self.computeDFs()
        self.computePhiLocsForVar()
        self.renameVersionsOfVars()


    def dump(self):
        
        for key in self.DFs:
            keyStr = f"{key.name}"
            valueStr = f"DF:[ "
            for value in self.DFs[key]:
                valueStr += f"{value.name} "
            valueStr += "]"
            print(f"{keyStr} -> {valueStr}")

    #private:

    """
    Algorithm 3.2 from SSA book:
    Block B belongs to the dominance frontier of block A if
    1. A does not strictly dominate B, but,
    2. A dominates an immediate predecessor of B.
    """
    def computeDFs(self):
        #naive implementation for Dominance Frontier
        for a in self.doms.bblist:
            self.DFs[a] = OrderedSet([]);
            for b in self.doms.bblist:
                dominatorsOfB = self.doms.dom[b]
                #a does not strictly dominates b
                if not ((a in dominatorsOfB) and (a != b)):
                    #a dominates an immediate predecessor of b
                    for bIPred in b.predecessors:
                        dominatorsOfbIPred = self.doms.dom[bIPred]
                        if a in dominatorsOfbIPred:
                            self.DFs[a].add(b)

    def collectDefsOfVarV(self, v:Variable, cfg:ControlFlowGraph):
        collectedDefs = []       #stmts ids 
        rwa = ReadWriteAnalyzer(cfg)
        for id, rwresults in rwa.analysis.items():
            writes = rwresults['writes']
            for write in writes:
                if write.baseVar == v:
                    collectedDefs.append(id)

        return collectedDefs
        
    def findBBStmtBelongsIn(self, id:int, bbg:BasicBlockGraph):
        for bb in bbg.blocks:
            if id in bb.nodes:
                return bb

    def findBBsForAllDefsOfV(self, v:Variable, bbg: BasicBlockGraph):
        stmtsFordefsOfV = self.collectDefsOfVarV(v, bbg.cfg)
        retList : List[BasicBlock] = []
        for stmtID in stmtsFordefsOfV:
            B = self.findBBStmtBelongsIn(stmtID, bbg)
            retList.append(B) #pyright: ignore
        return retList

    def insertPhiStmtForVar(self, v:Variable, bb: BasicBlock, cfg:ControlFlowGraph):
        phisAsText = f"{v.name} = phi();"
        newAstNode = HintzStatementBuilder().parse_statement(phisAsText)
        newCfgNode = CFGNode(id=cfg.stmt_id, stmt=newAstNode)

        if isinstance(cfg.nodes[bb.entryNode].stmt, (Label, IfJoin, SwitchJoin)):
            EditCfg.addNodeAfter(cfg, bb.entryNode, newCfgNode)
        else:
            EditCfg.addNodeBefore(cfg, bb.entryNode, newCfgNode)



    """
    Algorithm 3.1 from SSA Book:
    1 for v:variables in original program do:
    2  F←{} ▷set of basic blocks where φ is added
    3  W←{} ▷set of basic blocks that contain definitions of v
    4  for d ∈ Defs(v) do
    5   let B be the basic block containing d
    6   W ← W ∪ {B}
    7   while W != {} do
    8       remove a basic block X from W
    9       for Y: basicblock ∈ DF(X) do
    10          if Y ∈ F then
    11              add v ← φ(...) at entry of Y
    12              F ← F ∪ {Y}
    13              if Y ~∈ Defs(v) then
    14                  W ← W∪{Y}
    """
    def computePhiLocsForVar(self):
        var2PhiBBs = []
        bbg = self.doms.bbg
        currCfg = bbg.cfg
        currF = currCfg.fcn
        for v in currF.declaredVarsList:
            tmpList = []
            F = OrderedSet([])
            W = OrderedSet([])
            stmtIdsForDefsOfV = self.collectDefsOfVarV(v, currCfg)
            defBBList = self.findBBsForAllDefsOfV(v, bbg)
            for stmtID in stmtIdsForDefsOfV:
                B = self.findBBStmtBelongsIn(stmtID, bbg)
                W.append(B)                 # W ← W ∪ {B}
                while len(W) != 0:      # while W != {} do:
                    X = W.pop()
                    domFrontsOfX = self.DFs[X]
                    for Y in domFrontsOfX:
                        if Y not in F:
                            #print(f"Need to add a Phi for {v.name} to the top of {Y.name} before node {Y.entryNode}")
                            tmpList.append(Y)
                            F.append(Y)
                            if Y not in defBBList:
                                W.append(Y)

            var2PhiBBs.append((v, tmpList))

        #materialize
        for v, bblist in var2PhiBBs:
            for bb in bblist:
                self.insertPhiStmtForVar(v, bb, currCfg)


    def renameVersionsOfVars(self):
        pass
