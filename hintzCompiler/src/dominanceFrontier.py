# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from ordered_set import OrderedSet
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.dominators import Dominators

"""
This class as written is doing too much.
"""

class DominanceFrontiers:

    #public:

    """
    A do-it-all constructor.
    """
    def __init__(self, dominators:Dominators):
        self.doms   = dominators
        self.DFs    = {}
        self._createdWithVersion = dominators._createdWithVersion
        self.computeDFs()

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

########################################################################################
