# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from collections import defaultdict

"""
Computes the set of dominators for each node (block) in the CFG/basic block graph.

Args:
        blocks: List of BasicBlock (or CFGNode) objects with .successors and .predecessors
        entry_block: The entry BasicBlock (usually blocks[0])

Returns:
        dom: dict {block: set of dominating blocks}

Central-Idea:
        The algorithm starts by conservatively assuming that every node is dominated by all nodes.
        The exception is the entry node, which is only dominated by itself.
        The function then iteratively refines these sets: for each node (except the entry), 
                its set of dominators is updated to be the intersection of its predecessors’ dominator sets, plus itself.
        This update process continues in rounds until no dominator set changes in a complete pass over the graph.
"""

class Dominators:

    #public:

    def __init__(self, blocks):
        self.bblist = blocks
        self.dom = self.computeDoms();
        self.idoms = self.computeIDoms();
        self.domTree = self.buildDomTree();

    def dump(self):
        self.printDomTree(self.domTree, self.bblist[0])


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

###############################################################################################################################################

