# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from ordered_set import OrderedSet

class DominanceFrontiers:

    #public:

    def __init__(self, dominators):
        self.doms   = dominators
        self.DFs    = {}
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

    """
    Algorithm 3.1 from SSA Book:
     1 for v:variables in original program do:
     2  F←{} ▷set of basic blocks where φ is added
     3  W←{} ▷set of basic blocks that contain definitions of v
     4  for d∈Defs(v) do
     5   let B be the basic block containing d
     6   W←W∪{B}
     7   whileW={}do
     8       remove a basic block X from W
     9       for Y: basicblock∈DF(X) do
     10          if Y∈F then
     11              add v←φ(...) at entry of Y
     12              F ← F∪{Y}
     13              if Y ~∈ Defs(v) then
     14                  W←W∪{Y}
    """
    def computePhiLocsForVar(self):
        return
