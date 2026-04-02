# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from hintzCompiler.src.EditCfg import *
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.readWriteAnalyzer import ReadWriteAnalyzer
from hintzCompiler.src.PredicatedIRNodeIterator import IRNodeIterator


class SSAAwareDeadCodeElimination():

    #public:

    def __init__(self, cfg:ControlFlowGraph):
        self._cfg = cfg
        self._rootStmtIDList : List[int] = []
        self._markedStmtIDList : List[int] = []
        self._markedStmtIDSet : set[int] = set()
        self._rwa : ReadWriteAnalyzer = ReadWriteAnalyzer(cfg)

    def doit(self):
        if self._cfg.fcn._isInSSA == False:
            raise RuntimeError("SSA Aware DeadCodeElimination can only be run on Fcns which are already in SSA form.")

        self.determineRoots()
        self.mark()
        self.sweep()

    def xformName(self):
        return "SSA-Aware-DCE"

    #private:

    def determineRoots(self):

        # control flow roots
        for cfgNode in self._cfg.nodes: 
            n = cfgNode.stmt
            if isinstance(n, (If, IfJoin, While, DoWhile, DoJoin, For, Declaration)): 
                self._rootStmtIDList.append(cfgNode.id)

        # data flow roots
        for eachNode in IRNodeIterator(self._cfg.fcn, lambda n: isinstance(n, Return)):
            stmt = eachNode.rootStmt()
            if stmt is None:
                raise RuntimeError("Found a node whose root Stmt is None")
            self._rootStmtIDList.append(stmt._cfgNodeId)

    def traverseBackwardsInDataFlow(self, liveStmtId):
        if liveStmtId in self._markedStmtIDSet:
            return

        self._markedStmtIDSet.add(liveStmtId)
        self._markedStmtIDList.append(liveStmtId)
        liveStmtReads = self._rwa.get_reads(liveStmtId)
        for eachLiveRead in liveStmtReads:
            reachingDefForLiveRead = eachLiveRead.irVarAccessNode._ssaReachingDef
            if reachingDefForLiveRead is not None:
                stmt = reachingDefForLiveRead.rootStmt()
                if stmt is None:
                    raise RuntimeError("Found a node whose root Stmt is None")
                self.traverseBackwardsInDataFlow(stmt._cfgNodeId)

    def startMarkingFrom(self, stmtID):
        self.traverseBackwardsInDataFlow(stmtID)

    def mark(self):
        for eachS in self._rootStmtIDList:
            self.startMarkingFrom(eachS)

    def sweep(self):
        allNodes  = [x.id for x in self._cfg.nodes]
        liveNodes = self._markedStmtIDList
        deadNodes = [x for x in allNodes if x not in liveNodes]

        #print(f"\nLIVE-STMT-IDs: {liveNodes}")
        #print(f"\nDEAD-STMT-IDs: {deadNodes}")

        for deadStmtId in deadNodes:
            EditCfg.deleteNode(self._cfg, deadStmtId)
