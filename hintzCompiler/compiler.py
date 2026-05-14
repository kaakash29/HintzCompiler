# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

import os
import sys
import argparse
import shutil
import subprocess
from typing import List, cast
from hintzCompiler import __version__
from lark import Lark
from lark import Tree
from dataclasses import dataclass
from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.preprocessor import Preprocessor
from hintzCompiler.src.symbol_table import SymbolTable
from hintzCompiler.src.transformer import IRTransformer
from hintzCompiler.src.ir_nodes import Function, Program
from hintzCompiler.src.mlir_emitter import emit_mlir
from hintzCompiler.src.basic_blocks import BasicBlockGraph

from hintzCompiler.src.dominators import Dominators
from hintzCompiler.src.ssaConverter import SSAConverter
from hintzCompiler.src.ssaDCE import SSAAwareDeadCodeElimination
from hintzCompiler.src.dominanceFrontier import DominanceFrontiers


##############################################################################################

@dataclass
class CompilationContext:
    _parseTree: Tree
    _ast: Program
    cfgs: List[ControlFlowGraph]
    bbgs: List[BasicBlockGraph]
    symbolTableGlobalScope: SymbolTable

##############################################################################################

"""
Parses the preprocessed-input program with Lark based grammar, and builds SymbolTables,
ControlFlowGraph and BasicBlocksGraphs for all functions in the input. Wraps all the info
into a CompilationContext object and returns it.
"""
def parseAndBuildCompilationContextFromInput(code):
    # Text to ParseTree
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar", "c89.lark")
    with open(grammar_path) as f:
        grammar = f.read()
    parser = Lark(grammar, parser="lalr", start="start")
    tree = parser.parse(code)

    # ParseTree to HintzAst
    transformer = IRTransformer()
    ir = transformer.transform(tree)

    # HintzAst to Cfgs/Bbgs
    allCfgs = []
    allBbgs = []
    for decl in ir.declarations:
        if isinstance(decl, Function):
            fcn = cast(Function, decl)
            cfg = ControlFlowGraph(fcn)
            bbg = BasicBlockGraph(cfg)
            allCfgs.append(cfg)
            allBbgs.append(bbg)

    compCtx = CompilationContext(_parseTree=tree, _ast=ir, cfgs=allCfgs, bbgs=allBbgs, symbolTableGlobalScope=transformer.symtab_manager.global_scope)
    return compCtx


"""
Handles the compilation of a simplified compilation unit.
Top level driver for a hypothetical compiler written in python
"""
def Driver(code: str):

    """FRONT-END"""

    compCtx = parseAndBuildCompilationContextFromInput(code)



    """MIDDLE-END"""

    # 1) cfg level optimizations ?
    for aCfg, aBfg in zip(compCtx.cfgs, compCtx.bbgs):

        doms  = Dominators(aBfg)
        domFs = DominanceFrontiers(doms)

        toSSA = SSAConverter(domFs)
        toSSA.doit()

        ssaDce = SSAAwareDeadCodeElimination(aCfg)
        ssaDce.doit()

        #ssaPe = SSAAwareDataFlowPeepholeEngine(aCfg)
        #ssaPe.doit()

    # may be we want :
    # 2) program level optimizations ?
    # 3) both (what are we trying to get to?)
    # 4) none (rely solely on the backend optimizations?)



    """BACK-END"""

    # may be lower to a well-supported ir MLIR/LLVM ir ?
    # toVM = convertToVM(compCtx)
    # toVM.doit()

    return compCtx

##############################################################################################

"""
Handles compilation of the provided input files, often includes some include directives.
"""
def compile(path: str) -> CompilationContext: #pragma: no cover
    if not path.endswith(".hz"):
        raise ValueError(f"❌ Only .hz files are supported: {path}")

    fullIncludePath = os.path.join(os.path.dirname(__file__), "..", "hintzlib") 
    preprocessor = Preprocessor(include_paths=[fullIncludePath])
    code = preprocessor.preprocess(path)
    cctx = Driver(code)
    return cctx

##############################################################################################

