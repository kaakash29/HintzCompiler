# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from lark import Transformer, Token 
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.symbol_table import Symbol, ScopedSymbolTableManager

"""
Inherits from the Lark Transformer class and provides a visitor like traversal f
or every rule in the grammar, builds the AstNodes top down.

Shouts if an unhandled rule is encountered while parsing.
"""
class IRTransformer(Transformer):

    # public:

    def __init__(self):
        self.symtab_manager = ScopedSymbolTableManager()

    def get_global_symbol_table(self):
        return self.symtab_manager.global_scope

    ###############################################

    #private:
    def __default__(self, data, children, meta): # pragma: no cover
        print(f"Unhandled Pattern")
        print(f"Rule `{data}` with children: {children}")
        print(f"Meta {meta}")
        return children

    def program(self, items):
        flat = []
        for item in items:
            if item is None:
                continue  # skip struct_def returning None
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)
        return Program(declarations=flat)

    def start(self, items):
        return items[0]

    def struct_def(self, items):
        name = str(items[0])
        struct_body = items[2]

        fields = {}
        for field_type, field_name in struct_body:
            fields[field_name] = field_type

        self.symtab_manager.current_scope.define(
            Symbol(name=name, type="struct", attributes={"fields": fields})
        )
        return None

    def struct_body(self, items):
        fields = []
        for i in range(0, len(items), 3):
            type_spec = str(items[i])
            name = str(items[i + 1])
            fields.append((name, type_spec))
        return fields

    def type_specifier(self, items):
        if not items:
            raise ValueError("Empty type_specifier encountered. Check grammar or parser output.")
        return str(items[0])

    def struct_type(self, items):
        return items[0]  # CNAME

    def declarator_list(self, items):
        return items

    def declarator(self, items):
        name = str(items[0])

        if len(items) == 4:
            return Variable(name=name, type_spec="matrix", attributes={"dimensions": [int(items[2])]})

        return Variable(name=name, type_spec=None)

    def declaration(self, items):
        type_spec = items[0]
        vars = []
        declarators = items[1]
        for decl in declarators:
            if decl.type_spec == "matrix":
                self.symtab_manager.current_scope.define(Symbol(
                    name=decl.name,
                    type="matrix",
                    attributes={"element_type": type_spec, "dimensions": decl.attributes["dimensions"]}
                ))
            else:
                self.symtab_manager.current_scope.define(Symbol(name=decl.name, type=type_spec))
            decl.type_spec=type_spec
            vars.append(decl)
        return vars

    def function_def(self, items):
        return_type = items[0]
        fcnname = str(items[1])
        
        params = items[2]
        body = items[3]

        if self.symtab_manager.isInFcnBody:
            self.symtab_manager.current_scope.name = f"{fcnname}"

        for param in params:
            if isinstance(param, Variable):
                self.symtab_manager.current_scope.define(Symbol(name=param.name, type=param.type_spec)) # pyright: ignore
        
        fcnIrNode = Function(return_type=return_type, name=fcnname, params=params, body=body, symbolTable=self.symtab_manager.current_scope)

        if self.symtab_manager.isInFcnBody:
            self.symtab_manager.pop_scope()
            self.symtab_manager.isInFcnBody = False

        self.symtab_manager.current_scope.define(Symbol(name=fcnname, type=return_type, attributes={"params": params}))
        return fcnIrNode


    def param_list_container(self, items):
        if not self.symtab_manager.isInFcnBody:
            self.symtab_manager.isInFcnBody = True
            self.symtab_manager.push_scope(f"unnamedFcn")
        if len(items) > 2:
            return items[1]
        else:
            return [] 

    def param_list(self, items):
        args = [arg for arg in items if not (isinstance(arg, Token) and arg.type == "COMMA")]
        return args

    def compound_stmt(self, items):
        innerS = items[1:-1]
        return Block(statements=innerS)

    def expr_stmt(self, items):
        return items[0]

    def assignment(self, items):
        return items[0] if len(items) == 1 else Assignment(target=items[0], value=items[1])

    def relational(self, items):
        return self.reduce_ops(items);

    def equality(self, items):
        return self.reduce_ops(items)

    def logic_and(self, items):
        return self.reduce_ops(items)

    def logic_or(self, items):
        return self.reduce_ops(items)

    def add(self, items):
        return self.reduce_ops(items)

    def mul(self, items):
        return self.reduce_ops(items)

    def reduce_ops(self, items):
        if len(items) == 1:
            return items[0]
        node = items[0]
        for i in range(1, len(items), 2):
            node = BinaryOp(op=items[i], left=node, right=items[i+1])
        return node

    def primary(self, items):
        tok = items[0]
        if isinstance(tok, Token):
            if tok.type == "NUMBER":
                return Literal(value=float(tok))
            elif tok.type == "STRING":
                return Literal(value=str(tok)[1:-1])
            elif tok.type == "IDENT":
                return Identifier(name=str(tok))
        return tok

    def param(self, items):
        return Variable(name=str(items[1]), type_spec=str(items[0]))

    def unary(self, children):
        if len(children) == 2 and isinstance(children[1], Token):
            # postfix: primary ++ or primary --
            expr, op = children
            return UnaryOp(op=op, operand=expr, is_postfix=True)
        elif len(children) == 2 and isinstance(children[0], Token):
            # prefix: ++ expr
            op, expr = children
            return UnaryOp(op=op, operand=expr, is_postfix=False)
        else:
            return children[0]

    def expr(self, items):
        return items[0]

    def stmt(self, items):
        return items[0]

    def field_access(self, items):
        base = items[0]
        field = str(items[2])
        return FieldAccess(base=base, field=field)

    def array_access(self, items):
        base = items[0]
        index = items[2]
        return ArrayAccess(base=base, index=index)

    def return_stmt(self, items):
        if len(items) >= 2:
            return Return(items[0])
        return Return(None);

    def func_call(self, items):
        name = str(items[0])
        if len(items) > 3:
            args = [arg for arg in items[2:-1] if not (isinstance(arg, Token) and arg.type == "COMMA")]
        else:
            args = []

        return FunctionCall(name=name, args=args)

    def if_stmt(self, children):
        condition = children[1]
        then_branch = children[3]
        else_branch = children[4] if len(children) == 5 else None
        return If(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def for_stmt(self, children):
        init = children[1]
        cond = children[2]
        update = children[3]
        body = children[5]

        return For(init=init, condition=cond, update=update, body=body)

    def for_init(self, children):
        if len(children) == 1:
            return None
        return children[0]

    def for_cond(self, children):
        if len(children) == 1:
            return None
        return children[0]

    def for_update(self, children):
        if len(children) == 0:
            return None
        return children[0]

    def while_stmt(self, children):
        cond = children[1];
        body = children[3];
        return While(condition=cond, body=body)

    def do_while_stmt(self, children):
        body = children[0];
        cond = children[2];
        return DoWhile(body=body, condition=cond)

    def goto_stmt(self, children):
        label = children[0].value
        return Goto(label=label)

    def label_stmt(self, children):
        label = children[0].value
        return Label(name=label)

    def break_stmt(self, _):
        return Break()

    def case_block(self, children):
        value = children[0]
        stmts = children[2:]
        return Case(value=value, body=Block(statements=stmts))

    def default_block(self, children):
        stmts = children[1:]
        return Case(value=None, body=Block(statements=stmts))

    def switch_stmt(self, children):
        expr = children[1]
        cases = children[4:-1]
        return Switch(expr=expr, cases=cases)
