# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import graphviz
from typing import cast
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from hintzCompiler.src.ir_nodes import IRNode, Goto, Label, Block, Function, Return, If, While, DoWhile, For, Switch, Break, SwitchJoin, IfJoin, DoJoin 
from hintzCompiler.src.symbol_table import *
"""
This is a node in the control flow graph, encapsulates over an AstNode and its successors
in the graph. 
"""
@dataclass
class CFGNode:
    id: int
    stmt: IRNode
    successors: List["CFGNode"] = field(default_factory=list)
    predecessors: List["CFGNode"] = field(default_factory=list)
    compositeNodeExit : Optional["CFGNode"] = None
    compositeNodeEntry : Optional["CFGNode"] = None

    def add_successor(self, succ: "CFGNode"):
        if succ not in self.successors:
            self.successors.append(succ)
            succ.add_predecessor(self)
    
    def add_predecessor(self, pred:"CFGNode"):
        if pred not in self.predecessors:
            self.predecessors.append(pred)

    def __str__(self):
        stmt_str = str(self.stmt).replace("\n", " ")
        succs = ", ".join(str(s.id) for s in self.successors)
        return f"[{self.id}] {stmt_str} -> {succs}".rstrip()



"""
Builds the control flow graph for a function, in the IR and provides various traversal
paradigms.
"""
class ControlFlowGraph:

    # public:

    """
    A do-it-all constructor
    """
    def __init__(self, function: Function):
        self.fcn = function
        self.symbol_table = function.symbolTable
        self.nodes: List[CFGNode] = []
        self.label_map: Dict[str, CFGNode] = {}
        self.goto_links: List[Tuple[CFGNode, str]] = []
        self.stmt_id = 0
        self.version = 0
        self._pending_breaks: List[CFGNode] = []
        self._fcnName = function.name

        self._build_cfg(cast(Block, function.body))
        self._resolve_gotos()

    """
    Returns the list of CFGNode (or their indices/ids) in BFS traversal order starting from start_node.
    If start_node is None, starts from what is likely the entry node (self.nodes[0]).
    """
    def get_bfs_traversal_order(self, start_node=None):
        from collections import deque

        if not hasattr(self, "nodes") or not self.nodes:
            return []

        visited = set()
        order = []
        queue = deque()

        if start_node is None:
            start = self.nodes[0]
        else:
            start = start_node

        queue.append(start.id)
        visited.add(start.id)

        while queue:
            node_id = queue.popleft()
            node = self.nodes[node_id];

            order.append(node_id)
            for succ in getattr(node, "successors", []):
                succ_id = succ.id
                if succ_id not in visited:
                    visited.add(succ_id)
                    queue.append(succ_id)
        return order

    """
    Returns the list of CFGNode (or their indices/ids) in DFS traversal order starting from start_node.
    If start_node is None, starts from what is likely the entry node (self.nodes[0]).
    """
    def get_dfs_traversal_order(self, start_node=None):
        if not hasattr(self, "nodes") or not self.nodes:
            return []

        visited = set()
        order = []

        def dfs(node):
            visited.add(node.id)
            order.append(node.id)
            for succ in getattr(node, "successors", []):
                succ_id = succ.id
                if succ_id not in visited:
                    dfs(succ)

        if start_node is None:
            start = self.nodes[0]
        else:
            start = start_node

        dfs(start)
        return order


    """
    Methods for dumping and visualizing the CFG, used in the unit tester and
    the top level driver in compiler.py
    """

    def dump(self):
        print(f"Fcn : {self._fcnName}" )
        for node in self.nodes:
            print(node)

    def __str__(self): # pragma: no cover
        retStr = ""
        retStr += f"Fcn : {self._fcnName}\n"

        for node in self.nodes:
            retStr += str(node)
            retStr += "\n"

        return retStr

    def to_graphviz(self, output_path="cfg", view=False): # pragma: no cover
        dot = graphviz.Digraph(format="svg")

        # Add nodes with labels
        for node in self.nodes:
            label = f"[{node.id}]\\n{str(node.stmt)}"
            dot.node(str(node.id), label)

        # Add edges
        for node in self.nodes:
            for succ in node.successors:
                dot.edge(str(node.id), str(succ.id))

        # Render graph
        dot.render(output_path, view=view, cleanup=False)

    ############################################################

    #private:

    """
    Top level method called from the constructor.
    """
    def _build_cfg(self, block: Block):
        prev_node = None

        for stmt in block.statements:
            curr_node = self._handle_stmt(stmt)
            if prev_node:
                
                if isinstance(prev_node.stmt, (Switch, If)):
                    if prev_node.compositeNodeExit is not None:
                        prev_node.compositeNodeExit.add_successor(curr_node)
                    else:
                        prev_node.add_successor(curr_node)

                elif isinstance(stmt, (For, DoWhile)):
                    if curr_node.compositeNodeEntry is not None:
                        prev_node.add_successor(curr_node.compositeNodeEntry)
                    else:
                        prev_node.add_successor(curr_node)

                elif isinstance(prev_node.stmt, (Goto, Return)):
                    prev_node = curr_node
                    continue;

                else:
                    prev_node.add_successor(curr_node)

            prev_node = curr_node

    """
    Connects the goto nodes to their corresponding labels.
    """
    def _resolve_gotos(self):
        for node, label in self.goto_links:
            target = self.label_map.get(label)
            if target:
                node.add_successor(target)
            else:
                print(f"⚠️ Warning: unresolved label '{label}' at node {node.id}")

    """
    Handles a single stmt in the Ast and encapsulates it into a Cfg node.
    """
    def _handle_stmt(self, stmt: IRNode) -> CFGNode:

        node = CFGNode(id=self.stmt_id, stmt=stmt)
        self.nodes.append(node)
        self.stmt_id += 1
        
        if isinstance(stmt, Label):
            self.label_map[stmt.name] = node

        elif isinstance(stmt, Goto):
            self.goto_links.append((node, stmt.label))

        elif isinstance(stmt, If):
            exit_node = CFGNode(id=self.stmt_id, stmt=IfJoin())  # dummy "join" node
            self.nodes.append(exit_node)
            self.stmt_id += 1

            if stmt.then_branch:
                then_entry, then_last = self._build_branch(cast(Block, stmt.then_branch))
                node.add_successor(then_entry)
                then_last.add_successor(exit_node);
            else:
                node.add_successor(exit_node)

            if stmt.else_branch:
                else_entry, else_last = self._build_branch(cast(Block, stmt.else_branch))
                node.add_successor(else_entry)
                else_last.add_successor(exit_node)
            else:
                node.add_successor(exit_node)

            node.compositeNodeExit = exit_node;
            return node

        elif isinstance(stmt, While):
            body_entry, body_last = self._build_branch(cast(Block, stmt.body))
            node.add_successor(body_entry)
            body_last.add_successor(node)

        elif isinstance(stmt, DoWhile):
            entry_node = CFGNode(id=self.stmt_id, stmt=DoJoin())  # dummy "join" node
            self.nodes.append(entry_node)
            self.stmt_id += 1
            body_entry, dowhile_last = self._build_branch(cast(Block, stmt.body))
            entry_node.add_successor(body_entry)
            node.compositeNodeEntry = entry_node
            dowhile_last.add_successor(node)
            node.add_successor(entry_node)

        elif isinstance(stmt, For):
            orignode = node;
            if stmt.init:
                init_node = CFGNode(id=self.stmt_id, stmt=stmt.init)
                self.nodes.append(init_node)
                self.stmt_id += 1
                node.add_successor(init_node)
                node = init_node

            cond_node = CFGNode(id=self.stmt_id, stmt=stmt.condition) if stmt.condition else node
            if stmt.condition:
                self.nodes.append(cond_node)
                self.stmt_id += 1
                node.add_successor(cond_node)
            else:
                node.add_successor(cond_node)

            node = cond_node

            body_entry, body_last = self._build_branch(cast(Block, stmt.body))
            cond_node.add_successor(body_entry)
            after_body = body_last

            if stmt.update:
                update_node = CFGNode(id=self.stmt_id, stmt=stmt.update)
                self.nodes.append(update_node)
                self.stmt_id += 1
                after_body.add_successor(update_node)
                update_node.add_successor(cond_node)
            else:
                after_body.add_successor(cond_node)

            node.compositeNodeEntry = orignode;
            return node;

        elif isinstance(stmt, Switch):
            switch_node = node

            # Clear pending breaks for this switch block
            prev_pending_breaks = self._pending_breaks
            self._pending_breaks = []

            exit_node = CFGNode(id=self.stmt_id, stmt=SwitchJoin())  # dummy "join" node
            self.nodes.append(exit_node)
            self.stmt_id += 1

            for case in stmt.cases:
                case_entry, last_node = self._build_branch(case.body)
                switch_node.add_successor(case_entry)

            # All breaks in the switch go to the exit node
            for break_node in self._pending_breaks:
                break_node.add_successor(exit_node)

            self._pending_breaks = prev_pending_breaks
            node.compositeNodeExit = exit_node;
            return node

        elif isinstance(stmt, Break):
            self._pending_breaks.append(node)

        return node
    
    """
    Build control flow for branches in the graph
    returns the entry and exit node
    """
    def _build_branch(self, block: Block) -> tuple[CFGNode, CFGNode] :
        entry = None
        prev = None
        for stmt in block.statements:

            node = self._handle_stmt(stmt)

            if prev:
                if isinstance(stmt, (For, DoWhile)):
                    if node.compositeNodeEntry is not None:
                        prev.add_successor(node.compositeNodeEntry)
                    else:
                        prev.add_successor(node)

                elif isinstance(node.stmt, (Switch, If)):
                    prev.add_successor(node)

                elif not isinstance(prev.stmt, (Goto, Return)):
                    prev.add_successor(node)

            if entry is None:
                entry = node if node.compositeNodeEntry is None else node.compositeNodeEntry;

            if node.compositeNodeExit is not None:
                node = node.compositeNodeExit;

            prev = node

        return entry, prev # pyright: ignore
