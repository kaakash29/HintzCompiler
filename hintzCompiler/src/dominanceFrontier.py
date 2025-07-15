# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from ordered_set import OrderedSet
from dataclasses import replace
from hintzCompiler.src.ir_nodes import *
from typing import List, Tuple, Optional
from hintzCompiler.src.EditCfg import EditCfg
from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.cfg import ControlFlowGraph, CFGNode
from hintzCompiler.src.cfg import ControlFlowGraph, CFGNode
from hintzCompiler.src.readWriteAnalyzer import ReadWriteAnalyzer
from hintzCompiler.src.StmtBuilderFacade import HintzStatementBuilder
from hintzCompiler.src.basic_blocks import BasicBlock, BasicBlockGraph


"""
Data Structure to hold a Var and its stack of versions.
"""

class VarVersionStackMap:
    def __init__(self):
        self._items: List[Tuple[Variable, List[VarAccess]]] = []

    def insert(self, var: Variable, access: VarAccess):
        for key, stack in self._items:
            if key == var:
                stack.append(access)
                return
        self._items.append((var, [access]))

    def get(self, var: Variable) -> List[VarAccess]:
        for key, stack in self._items:
            if key == var:
                return stack
        return []

    def contains(self, var: Variable) -> bool:
        return any(key == var for key, _ in self._items)

    def __str__(self):
        result = []
        for var, stack in self._items:
            result.append(f"{var}: {[str(access) for access in stack]}")
        return "\n".join(result)

    def __repr__(self):
        return f"VarStackMap({self._items})"


