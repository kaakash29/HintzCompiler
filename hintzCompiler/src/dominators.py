# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from graphviz import Digraph

class Dominators:

    #public:

    """
    Do all constructor
    """
    def __init__(self, blocks):
        self.bblist = blocks
        self.dom = self.computeDoms();
        self.idoms = self.computeIDoms();
        self.domTree = self.buildDomTree();

    def dump(self):
        self.printDomTree(self.domTree, self.bblist[0])

    def to_graphviz(self, dot_path):
        self.printGraph(self.domTree, self.bblist[0], dot_path)


    #private:

    """
    The algorithm starts by conservatively assuming that every node is dominated by all nodes.
    The exception is the entry node, which is only dominated by itself.
    The function then iteratively refines these sets: 

    for each node (except the entry), 
            its set of dominators is updated to be the intersection
            of its predecessors’ dominator sets, plus itself.

    This update process continues in rounds until fixed-point is reached.
    """
    def computeDoms(self):

        blocks = self.bblist;
        entry_block = blocks[0]

        dom = {b: set(blocks) for b in blocks}
        dom[entry_block] = {entry_block}
        changed = True
        while changed:
            changed = False
            for b in blocks:
                if b == entry_block:
                    continue
                if b.predecessors:
                    new_dom = set([b]) | set.intersection(*(dom[p] for p in b.predecessors))
                else:
                    new_dom = set([b])
                if new_dom != dom[b]:
                    dom[b] = new_dom
                    changed = True
        return dom

    """
    Computes the immediate dominator for each node (block).
    The immediate dominator of a node is the unique node that
    strictly dominates the given node but does not strictly 
    dominate any other node that strictly dominates it. 
    """
    def computeIDoms(self):
        dom = self.dom
        idom = {}
        for b, doms in dom.items():
            if len(doms) <= 1:
                idom[b] = None
                continue
            doms_wo_b = doms - {b} #only strict dominators of b then
            idom_candidate = None
            for d in doms_wo_b:
                is_idom = True
                for other in doms_wo_b:

                    if other == d:
                        continue

                    if d in dom[other]:
                        is_idom = False 
                        break

                if is_idom:
                    idom_candidate = d
                    break
            idom[b] = idom_candidate
        return idom

    """
    Builds the dominator tree as a dict mapping each node to its list of children.
    """
    def buildDomTree(self):
        idom = self.idoms
        dom_tree = {b: [] for b in idom}
        for b, d in idom.items():
            if d is not None:
                dom_tree[d].append(b)
        return dom_tree

    """
    Recursively prints the dominator tree.
    """
    def printDomTree(self, dom_tree, entry_block, node_name_func=None, indent=0):
        if node_name_func is None:
            node_name_func = lambda b: getattr(b, "id", str(b))
        print(" " * indent + str(node_name_func(entry_block)))
        for child in dom_tree.get(entry_block, []):
            self.printDomTree(dom_tree, child, node_name_func, indent + 2)

    
    def printGraph(self, dom_tree, entry_block, output_path="cfg", node_name_func=None):
        """
        Dumps the dominator tree to a Graphviz .gv file and renders it to PDF/SVG.
    
        Parameters:
            dom_tree (dict): The dominator tree as a dict of {block: [children]}.
            entry_block: The entry node of the tree.
            filename (str): Output file name (with .gv extension).
            node_name_func (callable): Function to map block to string name.
        """
        if node_name_func is None:
            node_name_func = lambda b: f"{getattr(b, 'name', str(b))}"
    
        dot = Digraph(comment="Dominator Tree", format='svg')
        visited = set()
    
        def visit(block):
            block_name = node_name_func(block)
            if block_name not in visited:
                visited.add(block_name)
                dot.node(block_name)
            for child in dom_tree.get(block, []):
                child_name = node_name_func(child)
                dot.node(child_name)
                dot.edge(block_name, child_name)
                visit(child)
    
        visit(entry_block)
        dot.render(output_path, view=False, cleanup=False)

###############################################################################################################################################

