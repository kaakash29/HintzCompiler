# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from lark import Transformer, Token 
from typing import cast
from hintzCompiler.src.ir_nodes import *
from hintzCompiler.src.symbol_table import Symbol, ScopedSymbolTableManager
from dataclasses import fields

from hintzCompiler.src.ir_nodes import VarAccess, IRNode

class VarAccessCollector:
    def __init__(self):
        self.var_accesses = []

    def visit(self, node: IRNode):

        if not isinstance(node, IRNode):
            return

        if node is None:
            return
        
        if isinstance(node, VarAccess):
            self.var_accesses.append(node)

        # Recursively visit children if node has attributes that are IRNodes or lists of IRNodes
        for name, attr in vars(node).items():
            if isinstance(attr, IRNode):
                if not name.startswith("_"):
                    self.visit(attr)

            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, IRNode):
                        self.visit(item)

"""
Inherits from the Lark Transformer class and provides a visitor like traversal f
or every rule in the grammar, builds the AstNodes top down.

Shouts if an unhandled rule is encountered while parsing.
"""
class IRTransformer(Transformer):

    # public:

    def __init__(self):
        super().__init__()
        self.symtab_manager = ScopedSymbolTableManager()
        self.decldFcnVars : List[Variable] = []

    def get_global_scope(self):
        return self.symtab_manager.global_scope

    def transform(self, tree):
        return super().transform(tree)

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
            newV = Variable(name=name, type_spec="matrix", attributes={"dimensions": [int(items[2])]})
            self.decldFcnVars.append(newV)
            return newV

        newV = Variable(name=name, type_spec=None)
        self.decldFcnVars.append(newV)
        return newV

    def declaration(self, items):
        type_spec = items[0]
        vars = []
        declarators = items[1]
        for decl in declarators:


            if decl.type_spec == "matrix":
                newS = Symbol(  name=decl.name,
                                type="matrix",
                                attributes={"element_type": type_spec, "dimensions": decl.attributes["dimensions"]} )
                self.symtab_manager.current_scope.define(newS)
                decl._symbol = newS
            else:
                newS = Symbol(name=decl.name, type=type_spec)
                self.symtab_manager.current_scope.define(newS)
                decl._symbol = newS

            decl.type_spec=type_spec
            vars.append(decl)
        return vars

     

    
    @staticmethod
    def collect_from(stmt: IRNode) -> list[VarAccess]:
        collector = VarAccessCollector()
        collector.visit(stmt)
        return collector.var_accesses


    def function_def(self, items):
        return_type = items[0]
        fcnname = str(items[1])
        
        params = items[2]
        body = items[3]

        fcnIrNode = Function(return_type=return_type, name=fcnname, params=params, body=body, symbolTable=self.symtab_manager.current_scope, declaredVarsList=self.decldFcnVars)
       

        for stmt in body.statements:
            vas = IRTransformer.collect_from(stmt)
            #print(f"STMT: {stmt} VAS: {vas}")
            for va in vas:
                if va._var is None:
                    #print(f"\n * VAR was None. Looking for {va.name} in {self.decldFcnVars}")

                    varForSlot = next((v for v in self.decldFcnVars if v.name == va.name), None)
                    if varForSlot is not None:
                        va._var = varForSlot
                        #print(f" Set now.")


        if self.symtab_manager.isInFcnBody:
            self.symtab_manager.current_scope.name = f"{fcnname}"
            self.symtab_manager.pop_scope()
            self.symtab_manager.isInFcnBody = False
            self.decldFcnVars = []

        self.symtab_manager.current_scope.define(Symbol(name=fcnname, type=return_type, attributes={"params": params}))
        return fcnIrNode


    def param_list_container(self, items):
        if not self.symtab_manager.isInFcnBody:
            self.symtab_manager.isInFcnBody = True
            self.symtab_manager.push_scope(f"unnamedFcn")
        if len(items) > 2:
            for param in items[1]:
                if isinstance(param, Variable):
                    newS = Symbol(name=param.name, type=param.type_spec)  # pyright: ignore
                    self.symtab_manager.current_scope.define(newS)

                    param._symbol = newS
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
        if len(items) == 1:
            return items[0]
        else:
            assignS = Assignment(target=items[0], value=items[1])
            items[0]._parent = assignS
            items[1]._parent = assignS
            return assignS

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
            if isinstance(node.left, IRNode): node.left._parent = node
            if isinstance(node.right, IRNode): node.right._parent = node
        return node

    def primary(self, items):
        tok = items[0]
        if isinstance(tok, Token):
            if tok.type == "NUMBER":
                return Literal(value=float(tok))
            elif tok.type == "STRING":
                return Literal(value=str(tok)[1:-1])
            elif tok.type == "IDENT":
                symbol = self.symtab_manager.current_scope.lookup(str(tok));
                var = next((item for item in self.decldFcnVars if item.name == str(tok)), None)
                
                if symbol is None:
                    raise RuntimeError(f"\n Access of an undeclared symbol {str(tok)}.")

                # if var is None:
                #    raise RuntimeError(f"\n Access of an undeclared variable {str(tok)}.")
                
                va = VarAccess(name=str(tok), _var=var)
                return va
        return tok

    def param(self, items):
        var = Variable(name=str(items[1]), type_spec=str(items[0]), attributes={"isiovar":True})
        self.decldFcnVars.append(var)
        return var;

    def unary(self, children):
        if len(children) == 2 and isinstance(children[1], Token):
            # postfix: primary ++ or primary --
            expr, op = children
            uop = UnaryOp(op=op, operand=expr, is_postfix=True)
            uop.operand._parent = uop
            return uop
        elif len(children) == 2 and isinstance(children[0], Token):
            # prefix: ++ expr
            op, expr = children
            uop = UnaryOp(op=op, operand=expr, is_postfix=False)
            uop.operand._parent = uop
            return uop
        else:
            return children[0]

    def expr(self, items):
        return items[0]

    def stmt(self, items):
        return items[0]

    def field_access(self, items):
        base = items[0]
        field = str(items[2])
        fa = FieldAccess(base=base, field=field)
        fa.base._parent = fa #pyright: ignore
        return fa

    def array_access(self, items):
        base = items[0]
        index = items[2]
        aa = ArrayAccess(base=base, index=index)
        aa.base._parent = aa #pyright: ignore
        aa.index._parent = aa #pyright: ignore
        return aa

    def return_stmt(self, items):
        if len(items) >= 2:
            retN = Return(items[0])
            if retN.value is not None: retN.value._parent = retN
            return retN
        return Return(None);

    def func_call(self, items):
        name = str(items[0])
        fcnC = FunctionCall(name=name, args=[])
        if len(items) > 3:
            #fncC.args = [arg for arg in items[2:-1] if not (isinstance(arg, Token) and arg.type == "COMMA")]
            for item in items[2:-1]:
                if not isinstance(item, Token):
                    fcnC.args.append(item)
                    item._parent = fcnC
        return fcnC

    def if_stmt(self, children):
        condition = children[1]
        then_branch = children[3]
        else_branch = children[4] if len(children) == 5 else None
        ifs = If(condition=condition, then_branch=then_branch, else_branch=else_branch)
        ifs.condition._parent = ifs
        return ifs

    def for_stmt(self, children):
        init = children[1]
        cond = children[2]
        update = children[3]
        body = children[5]

        forS = For(init=init, condition=cond, update=update, body=body)
        if forS.init is not None: forS.init._parent = forS 
        if forS.condition is not None: forS.condition._parent = forS
        if forS.update is not None: forS.update._parent = forS
        return forS

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
        whileS = While(condition=cond, body=body)
        whileS.condition._parent = whileS
        return whileS

    def do_while_stmt(self, children):
        body = children[0];
        cond = children[2];
        doWhileS = DoWhile(body=body, condition=cond)
        doWhileS.condition._parent = doWhileS
        return doWhileS

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
        switchS = Switch(expr=expr, cases=cases)
        switchS.expr._parent = switchS
        return switchS





