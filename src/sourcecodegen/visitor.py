from compiler import ast

def triple_quote(doc):
    return '"""%s"""' % doc.replace('"""', '\"\"\"')

def format_argnames(argnames):
    return ", ".join(
        isinstance(name, tuple) and "(%s)" % format_argnames(name) or name \
        for name in argnames)

def format_ass(node):
    if isinstance(node, ast.AssTuple):
        return "(%s)" % ", ".join(format_ass(ass) for ass in node)
    return node.name

def binary(symbol):
    def visit(self, node, stream):
        stream.out('(')
        self.visit(node.left, stream)
        stream.out(' %s ' % symbol)
        self.visit(node.right, stream)
        stream.out(')')
    return visit

class ASTVisitor(object):
    def visit(self, node, stream):
        name = node.__class__.__name__
        try:
            func = getattr(self, 'visit%s' % name)
        except AttributeError:
            raise NotImplementedError(
                "Unable to visit `%s`." % repr(node))

        func(node, stream)

    def visitModule(self, node, stream):
        if node.doc is not None:
            stream.write(triple_quote(node.doc))

        for node in node.getChildNodes():
            self.visit(node, stream)

    def visitStmt(self, node, stream):
        for node in node.nodes:
            if node is None:
                continue
            self.visit(node, stream)            
            stream.write("")
            
    def visitIf(self, node, stream):
        for index, test in enumerate(node.tests):
            if index == 0:
                stream.out("if ")
            else:
                stream.out("elif ")

            condition, statement = test
            self.visit(condition, stream)
            stream.write(":")
            stream.indentation += 1
            self.visit(statement, stream)
            stream.indentation -= 1

        if node.else_:
            stream.write("else:")
            stream.indentation += 1
            self.visit(node.else_, stream)
            stream.indentation -= 1

    def visitAnd(self, node, stream):
        stream.out('(')
        for condition in tuple(node)[:-1]:
            self.visit(condition, stream)
            stream.out(" and ")
        self.visit(tuple(node)[-1], stream)
        stream.out(')')

    def visitOr(self, node, stream):
        stream.out('(')
        for condition in tuple(node)[:-1]:
            self.visit(condition, stream)
            stream.out(" or ")
        self.visit(tuple(node)[-1], stream)
        stream.out(')')
        
    def visitInvert(self, node, stream):
        stream.out('~(')
        self.visit(node.expr, stream)
        stream.out(')')

    def visitBitand(self, node, stream):
        stream.out('(')
        for condition in tuple(node)[:-1]:
            self.visit(condition, stream)
            stream.out(" & ")
        self.visit(tuple(node)[-1], stream)
        stream.out(')')
        
    def visitBitor(self, node, stream):
        stream.out('(')
        for condition in tuple(node)[:-1]:
            self.visit(condition, stream)
            stream.out(" | ")
        self.visit(tuple(node)[-1], stream)
        stream.out(')')
        
    def visitBitxor(self, node, stream):
        stream.out('(')
        for condition in tuple(node)[:-1]:
            self.visit(condition, stream)
            stream.out(" ^ ")
        self.visit(tuple(node)[-1], stream)
        stream.out(')')
        
    def visitName(self, node, stream):
        stream.out(node.name)

    def visitPass(self, node, stream):
        stream.write("pass")

    def visitDiscard(self, node, stream):
        self.visit(node.expr, stream)

    def visitAssign(self, node, stream):
        for index, ass in enumerate(tuple(node.nodes)):
            self.visit(ass, stream)
            if index < len(tuple(node.nodes)) - 1:
                stream.out(" = ")
        stream.out(" = ")
        self.visit(node.expr, stream)
        stream.write("")
        
    def visitAssName(self, node, stream):
        if node.flags == 'OP_DELETE':
            stream.out("del ")
        stream.out(node.name)

    def visitFunction(self, node, stream):
        if node.decorators:
            self.visit(node.decorators, stream)            

        stream.out("def %s(" % node.name)

        argnames = list(node.argnames)
        if argnames:
            if node.kwargs:
                kwargs = argnames.pop()
            if node.varargs:
                varargs = argnames.pop()

            if node.defaults:
                stream.out(format_argnames(argnames[:-len(node.defaults)]))
                for index, default in enumerate(node.defaults):
                    name = argnames[index-len(node.defaults)]
                    if len(argnames) > len(node.defaults) or index > 0:
                        stream.out(", %s=" % name)
                    else:
                        stream.out("%s=" % name)
                    self.visit(default, stream)
            else:
                stream.out(format_argnames(argnames))
                            
        if node.varargs:
            if node.argnames:
                stream.out(", ")
            stream.out("*%s" % varargs)

        if node.kwargs:
            if node.argnames:
                stream.out(", ")
            stream.out("**%s" % kwargs)

        stream.write("):")
        stream.indentation += 1
        for statement in node.code:
            if statement is not None:
                self.visit(statement, stream)
                stream.write("")
        stream.indentation -= 1

    def visitConst(self, node, stream):
        stream.out(repr(node.value))

    def visitDecorators(self, node, stream):
        for decorator in tuple(node):
            stream.out('@')
            self.visit(decorator, stream)
            stream.write("")

    def visitCallFunc(self, node, stream):
        self.visit(node.node, stream)
        stream.out("(")
        for arg in tuple(node.args)[:-1]:
            self.visit(arg, stream)
            stream.out(", ")
        if node.args:
            self.visit(node.args[-1], stream)
        if node.star_args:
            if node.args:
                stream.out(", *")
            self.visit(node.star_args, stream)
        if node.dstar_args:
            if node.args:
                stream.out(", **")
            self.visit(node.dstar_args, stream)
        stream.out(")")

    def visitKeyword(self, node, stream):
        stream.out("%s=" % node.name)
        self.visit(node.expr, stream)

    def visitAssTuple(self, node, stream):
        first = node
        while isinstance(first, ast.AssTuple):
            first = first.nodes[0]
        if first.flags == 'OP_DELETE':
            stream.out("del ")
        stream.out(format_ass(node))

    def visitTuple(self, node, stream):
        stream.out("(")
        for index, item in enumerate(tuple(node)):
            self.visit(item, stream)
            if index < len(tuple(node)) - 1:
                stream.out(", ")
        if len(node.nodes) == 1:
            stream.out(", ")
        stream.out(")")

    def visitGenExpr(self, node, stream):
        stream.out("(")
        self.visit(node.code, stream)
        stream.out(")")

    def visitListComp(self, node, stream):
        stream.out("[")
        self.visitGenExprInner(node, stream)
        stream.out("]")

    def visitGenExprInner(self, node, stream):
        self.visit(node.expr, stream)
        for qual in node.quals:
            self.visit(qual, stream)

    def visitGenExprFor(self, node, stream):
        stream.out(" for ")
        self.visit(node.assign, stream)
        stream.out(" in ")
        self.visit(node.iter, stream)
        for _if in node.ifs:
            self.visit(_if, stream)

    def visitGenExprIf(self, node, stream):
        stream.out(" if ")
        self.visit(node.test, stream)

    def visitListCompFor(self, node, stream):
        stream.out(" for ")
        self.visit(node.assign, stream)
        stream.out(" in ")
        self.visit(node.list, stream)
        for _if in node.ifs:
            self.visit(_if, stream)
            
    def visitListCompIf(self, node, stream):
        stream.out(" if ")
        self.visit(node.test, stream)

    def visitCompare(self, node, stream):
        self.visit(node.expr, stream)
        for op, expr in node.ops:
            stream.out(' %s ' % op)
            self.visit(expr, stream)

    def visitImport(self, node, stream):
        stream.out("import ")
        for index, (name, alias) in enumerate(node.names):
            stream.out(name)
            if alias is not None:
                stream.out(" as %s" % alias)
            if index < len(node.names) - 1:
                stream.out(", ")
        stream.write("")

    def visitFrom(self, node, stream):
        stream.out("from %s import " % node.modname)
        for index, (name, alias) in enumerate(node.names):
            stream.out(name)
            if alias is not None:
                stream.out(" as %s" % alias)
            if index < len(node.names) - 1:
                stream.out(", ")
        stream.write("")

    def visitReturn(self, node, stream):
        stream.out("return ")
        self.visit(node.value, stream)
        
    def visitWhile(self, node, stream):
        stream.out("while ")
        self.visit(node.test, stream)
        stream.write(":")

        stream.indentation += 1
        self.visit(node.body, stream)
        stream.indentation -= 1

        if node.else_ is not None:
            stream.write("else:")
            stream.indentation += 1
            self.visit(node.else_, stream)
            stream.indentation -= 1

    def visitTryExcept(self, node, stream):
        stream.write("try:")
        stream.indentation += 1
        self.visit(node.body, stream)
        stream.indentation -= 1
        for cls, var, body in node.handlers:
            stream.out("except")
            if cls is not None:
                stream.out(" ")
                self.visit(cls, stream)
            if var is not None:
                if cls is None:
                    stream.out(" ")
                else:
                    stream.out(", ")
                self.visit(var, stream)
            stream.write(":")
            stream.indentation += 1
            self.visit(body, stream)
            stream.indentation -= 1

        if node.else_:
            stream.write("else:")
            stream.indentation += 1
            self.visit(node.else_, stream)
            stream.indentation -= 1        
    
    def visitTryFinally(self, node, stream):
        self.visit(node.body, stream)
        stream.write("finally:")
        stream.indentation += 1
        self.visit(node.final, stream)
        stream.indentation -= 1

    def visitClass(self, node, stream):
        stream.out("class %s" % node.name)

        if node.bases:
            stream.out("(")
            for index, base in enumerate(node.bases):
                self.visit(base, stream)
                if index < len(node.bases) - 1:
                    stream.out(", ")
            stream.out(")")
        stream.write(":")
        stream.indentation += 1
        
        if node.doc:
            stream.write(triple_quote(node.doc))
            
        self.visit(node.code, stream)
        stream.indentation -= 1

    def visitLambda(self, node, stream):
        stream.out("lambda")
        argnames = list(node.argnames)
        if argnames:
            stream.out(" ")
            if node.kwargs:
                kwargs = argnames.pop()
            if node.varargs:
                varargs = argnames.pop()

            if node.defaults:
                stream.out(format_argnames(argnames[:-len(node.defaults)]))
                for index, default in enumerate(node.defaults):
                    name = argnames[index-len(node.defaults)]
                    stream.out(", %s=" % name)
                    self.visit(default, stream)
            else:
                stream.out(format_argnames(argnames))
                            
        if node.varargs:
            if node.argnames:
                stream.out(", ")
            stream.out("*%s" % varargs)

        if node.kwargs:
            if node.argnames:
                stream.out(", ")
            stream.out("**%s" % kwargs)

        stream.out(": ")
        self.visit(node.code, stream)

    def visitGetattr(self, node, stream):
        self.visit(node.expr, stream)
        stream.out(".%s" % node.attrname)

    def visitAssAttr(self, node, stream):
        self.visit(node.expr, stream)
        stream.out(".%s" % node.attrname)

    def visitSubscript(self, node, stream):
        self.visit(node.expr, stream)
        stream.out('[')
        for index, sub in enumerate(node.subs):
            self.visit(sub, stream)
            if index < len(node.subs) - 1:
                stream.out(', ')
        stream.out(']')

    def visitSlice(self, node, stream):
        self.visit(node.expr, stream)
        stream.out('[')
        if node.lower:
            self.visit(node.lower, stream)
        stream.out(':')
        if node.upper:
            self.visit(node.upper, stream)
        stream.out(']')

    def visitSliceobj(self, node, stream):
        for index, item in enumerate(tuple(node)):
            self.visit(item, stream)
            if index < len(tuple(node)) - 1:
                stream.out(":")
                
    def visitExec(self, node, stream):
        stream.out("exec ")
        self.visit(node.expr, stream)
        if node.locals:
            stream.out(" in ")
            self.visit(node.locals, stream)
        if node.globals:
            stream.out(", ")
            self.visit(node.globals, stream)
        stream.write("")

    def visitAssert(self, node, stream):
        stream.out("assert ")
        self.visit(node.test, stream)
        if node.fail is not None:
            stream.out(", ")
            self.visit(node.fail, stream)
        stream.write("")

    def visitRaise(self, node, stream):
        stream.out("raise ")
        self.visit(node.expr1, stream)
        if node.expr2:
            stream.out(", ")
            self.visit(node.expr2, stream)
        if node.expr3:
            stream.out(", ")
            self.visit(node.expr3, stream)

    def visitPrintnl(self, node, stream):
        stream.out("print ")
        if node.dest is not None:
            stream.out(">> ")
            self.visit(node.dest, stream)
            stream.out(", ")
        for index, expr in enumerate(tuple(node.nodes)):
            if expr is None:
                continue
            self.visit(expr, stream)
            if index < len(tuple(node.nodes)) - 1 and node.nodes[index+1] is not None:
                stream.out(", ")
        stream.write("")

    def visitWith(self, node, stream):
        raise NotImplementedError(
            "The `with` keyword is not supported.")

    def visitAugAssign(self, node, stream):
        self.visit(node.expr, stream)
        stream.out(" %s " % node.op)
        self.visit(node.node, stream)

    def visitList(self, node, stream):
        stream.out('[')
        for index, item in enumerate(node.nodes):
            self.visit(item, stream)
            if index < len(node.nodes) - 1:
                stream.out(", ")            
        stream.out(']')

    def visitDict(self, node, stream):
        stream.out('{')
        for index, (expr, value) in enumerate(node.items):
            self.visit(expr, stream)
            stream.out(': ')
            self.visit(value, stream)
            if index < len(node.items) - 1:
                stream.out(", ")            
        stream.out('}')

    def visitNot(self, node, stream):
        stream.out("not (")
        self.visit(node.expr, stream)
        stream.out(")")

    def visitFor(self, node, stream):
        stream.out("for %s in " % format_ass(node.assign))
        self.visit(node.list, stream)
        stream.write(":")
        stream.indentation += 1
        self.visit(node.body, stream)
        stream.indentation -= 1
        if node.else_ is not None:
            stream.write("else:")
            stream.indentation += 1
            self.visit(node.else_, stream)
            stream.indentation -= 1

    def visitYield(self, node, stream):
        stream.out("yield ")
        self.visit(node.value, stream)
        stream.write("")

    def visitUnaryAdd(self, node, stream):
        stream.out("+")
        self.visit(node.expr, stream)

    def visitUnarySub(self, node, stream):
        stream.out("-")
        self.visit(node.expr, stream)

    visitAdd = binary('+')
    visitSub = binary('-')
    visitMul = binary('*')
    visitPower = binary('**')
    visitMod = binary('%')    
    visitDiv = binary('/')
    visitLeftShift = binary('<<')
    visitRightShift = binary('>>')