"""
Main function for the Hintz Compiler
"""
def main(): #pragma: no cover

    parser = argparse.ArgumentParser(description="Hintz Compiler", add_help=False)
    parser.add_argument("source", nargs="?", help="Path to input .hz (hintz) source file")
    primary = parser.add_argument_group("main options")
    primary.add_argument("-h", "--help", action="help", help="show this help message and exit")
    primary.add_argument("-v", "--version", action="version", version=f"hintz {__version__}", help="show program's version number and exit")
    primary.add_argument("-o", "--out", help="Base output path for pipeline artifacts; executable defaults to ./<source>.out when omitted")

    pipeline = parser.add_argument_group("pipeline options")
    pipeline.add_argument("--emit-exe", action="store_true", help="Compile to a native executable")
    pipeline.add_argument("--emit-mlir", action="store_true", help="Emit Hintz MLIR")
    pipeline.add_argument("--emit-hintz-mlir", action="store_true", help="Write Hintz MLIR to a file")
    pipeline.add_argument("--emit-lowered-mlir", action="store_true", help="Lower Hintz MLIR to arith/func and write to a file")
    pipeline.add_argument("--emit-llvm", action="store_true", help="Lower to LLVM dialect and emit LLVM IR (.ll)")

    tooling = parser.add_argument_group("tool overrides")
    tooling.add_argument("--hintz-opt", help="Path to hintz-opt")
    tooling.add_argument("--mlir-opt", help="Path to mlir-opt")
    tooling.add_argument("--mlir-translate", help="Path to mlir-translate")
    tooling.add_argument("--clang", help="Path to clang")

    debug = parser.add_argument_group("debug options")
    debug.add_argument("-a", "--dumpAstToFile", action="store_true", help="Path to write IR output")
    debug.add_argument("-s", "--dumpSymbolTable", action="store_true", help="Dump symbol table for debugging")
    debug.add_argument("-p", "--dumpParseTree", action="store_true", help="Dump parse tree for debugging")
    debug.add_argument("-c", "--dumpCfgs", action="store_true", help="Dump control flow graph")
    args = parser.parse_args()

    if not args.source:
        parser.error("the following arguments are required: source")

    if _should_default_to_emit_exe(args):
        args.emit_exe = True

    try:
        cctx = compile(args.source)

        parsetree   = cctx._parseTree;
        ir          = cctx._ast;
        cfgs        = cctx.cfgs 
        globalScope = cctx.symbolTableGlobalScope

        if args.dumpParseTree:
            print("\n=== PARSE-TREE ===\n")
            print(parsetree.pretty())

        if args.dumpAstToFile:
            print("\n=== AST-DUMP ===\n")
            ir.dump()

        if args.emit_mlir:
            print("\n=== HINTZ-MLIR ===\n")
            print(emit_mlir(cctx))

        if args.emit_hintz_mlir or args.emit_lowered_mlir or args.emit_llvm or args.emit_exe:
            _run_mlir_pipeline(args, cctx)

        if args.dumpSymbolTable:
            print("\n=== SYMBOL-TABLE ===\n")
            globalScope.dumpDownwards()

        if args.dumpCfgs:
            print(f"\n=== INITIAL CFG-DUMP ===\n")
            if len(ir.declarations) == 0 or not isinstance(ir.declarations[0], Function):
                raise ValueError("\n❌ CFG generation requires a function declaration.\n")
            
            for cfg in cfgs:
                print(cfg);
                cfg.to_graphviz(output_path=cfg._fcnName, view=False);

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print(f"\n❌ Compilation failed: {e}\n")
        sys.exit(1)

##############################################################################################

