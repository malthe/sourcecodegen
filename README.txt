Overview
========

This package provides a module-level source-code generator which
operates on the AST from the built-in ``compiler.ast`` module.

Note that this AST is not compatible with the new ``ast`` module in
Python 2.6.

Usage
-----

The generator works on AST parse trees.

  >>> from compiler import parse
  >>> tree = parse("""\
  ...     print 'Hello, world!'
  ... """)

We can now generate Python-code equivalent to the original using the
source-code generator.
  
  >>> from sourcecodegen import ModuleSourceCodeGenerator
  >>> generator = ModuleSourceCodeGenerator(tree)
  >>> print generator.getSourceCode()
  print 'Hello, world!'

Author
------

Malthe Borch <mborch@gmail.com>
