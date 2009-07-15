from sourcecodegen.tests.base import TestSourceCodeGeneration as Base
from sourcecodegen.tests.base import verify

class TestSourceCodeGeneration(Base):
    @verify
    def testTryFinally(self):
        try:
            pass
        except:
            pass
        else:
            pass
        finally:
            pass

    @verify
    def testTernary(self):
        foo if bar else boo
