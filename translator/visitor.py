import sys
sys.path.insert(0, '../generated')

from generated.Python3ParserVisitor import Python3ParserVisitor
from generated.Python3Parser import Python3Parser


class PythonToGoVisitor(Python3ParserVisitor):

    def __init__(self):
        self.imports = set()        # paquetes Go que se necesitan
        self.indent_level = 0
        self.output = []
        self.declared_vars = set()  # variables ya declaradas → usar = en vez de :=

    # ─────────────────────────────────────────────
    # Utilidades internas
    # ─────────────────────────────────────────────

    def indent(self):
        return "\t" * self.indent_level

    def add_import(self, pkg):
        self.imports.add(pkg)

    def get_result(self, stmts_code: str, top_funcs: str = "") -> str:
        """Ensambla el archivo Go final con package + imports + funciones + func main()."""
        lines = ["package main", ""]
        if self.imports:
            lines.append("import (")
            for pkg in sorted(self.imports):
                lines.append(f'\t"{pkg}"')
            lines.append(")")
            lines.append("")
        # Indentar el cuerpo dentro de func main()
        # Proteger líneas internas de raw strings (backticks) de la indentación
        indented_lines = []
        inside_raw = False
        for line in stmts_code.splitlines():
            backtick_count = line.count("`")
            if inside_raw:
                indented_lines.append(line)
                if backtick_count % 2 == 1:
                    inside_raw = False
            else:
                if backtick_count % 2 == 1:
                    inside_raw = True
                indented_lines.append(f"\t{line}" if line.strip() else "")
        indented_body = "\n".join(indented_lines)
        if top_funcs:
            lines.append(top_funcs)
            lines.append("")
        lines.append("func main() {")
        lines.append(indented_body)
        lines.append("}")
        return "\n".join(lines)

    # ─────────────────────────────────────────────
    # Punto de entrada
    # ─────────────────────────────────────────────

    def visitFile_input(self, ctx: Python3Parser.File_inputContext):
        top_funcs = []   # funciones definidas a nivel top → fuera de main()
        stmts = []       # resto de statements → dentro de main()
        for child in ctx.children:
            if isinstance(child, Python3Parser.StmtContext):
                compound = child.compound_stmt() if hasattr(child, 'compound_stmt') else None
                is_funcdef = (compound is not None and
                              compound.funcdef() is not None)
                if is_funcdef:
                    top_funcs.append(self.visit(child))
                else:
                    stmts.append(self.visit(child))
        body = "\n".join(s for s in stmts if s)
        funcs = "\n\n".join(f for f in top_funcs if f)
        return self.get_result(body, funcs)

    # ─────────────────────────────────────────────
    # Statements
    # ─────────────────────────────────────────────

    def visitStmt(self, ctx: Python3Parser.StmtContext):
        return self.visit(ctx.getChild(0))

    def visitSimple_stmts(self, ctx: Python3Parser.Simple_stmtsContext):
        parts = []
        for child in ctx.children:
            if isinstance(child, Python3Parser.Simple_stmtContext):
                parts.append(self.visit(child))
        return "\n".join(p for p in parts if p)

    def visitSimple_stmt(self, ctx: Python3Parser.Simple_stmtContext):
        return self.visit(ctx.getChild(0))

    # ─────────────────────────────────────────────
    # Compound statements (if/elif/else)
    # ─────────────────────────────────────────────

    def visitCompound_stmt(self, ctx: Python3Parser.Compound_stmtContext):
        return self.visit(ctx.getChild(0))

    def visitIf_stmt(self, ctx: Python3Parser.If_stmtContext):
        """
        if_stmt: 'if' test ':' block
                 ('elif' test ':' block)*
                 ('else' ':' block)?
        Estructura del árbol (hijos):
          IF test COLON block (ELIF test COLON block)* (ELSE COLON block)?
        """
        children = list(ctx.children)
        result_lines = []
        i = 0
        first = True

        while i < len(children):
            token = children[i].getText()

            if token == "if" or token == "elif":
                keyword = "if" if first else "} else if"
                first = False
                cond = self.visit(children[i + 1])   # test
                # i+2 es ':'
                block = children[i + 3]              # block
                body = self._visit_block(block)
                result_lines.append(f"{self.indent()}{keyword} {cond} {{")
                result_lines.append(body)
                i += 4

            elif token == "else":
                # i+1 es ':'
                block = children[i + 2]
                body = self._visit_block(block)
                result_lines.append(f"{self.indent()}}} else {{")
                result_lines.append(body)
                i += 3

            else:
                i += 1

        result_lines.append(f"{self.indent()}}}")
        return "\n".join(result_lines)


    def _visit_block(self, ctx) -> str:
        """Visita un bloque indentado y devuelve su contenido con un nivel más de indentación."""
        self.indent_level += 1
        lines = []
        for child in ctx.children:
            if isinstance(child, Python3Parser.StmtContext):
                lines.append(self.visit(child))
            elif isinstance(child, Python3Parser.Simple_stmtsContext):
                lines.append(self.visit(child))
        self.indent_level -= 1
        return "\n".join(l for l in lines if l)


    # ─────────────────────────────────────────────
    # Listas
    # ─────────────────────────────────────────────

    def _translate_list(self, ctx) -> str:
        """Traduce una lista Python a []interface{}{...}"""
        if ctx.testlist_comp():
            # Verificar si es list comprehension
            tc = ctx.testlist_comp()
            if tc.comp_for():
                return self._translate_list_comprehension(tc)
            items = self._get_testlist_comp_items(tc)
            return f"[]interface{{}}{{{', '.join(items)}}}"
        return "[]interface{}{}"

    def _get_testlist_comp_items(self, ctx) -> list:
        """Extrae los elementos de un testlist_comp como lista de strings."""
        items = []
        for child in ctx.children:
            text = child.getText()
            if text == ",":
                continue
            if isinstance(child, Python3Parser.Comp_forContext):
                break
            items.append(self.visit(child))
        return items

    def _translate_list_comprehension(self, ctx) -> str:
        """
        [expr for var in iterable if cond]
        Genera una IIFE Go sin indentación propia (la maneja el statement padre).
        """
        expr = self.visit(ctx.getChild(0))
        comp_for = ctx.comp_for()
        target = self.visit(comp_for.exprlist())
        iterable = self.visit(comp_for.or_test())

        cond = ""
        if comp_for.comp_iter() and comp_for.comp_iter().comp_if():
            cond = self.visit(comp_for.comp_iter().comp_if().test_nocond())

        result_lines = ["func() []interface{} {"]
        result_lines.append("\tresult := []interface{}{}")

        if iterable.startswith("range("):
            inner = iterable[6:-1]
            args = [a.strip() for a in inner.split(",")]
            if len(args) == 1:
                loop = f"\tfor {target} := 0; {target} < {args[0]}; {target}++"
            elif len(args) == 2:
                loop = f"\tfor {target} := {args[0]}; {target} < {args[1]}; {target}++"
            else:
                loop = f"\tfor {target} := {args[0]}; {target} < {args[1]}; {target} += {args[2]}"
            result_lines.append(loop + " {")
        else:
            result_lines.append(f"\tfor _, {target} := range {iterable} {{")

        if cond:
            result_lines.append(f"\t\tif {cond} {{")
            result_lines.append(f"\t\t\tresult = append(result, {expr})")
            result_lines.append("\t\t}")
        else:
            result_lines.append(f"\t\tresult = append(result, {expr})")
        result_lines.append("\t}")
        result_lines.append("\treturn result")
        result_lines.append("}()")
        return "\n".join(result_lines)


    def visitFuncdef(self, ctx: Python3Parser.FuncdefContext):
        # 'def' name parameters ('->' test)? ':' block
        name = ctx.name().getText()
        params_go, defaults = self._translate_params(ctx.parameters())
        body = self._visit_block(ctx.block())

        # Detectar si hay return múltiple para inferir tipo de retorno
        return_type = self._infer_return_type(ctx.block())

        lines = []
        # Si hay valores por defecto, generar comentario explicativo
        if defaults:
            for param, val in defaults.items():
                lines.append(f"// Parámetro '{param}' tiene valor por defecto: {val}")

        rt = f" {return_type}" if return_type else ""
        lines.append(f"func {name}({params_go}){rt} {{")
        lines.append(body)
        lines.append("}")
        return "\n".join(lines)

    def _translate_params(self, ctx: Python3Parser.ParametersContext):
        """Traduce parámetros de Python a Go. Devuelve (params_str, defaults_dict)."""
        if not ctx.typedargslist():
            return "", {}

        args_ctx = ctx.typedargslist()
        params = []
        defaults = {}
        children = list(args_ctx.children)
        i = 0

        while i < len(children):
            child = children[i]
            text = child.getText()

            if text in (",", "(", ")"):
                i += 1
                continue

            if text == "*":
                # *args → args ...interface{}
                i += 1
                if i < len(children) and children[i].getText() not in (",", ")"):
                    arg_name = children[i].getText()
                    params.append(f"{arg_name} ...interface{{}}")
                    i += 1
                continue

            if text == "**":
                # **kwargs → kwargs map[string]interface{}
                i += 1
                if i < len(children) and children[i].getText() not in (",", ")"):
                    arg_name = children[i].getText()
                    params.append(f"{arg_name} map[string]interface{{}}")
                    i += 1
                continue

            # Nombre de parámetro (puede ser tfpdef: name o name:type)
            if hasattr(child, 'name') or isinstance(child, Python3Parser.TfpdefContext):
                param_name = child.getText().split(":")[0]  # ignorar anotación de tipo
                # Ver si el siguiente token es '='
                if i + 1 < len(children) and children[i+1].getText() == "=":
                    default_val = children[i+2].getText()
                    defaults[param_name] = default_val
                    params.append(f"{param_name} interface{{}}")
                    i += 3
                    continue
                else:
                    params.append(f"{param_name} interface{{}}")

            i += 1

        return ", ".join(params), defaults

    def _infer_return_type(self, block_ctx) -> str:
        """Detecta si la función retorna múltiples valores o ninguno."""
        returns = self._find_returns(block_ctx)
        if not returns:
            return ""  # void en Go → sin tipo
        # Si algún return tiene coma → retorno múltiple
        for r in returns:
            if r and "," in r:
                count = r.count(",") + 1
                return "(" + ", ".join(["interface{}"] * count) + ")"
        return "interface{}"

    def _find_returns(self, ctx, found=None) -> list:
        """Busca todos los return_stmt en un bloque."""
        if found is None:
            found = []
        if isinstance(ctx, Python3Parser.Return_stmtContext):
            if ctx.testlist():
                found.append(ctx.testlist().getText())
            else:
                found.append(None)
            return found
        for i in range(ctx.getChildCount()):
            self._find_returns(ctx.getChild(i), found)
        return found

    def visitReturn_stmt(self, ctx: Python3Parser.Return_stmtContext):
        if ctx.testlist():
            val = self.visit(ctx.testlist())
            return f"{self.indent()}return {val}"
        return f"{self.indent()}return"

    # ─────────────────────────────────────────────
    # Bucles: while y for
    # ─────────────────────────────────────────────

    def visitWhile_stmt(self, ctx: Python3Parser.While_stmtContext):
        # while test ':' block ('else' ':' block)?
        cond = self.visit(ctx.test())
        body = self._visit_block(ctx.block(0))
        lines = [f"{self.indent()}for {cond} {{", body, f"{self.indent()}}}"]
        # else en while no existe en Go
        if len(ctx.block()) > 1:
            else_body = self._visit_block(ctx.block(1))
            lines.append(f"{self.indent()}// else del while (no existe en Go):")
            lines.append(else_body)
        return "\n".join(lines)

    def visitFor_stmt(self, ctx: Python3Parser.For_stmtContext):
        # for exprlist 'in' testlist ':' block ('else' ':' block)?
        targets = self.visit(ctx.exprlist())   # variable(s) del for
        iterable_ctx = ctx.testlist()
        iterable = self.visit(iterable_ctx)

        # Detectar si el iterable es range(...)
        iterable_text = iterable_ctx.getText()
        if iterable_text.startswith("range("):
            return self._for_range(targets, iterable_ctx, ctx.block(0))

        # Detectar enumerate(...)
        if iterable_text.startswith("enumerate("):
            return self._for_enumerate(targets, iterable_ctx, ctx.block(0))

        # for x in iterable genérico → for _, x := range iterable
        body = self._visit_block(ctx.block(0))

        # Detectar marcadores de métodos de diccionario
        if iterable.startswith("__items__"):
            base = iterable[len("__items__"):]
            header = f"{self.indent()}for {targets} := range {base} {{"
        elif iterable.startswith("__keys__"):
            base = iterable[len("__keys__"):]
            # Solo un target → for k := range dict
            header = f"{self.indent()}for {targets} := range {base} {{"
        elif iterable.startswith("__values__"):
            base = iterable[len("__values__"):]
            header = f"{self.indent()}for _, {targets} := range {base} {{"
        elif "," in targets:
            header = f"{self.indent()}for {targets} := range {iterable} {{"
        else:
            header = f"{self.indent()}for _, {targets} := range {iterable} {{"
        lines = [header, body, f"{self.indent()}}}"]

        # else en for no existe en Go
        if len(ctx.block()) > 1:
            else_body = self._visit_block(ctx.block(1))
            lines.append(f"{self.indent()}// else del for (no existe en Go):")
            lines.append(else_body)
        return "\n".join(lines)

    def _for_range(self, targets: str, iterable_ctx, block_ctx) -> str:
        """Traduce for i in range(...) al estilo C de Go."""
        # Extraer argumentos del range del árbol
        # iterable_ctx es testlist que contiene un test → atom_expr → atom → name=range + trailer(arglist)
        args = self._extract_call_args(iterable_ctx)

        if len(args) == 1:
            # range(stop) → for i := 0; i < stop; i++
            stop = args[0]
            return self._for_c_style(targets, "0", stop, "1", block_ctx)
        elif len(args) == 2:
            # range(start, stop) → for i := start; i < stop; i++
            start, stop = args[0], args[1]
            return self._for_c_style(targets, start, stop, "1", block_ctx)
        elif len(args) == 3:
            # range(start, stop, step)
            start, stop, step = args[0], args[1], args[2]
            return self._for_c_style(targets, start, stop, step, block_ctx)

        # Fallback
        body = self._visit_block(block_ctx)
        return f"{self.indent()}for _, {targets} := range {self.visit(iterable_ctx)} {{{body}{self.indent()}}}"

    def _for_c_style(self, var: str, start: str, stop: str, step: str, block_ctx) -> str:
        """Genera un for estilo C: for i := start; i < stop; i += step"""
        body = self._visit_block(block_ctx)
        # step negativo → condición invertida
        try:
            step_val = int(step)
            if step_val < 0:
                cond = f"{var} > {stop}"
            else:
                cond = f"{var} < {stop}"
        except ValueError:
            cond = f"{var} < {stop}"

        if step == "1":
            post = f"{var}++"
        elif step == "-1":
            post = f"{var}--"
        else:
            post = f"{var} += {step}"

        header = f"{self.indent()}for {var} := {start}; {cond}; {post} {{"
        return "\n".join([header, body, f"{self.indent()}}}"])

    def _for_enumerate(self, targets: str, iterable_ctx, block_ctx) -> str:
        """Traduce for i, v in enumerate(iterable) → for i, v := range iterable"""
        args = self._extract_call_args(iterable_ctx)
        inner = args[0] if args else self.visit(iterable_ctx)
        body = self._visit_block(block_ctx)
        header = f"{self.indent()}for {targets} := range {inner} {{"
        return "\n".join([header, body, f"{self.indent()}}}"])

    def _extract_call_args(self, ctx) -> list:
        """Extrae los argumentos de texto de una llamada tipo range(...) o enumerate(...)
        recorriendo el árbol hasta encontrar el arglist."""
        # Buscar arglist en profundidad
        args = []
        self._find_args(ctx, args)
        return args

    def _find_args(self, ctx, args: list):
        from antlr4 import TerminalNode
        if isinstance(ctx, Python3Parser.ArgumentContext):
            args.append(self.visit(ctx))
            return
        if isinstance(ctx, TerminalNode):
            return
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, Python3Parser.ArglistContext):
                for arg in child.argument():
                    args.append(self.visit(arg))
                return
            self._find_args(child, args)

    def visitExprlist(self, ctx: Python3Parser.ExprlistContext):
        parts = []
        for child in ctx.children:
            if child.getText() != ",":
                parts.append(self.visit(child))
        return ", ".join(parts)

    # ─────────────────────────────────────────────
    # Asignaciones
    # ─────────────────────────────────────────────

    def visitExpr_stmt(self, ctx: Python3Parser.Expr_stmtContext):
        # Augmented assignment: x += 1
        if ctx.augassign():
            lhs = self.visit(ctx.testlist_star_expr(0))
            op  = ctx.augassign().getText()
            if op == "//=":
                op = "/="
            if op == "**=":
                self.add_import("math")
                rhs = self.visit(ctx.getChild(2))
                return f"{self.indent()}{lhs} = int(math.Pow(float64({lhs}), float64({rhs})))"
            rhs = self.visit(ctx.getChild(2))
            return f"{self.indent()}{lhs} {op} {rhs}"

        # Annotated assignment: x: int = 5
        if ctx.annassign():
            lhs = self.visit(ctx.testlist_star_expr(0))
            ann = ctx.annassign()
            if ann.getChildCount() == 4:
                rhs = self.visit(ann.getChild(3))
                op = "=" if lhs in self.declared_vars else ":="
                self.declared_vars.add(lhs)
                return f"{self.indent()}{lhs} {op} {rhs}"
            return ""

        exprs = [ctx.testlist_star_expr(i)
                 for i in range(len(ctx.testlist_star_expr()))]

        if len(exprs) == 2:
            lhs_ctx = exprs[0]
            rhs_ctx = exprs[1]
            lhs = self.visit(lhs_ctx)
            rhs = self.visit(rhs_ctx)

            # Asignación múltiple: a, b = 0, 1
            lhs_has_comma = any(
                lhs_ctx.getChild(i).getText() == ","
                for i in range(lhs_ctx.getChildCount())
            )

            # Determinar si usar := o =
            if lhs_has_comma:
                vars_list = [v.strip() for v in lhs.split(",")]
                any_new = any(v not in self.declared_vars for v in vars_list)
                op = ":=" if any_new else "="
                for v in vars_list:
                    self.declared_vars.add(v)
            elif "[" in lhs or "." in lhs:
                # Acceso a índice o atributo → siempre =
                op = "="
            else:
                op = "=" if lhs in self.declared_vars else ":="
                self.declared_vars.add(lhs)

            return f"{self.indent()}{lhs} {op} {rhs}"

        # Expresión sola (llamada a función, etc.)
        if len(exprs) == 1:
            return f"{self.indent()}{self.visit(exprs[0])}"

        return ""

    # Expresiones
    # ─────────────────────────────────────────────

    def visitTestlist_star_expr(self, ctx: Python3Parser.Testlist_star_exprContext):
        parts = []
        for child in ctx.children:
            text = child.getText()
            if text == ",":
                parts.append(", ")
            else:
                parts.append(self.visit(child))
        return "".join(parts)

    def visitTest(self, ctx: Python3Parser.TestContext):
        # Ternario: a if cond else b  →  Go no tiene ternario, se deja como comentario
        if ctx.getChildCount() == 5:
            val_true = self.visit(ctx.or_test(0))
            cond     = self.visit(ctx.or_test(1))
            val_false= self.visit(ctx.test())
            # Se emite como variable temporal con if/else
            return f"/* ternario: {val_true} if {cond} else {val_false} */"
        if ctx.lambdef():
            return self.visit(ctx.lambdef())
        return self.visit(ctx.or_test(0))

    def visitOr_test(self, ctx: Python3Parser.Or_testContext):
        parts = [self.visit(ctx.and_test(i)) for i in range(len(ctx.and_test()))]
        return " || ".join(parts)

    def visitAnd_test(self, ctx: Python3Parser.And_testContext):
        parts = [self.visit(ctx.not_test(i)) for i in range(len(ctx.not_test()))]
        return " && ".join(parts)

    def visitNot_test(self, ctx: Python3Parser.Not_testContext):
        if ctx.getChildCount() == 2:   # 'not' not_test
            operand = self.visit(ctx.not_test())
            # Solo añadir paréntesis si el operando es compuesto (tiene espacios)
            if " " in operand and not operand.startswith("!"):
                return f"!({operand})"
            return f"!{operand}"
        return self.visit(ctx.comparison())

    def visitComparison(self, ctx: Python3Parser.ComparisonContext):
        parts = [self.visit(ctx.expr(0))]
        for i, op_ctx in enumerate(ctx.comp_op()):
            op = self._comp_op(op_ctx)
            parts.append(op)
            parts.append(self.visit(ctx.expr(i + 1)))
        return " ".join(parts)

    def _comp_op(self, ctx: Python3Parser.Comp_opContext) -> str:
        text = ctx.getText()
        mapping = {
            "<": "<", ">": ">", "==": "==", ">=": ">=", "<=": "<=",
            "!=": "!=", "<>": "!=",
            "in": "/* in */",       # requiere lógica especial
            "notin": "/* not in */",
            "is": "==",
            "isnot": "!=",
        }
        return mapping.get(text, text)

    def visitExpr(self, ctx: Python3Parser.ExprContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.getChild(0))

        # Unario: +x  -x  ~x
        if ctx.getChildCount() == 2:
            op = ctx.getChild(0).getText()
            operand = self.visit(ctx.getChild(1))
            return f"{op}{operand}"

        # Binario
        left  = self.visit(ctx.getChild(0))
        op    = ctx.getChild(1).getText()
        right = self.visit(ctx.getChild(2))

        # Python ** → Go math.Pow
        if op == "**":
            self.add_import("math")
            return f"int(math.Pow(float64({left}), float64({right})))"

        # Python // → Go división entera (solo válida entre ints, igual en Go con /)
        if op == "//":
            return f"({left} / {right})"

        # Concatenación de strings con +: válida en Go también
        # Repetición de strings con *: no existe en Go → comentario
        if op == "+":
            # Concatenación de listas: nums + [5] → append(nums, 5)
            if right.startswith("[]interface{}"):
                inner = right[len("[]interface{}{"):-1]  # extraer elementos
                if inner:
                    return f"append({left}, {inner})"
                return left
            return f"({left} {op} {right})"

        if op == "*":
            # Solo advertir si alguno de los operandos parece un string literal
            if left.startswith('"') or right.startswith('"') or left.startswith('`') or right.startswith('`'):
                self.add_import("strings")
                return f"strings.Repeat({left}, {right})"
            return f"({left} * {right})"

        return f"({left} {op} {right})"

    def visitAtom_expr(self, ctx: Python3Parser.Atom_exprContext):
        # atom trailer* (llamadas, índices, atributos)
        base = self.visit(ctx.atom())
        for trailer in ctx.trailer():
            base = self._apply_trailer(base, trailer)
        return base

    def _apply_trailer(self, base: str, trailer: Python3Parser.TrailerContext) -> str:
        first = trailer.getChild(0).getText()

        # Llamada a función: base(args)
        if first == "(":
            args = self.visit(trailer.arglist()) if trailer.arglist() else ""
            return self._translate_call(base, args, trailer)

        # Índice / slice: base[...]
        if first == "[":
            subscript_ctx = trailer.subscriptlist()
            subscript = self.visit(subscript_ctx)
            # Detectar índice negativo: base[-1] → base[len(base)-1]
            subscript = self._fix_negative_index(base, subscript, subscript_ctx)
            return f"{base}[{subscript}]"

        # Atributo: base.name → puede ser método de lista
        if first == ".":
            attr = trailer.getChild(1).getText()
            return f"{base}.{attr}"

        return base

    def _fix_negative_index(self, base: str, subscript: str, ctx) -> str:
        """Convierte índices negativos: -1 → len(base)-1"""
        # Solo para índices simples (no slices)
        if ctx and len(ctx.subscript_()) == 1:
            sub = ctx.subscript_(0)
            # Índice simple (no slice): un solo test sin ':'
            if sub.getChildCount() == 1:
                text = sub.getText()
                if text.lstrip('-').isdigit() and text.startswith('-'):
                    n = int(text)
                    return f"len({base}){n}"  # n ya es negativo: len(base)-1
        return subscript

    def _translate_call(self, func: str, args: str,
                        trailer: Python3Parser.TrailerContext) -> str:
        """Traduce llamadas builtin especiales."""

        # ── append ────────────────────────────────────────────────────────
        if func.endswith(".append"):
            base = func[:-len(".append")]
            return f"{base} = append({base}, {args})"

        # ── dict / list methods ───────────────────────────────────────────
        for method in (".items", ".keys", ".values", ".copy",
                       ".split", ".strip", ".lower", ".upper",
                       ".replace", ".join"):
            if func.endswith(method):
                base = func[:-len(method)]
                return self._call_method(base, method[1:], args, trailer)

        # ── list + list (concatenación) ya se maneja en visitExpr con +
        # ── print ──────────────────────────────────────────────────────────
        if func == "print":
            self.add_import("fmt")
            if not trailer.arglist():
                return 'fmt.Println()'

            arg_nodes = trailer.arglist().argument() if trailer.arglist() else []

            # Separar args posicionales de keyword (sep=, end=)
            positional = []
            sep_val    = '" "'    # default
            end_val    = '"\\n"'  # default
            has_fstring = False

            for arg in arg_nodes:
                text = arg.getText()
                if text.startswith("sep="):
                    sep_val = self.visit(arg.test(1))
                elif text.startswith("end="):
                    end_val = self.visit(arg.test(1))
                else:
                    val = self.visit(arg)
                    if val.startswith('fmt.Sprintf'):
                        has_fstring = True
                    positional.append(val)

            # sep y end por defecto → Println
            if sep_val == '" "' and end_val == '"\\n"':
                return f'fmt.Println({", ".join(positional)})'

            # end personalizado sin sep → fmt.Print con el end concatenado
            if sep_val == '" "':
                args_str = ", ".join(positional)
                if end_val == '""':
                    # print("x", end="") → fmt.Print("x")
                    return f'fmt.Print({args_str})'
                # print("x", end="\n\n") → fmt.Print("x\n\n")  aproximado
                if len(positional) == 1:
                    return f'fmt.Print({positional[0]}, {end_val})'
                return f'fmt.Print({args_str}, {end_val})'

            # sep personalizado → construir con strings.Join
            self.add_import("strings")
            # Convertir positional a []string solo si son strings literales,
            # de lo contrario usar fmt.Sprintf
            joined = f'strings.Join([]string{{{", ".join(positional)}}}, {sep_val})'
            if end_val == '"\\n"':
                return f'fmt.Println({joined})'
            if end_val == '""':
                return f'fmt.Print({joined})'
            return f'fmt.Print({joined} + {end_val})'

        # ── input ──────────────────────────────────────────────────────────
        if func == "input":
            self.add_import("bufio")
            self.add_import("os")
            self.add_import("strings")
            if args:
                self.add_import("fmt")
                return (f'func() string {{\n'
                        f'{self.indent()}\tfmt.Print({args})\n'
                        f'{self.indent()}\treader := bufio.NewReader(os.Stdin)\n'
                        f'{self.indent()}\ttext, _ := reader.ReadString(\'\\n\')\n'
                        f'{self.indent()}\treturn strings.TrimRight(text, "\\r\\n")\n'
                        f'{self.indent()}}}()')
            return (f'func() string {{\n'
                    f'{self.indent()}\treader := bufio.NewReader(os.Stdin)\n'
                    f'{self.indent()}\ttext, _ := reader.ReadString(\'\\n\')\n'
                    f'{self.indent()}\treturn strings.TrimRight(text, "\\r\\n")\n'
                    f'{self.indent()}}}()')

        # ── append de lista: lista.append(x) → append(lista, x)
        if func.endswith(".append"):
            base = func[:-7]   # quitar ".append"
            return f"append({base}, {args})"

        # ── métodos de lista: .copy(), .pop(), etc. → comentario
        list_methods = {"sort", "reverse", "clear", "copy", "count", "index", "insert", "remove", "pop"}
        dot_idx = func.rfind(".")
        if dot_idx != -1 and func[dot_idx+1:] in list_methods:
            method = func[dot_idx+1:]
            base = func[:dot_idx]
            if method == "pop":
                idx_arg = args if args else f"len({base})-1"
                return f"{base}[{idx_arg}] /* pop: remover elemento manualmente en Go */"
            if method == "copy":
                return f"append([]interface{{}}{{}}, {base}...)"
            # Para el resto: llamada directa con comentario
            return f"{base}.{method}({args}) /* método de lista */"

        # ── len ────────────────────────────────────────────────────────────
        if func == "len":
            return f"len({args})"

        # ── int / float / str conversiones ────────────────────────────────
        if func == "int":
            self.add_import("strconv")
            return f"func() int {{ v, _ := strconv.Atoi({args}); return v }}()"
        if func == "float":
            self.add_import("strconv")
            return f"func() float64 {{ v, _ := strconv.ParseFloat({args}, 64); return v }}()"
        if func == "str":
            self.add_import("fmt")
            return f'fmt.Sprintf("%v", {args})'

        # Cualquier otra llamada: se pasa tal cual
        return f"{func}({args})"

    def _call_method(self, base: str, method: str, args: str, trailer=None) -> str:
        """Traduce llamadas a métodos de dict, list y string."""
        ind = self.indent()
        i1  = ind + "\t"
        i2  = ind + "\t\t"

        if method == "items":
            return f"__items__{base}"
        if method == "keys":
            return f"__keys__{base}"
        if method == "values":
            return f"__values__{base}"

        if method == "copy":
            return (f"func() map[string]interface{{}} {{\n"
                    f"{i1}_copy := make(map[string]interface{{}})\n"
                    f"{i1}for _k, _v := range {base} {{\n"
                    f"{i2}_copy[_k] = _v\n"
                    f"{i1}}}\n"
                    f"{i1}return _copy\n"
                    f"{ind}}}()")

        if method == "get":
            key = args.split(",")[0].strip() if args else '""'
            default = args.split(",")[1].strip() if "," in args else "nil"
            return (f"func() interface{{}} {{\n"
                    f"{i1}if _v, _ok := {base}[{key}]; _ok {{\n"
                    f"{i2}return _v\n"
                    f"{i1}}}\n"
                    f"{i1}return {default}\n"
                    f"{ind}}}()")

        if method == "split":
            self.add_import("strings")
            return f"strings.Split({base}, {args})" if args else f"strings.Fields({base})"

        if method == "strip":
            self.add_import("strings")
            return f"strings.TrimSpace({base})" if not args else f"strings.Trim({base}, {args})"

        if method == "lower":
            self.add_import("strings")
            return f"strings.ToLower({base})"

        if method == "upper":
            self.add_import("strings")
            return f"strings.ToUpper({base})"

        if method == "replace":
            self.add_import("strings")
            return f"strings.ReplaceAll({base}, {args})"

        if method == "join":
            self.add_import("strings")
            return f"strings.Join({args}, {base})"

        return f"{base}.{method}({args})"

    def visitAtom(self, ctx: Python3Parser.AtomContext):
        text = ctx.getText()

        # None → nil, True/False
        if text == "None":  return "nil"
        if text == "True":  return "true"
        if text == "False": return "false"

        # Números
        if ctx.NUMBER():
            return text

        # Strings
        if ctx.STRING():
            return self._translate_strings(ctx)

        # Identificador
        if ctx.name():
            return self.visit(ctx.name())

        # Expresión entre paréntesis
        if text.startswith("("):
            inner = ctx.getChild(1)
            return f"({self.visit(inner)})"

        # Lista []
        if text.startswith("["):
            return self._translate_list(ctx)

        # Dict/set {}
        if text.startswith("{"):
            if ctx.dictorsetmaker():
                return self.visit(ctx.dictorsetmaker())
            return "map[string]interface{}{}"

        return text

    def _translate_strings(self, ctx: Python3Parser.AtomContext) -> str:
        """Maneja strings normales, f-strings y multilínea."""
        parts = []
        for i in range(ctx.getChildCount()):
            token = ctx.getChild(i).getText()
            parts.append(self._convert_string_token(token))
        if len(parts) == 1:
            return parts[0]
        # Concatenación implícita de strings en Python
        self.add_import("fmt")
        return " + ".join(parts)

    def _convert_string_token(self, token: str) -> str:
        """Convierte un token string de Python a Go."""
        # f-string: f"hola {var}" → fmt.Sprintf("hola %v", var)
        if token.startswith(('f"', "f'", 'F"', "F'", 'f"""', "f'''")):
            return self._translate_fstring(token)

        # Triple comilla → raw string con backtick en Go
        if token.startswith('"""') or token.startswith("'''"):
            inner = token[3:-3]
            # Los backticks en Go no permiten backtick dentro
            inner = inner.replace("`", "`+\"`\"+`")
            return f"`{inner}`"

        # Comilla simple → comilla doble en Go
        if token.startswith("'") and not token.startswith("'''"):
            inner = token[1:-1].replace('"', '\\"')
            return f'"{inner}"'

        # Comilla doble normal
        return token

    def _translate_fstring(self, token: str) -> str:
        """Convierte f-string de Python a fmt.Sprintf."""
        self.add_import("fmt")
        # Extraer contenido interno
        if token.startswith(('f"""', "f'''")):
            inner = token[4:-3]
        else:
            inner = token[2:-1]

        format_str = ""
        args = []
        i = 0
        while i < len(inner):
            if inner[i] == '{' and i + 1 < len(inner) and inner[i+1] != '{':
                end = inner.find('}', i)
                if end == -1:
                    format_str += inner[i]
                    i += 1
                else:
                    expr = inner[i+1:end]
                    format_str += "%v"
                    args.append(expr)
                    i = end + 1
            elif inner[i:i+2] == '{{':
                format_str += '{'
                i += 2
            elif inner[i:i+2] == '}}':
                format_str += '}'
                i += 2
            else:
                format_str += inner[i]
                i += 1

        args_str = ", ".join(args)
        return f'fmt.Sprintf("{format_str}", {args_str})'

    # ─────────────────────────────────────────────
    # Listas
    # ─────────────────────────────────────────────

    def _visit_list_contents(self, ctx: Python3Parser.Testlist_compContext) -> str:
        """Traduce los elementos de una lista, detectando list comprehension."""
        # List comprehension: [x for x in ...]
        if ctx.comp_for():
            return self._translate_list_comprehension(ctx)
        # Lista normal
        parts = []
        for child in ctx.children:
            if child.getText() == ",":
                continue
            parts.append(self.visit(child))
        return ", ".join(parts)

    def _translate_subscript(self, base: str, trailer: Python3Parser.TrailerContext) -> str:
        """Traduce base[...] manejando índices negativos y slicing."""
        sub_ctx = trailer.subscriptlist() if trailer.subscriptlist() else None
        if sub_ctx is None:
            return f"{base}[]"

        # Un solo subscript
        subs = sub_ctx.subscript_()
        if len(subs) == 1:
            sub = subs[0]
            # Índice simple (no slice)
            if sub.getChildCount() == 1:
                idx = self.visit(sub.test(0))
                return self._index_with_negative(base, idx)
            # Slice
            return self._translate_slice(base, sub)

        # Múltiples índices (matriz): base[i][j]
        result = base
        for sub in subs:
            if sub.getChildCount() == 1:
                idx = self.visit(sub.test(0))
                result = self._index_with_negative(result, idx)
            else:
                result = self._translate_slice(result, sub)
        return result

    def _index_with_negative(self, base: str, idx: str) -> str:
        """Convierte índices negativos: base[-1] → base[len(base)-1]"""
        # Detectar literal negativo
        if idx.startswith("-") and idx[1:].isdigit():
            n = int(idx)
            if n == -1:
                return f"{base}[len({base})-1]"
            else:
                return f"{base}[len({base}){n}]"
        return f"{base}[{idx}]"

    def _translate_slice(self, base: str, sub: Python3Parser.Subscript_Context) -> str:
        """Traduce slicing: base[start:stop:step]"""
        tests = sub.test()
        has_step = sub.sliceop() is not None

        start = self.visit(tests[0]) if len(tests) > 0 else ""
        stop  = self.visit(tests[1]) if len(tests) > 1 else ""
        step  = ""
        if has_step and sub.sliceop().test():
            step = self.visit(sub.sliceop().test())

        # Normalizar índices negativos en start/stop
        if start.startswith("-") and start[1:].isdigit():
            start = f"len({base}){start}"
        if stop.startswith("-") and stop[1:].isdigit():
            stop = f"len({base}){stop}"

        if step:
            # Go no tiene slice con step → función auxiliar inline
            start_val = start if start else "0"
            stop_val  = stop  if stop  else f"len({base})"
            step_int = int(step) if step.lstrip("-").isdigit() else None
            start_val = start if start else "0"
            stop_val = stop if stop else f"len({base})"
            go_lines = [
                "func() []interface{} {",
                "\t\tvar _r []interface{}",
                f"\t\tfor _i := {start_val}; _i < {stop_val}; _i += {step} {{",
                f"\t\t\t_r = append(_r, {base}[_i])",
                "\t\t}",
                "\t\treturn _r",
                "\t}()",
            ]
            return "\n".join(go_lines)
        return f"{base}[{start}:{stop}]"

    def _translate_attr(self, base: str, attr: str,
                        trailer: Python3Parser.TrailerContext) -> str:
        """Traduce acceso a atributos — el método se completa en _translate_call."""
        return f"{base}.{attr}"

    # ─────────────────────────────────────────────
    # Diccionarios
    # ─────────────────────────────────────────────

    def visitDictorsetmaker(self, ctx: Python3Parser.DictorsetmakerContext):
        """Traduce dict literal {k: v, ...} → map[string]interface{}{k: v, ...}"""
        children = list(ctx.children)
        pairs = []
        i = 0
        while i < len(children):
            token = children[i].getText()
            if token == ",":
                i += 1
                continue
            if token == "**":
                # **otro_dict → ignorar por ahora
                i += 2
                continue
            # Detectar comp_for (dict comprehension — dejamos como TODO)
            if isinstance(children[i], Python3Parser.Comp_forContext):
                i += 1
                continue
            # Par key: value
            if i + 2 < len(children) and children[i+1].getText() == ":":
                key = self.visit(children[i])
                val = self.visit(children[i+2])
                pairs.append(f"{key}: {val}")
                i += 3
            else:
                i += 1
        inner = ", ".join(pairs)
        return f"map[string]interface{{}}{{{inner}}}"

    def _translate_dict_method(self, base: str, method: str,
                               trailer: Python3Parser.TrailerContext) -> str:
        """Traduce métodos de diccionario a construcciones Go equivalentes."""
        ind  = self.indent()
        i1   = ind + "	"
        i2   = ind + "		"

        if method == "items":
            # user.items() usado en for k, v → devuelve el dict para range
            return base

        if method == "keys":
            # for k in user.keys() → for k := range user
            return f"__keys__{base}"   # marcador que visitFor_stmt detecta

        if method == "values":
            return f"__values__{base}"  # marcador similar

        if method == "copy":
            tmp = "_copy"
            copy_lines = [
                "func() map[string]interface{} {",
                f"\t_copy := make(map[string]interface{{}})",
                f"\tfor _k, _v := range {base} {{",
                "\t\t_copy[_k] = _v",
                "\t}",
                "\treturn _copy",
                "}()",
            ]
            return "\n".join(copy_lines)
        if method == "get":
            # user.get(key) → user[key] (sin default por ahora)
            return f"{base}[__get_args__]"

        return f"{base}.{method}"

    # ─────────────────────────────────────────────
    # Subscript / Slicing
    # ─────────────────────────────────────────────

    def visitSubscriptlist(self, ctx: Python3Parser.SubscriptlistContext):
        parts = [self.visit(ctx.subscript_(i))
                 for i in range(len(ctx.subscript_()))]
        return ", ".join(parts)

    def visitSubscript_(self, ctx: Python3Parser.Subscript_Context):
        # Índice simple (sin ':')
        if ctx.getChildCount() == 1:
            return self.visit(ctx.test(0))

        # Slice: detectar si hay start y/o stop mirando los tokens directamente
        # Hijos pueden ser: test? ':' test? sliceop?
        # Necesitamos saber si el primer hijo es un test o un ':'
        start = ""
        stop  = ""
        step  = ""
        children = list(ctx.children)
        i = 0
        # ¿Hay start?
        if i < len(children) and children[i].getText() != ":":
            start = self.visit(children[i])
            i += 1
        # Saltar ':'
        if i < len(children) and children[i].getText() == ":":
            i += 1
        # ¿Hay stop?
        if i < len(children) and children[i].getText() not in (":", ):
            # Puede ser sliceop o test
            if not isinstance(children[i], Python3Parser.SliceopContext):
                stop = self.visit(children[i])
                i += 1
        # ¿Hay sliceop?
        if ctx.sliceop() and ctx.sliceop().test():
            step = self.visit(ctx.sliceop().test())

        if step:
            return f"{start}:{stop}:{step} /* step: usar loop en Go */"
        return f"{start}:{stop}"

    # ─────────────────────────────────────────────
    # Arglist / Arguments
    # ─────────────────────────────────────────────

    def visitArglist(self, ctx: Python3Parser.ArglistContext):
        parts = [self.visit(a) for a in ctx.argument()]
        return ", ".join(parts)

    def visitArgument(self, ctx: Python3Parser.ArgumentContext):
        # keyword argument: name=value
        if ctx.getChildCount() == 3 and ctx.getChild(1).getText() == "=":
            # En Go no hay keyword args; se traduce solo el valor
            return self.visit(ctx.test(1))
        return self.visit(ctx.test(0))

    # ─────────────────────────────────────────────
    # Nombres e identificadores
    # ─────────────────────────────────────────────

    def visitName(self, ctx: Python3Parser.NameContext):
        return ctx.getText()

    def visitTestlist(self, ctx: Python3Parser.TestlistContext):
        parts = [self.visit(ctx.test(i)) for i in range(len(ctx.test()))]
        return ", ".join(parts)

    # ─────────────────────────────────────────────
    # Lambdas (traducción básica)
    # ─────────────────────────────────────────────

    def visitLambdef(self, ctx: Python3Parser.LambdefContext):
        params = self.visit(ctx.varargslist()) if ctx.varargslist() else ""
        body   = self.visit(ctx.test())
        return f"func({params}) interface{{}} {{ return {body} }}"

    def visitVarargslist(self, ctx: Python3Parser.VarargslistContext):
        parts = []
        for child in ctx.children:
            t = child.getText()
            if t not in (",", "*", "**"):
                parts.append(t)
        return ", ".join(f"{p} interface{{}}" for p in parts)

    # ─────────────────────────────────────────────
    # Fallback: nodos no visitados explícitamente
    # ─────────────────────────────────────────────

    def visitChildren(self, node):
        results = []
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            result = self.visit(child)
            if result:
                results.append(result)
        return "".join(results)

    def visitTerminal(self, node):
        return node.getText()
