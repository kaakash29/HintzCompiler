# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from __future__ import annotations

from typing import Iterable, List, Optional

from hintzCompiler.src.cfg import ControlFlowGraph
from hintzCompiler.src.ir_nodes import (
    ArrayAccess,
    Assignment,
    BinaryOp,
    Block,
    Break,
    Case,
    Declaration,
    DoWhile,
    FieldAccess,
    For,
    Function,
    FunctionCall,
    Goto,
    If,
    IRNode,
    Label,
    Literal,
    Return,
    Switch,
    UnaryOp,
    VarAccess,
    Variable,
    While,
    Call,
)


class HintzCfgDumper:
    """
    Emits Hintz source code from a ControlFlowGraph's IR.

    This is a structured, AST-based dump of the function IR attached to the CFG.
    """

    def __init__(self, cfg: ControlFlowGraph, de_ssa: bool = False):
        self.cfg = cfg
        self._indent_unit = "    "
        self._de_ssa = de_ssa

    def dump(self) -> str:
        return self._emit_function(self.cfg.fcn)

    def _emit_function(self, fcn: Function) -> str:
        params = ", ".join(self._emit_param(p) for p in fcn.params)
        header = f"{fcn.return_type} {fcn.name}({params})"
        body = self._emit_block(fcn.body, indent=0)
        return f"{header} {body}"

    def _emit_block(self, block: Block, indent: int) -> str:
        lines: List[str] = []
        lines.append(f"{self._indent(indent)}{{")
        for stmt in block.statements:
            lines.extend(self._emit_stmt_lines(stmt, indent + 1))
        lines.append(f"{self._indent(indent)}}}")
        return "\n".join(lines)

    def _emit_stmt_lines(self, stmt: IRNode, indent: int) -> List[str]:
        if isinstance(stmt, Block):
            return self._emit_block(stmt, indent=indent).splitlines()

        if isinstance(stmt, Declaration):
            return self._emit_declaration_lines(stmt, indent)

        if isinstance(stmt, If):
            return self._emit_if(stmt, indent)

        if isinstance(stmt, While):
            return self._emit_while(stmt, indent)

        if isinstance(stmt, DoWhile):
            return self._emit_do_while(stmt, indent)

        if isinstance(stmt, For):
            return self._emit_for(stmt, indent)

        if isinstance(stmt, Switch):
            return self._emit_switch(stmt, indent)

        if isinstance(stmt, Return):
            if stmt.value is None:
                return [f"{self._indent(indent)}return;"]
            return [f"{self._indent(indent)}return {self._emit_expr(stmt.value)};"]

        if isinstance(stmt, Break):
            return [f"{self._indent(indent)}break;"]

        if isinstance(stmt, Goto):
            return [f"{self._indent(indent)}goto {stmt.label};"]

        if isinstance(stmt, Label):
            return [f"{self._indent(indent)}{stmt.name}:"]

        # Expression statement (assignment, call, etc.)
        return [f"{self._indent(indent)}{self._emit_expr(stmt)};"]

    def _emit_if(self, stmt: If, indent: int) -> List[str]:
        cond = self._emit_expr(stmt.condition)
        lines: List[str] = []
        lines.extend(self._emit_prefixed_stmt(f"if ({cond})", stmt.then_branch, indent))
        if stmt.else_branch is not None:
            lines.extend(self._emit_prefixed_stmt("else", stmt.else_branch, indent))
        return lines

    def _emit_while(self, stmt: While, indent: int) -> List[str]:
        cond = self._emit_expr(stmt.condition)
        return self._emit_prefixed_stmt(f"while ({cond})", stmt.body, indent)

    def _emit_do_while(self, stmt: DoWhile, indent: int) -> List[str]:
        lines: List[str] = []
        if isinstance(stmt.body, Block):
            body_lines = self._emit_block(stmt.body, indent=indent).splitlines()
            lines.append(f"{self._indent(indent)}do")
            lines.extend(body_lines)
            lines.append(f"{self._indent(indent)}while ({self._emit_expr(stmt.condition)});")
            return lines

        body_line = self._emit_stmt_lines(stmt.body, indent)
        lines.append(f"{self._indent(indent)}do")
        lines.extend(body_line)
        lines.append(f"{self._indent(indent)}while ({self._emit_expr(stmt.condition)});")
        return lines

    def _emit_for(self, stmt: For, indent: int) -> List[str]:
        init = self._emit_expr(stmt.init) if stmt.init is not None else ""
        cond = self._emit_expr(stmt.condition) if stmt.condition is not None else ""
        update = self._emit_expr(stmt.update) if stmt.update is not None else ""
        return self._emit_prefixed_stmt(f"for ({init}; {cond}; {update})", stmt.body, indent)

    def _emit_switch(self, stmt: Switch, indent: int) -> List[str]:
        lines: List[str] = []
        lines.append(f"{self._indent(indent)}switch ({self._emit_expr(stmt.expr)}) {{")
        for case in stmt.cases:
            lines.extend(self._emit_case(case, indent + 1))
        lines.append(f"{self._indent(indent)}}}")
        return lines

    def _emit_case(self, case: Case, indent: int) -> List[str]:
        lines: List[str] = []
        if case.value is None:
            lines.append(f"{self._indent(indent)}default:")
        else:
            lines.append(f"{self._indent(indent)}case {self._emit_expr(case.value)}:")

        for stmt in case.body.statements:
            lines.extend(self._emit_stmt_lines(stmt, indent + 1))
        return lines

    def _emit_prefixed_stmt(self, prefix: str, stmt: IRNode, indent: int) -> List[str]:
        if isinstance(stmt, Block):
            lines: List[str] = []
            lines.append(f"{self._indent(indent)}{prefix} {{")
            for inner in stmt.statements:
                lines.extend(self._emit_stmt_lines(inner, indent + 1))
            lines.append(f"{self._indent(indent)}}}")
            return lines

        return [f"{self._indent(indent)}{prefix} {self._emit_stmt_single(stmt, indent)}"]

    def _emit_stmt_single(self, stmt: IRNode, indent: int) -> str:
        if isinstance(stmt, Return):
            if stmt.value is None:
                return "return;"
            return f"return {self._emit_expr(stmt.value)};"
        if isinstance(stmt, Break):
            return "break;"
        if isinstance(stmt, Goto):
            return f"goto {stmt.label};"
        if isinstance(stmt, Label):
            return f"{stmt.name}:"
        if isinstance(stmt, Declaration):
            decl_lines = self._emit_declaration_lines(stmt, indent)
            if len(decl_lines) == 1:
                return decl_lines[0].strip()
        return f"{self._emit_expr(stmt)};"

    def _emit_declaration_lines(self, stmt: Declaration, indent: int) -> List[str]:
        lines: List[str] = []
        groups: dict[str, List[Variable]] = {}
        for v in stmt.decls:
            if v.type_spec is None:
                continue
            groups.setdefault(v.type_spec, []).append(v)

        for type_spec, vars_list in groups.items():
            decls = ", ".join(self._emit_var_decl(v) for v in vars_list)
            lines.append(f"{self._indent(indent)}{type_spec} {decls};")
        return lines

    def _emit_param(self, var: Variable) -> str:
        type_spec = var.type_spec or "int"
        return f"{type_spec} {self._emit_var_decl(var)}"

    def _emit_var_decl(self, var: Variable) -> str:
        name = var.name
        dims = var.attributes.get("dimensions") if var.attributes else None
        if dims:
            suffix = "".join(f"[{d}]" for d in dims)
            return f"{name}{suffix}"
        return name

    def _emit_expr(self, node: IRNode, parent_prec: int = 0) -> str:
        if isinstance(node, Assignment):
            expr = f"{self._emit_expr(node.target, parent_prec=1)} = {self._emit_expr(node.value, parent_prec=1)}"
            return self._maybe_paren(expr, parent_prec, 1)

        if isinstance(node, BinaryOp):
            op = self._op_value(node.op)
            prec = self._bin_prec(op)
            left = self._emit_expr(node.left, parent_prec=prec)
            right = self._emit_expr(node.right, parent_prec=prec)
            expr = f"{left} {op} {right}"
            return self._maybe_paren(expr, parent_prec, prec)

        if isinstance(node, UnaryOp):
            op = self._op_value(node.op)
            if node.is_postfix:
                expr = f"{self._emit_expr(node.operand, parent_prec=8)}{op}"
            else:
                expr = f"{op}{self._emit_expr(node.operand, parent_prec=8)}"
            return self._maybe_paren(expr, parent_prec, 8)

        if isinstance(node, Literal):
            if isinstance(node.value, str):
                return self._quote_string(node.value)
            if isinstance(node.value, float) and node.value.is_integer():
                return str(int(node.value))
            return str(node.value)

        if isinstance(node, VarAccess):
            return self._de_ssa_name(node.name) if self._de_ssa else node.name

        if isinstance(node, FieldAccess):
            base = self._emit_expr(node.base, parent_prec=9)
            return f"{base}.{node.field}"

        if isinstance(node, ArrayAccess):
            base = self._emit_expr(node.base, parent_prec=9)
            index = self._emit_expr(node.index, parent_prec=0)
            return f"{base}[{index}]"

        if isinstance(node, FunctionCall):
            args = ", ".join(self._emit_expr(a, parent_prec=0) for a in node.args)
            return f"{node.name}({args})"

        if isinstance(node, Call):
            args = ", ".join(self._emit_expr(a, parent_prec=0) for a in node.args)
            return f"{node.func}({args})"

        return str(node)

    def _bin_prec(self, op: str) -> int:
        if op in {"||"}:
            return 2
        if op in {"&&"}:
            return 3
        if op in {"==", "!="}:
            return 4
        if op in {"<", ">", "<=", ">="}:
            return 5
        if op in {"+", "-"}:
            return 6
        if op in {"*", "/", "%"}:
            return 7
        return 9

    def _op_value(self, op) -> str:
        return op.value if hasattr(op, "value") else str(op)

    def _maybe_paren(self, expr: str, parent_prec: int, my_prec: int) -> str:
        if my_prec < parent_prec:
            return f"({expr})"
        return expr

    def _quote_string(self, value: str) -> str:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f"\"{escaped}\""

    def _de_ssa_name(self, name: str) -> str:
        i = len(name)
        while i > 0 and name[i - 1].isdigit():
            i -= 1
        return name[:i] if i != len(name) else name

    def _indent(self, level: int) -> str:
        return self._indent_unit * level
