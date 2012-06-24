__all__ = ['RContext', 'Rentity', 'AllIndices', 'Source', 'Function',
           'Assign', 'Statements', 'Bloc', 'If', 'IfElse', 'Return',
           'Immed', 'Name', 'Param', 'Param_list', 'Call', 'Script',
           'For', 'While', 'Repeat', 'Subexpr', 'Unary_plus_or_minus',
           'Indexing', 'Negation', 'BinOp', 'Sequence', 'Addsub',
           'Special_op', 'Muldiv', 'Comparison', 'Bool_and', 'Bool_or',
           'Formula', 'Exponentiation', 'Slot_extraction', 'Any']

from itertools import *
from entities_base import *
import os


class Name(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self)
        if len(ast) == 4:
            self.namespace = type(ast[1]) is tuple and ast[1][1] or ast[1]
            self.visibility = ast[2][1]
            self.name = ast[3][1]
        else:
            self.namespace = None
            self.visibility = None
            self.name = ast[1][1]

    def __str__(self):
        ret = 'Name('
        if self.namespace is not None:
            ret += str(self.namespace)
            ret += self.visibility
        ret += self.name
        ret += ')'
        return ret

    def eval_to(self):
        defs = self - Any // Assign(lhs=lambda x: type(x) is Name
                                                  and x == self)
        if len(defs) == 0:
            return self
        if len(defs) > 1:
            return strip_common_path(*defs)
        return defs[0].rhs

#        #print "eval_to   ", self
#        #print "| previous", self.previous
#        #print "|   parent", self.parent
#        # if name is scoped, then don't resolve. (external package)
#
#        #def _find(p):
#        #    while p.previous is not None:
#        #        p = p.previous
#        #        #print "|    (previous) on", p
#        #        r = p.resolve(self)
#        #        if r is not None and r is not self:
#        #            #print "| => found (in previous) !", r
#        #            return r.eval_to()
#        #    return None
#
#        if self.visibility is not None:
#            #print "| => namespace."
#            return self
#        # search for locally defined name (going back to beginning of script)
#        #r = _find(self)
#        #if r is not None:
#        #    return r
#        tmp = self
#        p = self.previous
#        while p is not None:
#            tmp = p
#            r = p.resolve(self)
#            if r is not None and r is not self:
#                return r.eval_to()
#            p = p.previous
#        for p in reversed(RContext.call_resolution):
#            r = p.resolve(self)
#            if r is not None and r is not self:
#                #print "| => found (in call stack) !", r
#                return r.eval_to()
#        p = tmp.parent and tmp.parent.previous
#        while p is not None:
#            r = p.resolve(self)
#            if r is not None and r is not self:
#                return r.eval_to()
#            p = p.previous or p.parent
#        #print "| => failed."
#        return self

    def resolve(self, n):
        if self is n:
            return self
        return None

    def __eq__(self, a):
        if type(a) is type(self):
            return (self.namespace == a.namespace and self.name == a.name)
        else:
            return False

    def __hash__(self):
        return hash(self.namespace) + hash(self.name)


class Source(Rentity):
    entrails = ['contents']
    previous = wrap_previous(lambda s: s.contents)

    def __init__(self, ast):
        Rentity.__init__(self)
        self.filename = os.path.join(RContext.current_dir[-1], ast[3][1][1:-1])
        #print "Sourcing", self.filename
        self.contents = RContext.parse(self.filename)

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

    def set_parent(self, par):
        Rentity.set_parent(self, par)
        for name, value in self.names.iteritems():
            par.reg_name(name, value)


class Function(Renv, Rentity):
    entrails = ['code', 'params']

    def __init__(self, ast):
        Renv.__init__(self)
        Rentity.__init__(self)
        self.ast = ast
        self.code = ast[-1]
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

    #def make_name(self, name):
    #    ret = Function(self.ast)
    #    ret.name = name
    #    return ret

    #def eval_to(self):
    #    return self.code.eval_to()


class Assign(Statement):
    entrails = ['lhs', 'rhs']

    def __set_previous(s, p):
        if s.lhs:
            s.lhs.previous = p
        if s.rhs:
            s.rhs.previous = p

    def __get_previous(s):
        return s.lhs and s.lhs.previous or None

    previous = property(__get_previous, __set_previous)

