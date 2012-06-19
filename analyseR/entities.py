__all__ = ['RContext', 'Rentity', 'AllIndices', 'Source', 'Function',
           'Assign', 'Statements', 'Bloc', 'If', 'Return', 'Immed',
           'Name', 'Param', 'Param_list', 'Call', 'Script', 'For',
           'While', 'Repeat', 'Subexpr', 'Unary_plus_or_minus',
           'Indexing', 'Negation', 'BinOp', 'Sequence', 'Addsub',
           'Special_op', 'Muldiv', 'Comparison', 'Bool_and', 'Bool_or',
           'Formula', 'Exponentiation', 'Slot_extraction']

from itertools import *
from entities_base import *


def wrap_previous(get_target):

    def _set(s, v):
        t = get_target(s)
        if t is not None:
            t.previous = v

    def _get(s):
        t = get_target(s)
        return t and t.previous

    return property(_get, _set)


class Source(Rentity):
    entrails = ['contents']
    previous = wrap_previous(lambda s: s.contents)

    def __init__(self, filename):
        Rentity.__init__(self)
        self.filename = filename
        self.contents = RContext.parse(filename[1:-1])

    def __str__(self):
        return 'Source(' + self.filename + ')'

    def eval_to(self):
        return None


class Function(Renv, Rentity):
    entrails = ['code', 'params']

    def __init__(self, ast):
        Renv.__init__(self)
        Rentity.__init__(self)
        self.ast = ast
        self.code = ast[-1]
        self.params = ast[-3]
        #self.name = None
        lineno = RContext.current_text[-1][:ast[1][2]].count('\n') + 1
        self.name = Name((tuple(),
                          ('', RContext.current_file[-1]
                               + ':' + str(lineno))))

    def __str__(self):
        return ('Function'
                + (self.name and ':' + str(self.name) or '')
                + '(' + str(self.params) + ') '
                + str(self.code))

    #def make_name(self, name):
    #    ret = Function(self.ast)
    #    ret.name = name
    #    return ret

    def eval_to(self):
        return self.code.eval_to()


class Assign(Statement):
    entrails = ['lhs', 'rhs']

    def __new__(self, ast, rightwards=False):
        if rightwards:
            n, f = 3, 1
        else:
            n, f = 1, 3
        #if type(ast[n]) is Name and type(ast[f]) is Function:
        #    return ast[f].make_name(ast[n])
        return Rentity.__new__(Assign)

    def __init__(self, ast, rightwards=False):
        Statement.__init__(self)
        if rightwards:
            self.lhs = ast[3]
            self.rhs = ast[1]
        else:
            self.lhs = ast[1]
            self.rhs = ast[3]

    def __str__(self):
        return 'Assign(lhs=' + str(self.lhs) + ', rhs=' + str(self.rhs) + ')'

    def eval_to(self):
        return self.rhs

    def set_parent(self, p):
        Statement.set_parent(self, p)
        self.reg_name(self.lhs, self.rhs)

    def resolve(self, name):
        if self.lhs == name:
            return self.rhs
        return None


_prev_get = lambda s: len(s.statements) and s.statements[0].previous or None


def _prev_set(s, v):
    if s.statements is None or not len(s.statements):
        return
    s.statements[0].previous = v


class Statements(Statement):
    entrails = ['statements']

    previous = property(_prev_get, _prev_set)

    def __init__(self, statements):
        Statement.__init__(self)
        self.statements = statements
        for i in xrange(1, len(statements)):
                statements[i].previous = statements[i - 1]

    def __str__(self):
        return (type(self).__name__ + '('
                + str(len(self.statements)) + ' statements)')

    def eval_to(self):
        return self.statements[-1].eval_to()


class Bloc(Statements):

    def __init__(self, ast):
        Statements.__init__(self, ast[2:-1])
        returns = filter(lambda x: type(x) is Return, self.statements)
        self.has_return = returns and returns[0] or None

    def eval_to(self):
        return (self.has_return and self.has_return.eval_to()
                or self.statements[-1])


class If(Statement):
    entrails = ['condition', 'then', 'els_']

    def __init__(self, ast):
        Statement.__init__(self)
        #print "IF (ast)", ast
        self.condition = ast[3]
        self.then = ast[5]
        self.els_ = len(ast) == 8 and ast[7] or None
        #print "IF (properties)", self.condition, self.then, self.els_

    def __str__(self):
        ret = 'If(condition=' + str(self.condition)
        ret += ', then=' + str(self.then)
        if self.els_ is not None:
            ret += ', else=' + str(self.els_)
        ret += ')'
        return ret


class Return(Statement):
    entrails = ['expression']

    def __init__(self, ast):
        Statement.__init__(self)
        self.expression = ast[3]

    def __str__(self):
        return 'Return(' + str(self.expression) + ')'

    def eval_to(self):
        return self.expression


class Immed(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self)
        self.typ = ast[1][0]
        self.val = ast[1][1]

    def __str__(self):
        return str(self.typ) + '(' + str(self.val) + ')'

    def value(self):
        if self.typ == "STRING":
            return self.val
        elif self.typ == "NUM":
            return float(self.val)


class Param(Rentity):
    entrails = ['value']

    def __init__(self, ast):
        Rentity.__init__(self)
        if type(ast) is Assign:
            # named parameter
            self.name = ast.lhs
            self.value = ast.rhs
        else:
            self.name = ast[1][1]
            self.value = None

    def __str__(self):
        ret = 'Param('
        if self.name:
            ret += 'name=' + str(self.name) + ', '
        ret += 'value=' + str(self.value) + ')'
        return ret


