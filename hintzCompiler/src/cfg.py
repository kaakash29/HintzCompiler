from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from hintzCompiler.src.ir_nodes import IRNode, Goto, Label, Block, Function, Return, If, While, DoWhile, For, Switch, Case, Break
from typing import cast
import graphviz

@dataclass
class CFGNode:
    id: int
    stmt: IRNode
    successors: List["CFGNode"] = field(default_factory=list)
    compositeNodeExit : Optional["CFGNode"] = None
    compositeNodeEntry : Optional["CFGNode"] = None

    def add_successor(self, succ: "CFGNode"):
        if succ not in self.successors:
            self.successors.append(succ)

    def __str__(self):
        stmt_str = str(self.stmt).replace("\n", " ")
        succs = ", ".join(str(s.id) for s in self.successors)
        return f"[{self.id}] {stmt_str} -> {succs}"

class ControlFlowGraph:
    def __init__(self, function: Function):
        self._fcnName = function.name
        self.nodes: List[CFGNode] = []
        self.label_map: Dict[str, CFGNode] = {}
        self.goto_links: List[Tuple[CFGNode, str]] = []
        self.stmt_id = 0
        self._pending_breaks: List[CFGNode] = []
        self._build_cfg(cast(Block, function.body))
        self._resolve_gotos()

    def _build_cfg(self, block: Block):
        prev_node = None

        for stmt in block.statements:

            #print(f"Curr Stmt: {stmt}")

            curr_node = self._handle_stmt(stmt)

            #print(f"Curr Node: {curr_node}")
            #print(f"Prev Node: {prev_node}")

            if prev_node:
                
                if isinstance(prev_node.stmt, Switch):
                    if prev_node.compositeNodeExit is not None:
                        prev_node.compositeNodeExit.add_successor(curr_node)
                    else:
                        prev_node.add_successor(curr_node)

                elif isinstance(stmt, For):
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

    def _handle_stmt(self, stmt: IRNode) -> CFGNode:
        node = CFGNode(id=self.stmt_id, stmt=stmt)
        self.nodes.append(node)
        self.stmt_id += 1
        if isinstance(stmt, Label):
            self.label_map[stmt.name] = node

        if isinstance(stmt, Goto):
            self.goto_links.append((node, stmt.label))

        elif isinstance(stmt, If):
            then_entry = self._build_branch(cast(Block, stmt.then_branch))
            node.add_successor(then_entry)
            if stmt.else_branch:
                else_entry = self._build_branch(cast(Block, stmt.else_branch))
                node.add_successor(else_entry)

        elif isinstance(stmt, While):
            body_entry = self._build_branch(cast(Block, stmt.body))
            node.add_successor(body_entry)
            last = self._last_node(body_entry)
            last.add_successor(node)

        elif isinstance(stmt, DoWhile):
            body_entry = self._build_branch(cast(Block, stmt.body))
            node.stmt = stmt  # node represents the condition
            last = self._last_node(body_entry)
            last.add_successor(node)

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

            body_entry = self._build_branch(cast(Block, stmt.body))
            cond_node.add_successor(body_entry)
            after_body = self._last_node(body_entry)

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

        #Handling for Switch Stmt.
        elif isinstance(stmt, Switch):
            switch_node = node

            # Clear pending breaks for this switch block
            prev_pending_breaks = self._pending_breaks
            self._pending_breaks = []

            exit_node = CFGNode(id=self.stmt_id, stmt=IRNode())  # dummy "join" node

            self.nodes.append(exit_node)
            self.stmt_id += 1

            for case in stmt.cases:
                case_entry = self._build_branch(case.body)
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

    def _build_branch(self, block: Block) -> CFGNode:
        entry = None
        prev = None
        for stmt in block.statements:
            node = self._handle_stmt(stmt)
            if prev and not isinstance(prev.stmt, (Goto, Return)):
                prev.add_successor(node)
            if entry is None:
                entry = node
            prev = node
        return entry

    def _last_node(self, start: CFGNode) -> CFGNode:
        current = start
        visited = set()
        while current.successors and len(current.successors) == 1 and current not in visited:
            visited.add(current)
            current = current.successors[0]
        return current

    def _resolve_gotos(self):
        for node, label in self.goto_links:
            target = self.label_map.get(label)
            if target:
                node.add_successor(target)
            else:
                print(f"⚠️ Warning: unresolved label '{label}' at node {node.id}")

    def dump(self):
        print(f"=== CFG ===" )
        print(f"Fcn : {self._fcnName}" )
        for node in self.nodes:
            print(node)

    def __str__(self):
        retStr = ""
        retStr += f"=== CFG ===\n"
        retStr += f"Fcn : {self._fcnName}\n"

        for node in self.nodes:
            retStr += str(node)
            retStr += "\n"

        return retStr


    def to_graphviz(self, output_path="cfg", view=False):
        dot = graphviz.Digraph(format="jpeg")

        # Add nodes with labels
        for node in self.nodes:
            #label = f"[{node.id}]\\n{type(node.stmt).__name__}"
            label = f"[{node.id}]\\n{str(node.stmt)}"
            dot.node(str(node.id), label)

        # Add edges
        for node in self.nodes:
            for succ in node.successors:
                dot.edge(str(node.id), str(succ.id))

        # Render graph
        dot.render(output_path, view=view, cleanup=True)

