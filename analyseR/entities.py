__all__ = ['RContext', 'Rentity', 'AllIndices', 'Source', 'Function',
           'Assign', 'Statements', 'Bloc', 'If', 'IfElse', 'Return',
           'Immed', 'Name', 'Param', 'Param_list', 'Call', 'Script',
           'For', 'While', 'Repeat', 'Subexpr', 'Unary_plus_or_minus',
           'Indexing', 'Negation', 'BinOp', 'Sequence', 'Addsub',
           'Special_op', 'Muldiv', 'Comparison', 'Bool_and', 'Bool_or',
           'Formula', 'Exponentiation', 'Slot_extraction', 'Any',
           'Expression_list',
           'strip_common_path', 'path_str']

from itertools import *
from entities_base import *
import os


Dummy = Rentity(tuple())


class Source(Rentity):
    entrails = ['contents']
    previous = wrap_previous(lambda s: s.contents)

    def __init__(self, ast, parse=True):
        Rentity.__init__(self, ast)
        if parse:
            self.filename = os.path.join(RContext.current_dir[-1],
                                         ast[3][1][1:-1])
            #print "Sourcing", self.filename
            self.contents = RContext.parse(self.filename)

    def copy(self):
        ret = Source(self.ast, False)
        ret.filename = str(self.filename)
        ret.contents = self.contents.copy()
        ret.previous = self.previous

    def __str__(self):
        return 'Source(' + self.filename + ')'

    def eval_to(self):
        return self.contents.eval_to()

    @property
    def names(self):
        return self.contents.names

    def resolve(self, n):
        return self.contents.resolve(n)

    def __str__(self):
        return ('Sourced_Script('
                + str(len(self.contents.statements)) + ' statements)')

    #def set_parent(self, par):
    #    Rentity.set_parent(self, par)
    #    for name, value in self.names.iteritems():
    #        par.reg_name(name, value)


class Function(Renv, Rentity):
    entrails = ['code', 'params']

    def __init__(self, ast):
        Renv.__init__(self)
        Rentity.__init__(self, ast)
        self.ast = ast
        self.code = ast[-1]
        self.code.previous = Dummy
        self.params = isinstance(ast[-3], Param_list) and ast[-3] or None
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


class Statements(Renv, Statement):
    entrails = ['statements']

    #previous = property(_prev_get, _prev_set)
    previous = wrap_previous(lambda s: s.statements and s.statements[0])

    def __init__(self, statements):
        Renv.__init__(self)
        Statement.__init__(self, statements)
        self.statements = statements[1:]
        for i in xrange(1, len(self.statements)):
                self.statements[i].previous = self.statements[i - 1]
        returns = filter(lambda x: type(x) is Return, self.statements)
        self.has_return = returns and returns[0] or None

    @cached_eval_to
    def eval_to(self):
        if self.has_return:
            return self.has_return.eval_to()
        for s in reversed(self.statements):
            ret = s.eval_to()
            if ret is not None:
                return ret
        return None

    def __str__(self):
        return (type(self).__name__ + '('
                + str(len(self.statements)) + ' statements)')

    #def eval_to(self):
    #    return reduce(lambda a, b: a or b.eval_to(),
    #                  reversed(self.statements),
    #                  None)

    #def resolve(self, n):
    #    for s in reversed(self.statements):
    #        r = s.resolve(n)
    #        if r is not None:
    #            return r
    #    return None
    def resolve(self, n):
        if n in self.names:
            try:
                return self.names[n][-1].copy()
            except Exception, e:
                print self
                print n
                print self.names[n]
                raise e
        return None

    def __getitem__(self, i):
        return self.statements[i]


class Bloc(Statements):

    def __init__(self, ast):
        Statements.__init__(self, ast[1:-1])
        self.ast = ast


class Return(Statement):
    entrails = ['expression']

    previous = wrap_previous(lambda s: s.expression)

    def __init__(self, ast):
        Statement.__init__(self, ast)
        self.expression = ast[3]

    def __str__(self):
        return 'Return(' + str(self.expression) + ')'

    def eval_to(self):
        return self.expression.eval_to()


class Param(Rentity):
    entrails = ['value']

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        #print "Param ast", ast
        self.name = ast[1][1]
        if len(ast) == 4:
            self.value = ast[3]
            self.value.previous = Dummy
        else:
            self.value = None

    def __str__(self):
        ret = 'Param('
        if self.name:
            ret += 'name=' + str(self.name) + ', '
        ret += 'value=' + str(self.value) + ')'
        return ret


class Param_list(Rentity):
    entrails = ['params']

    previous = wrap_previous(lambda s: s.params and s.params[0])

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        #print "param list", ast
        self.params = extract_list(ast[1:])
        for p in self.params:
            p.previous = Dummy
        #print "param list", self.params

    def __str__(self):
        return 'ParamList(' + ', '.join(str(x) for x in self.params) + ')'

    def set_parent(self, par):
        Rentity.set_parent(self, par)
        for p in self.params:
            par.reg_name(p.name, p)