def _run_mlir_pipeline(args, cctx: CompilationContext) -> None:
    base = args.out if args.out else os.path.splitext(args.source)[0]
    hintz_mlir_path = f"{base}.hintz.mlir"
    lowered_mlir_path = f"{base}.lowered.mlir"
    llvm_dialect_path = f"{base}.llvm.mlir"
    llvm_ir_path = f"{base}.ll"
    exe_path = _default_exe_path(args, base)

    hintz_mlir = emit_mlir(cctx)
    _write_text(hintz_mlir_path, hintz_mlir)
    if args.emit_hintz_mlir:
        print(f"\n=== HINTZ-MLIR (file) ===\n{hintz_mlir_path}")

    if not (args.emit_lowered_mlir or args.emit_llvm or args.emit_exe):
        return

    hintz_opt = _resolve_tool(
        name="hintz-opt",
        arg_value=args.hintz_opt,
        env_var="HINTZ_OPT",
        default_path=_default_hintz_opt_path(),
    )

    _run_cmd([hintz_opt, hintz_mlir_path, "--convert-hintz-to-arith-func"], lowered_mlir_path)
    if args.emit_lowered_mlir or args.emit_llvm or args.emit_exe:
        print(f"\n=== LOWERED-MLIR (file) ===\n{lowered_mlir_path}")

    if not (args.emit_llvm or args.emit_exe):
        return

    mlir_opt = _resolve_tool(
        name="mlir-opt",
        arg_value=args.mlir_opt,
        env_var="MLIR_OPT",
    )
    _run_cmd(
        [
            mlir_opt,
            lowered_mlir_path,
            "--convert-arith-to-llvm",
            "--finalize-memref-to-llvm",
            "--convert-func-to-llvm",
            "--reconcile-unrealized-casts",
        ],
        llvm_dialect_path,
    )

    mlir_translate = _resolve_tool(
        name="mlir-translate",
        arg_value=args.mlir_translate,
        env_var="MLIR_TRANSLATE",
    )
    _run_cmd(
        [mlir_translate, "--mlir-to-llvmir", llvm_dialect_path],
        llvm_ir_path,
    )
    print(f"\n=== LLVM-IR (file) ===\n{llvm_ir_path}")

    if not args.emit_exe:
        return

    clang = _resolve_tool(
        name="clang",
        arg_value=args.clang,
        env_var="CLANG",
    )
    _run_cmd([clang, llvm_ir_path, "-o", exe_path], output_path=None)
    print(f"\n=== EXECUTABLE ===\n{exe_path}")


def _should_default_to_emit_exe(args) -> bool:
    return not any(
        [
            args.dumpAstToFile,
            args.dumpSymbolTable,
            args.dumpParseTree,
            args.dumpCfgs,
            args.emit_mlir,
            args.emit_hintz_mlir,
            args.emit_lowered_mlir,
            args.emit_llvm,
            args.emit_exe,
        ]
    )


def _default_exe_path(args, base: str) -> str:
    if args.out:
        return base
    source_stem = os.path.splitext(os.path.basename(args.source))[0]
    return os.path.join(os.getcwd(), f"{source_stem}.out")


def _write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _run_cmd(cmd: list[str], output_path: str | None) -> None:
    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            subprocess.run(cmd, check=True, stdout=out)
    else:
        subprocess.run(cmd, check=True)


def _resolve_tool(name: str, arg_value: str | None, env_var: str, default_path: str | None = None) -> str:
    tool = _find_tool(
        name=name,
        arg_value=arg_value,
        env_var=env_var,
        default_path=default_path,
    )
    if tool:
        return tool
    raise RuntimeError(
        f"❌ Unable to find '{name}'. Set {env_var}, pass --{name}, or add it to PATH."
    )


def _find_tool(name: str, arg_value: str | None, env_var: str, default_path: str | None = None) -> str | None:
    if arg_value:
        return arg_value
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    bundled = _bundled_tool_path(name)
    if bundled:
        return bundled
    if default_path and os.path.exists(default_path):
        return default_path
    return shutil.which(name)


def _bundled_tool_path(name: str) -> str | None:
    tools_dir = _tools_dir()
    if not tools_dir:
        return None
    candidate = os.path.join(tools_dir, name)
    if os.path.exists(candidate) and os.access(candidate, os.X_OK):
        return candidate
    return None


def _tools_dir() -> str | None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tools_dir = os.path.join(repo_root, "tools")
    if os.path.isdir(tools_dir):
        return tools_dir
    return None


def _default_hintz_opt_path() -> str:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(repo_root, "hintz-mlir-dialect", "build", "bin", "hintz-opt")


if __name__ == "__main__":
    main()
