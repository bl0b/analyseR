def find_closest_common_parent(patha, pathb):
    return reduce(lambda a, (pa, pb): pa == pb and pa or a,
                  izip(patha, pathb))


_entrail_get = lambda e: lambda self: getattr(self, '_' + e)


def _entrail_set(e):

    def _(self, v):
        if type(v) in (list, tuple):
            for x in v:
                if isinstance(x, Rentity):
                    x.set_parent(self)
        elif isinstance(v, Rentity):
            v.set_parent(self)
        setattr(self, '_' + e, v)
        #print "set entrail", e, v, getattr(self, '_' + e)
        return v

    return _


class RentityMeta(type):
    registry = {}

    def __init__(cls, name, bases, dic):
        RentityMeta.registry[name.lower()] = cls
        for e in cls.entrails:
            setattr(cls, e, property(_entrail_get(e), _entrail_set(e)))


class Rentity(object):
    __metaclass__ = RentityMeta
    entrails = []

    def __init__(self):
        for e in self.entrails:
            setattr(self, '_' + e, None)
        self.filename = RContext.current_file[-1]
        self.parent = None
        self.previous = None
        #for e in self.entrails:
        #    setattr(self, e, None)

    def set_parent(self, p):
        self.parent = p

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

    def eval_to(self):
        return self

    def reg_name(self, name, value):
        if self.parent:
            self.parent.reg_name(name, value)

    def get_path(self):
        if self.parent:
            return self.parent.get_path() + [self]
        else:
            return [self]

    def resolve(self, name):
        if type(name) is Name:
            if name.visibility is not None:
                return name
            name = name.name
        if hasattr(self, "names") and name in self.names:
            return self.names[name][-1]
        return None


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
        if self.visibility is not None:
            return self
        p = self.previous
        while p is not None:
            r = p.resolve(self)
            if r is not None:
                return r
            p = p.previous
        return self

    def __eq__(self, a):
        return (self.namespace == a.namespace and self.name == a.name)


class Renv(object):

    def __init__(self):
        self.names = {}

    def reg_name(self, name, value):
        if name in self.names:
            self.names[names].append(value)
        else:
            self.names[name] = [value]


class RContext(object):
    current_file = ['']   # implementing reentrant parses
    current_text = []     #      //         //      //
    parse = None          # shameful hack to prevent hard circular dependency.
    call_resolution = []  # implementing call stack


class Statement(Rentity):

    def __init__(self):
        Rentity.__init__(self)


class AllIndices(Rentity):

    def __str__(self):
        return "AllIndices"


allindices = AllIndices()


def extract_list(ast):
    ret = []
    on_comma = True
    print "extract_list", ast
    for a in ast:
        print "extract_list on", a
        if type(a) is tuple:
            if a[0] == 'COMMA':
                if on_comma:
                    ret.append(allindices)
                else:
                    on_comma = True
            else:
                print "extract_list on tuple", a
        else:
            on_comma = False
            ret.append(a)
    return ret