class Expression_list(Rentity):
    entrails = ['expressions']

    previous = wrap_previous(lambda s: s.expressions and s.expressions[0])

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        #print "expr list", ast
        #self._prev = None
        self.expressions = extract_list(ast[1:])
        for i in xrange(1, len(self.expressions)):
            self.expressions[i].previous = self.expressions[i - 1]
        #print "expr list", self.expressions

    def __str__(self):
        return 'ExprList(' + ', '.join(str(x) for x in self.expressions) + ')'

    def eval_to(self):
        return Expression_list([None] + [p.eval_to()
                                         for p in self.expressions])

    def pp(self):
        return ', '.join(x.pp() for x in self.expressions)


class Toplevel_expression(Statement):
    entrails = ['expression']

    def __new__(self, ast):
        if isinstance(ast[1], Statement) or type(ast[1]) in (Bloc, Function):
            return ast[1]

    def __init__(self, ast):
        Statement.__init__(self, ast)
        self.expression = ast[-1]

    def __str__(self):
        return 'Expr(' + str(self.expression) + ')'

    def eval_to(self):
        return self.expression.eval_to()


class Call(Rentity):
    entrails = ['callee', 'params']
    previous = wrap_previous(lambda s: s.callee)

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        self.callee = ast[1]
        self.params = isinstance(ast[3], Rentity) and ast[3] or None
        if self.params:
            self.params.previous = self.callee

    def __str__(self):
        return ('Call(callee=' + str(self.callee) + ', params='
                + str(self.params) + ')')

    def pp(self):
        if self.params:
            return self.callee.pp() + '(' + self.params.pp() + ')'
        else:
            return self.callee.pp() + '()'

    def _eval_call(self, f, what):
        #print "EVAL CALL", f
        if isinstance(f, IfElse):
            t = f.then and f.then.eval_to()
            e = f.els_ and f.els_.eval_to()
            #print "t", t
            #print "e", e
            return IfElse(f, f.condition,
                          (isinstance(t, Function) or isinstance(t, IfElse))
                          and self._eval_call(t, what) or t,
                          (isinstance(e, Function) or isinstance(e, IfElse))
                          and self._eval_call(e, what) or e)
        if not isinstance(f, Function):
            return
        if not f.params:
            names = []
            values = []
        else:
            names = [p.name for p in f.params.params]
            values = [p.value for p in f.params.params]
            for j, par in enumerate(self.params.expressions):
                # FIXME : make some kind of NamedArgument to avoid
                # conflicts when exporting the assigned name.
                if isinstance(par, Assign):
                    if par.assign == 'EQUAL':
                        i = names.index(par.lhs.name)
                    else:
                        i = j
                    value = par.rhs.eval_to()
                else:
                    i = j
                    value = par.eval_to()
                values[i] = value
        code = f.code.copy()
        #print "Called code",
        #print isinstance(f.code, Statements) and f.code.statements or f.code
        env = Statements([None]
                         + [Assign((None, Name((None, (None, n))),
                                   ('LEFT_ARROW',),
                                   v.copy()))
                            for n, v in izip(names, values)]
                         + (isinstance(code, Statements)
                            and code.statements
                             or [code]))
        env.previous = self.previous
        RContext.call_resolution.append(env)
        #print "Call frame", env.statements
        ret = what(env)
        RContext.call_resolution.pop()
        return ret

    @cached_eval_to
    def eval_to(self):
        return self.eval_call(lambda env: env.eval_to()) or self.copy()

    def eval_call(self, what):
        f = self.callee.eval_to()
        if f in (self.callee, None):
            par = []
            for p in self.params.expressions:
                if isinstance(p, Assign):
                    par.append(Assign((None, p.lhs.copy(), (p.assign,),
                                       p.rhs.eval_to())))
                else:
                    par.append(p.eval_to())
            return Call((None, self.callee.copy(), None,
                         Expression_list([None] + par)))
        return self._eval_call(f, what)


class Script(Statements):

    previous = Statements.previous

    def __init__(self, ast):
        Statements.__init__(self, ast)


class For(Statement):
    entrails = ['var', 'iteration', 'statement']

    previous = wrap_previous(lambda s: s.iter_resolve)

    def __init__(self, ast):
        Statement.__init__(self, ast)
        #self.iteration = ast[3:-2]
        self.iteration = ast[-3]
        self.var = Name(ast[2:4])
        #print 'For', self.iteration, self.var
        self.iter_resolve = Assign((None, self.var.copy(),
                                    ('LEFT_ARROW',), self.iteration.copy()))
        self.statement = ast[-1]
        self.statement.previous = self.iter_resolve
        self.var.previous = self.iter_resolve
        self.iteration.previous = self.iter_resolve

    def __str__(self):
        return ('For(iteration=' + str(self.iteration)
                + ', statement=' + str(self.statement) + ')')


class While(Statement):
    entrails = ['condition', 'statement']
    previous = wrap_previous(lambda s: s.condition)

    def __init__(self, ast):
        Statement.__init__(self, ast)
        self.condition = ast[-3]
        self.statement = ast[-1]
        self.statement.previous = self.condition

    def __str__(self):
        return ('While(condition=' + str(self.condition)
                + ', statement=' + str(self.statement) + ')')


