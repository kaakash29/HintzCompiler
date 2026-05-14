# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence

from hintzCompiler.src.ir_nodes import (
    IRNode,
    Function,
    Block,
    Return,
    BinaryOp,
    Literal,
    Declaration,
    If,
    While,
    DoWhile,
    For,
    Switch,
    Break,
    Goto,
    Label,
    Assignment,
    Call,
    VarAccess,
    FunctionCall,
    FieldAccess,
    ArrayAccess,
    UnaryOp,
)


class MLIREmitterError(Exception):
    pass


@dataclass
class _EmitState:
    lines: List[str]
    indent: int
    next_value_id: int
    var_slots: Dict[str, str] = field(default_factory=dict)


class MLIREmitter:
    def __init__(self) -> None:
        self._state = _EmitState(lines=[], indent=0, next_value_id=0)
        self._saw_return = False

    def emit_cfgs(self, cfgs: Sequence) -> str:
        self._state = _EmitState(lines=[], indent=0, next_value_id=0)
        self._emit_line("module {")
        self._state.indent += 1

        for cfg in cfgs:
            self._emit_function_from_cfg(cfg)

        self._state.indent -= 1
        self._emit_line("}")
        return "\n".join(self._state.lines)

    def _emit_function_from_cfg(self, cfg) -> None:
        fcn: Function = cfg.fcn
        self._saw_return = False
        self._state.var_slots.clear()
        args = ", ".join(f"%arg{i}: i64" for i in range(len(fcn.params)))
        self._emit_line(f"func.func @{fcn.name}({args}) -> i64 {{")
        self._state.indent += 1

        for node_id in cfg.get_dfs_traversal_order():
            stmt = cfg.nodes[node_id].stmt
            self._emit_stmt(stmt)

        self._state.indent -= 1
        self._emit_line("}")

        if not self._saw_return:
            raise MLIREmitterError(
                f"Function '{fcn.name}' has no return; only value returns are supported."
            )

    def _emit_block_or_stmt(self, node: IRNode) -> None:
        if isinstance(node, Block):
            for stmt in node.statements:
                self._emit_stmt(stmt)
        else:
            self._emit_stmt(node)

    def _emit_stmt(self, stmt: IRNode) -> None:
        if isinstance(stmt, Declaration):
            # The frontend rewrites locals into SSA-style names (`x1`, `x2`, ...).
            # Storage is therefore created lazily when a concrete SSA value is used.
            return

        if isinstance(stmt, Assignment):
            if not isinstance(stmt.target, VarAccess):
                raise MLIREmitterError(
                    "Only scalar variable assignments are supported in MLIR emission."
                )
            value = self._emit_expr(stmt.value)
            slot = self._ensure_var_slot(stmt.target.name)
            self._emit_line(f"hintz.store {value}, {slot} : i64, memref<i64>")
            return

        if isinstance(stmt, Return):
            if stmt.value is None:
                raise MLIREmitterError("Return without a value is not supported.")
            value = self._emit_expr(stmt.value)
            self._emit_line(f"hintz.return {value} : i64")
            self._saw_return = True
            return

        if isinstance(
            stmt,
            (
                If,
                While,
                DoWhile,
                For,
                Switch,
                Break,
                Goto,
                Label,
                Call,
                FunctionCall,
                FieldAccess,
                ArrayAccess,
                UnaryOp,
                Block,
            ),
        ):
            raise MLIREmitterError(
                f"Unsupported control/stmt node in CFG emission: {stmt.__class__.__name__}"
            )

        raise MLIREmitterError(
            f"Unsupported statement in CFG emission: {stmt.__class__.__name__}"
        )

    def _emit_expr(self, expr: IRNode) -> str:
        if isinstance(expr, Literal):
            return self._emit_const(expr)
        if isinstance(expr, VarAccess):
            slot = self._lookup_var_slot(expr.name)
            name = self._fresh_value()
            self._emit_line(f"{name} = hintz.load {slot} : memref<i64> -> i64")
            return name
        if isinstance(expr, BinaryOp):
            op = self._normalize_op(expr.op)
            if op != "+":
                raise MLIREmitterError(f"Unsupported binary op: {op}")
            lhs = self._emit_expr(expr.left)
            rhs = self._emit_expr(expr.right)
            name = self._fresh_value()
            self._emit_line(f"{name} = hintz.add {lhs}, {rhs} : i64")
            return name

        raise MLIREmitterError(f"Unsupported expression: {expr.__class__.__name__}")

    def _emit_const(self, lit: Literal) -> str:
        value = lit.value
        if isinstance(value, float):
            if not value.is_integer():
                raise MLIREmitterError(f"Non-integer literal not supported: {value}")
            value = int(value)
        elif isinstance(value, int):
            value = int(value)
        else:
            raise MLIREmitterError(f"Literal type not supported: {type(value).__name__}")

        name = self._fresh_value()
        self._emit_line(f"{name} = hintz.const {value} : i64")
        return name

    def _normalize_op(self, op) -> str:
        if hasattr(op, "value"):
            return str(op.value)
        return str(op)

    def _fresh_value(self) -> str:
        name = f"%{self._state.next_value_id}"
        self._state.next_value_id += 1
        return name

    def _ensure_var_slot(self, var_name: str) -> str:
        slot = self._state.var_slots.get(var_name)
        if slot is not None:
            return slot

        slot = self._fresh_value()
        self._state.var_slots[var_name] = slot
        self._emit_line(f"{slot} = hintz.alloca : memref<i64>")
        return slot

    def _lookup_var_slot(self, var_name: str) -> str:
        slot = self._state.var_slots.get(var_name)
        if slot is None:
            raise MLIREmitterError(
                f"Read of variable '{var_name}' is unsupported before assignment."
            )
        return slot

    def _emit_line(self, text: str) -> None:
        self._state.lines.append(("    " * self._state.indent) + text)


def emit_mlir(comp_ctx_or_cfgs) -> str:
    if hasattr(comp_ctx_or_cfgs, "cfgs"):
        return MLIREmitter().emit_cfgs(comp_ctx_or_cfgs.cfgs)
    if isinstance(comp_ctx_or_cfgs, Iterable):
        return MLIREmitter().emit_cfgs(list(comp_ctx_or_cfgs))
    raise MLIREmitterError(
        "emit_mlir expects a CompilationContext (with .cfgs) or a list of CFGs."
    )
