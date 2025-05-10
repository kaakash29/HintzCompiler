from lark import Transformer, Token, Tree
from src.ir_nodes import *
from src.symbol_table import Symbol, ScopedSymbolTableManager

class IRTransformer(Transformer):
    def __init__(self):
        self.symtab_manager = ScopedSymbolTableManager()

    def get_global_symbol_table(self):
        return self.symtab_manager.global_scope

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

    def __default__(self, data, children, meta):
        print(f"DEFAULT HANDLER: Rule `{data}` with children: {children}")
        print(f"META: {meta}")
        return children

    def start(self, items):
        return items[0]

    def declaration_or_function(self, items):
        flat = []
        for item in items:
            if isinstance(item, list):
                flat.extend(item);
            else:
                flat.append(item);
        return flat;

    def struct_def(self, items):
        # Expecting:
        # [IDENT, ..., struct_body_tree, ...]
        name = str(items[0])  # items[1] is IDENT
        struct_body = items[2]  # items[3] is Tree('struct_body', [...])

        #print(f"StructName: ", name)
        #print(f"StructBody: ", struct_body)
        fields = {}
        for field_type, field_name in struct_body:
            fields[field_name] = field_type

        self.symtab_manager.current_scope.define(
            Symbol(name=name, type="struct", attributes={"fields": fields})
        )
        return None  # You may not need to return anything

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

        if isinstance(items[0], Tree) and items[0].data == "struct_type":
            return f"struct {items[0].children[0]}"
        return str(items[0])


    def struct_type(self, items):
        #print(f"in struct_type", items);
        return items[0]  # CNAME

    def declarator_list(self, items):
        return items

    def declarator(self, items):
        name = str(items[0])
        if len(items) == 2:
            return Variable(name=name, type_spec="matrix", attributes={"dimensions": [int(items[1])]})
        return Variable(name=name, type_spec=None)

    def declaration(self, items):
        #print(f"in declaration", items);
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
        name = str(items[1])
        params = []
        body = items[2]
        if len(items) == 5:
            body = items[4]
        elif len(items) > 5:
            params = items[3]
            body = items[5]
        self.symtab_manager.current_scope.define(Symbol(name=name, type=return_type, attributes={"params": params}))
        self.symtab_manager.push_scope()
        for param in params:
            if isinstance(param, Variable):
                self.symtab_manager.current_scope.define(Symbol(name=param.name, type=param.type_spec))
        self.symtab_manager.pop_scope()
        return Function(return_type=return_type, name=name, params=params, body=body)

    def param_list(self, items):
        return items

    def compound_stmt(self, items):
        #print(f"in compound_stmt", items);
        return Block(statements=items)

    def expr_stmt(self, items):
        #print(f"in expr_stmt", items);
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
        #print(f"in add", items);
        return self.reduce_ops(items)

    def mul(self, items):
        #print(f"in mul", items);
        return self.reduce_ops(items)

    def reduce_ops(self, items):
        #print(f"in reduce_ops", items);
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
        return tok  # already a transformed node (e.g., func_call, array_access, etc.)

    def param(self, items):
        return Variable(name=str(items[1]), type_spec=str(items[0]))

    def unary(self, items):
        return items[0]  # unwrap Identifier or Literal

    def expr(self, items):
        return items[0]  # usually an assignment

    def stmt(self, items):
        return items[0]  # usually an expr_stmt or compound_stmt

    def field_access(self, items):
        base = Identifier(name=str(items[0]))
        field = str(items[2])
        return FieldAccess(base=base, field=field)

    def array_access(self, items):
        base = Identifier(name=str(items[0]))
        index = items[2]
        return ArrayAccess(base=base, index=index)

    def return_stmt(self, items):
        if len(items) >= 1:
            return Return(items[0])
        return Return(None);

    def func_call(self, items):
        name = str(items[0])
        if len(items) > 1:
            args = items[1:]
            if isinstance(args[0], list):  # for grouped arguments
                args = args[0]
        else:
            args = []

        return FunctionCall(name=name, args=args)

