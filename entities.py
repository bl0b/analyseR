class RContext(object):
    current_file = []
    parse = None


class RentityMeta(type):
    registry = {}

    def __init__(cls, name, bases, dic):
        RentityMeta.registry[name.lower()] = cls


class Rentity(object):
    __metaclass__ = RentityMeta
    entrails = []

    def __init__(self):
        self.filename = RContext.current_file[-1]

    def __repr__(self):
        return str(self)

    def search(self, predicate):
        return [x
                for e in type(self).entrails
                for x in getattr(self, e) if predicate(x)]


class Renv(Rentity, dict):

    def __init__(self, parent=None):
        Rentity.__init__(self)
        dict.__init__(self)
        self.parent = parent

    def resolve(self, name):
        if name.namespace:
            return name
        if name.name in self:
            return self[name.name]
        if self.parent:
            return self.parent.resolve(name)
        return name


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
    entrails = ['cond', 'then', 'els_']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.cond = ast[3]
        self.then = ast[5]
        self.els_ = len(ast) == 7 and ast[7] or None

    def __str__(self):
        ret = 'If(cond=' + str(self.cond) + ', then=' + str(self.then)
        if self.els_ is not None:
            ret += ', else=' + str(self.els_)
        ret += ')'
        return ret


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


class Call(Rentity):
    entrails = ['params']

    def __init__(self, ast):
        Rentity.__init__(self)
        self.callee = ast[1]
        self.params = tuple(Param(x) for x in ast[3::2])

    def __str__(self):
        return ('Call(callee=' + str(self.callee) + ', params='
                + str(self.params) + ')')


class Script(Statements):

    def __init__(self, ast):
        Statements.__init__(self, ast[1:])