############################################################################



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
        newAstNode = HintzStatementBuilder(cfg).parse_statement(phisAsText)
        newAstNode._ssaIsPhi = True

        newCfgNode = CFGNode(id=cfg.stmt_id, stmt=newAstNode)

        if isinstance(cfg.nodes[bb.entryNode].stmt, (Label, IfJoin, SwitchJoin, DoJoin)):
            EditCfg.addNodeAfter(cfg, bb.entryNode, newCfgNode)
            bb.nodes.append(newCfgNode.id)
        else:
            EditCfg.addNodeBefore(cfg, bb.entryNode, newCfgNode)
            bb.nodes.append(newCfgNode.id)
            bb.entryNode = newCfgNode.id


    """
    Algorithm 3.1 from SSA Book:
    1 for v:variables in original program do:
    2  F ← {} ▷set of basic blocks where φ is added
    3  W ← {} ▷set of basic blocks that contain definitions of v
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

    """
    Procedure updateReachingDef(v,p)
    Data: v : variable from program
    Data: p : program point
    ▷ search through chain of definitions for v until we find the closest definition that dominates
    p, then update v.reachingDef in-place with this definition
    1 r ← v
    2 repeat
    3 r ← r.reachingDef
    4 until r == ⊥ or definition(r) dominates p
    5 v.reachingDef ← r
    """
    def updateReachingDef(self, var_access: VarAccess, doms: Dominators):
        r = var_access._ssaReachingDef
        use_stmt = var_access.rootStmt()
        while r is not None:
            def_stmt = r.rootStmt()
            if doms.dominates(def_stmt, use_stmt):
                break  # Found the nearest dominating def
            r = r._ssaReachingDef  # Walk up the def chain
        var_access._ssaReachingDef = r


    """
    Algorithm 3.3 from the SSA book

    ▷ rename variable definitions and uses to have one definition per variable name

    1 for each v:variable do
    2   v.reachingDef←⊥
    3 for eachBB:basicblock in depth-first search preorder traversal of the dom.tree do  (ensures definitions are seen before uses in dominance order.)
    4   for each i :instruction in linear code sequence of BB do
    5       for each v:variable used by non-φ-function i do
    6           updateReachingDef(v,i)
    7           replace this use of v by v.reachingDef in i
    8       for each v:variable defined by i(may be a φ-function) do
    9           updateReachingDef(v,i)
    10          create fresh variable v'
    11          replace this definition of v by v' in i
    12          v'.reachingDef ← v.reachingDef
    13          v.reachingDef ← v'
    14  for each φ:φ-function in a direct successor of BB do
    15      let v:variable used by φ coming from BB
    16      updateReachingDef(v,end of BB)
    17      replace this use of v by v.reachingDef in φ
    """

    def createNewVersionForOrigVar(self, cfg, origVar:Variable):
        newVarName = origVar.name+f"{len(origVar._ssaVersions)+1}" 
        newVar = EditCfg.createNewLocalVar(cfg, newVarName, origVar.type_spec, origVar.attributes)
        origVar._ssaVersions.append(newVar)
        newVar._ssaUnversioned = origVar
        newVar._ssaIsVersionOfAVar = True
        return newVar

    def renameVersionsOfVars(self):

        var_stacks = VarVersionStackMap()
        cfg = self.doms.bbg.cfg
        updatedReadWriteAnalyzer = ReadWriteAnalyzer(self.doms.bbg.cfg)
        updatedDominators = Dominators(self.doms.bbg)

        for node_id, rw in updatedReadWriteAnalyzer.analysis.items():
            reads = rw['reads']
            for read in reads:
                read.irVarAccessNode._ssaReachingDef = None

        for eachBB in self.doms.dfs_preorder():
            for instId in eachBB.getLinearStmtOrderInBB(cfg):

                readsInStmtInst = updatedReadWriteAnalyzer.get_reads(instId)
                for readOcc in readsInStmtInst:
                    self.updateReachingDef(readOcc.irVarAccessNode, updatedDominators)
                    if var_stacks.contains(readOcc.irVarAccessNode._var): #pyright: ignore
                        versionStack = var_stacks.get(readOcc.irVarAccessNode._var) #pyright: ignore
                        if len(versionStack) != 0:
                            versionedAccess = replace(readOcc.irVarAccessNode, name=versionStack[-1].name, _var=versionStack[-1])
                            EditCfg.swapIntoCfg(versionedAccess, readOcc.irVarAccessNode)
                            #print(f"* Replaced read of {readOcc.irVarAccessNode.name} on {readOcc.irVarAccessNode.rootStmt()} with access {versionStack[-1]}")

                writesInStmtInst = updatedReadWriteAnalyzer.get_writes(instId)
                for writeOcc in writesInStmtInst:
                    self.updateReachingDef(writeOcc.irVarAccessNode, updatedDominators)
                    origVar = writeOcc.irVarAccessNode._var 
                    version = self.createNewVersionForOrigVar(cfg, origVar) #pyright: ignore
                    versionAccess = VarAccess(version.name, version, None)
                    EditCfg.swapIntoCfg(versionAccess, writeOcc.irVarAccessNode) 
                    var_stacks.insert(origVar, versionAccess) #pyright: ignore
                    #print(f"* Created a new version of the variable {origVar.name} on stmt: {writeOcc.irVarAccessNode.rootStmt()} named: {version.name}")

            for succBB in eachBB.successors:

                bbEntry = cfg.nodes[succBB.getLinearStmtOrderInBB(cfg)[0]]
                if not bbEntry.stmt._ssaIsPhi and len(succBB.nodes) > 1: 
                    bbEntry = cfg.nodes[succBB.getLinearStmtOrderInBB(cfg)[1]]
                stmts = succBB.getLinearStmtOrderInBB(cfg)
                for stmtId in stmts:
                    bbEntry = cfg.nodes[stmtId]
                    if bbEntry.stmt._ssaIsPhi:
                        phiLhs = bbEntry.stmt.target
                        if isinstance(phiLhs, VarAccess):
                            phiVar = phiLhs._var if not phiLhs._var._ssaIsVersionOfAVar else phiLhs._var._ssaUnversioned
                            versionStack = var_stacks.get(phiVar) #pyright: ignore
                            if len(versionStack) > 0:
                                #we pop the top of the var stack here because a new def is now dominating from the phi
                                cloneVersionedAccess = replace(versionStack.pop())
                                phi = bbEntry.stmt.value
                                EditCfg.addInputToPhi(cloneVersionedAccess, phi)