class Param_list(Rentity):
    entrails = ['params']

    def __init__(self, ast):
        Rentity.__init__(self)
        print "param list", ast
        self.params = extract_list(ast[1:])

    def __str__(self):
        return 'ParamList(' + ', '.join(str(x) for x in self.params) + ')'

    def set_parent(self, p):
        Rentity.set_parent(self, p)
        for p in self.params:
            p.reg_name(p.name, p)


class Toplevel_expression(Statement):
    entrails = ['expression']

    def __new__(self, ast):
        if isinstance(ast[1], Statement) or type(ast[1]) in (Bloc, Function):
            return ast[1]

    def __init__(self, ast):
        Statement.__init__(self)
        self.expression = ast[-1]

    def __str__(self):
        return 'Expr(' + str(self.expression) + ')'

    def eval_to(self):
        return self.expression.eval_to()


class Call(Rentity):
    entrails = ['callee', 'params']
    previous = wrap_previous(lambda s: s.callee)

    def __init__(self, ast):
        Rentity.__init__(self)
        self.callee = ast[1]
        self.params = ast[3]

    def __str__(self):
        return ('Call(callee=' + str(self.callee) + ', params='
                + str(self.params) + ')')

    def eval_to(self):
        f = self.callee.eval_to()
        if f == self.callee:
            return self
        p = f.code.previous
        env = Renv()
        names = [p.name for p in f.params]
        values = [p.value for p in f.params]
        for j, par in enumerate(self.params):
            if par.name:
                i = names.index(par.name)
            else:
                i = j
            values[i] = par.value.eval_to()


class Script(Renv, Statements):

    def __init__(self, ast):
        Renv.__init__(self)
        Statements.__init__(self, ast[1:])


class For(Statement):
    entrails = ['iteration', 'statement']

    def __init__(self, ast):
        Statement.__init__(self)
        self.iteration = ast[3:-2]
        self.statement = ast[-1]

    def __str__(self):
        return ('For(iteration=' + str(self.iteration)
                + ', statement=' + str(self.statement) + ')')


class While(Statement):
    entrails = ['condition', 'statement']

    def __init__(self, ast):
        Statement.__init__(self)
        self.condition = ast[3:-2]
        self.statement = ast[-1]

    def __str__(self):
        return ('While(condition=' + str(self.condition)
                + ', statement=' + str(self.statement) + ')')


class Repeat(Statement):
    entrails = ['statement']

    def __init__(self, ast):
        Statement.__init__(self)
        self.statement = ast[-1]

    def __str__(self):
        return 'Repeat(' + str(self.statement) + ')'


class Subexpr(Rentity):

    def __new__(self, ast):
        return ast[2]


class Unary_plus_or_minus(Rentity):
    entrails = ['expression']

    def __new__(self, ast):
        if ast[1][0] == 'PLUS':
            return ast[2]
        return Rentity.__new__(self)

    def __init__(self, ast):
        self.expression = ast[2]

    def __str__(self):
        return 'Minus(' + str(self.expression) + ')'


class Indexing(Rentity):
    entrails = ['collection', 'indices']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.collection = ast[1]
        self.indices = extract_list(ast[2:-1])

    def __str__(self):
        return ('Indexing(coll=' + str(self.collection) + ', indices=('
                + ', '.join(str(x) for x in self.indices) + '))')


class Negation(Rentity):
    entrails = ['expression']

    def __init__(self, ast):
        self.expression = ast[2]

    def __str__(self):
        return 'Not(' + str(self.expression) + ')'


_binop_prev_get = lambda s: s.operands[0].previous


def _binop_prev_set(s, p):
    s.operands[0].previous = p


class BinOp(Rentity):
    entrails = ['operands']

    previous = property(_binop_prev_get, _binop_prev_set)

    def __init__(self, ast):
        self.operator = ast[2][0]
        self.operands = ast[1::2]
        print self.operands
        self.operands[1].previous = self.operands[0]

    def __str__(self):
        return (self.operator.capitalize() + '('
                + ', '.join(str(x) for x in self.operands) + ')')
        self.op1 = ast[1]
        self.op2 = ast[3]

    def eval_to(self):
        a = self.operands[0].eval_to()
        b = self.operands[1].eval_to()
        if type(a) is Immed and type(b) is Immed:
            return Immed((None, (a.typ, self.op(a.value(), b.value()))))
        return type(self)((None, a, (self.operator,), b))

    def op(self, a, b):
        return type(self)((None, a, (self.operator,), b))


class Sequence(BinOp):

    def op(self, a, b):
        return Sequence((None, a, ('COLON',), b))


class Addsub(BinOp):

    def op(self, a, b):
        if self.operator == 'PLUS':
            return a + b
        else:
            return a - b


class Special_op(BinOp):
    pass


class Muldiv(BinOp):

    def op(self, a, b):
        if self.operator == 'STAR':
            return a * b
        else:
            return a / b


class Comparison(BinOp):
    pass


class Bool_and(BinOp):
    pass


class Bool_or(BinOp):
    pass


class Formula(BinOp):
    pass


class Exponentiation(BinOp):

    def op(self, a, b):
        return a ** b


class Slot_extraction(BinOp):

    @property
    def name(self):
        return str(self.operands[0]) + '$' + str(self.operands[1])