class Repeat(Statement):
    entrails = ['statement']
    previous = wrap_previous(lambda s: s.statement)

    def __init__(self, ast):
        Statement.__init__(self, ast)
        self.statement = ast[-1]

    def __str__(self):
        return 'Repeat(' + str(self.statement) + ')'


class Subexpr(Rentity):

    def __new__(self, ast):
        return ast[2]


class Unary_plus_or_minus(Rentity):
    entrails = ['expression']
    previous = wrap_previous(lambda s: s.expression)

    def __new__(self, ast):
        if ast[1][0] == 'PLUS':
            return ast[2]
        return Rentity.__new__(self)

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        self.expression = ast[2]

    def __str__(self):
        return 'Minus(' + str(self.expression) + ')'

    @cached_eval_to
    def eval_to(self):
        x = self.expression.eval_to()
        if isinstance(x, Immed) and x.typ == 'NUM':
            v = - x.value()
            return Immed((None, ('NUM', str(v))))

    def pp(self):
        return '-' + self.expression.pp()


class Indexing(Rentity):
    entrails = ['collection', 'indices']
    previous = wrap_previous(lambda s: s.collection)

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        self.collection = ast[1]
        self.indices = ast[-2]
        self.indices.previous = self.collection
        #print "INDEXING", ast
        #print self.collection, self.indices.previous

    def __str__(self):
        return ('Indexing(coll=' + str(self.collection) + ', indices=('
                + ', '.join(str(x) for x in self.indices) + '))')

    def pp(self):
        return (self.collection.pp() + '['
                + ', '.join(x.pp() for x in self.indices)
                + ']')


_binop_prev_get = lambda s: s.operands[0].previous


def _binop_prev_set(s, p):
    s.operands[0].previous = p


class BinOp(Rentity):
    entrails = ['operands']

    previous = wrap_previous(lambda s: s.operands[0])
    #previous = property(_binop_prev_get, _binop_prev_set)

    def __init__(self, ast):
        try:
            Rentity.__init__(self, ast)
            self.operator = ast[2][0]
            self.operands = ast[1::2]
            if type(self.operands[1]) is tuple:
                print "BinOp"
                print "   operator", self.operator
                print "   operands", self.operands[0], self.operands[1]
            self.operands[1].previous = self.operands[0]
        except Exception, e:
            print "BinOp error", ast
            raise e

    def __str__(self):
        return (self.operator.capitalize() + '('
                + ', '.join(str(x) for x in self.operands) + ')')

    @cached_eval_to
    def eval_to(self):
        a = self.operands[0].eval_to()
        b = self.operands[1].eval_to()
        if type(a) is Immed and type(b) is Immed:
            try:
                result = self.op(a.value(), b.value())
                typ = type(result) is str and 'STRING' or 'NUM'
                result = type(result) is str and result or int(result)
                ret = Immed((None, (typ, result)))
                ret.previous = self.previous
                ret.parent = self.parent
                return ret
            except:
                pass
        #print "binop-eval", a, self.operator, b
        return type(self)((None, a, (self.operator,), b))

    def op(self, a, b):
        return type(self)((None, a, (self.operator,), b))

    def ppop(self):
        return {'COLON': ':',
                'PLUS': '+',
                'SLASH': '/',
                'STAR': '*',
                'MINUS': '-',
                'SUP': '>',
                'INF': '<',
                'LE': '<=',
                'GE': '>=',
                'NE': '!=',
                'EQ': '==',
                'LOG_AND': '&&',
                'LOG_OR': '||',
                'AMPERSAND': '&',
                'PIPE': '|',
                'CIRCONFLEX': '^'}[self.operator]

    def pp(self):
        return ('(' + self.operands[0].pp()
                + ' ' + self.ppop()
                + ' ' + self.operands[1].pp() + ')')


class Sequence(BinOp):

    def op(self, a, b):
        return Sequence((None, ('NUM', a), ('COLON',), ('NUM', b)))


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

    def op(self, a, b):
        return {'EQ': lambda a, b: a == b,
                'NE': lambda a, b: a != b,
                'LE': lambda a, b: a <= b,
                'GE': lambda a, b: a >= b,
                'INF': lambda a, b: a < b,
                'SUP': lambda a, b: a > b}[self.operator](a, b)


class Bool_and(BinOp):

    def op(self, a, b):
        return (a and b) and 1 or 0


class Bool_or(BinOp):

    def op(self, a, b):
        return (a or b) and 1 or 0


class Formula(BinOp):
    pass


class Exponentiation(BinOp):

    def op(self, a, b):
        return a ** b


class Slot_extraction(BinOp):

    def __init__(self, ast):
        if type(ast[-1]) is Name:
            BinOp.__init__(self, ast)
        else:
            BinOp.__init__(self, ast[:-1] + (Name(ast[-2:]),))
        #self.operands[1] = Name((None, (None, self.operands[1])))

    @property
    def name(self):
        return str(self.operands[0]) + '$' + str(self.operands[1])
