from cStringIO import StringIO
from visitor import ASTVisitor

class ModuleSourceCodeGenerator(object):
    """Generates Python source code from an AST tree (as parsed by the
    ``compiler.parse`` method)."""

    visitor = ASTVisitor()
    
    def __init__(self, tree):
        self.tree = tree

    def getSourceCode(self):
        stream = CodeStream()
        self.visitor.visit(self.tree, stream)
        return str(stream)

class CodeStream(object):
    def __init__(self, indentation_string="\t"):
        self.indentation_string = indentation_string
        self.indentation = 0
        self.stream = StringIO()
        self.clear = True
        
    def write(self, text):
        self.out(text)
        self.stream.write('\n')
        self.clear = True
    
    def out(self, text):
        if self.clear is True:
            indentation = self.indentation_string * self.indentation
            self.stream.write(indentation)
            self.clear = False
        self.stream.write(text)

    def __str__(self):
        return self.stream.getvalue()
    
