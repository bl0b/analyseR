class RContext(object):
    current_file = ['']
    parse = None


_entrail_get = lambda self, e: getattr(self, '_' + e)


def _entrail_set(self, e, v):
    if type(v) in (list, tuple):
        for x in v:
            if isinstance(x, Rentity):
                x.parent = self
    elif isinstance(v, Rentity):
        v.parent = self
    setattr(self, '_' + e, v)


class RentityMeta(type):
    registry = {}

    def __init__(cls, name, bases, dic):
        RentityMeta.registry[name.lower()] = cls
        for e in cls.entrails:
            setattr(cls, e, property(lambda s: _entrail_get(s, e),
                                     lambda s, v: _entrail_set(s, e, v)))


class Rentity(object):
    __metaclass__ = RentityMeta
    entrails = []

    def __init__(self):
        self.filename = RContext.current_file[-1]
        self.parent = None

    def __repr__(self):
        return str(self)

    def search_iter(self, predicate):
        if predicate(self):
            yield self
        for e in self.entrails:
            x = getattr(self, e)
            if type(x) in (list, tuple):
                for k in x:
                    if not isinstance(k, Rentity):
                        if predicate(k):
                            yield k
                        continue
                    for result in k.search_iter(predicate):
                        yield result
            elif isinstance(x, Rentity):
                for result in x.search_iter(predicate):
                    yield result

    def get_filename(self):
        if hasattr(self, 'filename'):
            return self.filename
        elif self.parent:
            return self.parent.get_filename()


class AllIndices(Rentity):

    def __str__(self):
        return "AllIndices"


allindices = AllIndices()


def extract_list(ast):
    ret = []
    on_comma = True
    for a in ast:
        if type(a) is tuple and a[0] == 'COMMA':
            if on_comma:
                ret.append(allindices)
            else:
                on_comma = True
        else:
            on_comma = False
            ret.append(a)
    return ret


class Source(Rentity):
    entrails = ['contents']

    def __init__(self, filename):
        Rentity.__init__(self)
        self.filename = filename
        self.contents = RContext.parse(filename[1:-1])

    def __str__(self):
        return 'Source(' + self.filename + ')'

    def eval(self):
        return None


class Function(Rentity):
    entrails = ['ast']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.ast = ast
        self.name = None

    def __str__(self):
        return ('Function'
                + (self.name and ':' + str(self.name) or '')
                + str(self.ast[1:]))

    def make_name(self, name):
        ret = Function(self.ast)
        ret.name = name
        return ret

    def eval(self):
        return self


class Assign(Rentity):
    entrails = ['lhs', 'rhs']

    def __new__(self, ast, rightwards=False):
        if rightwards:
            n, f = 3, 1
        else:
            n, f = 1, 3
        if type(ast[n]) is Name and type(ast[f]) is Function:
            return ast[f].make_name(ast[n])
        return Rentity.__new__(Assign)

    def __init__(self, ast, rightwards=False):
        Rentity.__init__(self)
        if rightwards:
            self.lhs = ast[3]
            self.rhs = ast[1]
        else:
            self.lhs = ast[1]
            self.rhs = ast[3]

    def __str__(self):
        return 'Assign(lhs=' + str(self.lhs) + ', rhs=' + str(self.rhs) + ')'

    def eval(self):
        return self.rhs


class Statements(Rentity):
    entrails = ['statements']

    def __init__(self, statements):
        Rentity.__init__(self)
        self.statements = statements

    def __str__(self):
        return (type(self).__name__ + '('
                + str(len(self.statements)) + ' statements)')


class Bloc(Statements):

    def __init__(self, ast):
        Statements.__init__(self, ast[2:-1])


class If(Rentity):
    entrails = ['condition', 'then', 'els_']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.condition = ast[3]
        self.then = ast[5]
        self.els_ = len(ast) == 7 and ast[7] or None

    def __str__(self):
        ret = 'If(condition=' + str(self.condition)
        ret += ', then=' + str(self.then)
        if self.els_ is not None:
            ret += ', else=' + str(self.els_)
        ret += ')'
        return ret


class Return(Rentity):
    entrails = ['expression']

    def __init__(self, ast):
        self.expression = ast[3]

    def __str__(self):
        return 'Return(' + str(self.expression) + ')'


class Immed(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self)
        self.typ = ast[1][0]
        self.val = ast[1][1]

    def __str__(self):
        return str(self.typ) + '(' + str(self.val) + ')'


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


class Param(Rentity):
    entrails = ['value']

    def __init__(self, ast):
        Rentity.__init__(self)
        if type(ast) is Assign:
            # named parameter
            self.name = ast.lhs
            self.value = ast.rhs
        else:
            self.name = None
            self.value = ast

    def __str__(self):
        ret = 'Param('
        if self.name:
            ret += 'name=' + str(self.name.name) + ', '
        ret += 'value=' + str(self.value) + ')'
        return ret


class Param_list(Rentity):
    entrails = ['params']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.params = extract_list(ast[2:-1])

    def __str__(self):
        return 'ParamList(' + ', '.join(str(x) for x in self.params) + ')'


class Call(Rentity):
    entrails = ['params']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.callee = ast[1]
        self.params = ast[3]

    def __str__(self):
        return ('Call(callee=' + str(self.callee) + ', params='
                + str(self.params) + ')')


class Script(Statements):

    def __init__(self, ast):
        Statements.__init__(self, ast[1:])


class For(Rentity):
    entrails = ['iteration', 'statement']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.iteration = ast[3:-2]
        self.statement = ast[-1]

    def __str__(self):
        return ('For(iteration=' + str(self.iteration)
                + ', statement=' + str(self.statement) + ')')


class While(Rentity):
    entrails = ['condition', 'statement']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.condition = ast[3:-2]
        self.statement = ast[-1]

    def __str__(self):
        return ('While(condition=' + str(self.condition)
                + ', statement=' + str(self.statement) + ')')


class Repeat(Rentity):
    entrails = ['statement']

    def __init__(self, ast):
        Rentity.__init__(self)
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


class BinOp(Rentity):
    entrails = ['operands']

    def __init__(self, ast):
        self.operator = ast[2][0]
        self.operands = ast[1::2]

    def __str__(self):
        return (self.operator.capitalize() + '('
                + ', '.join(str(x) for x in self.operands) + ')')
        self.op1 = ast[1]
        self.op2 = ast[3]


class Sequence(BinOp):
    pass


class Addsub(BinOp):
    pass


class Special_op(BinOp):
    pass


class Muldiv(BinOp):
    pass


class Comparison(BinOp):
    pass


class Bool_and(BinOp):
    pass


class Bool_or(BinOp):
    pass


class Formula(BinOp):
    pass


class Exponentiation(BinOp):
    pass


class Slot_extraction(BinOp):
    pass
