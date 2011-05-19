import sys
import unittest
import doctest
import inspect
import textwrap
import base64

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

from compiler import ast
from compiler import parse
from compiler import pycodegen

from sourcecodegen.generation import ModuleSourceCodeGenerator

version = sys.version_info[:3]

def fix_tree(node):
    if isinstance(node, (
        ast.Module, ast.Class, ast.Function, ast.GenExpr, ast.Lambda)):
        node.filename = '<string>' # workaround for bug in pycodegen
    map(fix_tree, node.getChildNodes())
    return node

def verify_source(source):
    tree = fix_tree(parse(source, 'exec'))
    code = pycodegen.ModuleCodeGenerator(tree).getCode()
    generator = ModuleSourceCodeGenerator(tree)
    generated = generator.getSourceCode()
    try:
        new = fix_tree(parse(generated, 'exec'))
    except SyntaxError:
        return generated

    old = code.co_code
    new = pycodegen.ModuleCodeGenerator(new).getCode().co_code

    if old != new:
        return generated

def verify(func):
    def test(suite):
        source = textwrap.dedent(
            "\n".join(inspect.getsource(func).split('\n')[2:])
            )

        result = verify_source(source)
        return suite.assertEqual(result, None, "%r != %r" % (source, result))

    return test

class TestSourceCodeGeneration(unittest.TestCase):
    """The ``verify`` decorator is used to create a test-case out of
    simple functions. The objective is to verify correct source-code
    generation, not actual evaluation."""

    @verify
    def testModule(self):
        """Module doc-string."""
        
    @verify
    def testAssignment(self):
        foo = bar
        foo = bar = moo
        foo, bar = bar
        foo, bar = foo, bar
        foo, (bar, moo) = foo
        ((foo, bar), foo) = moo

    @verify
    def testAugmentAssignment(self):
        foo -= bar
        foo += bar
        foo %= bar
        foo /= bar
        foo **= bar
        foo -= 1
        bar += 1
                
    @verify
    def testConditions(self):
        if foo and bar:
            pass
        elif boo:
            pass
        else:
            pass

    @verify
    def testFunctions(self):
        def foo(bar):
            pass

        def foo(*bar):
            pass

        def foo(**bar):
            pass

        def foo(bar, *args):
            pass

        def foo(bar, *args, **kwargs):
            pass

        def foo(foo=None):
            pass

        def foo(bar, foo=None, *args, **kwargs):
            pass

        def foo(bar, boo, foo=None, moo=42, *args, **kwargs):
            pass

    @verify
    def testDecorators(self):
        @foo
        @bar(boo)
        def bar(foo):
            pass

    @verify
    def testCallFunc(self):
        foo(bar)
        foo(bar=None)
        foo(bar, moo=None)
        foo(boo, *args)
        foo(boo, *args, **kwargs)

    @verify
    def testDel(self):
        del foo
        del foo, bar
        del foo.bar
        del foo[bar]
        del foo[bar:boo]

    @verify
    def testListComprehensions(self):
        [x for x in xs]
        [x for x in xs if x]
        [x for x in xs if x == y]

    @verify
    def testMultipleListComprehensions(self):
        [(x * y) for x in xs for y in ys]

    @verify
    def testGeneratorComprehensions(self):
        (x for x in xs)
        (x for x in xs if x)
        (x for x in xs if x == y)

    @verify
    def testMultipleGeneratorComprehensions(self):
        (x*y for x in xs for x in xs for y in ys)

    @verify
    def testImports(self):
        import foo
        import foo.bar
        from foo import bar
        from foo.bar import foo, bar

    @verify
    def testReturn(self):
        def test():
            return foo
        return foo, bar

    @verify
    def testWhile(self):
        while True: # don't try this at home
            pass
        while False:
            pass
        else:
            pass

    @verify
    def testTryExcept(self):
        try:
            pass
        except Exception, e:
            pass
        except:
            pass

    @verify
    def testClasses(self):
        class foo:
            pass

        class foo(moo, boo):
            pass

        class foo(moo, boo):
            """this is foo."""

    @verify
    def testLambda(self):
        foo = lambda: bar
        bar = lambda foo: bar
        bar = lambda foo, bar: bar
        bar = lambda (foo, bar): bar
        bar = lambda foo, **kwargs: kwargs
        bar = lambda foo, bar, **kwargs: kwargs
        bar = lambda foo, *args: args
        bar = lambda foo, bar, *args: args
        bar = lambda **kwargs: kwargs
        bar = lambda *args, **kwargs: (args, kwargs)
        
    @verify
    def testGetAttr(self):
        foo.bar

    @verify
    def testGetItem(self):
        foo['bar']

    @verify
    def testSetAttr(self):
        foo.bar = moo

    @verify
    def testSetItem(self):
        foo['bar'] = moo

    @verify
    def testSlicing(self):
        foo[:]
        foo[1:]
        foo[:2]
        foo[1:2:3]

    @verify
    def testAssert(self):
        assert foo
        
    @verify
    def testExec(self):
        exec foo
        exec foo in bar
        exec foo in foo, bar

    @verify
    def testSemicolon(self):
        foo; bar

    @verify
    def testPrint(self):
        print foo
        print foo, bar
        print "Hello %s" % bar
        print >> foo, bar
        
    @verify
    def testRaise(self):
        raise foo            

    @verify
    def testArithmetic(self):
        bar + foo
        bar - foo
        bar * foo
        bar ** foo
        bar % foo
        bar / foo
        bar << foo
        bar >> foo

    @verify
    def testTuples(self):
        (a, b, c)

    @verify
    def testLists(self):
        [a, b, c]

    @verify
    def testDicts(self):
        {'a': a, 'b': b, 'c': c}

    @verify
    def testComparisons(self):
        foo < bar
        foo > bar
        foo == bar
        foo != bar
        foo >= bar
        foo <= bar

    @verify
    def testLogicalOperators(self):
        foo | bar & bar ^ foo
        ~ bar
        ~ (foo or bar)
        
    @verify
    def testOperators(self):
        not foo
        bar or foo
        not (foo or bar)

    @verify
    def testIdentity(self):
        foo is bar
        
    @verify
    def testFormatString(self):
        foo % (bar, moo)
        foo % (bar or foo)
        foo % (bar and foo)
        
    @verify
    def testLoop(self):
        for foo in bar:
            pass
        else:
            pass
        for foo, (bar, moo) in boo:
            pass

    @verify
    def testYield(self):
        yield foo

    @verify
    def testUnary(self):
        +foo
        -bar
        
    @verify
    def testOperatorPrecenceRules(self):
        a + b / c % d * e - b / c + a
        a & c | d ^ e
        not abc()

    @verify
    def testOptimalOperatorPredence(self):
        a + b + c + d + e + f + g + h + i + j + k + l + m + n + a + b + \
        a + b + c + d + e + f + g + h + i + j + k + l + m + n + a + b + \
        a + b + c + d + e + f + g + h + i + j + k + l + m + n + a + b + \
        a + b + c + d + e + f + g + h + i + j + k + l + m + n + a + b + \
        a + b + c + d + e + f + g + h + i + j + k + l + m + n + a + b

    @verify
    def testFunctionNesting(self):
        def abc():
            def ghi():
                a = lambda jkl: mno

    def testStandaloneString(self):
        self.assertEqual(verify_source(
            "'0'\n0"), None)

    @verify
    def testIndentation(self):
        for abc in abc:
            ppp
            ppp

    @verify
    def testMethod(self):
        abc(*args)
        abc(**kwargs)
        abc(ghi, *args)
        abc(ghi, **kwargs)
        abc(ghi, *args, **kwargs)

    @verify
    def testBreak(self):
        for i in range(5):
            break

    @verify
    def testContinue(self):
        for i in range(5):
            continue

    @verify
    def testFunctionDocString(self):
        def foo():
            """bar."""

        def bar():
            "hello"

        def boo():
            """bar."""
            return foo

        def baz():
            "hello"
            return boo

    def testSliceobj(self):
        node = ast.Sliceobj([ast.Const(1), ast.Const(2), ast.Const(3)])
        source = ModuleSourceCodeGenerator(node).getSourceCode()
        self.assertEqual(source, 'slice(1, 2, 3)')
