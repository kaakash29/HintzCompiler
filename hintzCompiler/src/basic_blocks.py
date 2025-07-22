# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import graphviz
from typing import List, Dict
from dataclasses import dataclass, field
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.cfg import ControlFlowGraph

@dataclass
class BasicBlock:
    name: str
    id: int
    nodes: List[int] = field(default_factory=list)
    entryNode: int = -1
    successors: List["BasicBlock"] = field(default_factory=list)
    predecessors: List["BasicBlock"] = field(default_factory=list)

    def add_node(self, node):
        if self.entryNode == -1:
            self.entryNode = node

        self.nodes.append(node)

    def getLinearStmtOrderInBB(self, cfg:ControlFlowGraph):
        linearOrder : List[int] = []
        currIndex: int = self.entryNode
        linearOrder.append(currIndex)
        while len(cfg.nodes[currIndex].successors) == 1 and cfg.nodes[currIndex].successors[0].id in self.nodes :
            currIndex = cfg.nodes[currIndex].successors[0].id
            linearOrder.append(currIndex)

        return linearOrder

    def __str__(self):
        stmt_strs = f"Nodes: {self.nodes}"
        succ_names = ", ".join(s.name for s in self.successors)
        return f"{self.name}: {stmt_strs}  -> {succ_names}"

    def __eq__(self, other):
        return isinstance(other, BasicBlock) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

###########################################################################

class BasicBlockGraph:

    #public:

    """
    Do all constructor
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.label_map: Dict[str, BasicBlock] = {}
        self.blocks: List[BasicBlock] = self.build_basic_blocks_from_cfg(cfg)
        self._createdWithVersion = cfg._version

    def belongsToBB(self, stmtId):
        for bb in self.blocks:
            if stmtId in bb.nodes:
                return bb
        return None

    def dump(self):
        for block in self.blocks:
            print(block)

    def to_graphviz(self, output_path="cfg"): #pragma: no cover
        dot = graphviz.Digraph(comment="Basic Block Graph", format="svg")

        # Add nodes with labels
        for node in self.blocks:
            label = f"{node.name}\n{node.nodes}"
            dot.node(str(node.name), label)

        # Add edges
        for node in self.blocks:
            for succ in node.successors:
                dot.edge(str(node.name), str(succ.name))

        # Render graph
        dot.render(output_path, view=False, cleanup=False)


    #private:

    """
    Returns True if node's statement is a branch (If, Switch, Goto, Return, etc.)
    You may need to adjust this based on your IR.
    """
    def is_branch_node(self, node):
        #TODO: This is not the best way to check this, use the isinstance method here instead aaku.
        
        # even if dojoin has exactly one successor it needs to be treated as a branch because a backedge plugs into it which means
        # control flow may start at that node.
        return type(node.stmt).__name__ in {"If", "Switch", "Goto", "Return", "Break", "Continue", "While", "DoWhile", "DoJoin" }


    """
    Given a ControlFlowGraph instance `cfg`, returns a list of BasicBlock objects 
    forming the basic block graph.
    """
    def build_basic_blocks_from_cfg(self, cfg):

        # Step 2: Identify leaders (start of basic blocks)
        leaders = set()
        dfs_order = cfg.get_dfs_traversal_order()
        if not dfs_order:
            return []

        # Entry node is a leader
        leaders.add(dfs_order[0])

        # Any node that is target of a branch (has >1 predecessor) is a leader
        for node in cfg.nodes:
            if len(node.predecessors) > 1:
                leaders.add(node.id)

        # Any node that immediately follows a branch is a leader
        for node in cfg.nodes:
            if len(node.successors) > 1 or self.is_branch_node(node):
                for succ in node.successors:
                    leaders.add(succ.id)

        # Step 3: Map from node to leader
        node_to_block = {}
        basic_blocks = []
        visited = set()

        i = 0
        while i < len(dfs_order):

            node_id = dfs_order[i]
            if node_id in visited:
                i += 1
                continue

            if node_id in leaders or not basic_blocks:
                nextBBid = len(basic_blocks) + 1;
                block = BasicBlock(f"BB{nextBBid}", nextBBid)
                basic_blocks.append(block)
            else:
                block = basic_blocks[-1]

            # Add nodes sequentially until another leader or end/branch
            j = 0
            while j < len(dfs_order):

                node_id = dfs_order[j]

                if node_id in visited:
                    j += 1
                    continue

                if node_id in leaders and block.nodes:
                    break
                
                block.add_node(node_id)
                node_to_block[node_id] = block
                visited.add(node_id)

                # End block if this is a branch node or has multiple successors
                node = cfg.nodes[node_id]
                if len(node.successors) > 1 or self.is_branch_node(node):
                    break

                j += 1
                
            i += 1

        # Step 4: Set block successors
        for block in basic_blocks:
            last_node_id = block.nodes[-1]
            last_node = cfg.nodes[last_node_id]
            for succ in last_node.successors:
                succ_block = node_to_block.get(succ.id)
                if succ_block and succ_block != block:
                    block.successors.append(succ_block)
                    succ_block.predecessors.append(block)
                    
        return basic_blocks


