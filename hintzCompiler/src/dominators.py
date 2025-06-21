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

def compute_dominators(blocks, entry_block):
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

Args:
        dom: dict from compute_dominators

Returns:
        idom: dict {block: immediate dominator block or None}

Central-Idea:
        For each node, its immediate dominator is the unique node that strictly dominates it 
        and is closest to it in the flow of control—meaning it is the last dominator on any
        path from the entry node before reaching the node itself. 
        The algorithm works by examining each node’s set of dominators (excluding the node itself)
        and selecting the dominator that is not dominated by any other dominator in this set.
        This node is, by definition, the immediate dominator. 
        If a node has no such dominator (which is the case for the entry node),
        its immediate dominator is set to None
"""

def compute_idoms(dom):
    idom = {}
    for b, doms in dom.items():
        if len(doms) <= 1:
            idom[b] = None
            continue
        doms_wo_b = doms - {b}
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

Args:
        idom: dict from compute_idoms

Returns:
        dom_tree: dict {block: [children blocks]}

Central-Idea:
       The function iterates through the mapping of nodes to their immediate dominators,
       and for each node, it adds the node as a child to its immediate dominator in the tree structure.
       If a node does not have an immediate dominator (such as the entry node of the control flow graph),
       it becomes the root of the dominator tree. 
"""

def build_dom_tree(idom):
    dom_tree = {b: [] for b in idom}
    for b, d in idom.items():
        if d is not None:
            dom_tree[d].append(b)
    return dom_tree


###################################################################################################################################

def print_dominator_tree(dom_tree, entry_block, node_name_func=None, indent=0):
    """
    Recursively prints the dominator tree.
    Args:
        dom_tree: dict from build_dom_tree
        entry_block: root node
        node_name_func: optional function to get the name/id of a node
        indent: current indentation level (for recursion)
    """
    if node_name_func is None:
        node_name_func = lambda b: getattr(b, "id", str(b))
    print(" " * indent + str(node_name_func(entry_block)))
    for child in dom_tree.get(entry_block, []):
        print_dominator_tree(dom_tree, child, node_name_func, indent + 2)

# Example usage (assuming you have your BasicBlocks or CFGNodes with .successors and .predecessors):
#
# blocks = ...  # List of BasicBlock objects
# entry_block = blocks[0]
# dom = compute_dominators(blocks, entry_block)
# idom = compute_idoms(dom)
# dom_tree = build_dom_tree(idom)
# print_dominator_tree(dom_tree, entry_block)
