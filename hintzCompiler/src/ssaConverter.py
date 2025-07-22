# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers

class SSAConverter():

    #public:

    def __init__(self, domFronts: DominanceFrontiers):
        self.dom_fronts = domFronts

    def doit(self, cfg: ControlFlowGraph):
        #self.computePhiLocsForVar()
        #self.renameVersionsOfVars()
        pass

    #private

