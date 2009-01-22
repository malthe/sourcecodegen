from visitor import ASTVisitor

class ModuleSourceCodeGenerator(object):
    """Generates Python source code from an AST tree (as parsed by the
    ``compiler.parse`` method)."""

    def __init__(self, tree):
        self.tree = tree

    def getSourceCode(self):
        visitor = ASTVisitor(self.tree)
        return visitor()

def generate_code(tree):
    return ModuleSourceCodeGenerator(tree).getSourceCode()