#    def __new__(self, ast, rightwards=False):
#        if rightwards:
#            n, f = 3, 1
#        else:
#            n, f = 1, 3
#        #if type(ast[n]) is Name and type(ast[f]) is Function:
#        #    return ast[f].make_name(ast[n])
#        return Rentity.__new__(Assign)

    def __init__(self, ast, rightwards=False):
        Statement.__init__(self)
        if rightwards:
            self.lhs = ast[3]
            self.rhs = ast[1]
        else:
            self.lhs = ast[1]
            self.rhs = ast[3]
        self.assign = ast[2][0]

    def __str__(self):
        return 'Assign(lhs=' + str(self.lhs) + ', rhs=' + str(self.rhs) + ')'

    def eval_to(self):
        return self.rhs.eval_to()

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

    def resolve(self, n):
        for s in reversed(self.statements):
            r = s.resolve(n)
            if r is not None:
                return r
        return None


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

    def __get_previous(self):
        return self.condition and self.condition.previous

    def __set_previous(self, p):
        if self.condition:
            self.condition.previous = p

    previous = property(__get_previous, __set_previous)

    def __init__(self, ast):
        Statement.__init__(self)
        #print "IF (ast)", ast
        self.condition = ast[3]
        self.then = ast[5]
        if self.then == None:
            raise Exception('IF ' + str(ast) + ' '
                            + str(ast[3]) + ' '
                            + str(ast[5]) + ' '
                            + str(ast[7]))
        self.els_ = len(ast) == 8 and ast[7] or None
        if self.then:
            self.then.previous = self.condition
        if self.els_:
            self.els_.previous = self.condition
        #print "IF (properties)", self.condition, self.then, self.els_

    def __str__(self):
        ret = type(self).__name__
        ret += '(condition=' + str(self.condition)
        ret += ', then=' + str(self.then)
        if self.els_ is not None:
            ret += ', else=' + str(self.els_)
        ret += ')'
        return ret

    def resolve(self, n):
        cond = self.condition.eval_to()
        #print "[resolve] If eval cond to", cond
        if isinstance(cond, Immed):
            if cond.value():
                return self.then.resolve(n)
            elif self.els_:
                return self.els_.resolve(n)
        else:
            then = self.then and self.then.resolve(n)
            els_ = self.els_ and self.els_.resolve(n)
            if then is None:
                if els_ is None:
                    return None
                elif isinstance(cond, Negation):
                    return IfElse(self.previous, cond.expression, els_, None)
                else:
                    return IfElse(self.previous, Negation(cond), els_, None)
            return IfElse(self.previous, cond, then, els_)

    def eval_to(self):
        cond = self.condition.eval_to()
        #print "[eval_to] If eval cond to", cond
        if isinstance(cond, Immed):
            if cond.value():
                return self.then.eval_to()
            elif self.els_:
                return self.els_.eval_to()
        else:
            ret = IfElse(self.previous, cond, self.then.eval_to(),
                         self.els_ and self.els_.eval_to())
        return ret


class IfElse(If):

    def __init__(self, prev, cond, then, els_):
        #print "IfElse", prev, cond, then, els_
        if isinstance(cond, bool):
            raise Exception()
        If.__init__(self, (None, None, None, cond,
                           None, then, None, els_))
        self.previous = prev


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
        #print "Param ast", ast
        self.name = ast[1][1]
        if len(ast) == 4:
            self.value = ast[3]
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

    def __init__(self, ast):
        Rentity.__init__(self)
        #print "param list", ast
        self.params = extract_list(ast[1:])
        #print "param list", self.params

    def __str__(self):
        return 'ParamList(' + ', '.join(str(x) for x in self.params) + ')'

    def set_parent(self, par):
        Rentity.set_parent(self, par)
        for p in self.params:
            par.reg_name(p.name, p)


class Expression_list(Rentity):
    entrails = ['expressions']

    def __set_p(self, p):
        self._prev = p
        if not self.expressions:
            return
        for e in self.expressions:
            e.previous = p

    def __get_p(self):
        return self._prev

    previous = property(__get_p, __set_p)

    def __init__(self, ast):
        Rentity.__init__(self)
        #print "expr list", ast
        self._prev = None
        self.expressions = extract_list(ast[1:])
        #print "expr list", self.expressions

    def __str__(self):
        return 'ExprList(' + ', '.join(str(x) for x in self.expressions) + ')'

    def eval_to(self):
        return Expression_list([None] + [p.eval_to()
                                         for p in self.expressions])


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


class CallContext(Renv, Rentity):

    def __init__(self):
        Renv.__init__(self)
        Rentity.__init__(self)

    def resolve(self, name):
        #print "resolution of", name, "in (call context)", self.names
        if name.name in self.names:
            return self.names[name.name][-1]
        return None


class Call(Rentity):
    entrails = ['callee', 'params']
    previous = wrap_previous(lambda s: s.callee)

    def __init__(self, ast):
        Rentity.__init__(self)
        self.callee = ast[1]
        self.params = isinstance(ast[3], Rentity) and ast[3] or None
        if self.params:
            self.params.previous = self.callee

    def __str__(self):
        return ('Call(callee=' + str(self.callee) + ', params='
                + str(self.params) + ')')

#    def _eval_call(self, f):
#        #print "EVAL CALL", f
#        if isinstance(f, IfElse):
#            t = f.then and f.then.eval_to()
#            e = f.els_ and f.els_.eval_to()
#            #print "t", t
#            #print "e", e
#            return IfElse(f.previous, f.condition,
#                          (isinstance(t, Function) or isinstance(t, IfElse))
#                          and self._eval_call(t) or t,
#                          (isinstance(e, Function) or isinstance(e, IfElse))
#                          and self._eval_call(e) or e)
#        #p = f.code.previous
#        env = CallContext()
#        #env.previous = self.previous
#        names = [p.name for p in f.params.params]
#        values = [[p.value] for p in f.params.params]
#        for j, par in enumerate(self.params.expressions):
#            # FIXME : make some kind of NamedArgument to avoid
#            # conflicts when exporting the assigned name.
#            if isinstance(par, Assign):
#                if par.assign == 'EQUAL':
#                    i = names.index(par.lhs.name)
#                else:
#                    i = j
#                value = par.rhs.eval_to()
#            else:
#                i = j
#                value = par.eval_to()
#            values[i] = [value]
#        env.names.update(izip(names, values))
#        #print "Call context :"
#        #for n, v in env.names.iteritems():
#        #    print "    ", n, v
#        backup = f.code.previous
#        env.previous = (RContext.call_resolution
#                        and RContext.call_resolution[-1]
#                        or None)
#        f.code.previous = env
#        ##f.code.previous = env
#        RContext.call_resolution.append(env)
#        ret = f.code.eval_to()
#        RContext.call_resolution.pop()
#        f.code.previous = backup
#        return ret

    def _eval_call(self, f):
        #print "EVAL CALL", f
        if isinstance(f, IfElse):
            t = f.then and f.then.eval_to()
            e = f.els_ and f.els_.eval_to()
            #print "t", t
            #print "e", e
            return IfElse(f.previous, f.condition,
                          (isinstance(t, Function) or isinstance(t, IfElse))
                          and self._eval_call(t) or t,
                          (isinstance(e, Function) or isinstance(e, IfElse))
                          and self._eval_call(e) or e)
        #p = f.code.previous
        #env.previous = self.previous
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
        #env.names.update(izip(names, values))
        print names
        print values
        env = Statements([Assign((None, Name((None, (None, n))),
                                 ('LEFT_ARROW',),
                                 v))
                          for n, v in izip(names, values)])
        print env
        #print "Call context :"
        #for n, v in env.names.iteritems():
        #    print "    ", n, v
        backup = f.code.previous
        env.previous = (RContext.call_resolution
                        and RContext.call_resolution[-1]
                        or None)
        f.code.previous = env.statements and env.statements[-1] or env.previous
        RContext.call_resolution.append(env)
        print str(env.statements)
        ret = f.code.eval_to()
        RContext.call_resolution.pop()
        f.code.previous = backup
        return ret

    def eval_to(self):
        f = self.callee.eval_to()
        if f is self.callee:
            par = []
            for p in self.params.expressions:
                if isinstance(p, Assign):
                    par.append(Assign((None, p.lhs, p.assign, p.eval_to())))
                else:
                    par.append(p.eval_to())
            return Call((None, self.callee, None,
                         Expression_list([None] + par)))
        return self._eval_call(f)


class Script(Renv, Statements):

    def __init__(self, ast):
        Renv.__init__(self)
        Statements.__init__(self, ast[1:])


class For(Statement):
    entrails = ['var', 'iteration', 'statement']

    def __init__(self, ast):
        Statement.__init__(self)
        #self.iteration = ast[3:-2]
        self.iteration = ast[-3]
        self.var = Name(ast[2:4])
        #print 'For', self.iteration, self.var
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
        Rentity.__init__(self)
        self.expression = ast[2]

    def __str__(self):
        return 'Minus(' + str(self.expression) + ')'

    def eval_to(self):
        x = self.expression.eval_to()
        if isinstance(x, Immed) and x.typ == 'NUM':
            v = - x.value()
            return Immed((None, ('NUM', str(v))))


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
        Rentity.__init__(self)
        self.expression = ast[2]

    def __str__(self):
        return 'Not(' + str(self.expression) + ')'

    def eval_to(self):
        x = self.expression.eval_to()
        if isinstance(x, Name) and x.visibility is None:
            if x.name in ('T', 'TRUE'):
                return Immed((None, ('NUM', '0')))
            elif x.name in ('F', 'FALSE'):
                return Immed((None, ('NUM', '1')))
        if isinstance(x, Immed) and x.typ == 'NUM':
            return Immed((None, ('NUM', x.value() and '0' or '1')))
        return Negation((None, None, x))


_binop_prev_get = lambda s: s.operands[0].previous


def _binop_prev_set(s, p):
    s.operands[0].previous = p


class BinOp(Rentity):
    entrails = ['operands']

    previous = wrap_previous(lambda s: s.operands[0])
    #previous = property(_binop_prev_get, _binop_prev_set)

    def __init__(self, ast):
        Rentity.__init__(self)
        self.operator = ast[2][0]
        self.operands = ast[1::2]
        if type(self.operands[1]) is tuple:
            print "BinOp"
            print "   operator", self.operator
            print "   operands", self.operands[0], self.operands[1]
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
            try:
                result = self.op(a.value(), b.value())
                return Immed((None, (a.typ, result)))
            except:
                pass
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

    def __init__(self, ast):
        BinOp.__init__(self, ast[:-1] + (Name(ast[-2:]),))
        #self.operands[1] = Name((None, (None, self.operands[1])))

    @property
    def name(self):
        return str(self.operands[0]) + '$' + str(self.operands[1])
