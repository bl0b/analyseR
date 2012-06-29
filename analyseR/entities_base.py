import os
import sys


R_base_names = set([u'base-package', u'abbreviate', u'abs', u'acos', u'acosh',
u'addNA', u'addTaskCallback', u'agrep', u'alist', u'all', u'all.equal',
u'all.equal.POSIXct', u'all.names', u'all.vars', u'any', u'anyDuplicated',
u'aperm', u'append', u'apply', u'args', u'array', u'arrayInd', u'as.array',
u'as.call', u'as.character', u'as.character.condition', u'as.character.Date',
u'as.character.hexmode', u'as.character.numeric_version',
u'as.character.octmode', u'as.character.POSIXt', u'as.character.srcref',
u'as.complex', u'as.data.frame', u'as.data.frame.AsIs', u'as.data.frame.Date',
u'as.data.frame.numeric_version', u'as.data.frame.POSIXct',
u'as.data.frame.table', u'as.Date', u'as.difftime', u'as.double',
u'as.double.difftime', u'as.double.POSIXlt', u'as.environment',
u'as.expression', u'as.factor', u'as.function', u'as.hexmode', u'as.integer',
u'as.list', u'as.list.Date', u'as.list.numeric_version', u'as.list.POSIXct',
u'as.logical', u'as.matrix', u'as.matrix.noquote', u'as.matrix.POSIXlt',
u'as.name', u'as.null', u'as.numeric', u'as.numeric_version', u'as.octmode',
u'as.ordered', u'as.package_version', u'as.pairlist', u'as.POSIXct',
u'as.POSIXlt', u'as.qr', u'as.raw', u'as.real', u'as.single', u'as.symbol',
u'as.table', u'as.vector', u'asin', u'asinh', u'asS3', u'asS4', u'assign',
u'assignOps', u'atan', u'atan2', u'atanh', u'atomic', u'attach',
u'attachNamespace', u'attr', u'attr.all.equal', u'attributes', u'autoload',
u'autoloader', u'backquote', u'backsolve', u'backtick', u'base', u'baseenv',
u'basename', u'bessel', u'besselI', u'besselJ', u'besselK', u'besselY',
u'beta', u'bindenv', u'bindingIsActive', u'bindingIsLocked', u'bindtextdomain',
u'body', u'bquote', u'break', u'browser', u'browserCondition',
u'browserSetDebug', u'browserText', u'builtins', u'by', u'bzfile', u'c',
u'c.Date', u'c.noquote', u'c.numeric_version', u'c.POSIXct', u'call',
u'callCC', u'capabilities', u'casefold', u'cat', u'cbind', u'cbind.data.frame',
u'ceiling', u'char.expand', u'character', u'charmatch', u'charToRaw',
u'chartr', u'check_tzones', u'chol', u'chol2inv', u'choose', u'class',
u'clipboard', u'close', u'close.srcfile', u'close.srcfilealias',
u'closeAllConnections', u'closure', u'col', u'collation', u'colMeans',
u'colnames', u'colon', u'colSums', u'commandArgs', u'comment', u'complex',
u'computeRestarts', u'condition', u'conditionCall', u'conditionCall.condition',
u'conditionMessage', u'conditionMessage.condition', u'conditions',
u'conflicts', u'connection', u'connections', u'contributors', u'copyright',
u'copyrights', u'cos', u'cosh', u'crossprod', u'cummax', u'cummin', u'cumprod',
u'cumsum', u'cut', u'cut.POSIXt', u'data.class', u'data.frame', u'data.matrix',
u'date', u'date-time', u'debug', u'debugonce', u'default.stringsAsFactors',
u'defunct', u'delayedAssign', u'deparse', u'deprecated', u'det', u'detach',
u'determinant', u'dget', u'diag', u'diff', u'difftime', u'digamma', u'dim',
u'dimnames', u'dir', u'dir.create', u'dirname', u'do.call', u'double', u'dput',
u'dQuote', u'drop', u'droplevels', u'dump', u'duplicated',
u'duplicated.numeric_version', u'duplicated.POSIXlt', u'dyn.load',
u'dyn.unload', u'eapply', u'eigen', u'else', u'emptyenv', u'enc2native',
u'enc2utf8', u'enclosure', u'encodeString', u'enquote', u'env.profile',
u'environment', u'environment variables', u'environmentIsLocked',
u'environmentName', u'eval', u'eval.parent', u'evalq', u'exists', u'exp',
u'expand.grid', u'expm1', u'expression', u'factor', u'factorial', u'fifo',
u'file', u'file.access', u'file.append', u'file.choose', u'file.copy',
u'file.create', u'file.exists', u'file.info', u'file.link', u'file.path',
u'file.remove', u'file.rename', u'file.show', u'file.symlink', u'files',
u'find.package', u'findInterval', u'findRestart', u'finite', u'floor',
u'flush', u'for', u'force', u'formals', u'format', u'format.Date',
u'format.difftime', u'format.hexmode', u'format.info', u'format.libraryIQR',
u'format.numeric_version', u'format.octmode', u'format.packageInfo',
u'format.POSIXct', u'format.pval', u'format.summaryDefault', u'formatC',
u'formatDL', u'forwardsolve', u'function', u'fuzzy matching', u'gamma', u'gc',
u'gc.time', u'gcinfo', u'gctorture', u'gctorture2', u'get',
u'getAllConnections', u'getCConverterDescriptions', u'getCConverterStatus',
u'getConnection', u'getDLLRegisteredRoutines', u'getElement', u'geterrmessage',
u'getHook', u'getLoadedDLLs', u'getNativeSymbolInfo', u'getNumCConverters',
u'getOption', u'getRversion', u'getSrcLines', u'getTaskCallbackNames',
u'gettext', u'gettextf', u'getwd', u'gl', u'globalenv', u'gregexpr', u'grep',
u'grepl', u'grepRaw', u'group generic', u'groupGeneric', u'gsub', u'gzcon',
u'gzfile', u'hexmode', u'iconv', u'iconvlist', u'icuSetCollate', u'identical',
u'identity', u'if', u'ifelse', u'in', u'inherits', u'integer', u'interaction',
u'interactive', u'internal generic', u'intersect', u'intersection',
u'intToBits', u'intToUtf8', u'inverse.rle', u'invisible', u'invokeRestart',
u'invokeRestartInteractively', u'is.array', u'is.atomic', u'is.call',
u'is.character', u'is.complex', u'is.data.frame', u'is.double', u'is.element',
u'is.environment', u'is.expression', u'is.factor', u'is.finite',
u'is.function', u'is.infinite', u'is.integer', u'is.language', u'is.list',
u'is.loaded', u'is.logical', u'is.matrix', u'is.na', u'is.na.numeric_version',
u'is.na.POSIXlt', u'is.name', u'is.nan', u'is.null', u'is.numeric',
u'is.numeric.difftime', u'is.numeric_version', u'is.object', u'is.ordered',
u'is.package_version', u'is.pairlist', u'is.primitive', u'is.qr', u'is.R',
u'is.raw', u'is.real', u'is.recursive', u'is.single', u'is.symbol',
u'is.table', u'is.unsorted', u'is.vector', u'isatty', u'isdebugged',
u'isIncomplete', u'isOpen', u'isRestart', u'isS4', u'isSeekable',
u'isSymmetric', u'isTRUE', u'jitter', u'julian', u'kappa', u'kronecker',
u'l10n_info', u'labels', u'lapply', u'last.warning', u'lbeta', u'lchoose',
u'length', u'length.POSIXlt', u'letters', u'levels', u'lfactorial', u'lgamma',
u'library', u'library.dynam', u'library.dynam.unload', u'licence', u'license',
u'list', u'list.dirs', u'list.files', u'list2env', u'load',
u'loadedNamespaces', u'loadNamespace', u'local', u'localeconv', u'locales',
u'lockBinding', u'lockEnvironment', u'log', u'log10', u'log1p', u'log2',
u'logb', u'logical', u'lower.tri', u'ls', u'make.names', u'make.unique',
u'makeActiveBinding', u'mapply', u'margin.table', u'mat.or.vec', u'match',
u'match.arg', u'match.call', u'match.fun', u'matmult', u'matrix', u'max',
u'max.col', u'mean', u'mean.Date', u'mean.difftime', u'mean.POSIXct',
u'memCompress', u'memDecompress', u'memory.profile', u'merge', u'message',
u'mget', u'min', u'missing', u'mode', u'month.abb', u'months', u'name',
u'names', u'names.POSIXlt', u'nargs', u'nchar', u'ncol', u'new.env', u'next',
u'ngettext', u'nlevels', u'noquote', u'norm', u'normalizePath', u'nrow',
u'numeric', u'numeric_version', u'nzchar', u'objects', u'octmode', u'oldClass',
u'on.exit', u'open', u'open.srcfile', u'open.srcfilealias', u'option',
u'options', u'order', u'ordered', u'outer', u'packageEvent',
u'packageStartupMessage', u'package_version', u'packBits', u'pairlist',
u'parent.env', u'parent.frame', u'parse', u'paste', u'paste0', u'path.expand',
u'path.package', u'pi', u'pipe', u'pmatch', u'pmax', u'pmax.int', u'pmin',
u'pmin.int', u'polyroot', u'pos.to.env', u'pretty', u'prettyNum', u'primitive',
u'print', u'print.AsIs', u'print.by', u'print.condition', u'print.connection',
u'print.data.frame', u'print.Date', u'print.default', u'print.difftime',
u'print.DLLInfo', u'print.hexmode', u'print.libraryIQR',
u'print.NativeRoutineList', u'print.noquote', u'print.numeric_version',
u'print.octmode', u'print.packageInfo', u'print.POSIXct', u'print.proc_time',
u'print.rle', u'print.simple.list', u'print.srcfile', u'print.srcref',
u'print.summary.table', u'print.summaryDefault', u'print.table',
u'print.warnings', u'prmatrix', u'proc.time', u'prod', u'promise', u'promises',
u'prop.table', u'psigamma', u'pushBack', u'pushBackLength', u'q', u'qr',
u'qr.coef', u'qr.default', u'qr.fitted', u'qr.Q', u'qr.qty', u'qr.qy', u'qr.R',
u'qr.resid', u'qr.solve', u'qr.X', u'quarters', u'quit', u'quote', u'range',
u'rank', u'rapply', u'raw', u'rawConnection', u'rawConnectionValue',
u'rawShift', u'rawToBits', u'rawToChar', u'rbind', u'rbind.data.frame',
u'rcond', u'read.dcf', u'readBin', u'readChar', u'readline', u'readLines',
u'readRDS', u'readRenviron', u'real', u'reg.finalizer', u'regex', u'regexec',
u'regexp', u'regexpr', u'regmatches', u'regular expression', u'remove',
u'removeCConverter', u'removeTaskCallback', u'rep', u'rep.numeric_version',
u'repeat', u'replace', u'replicate', u'require', u'requireNamespace',
u'reserved', u'restartDescription', u'restartFormals', u'retracemem',
u'return', u'rev', u'rle', u'rm', u'round', u'round.Date', u'round.POSIXt',
u'row', u'row.names', u'rowMeans', u'rownames', u'rowsum', u'rowSums',
u'sample', u'sapply', u'save', u'saveRDS', u'scale', u'scan', u'search',
u'searchpaths', u'seek', u'seq', u'seq.Date', u'seq.POSIXt', u'sequence',
u'seq_along', u'seq_len', u'serialize', u'set.seed', u'setCConverterStatus',
u'setdiff', u'setequal', u'setHook', u'setSessionTimeLimit', u'setTimeLimit',
u'setwd', u'showConnections', u'shQuote', u'sign', u'signalCondition',
u'signif', u'simpleCondition', u'simpleError', u'simpleMessage',
u'simpleWarning', u'simplify2array', u'sin', u'single', u'sinh', u'sink',
u'slice.index', u'socketConnection', u'socketSelect', u'solve', u'solve.qr',
u'sort', u'sort.list', u'source', u'split', u'split.Date', u'split.POSIXct',
u'sprintf', u'sqrt', u'sQuote', u'srcfile', u'srcfile-class', u'srcfilealias',
u'srcfilealias-class', u'srcfilecopy', u'srcfilecopy-class', u'srcref',
u'srcref-class', u'stderr', u'stdin', u'stdout', u'stop', u'stopifnot',
u'storage.mode', u'str.POSIXt', u'strftime', u'strptime', u'strsplit',
u'strtoi', u'strtrim', u'structure', u'strwrap', u'sub', u'subset',
u'substitute', u'substr', u'substring', u'sum', u'summary',
u'summary.connection', u'summary.Date', u'summary.POSIXct', u'summary.srcfile',
u'summary.srcref', u'summary.table', u'suppressMessages',
u'suppressPackageStartupMessages', u'suppressWarnings', u'svd', u'sweep',
u'switch', u'sys.on.exit', u'sys.parent', u'sys.source', u'sys.status',
u'system', u'system.file', u'system.time', u'system2', u't', u'table',
u'tabulate', u'tan', u'tanh', u'tapply', u'taskCallbackManager', u'tcrossprod',
u'tempdir', u'tempfile', u'textConnection', u'textConnectionValue', u'tilde',
u'tilde expansion', u'time interval', u'time zone', u'time zones', u'timezone',
u'tolower', u'topenv', u'toString', u'toupper', u'trace', u'traceback',
u'tracemem', u'tracingState', u'transform', u'trigamma', u'trunc',
u'trunc.Date', u'trunc.POSIXt', u'truncate', u'try', u'tryCatch', u'type',
u'typeof', u'umask', u'unclass', u'undebug', u'union', u'unique',
u'unique.numeric_version', u'unique.POSIXlt', u'units', u'units.difftime',
u'unix.time', u'unlink', u'unlist', u'unloadNamespace', u'unlockBinding',
u'unname', u'unserialize', u'unsplit', u'untrace', u'untracemem', u'unz',
u'upper.tri', u'url', u'utf8ToInt', u'vapply', u'vector', u'version',
u'warning', u'warnings', u'weekdays', u'which', u'which.max', u'which.min',
u'while', u'with', u'withCallingHandlers', u'within', u'withRestarts',
u'withVisible', u'write', u'write.dcf', u'writeBin', u'writeChar',
u'writeLines', u'xor', u'xor.hexmode', u'xor.octmode', u'xtfrm',
u'xtfrm.numeric_version', u'xzfile', u'zapsmall', u'.amatch_bounds',
u'.amatch_costs', u'.Autoloaded', u'.AutoloadEnv', u'.BaseNamespaceEnv', u'.C',
u'.Call', u'.Class', u'.colMeans', u'.colSums', u'.conflicts.OK',
u'.decode_numeric_version', u'.Defunct', u'.deparseOpts', u'.Deprecated',
u'.Device', u'.Devices', u'.doTrace', u'.dynLibs', u'.encode_numeric_version',
u'.expand_R_libs_env_var', u'.External', u'.find.package', u'.First',
u'.First.sys', u'.Fortran', u'.Generic', u'.GlobalEnv', u'.Group',
u'.handleSimpleError', u'.Internal', u'.isOpen', u'.kronecker', u'.Last',
u'.Last.lib', u'.Last.sys', u'.Last.value', u'.leap.seconds', u'.libPaths',
u'.Library', u'.Library.site', u'.Machine', u'.makeMessage',
u'.make_numeric_version', u'.Method', u'.noGenerics', u'.NotYetImplemented',
u'.NotYetUsed', u'.onAttach', u'.onLoad', u'.onUnload', u'.Options',
u'.OptRequireMethods', u'.packages', u'.packageStartupMessage',
u'.path.package', u'.Platform', u'.Primitive', u'.Random.seed', u'.Renviron',
u'.rowMeans', u'.rowSums', u'.Rprofile', u'.S3PrimitiveGenerics',
u'.signalSimpleWarning', u'.standard_regexps', u'.Traceback', u'.userHooksEnv',
u'.__H__.cbind', u'.__H__.rbind',
u'read.table', u'read.csv', u'write.table', u'write.csv',
])


def strip_common_path(*ents):
    i = -1
    paths = zip(*[e.get_path() for e in ents])
    for p in paths:
        if reduce(lambda a, b: a is b and a or None, p) is not None:
            i += 1
        else:
            break
    return paths[i][0]


def find_closest_common_parent(patha, pathb):
    return reduce(lambda a, (pa, pb): pa == pb and pa or a,
                  izip(patha, pathb))


#_entrail_get = lambda e: lambda self: getattr(self, '_' + e)


class NotWanted(Exception):
    pass


class Path(object):

    def __init__(self, ev, it, pr=lambda e: True):
        self.x = {'e': ev, 'i': it, 'p': pr}

    def __call__(self, **kw):
        check = lambda e, k, v: hasattr(e, k) and v(getattr(e, k))
        pred = lambda e: (self.x['p'](e)
                          and reduce(lambda a, b: a and check(e, *b),
                                     kw.iteritems(),
                                     True))
        return Path(self.x['e'], self.x['i'], pred)

    def search(self, ent):
        i = self.x['i']
        e = self.x['e']
        p = self.x['p']
        try:
            for x in i(ent):
                if p(x):
                    yield e(x)
        except NotWanted:
            pass
        #return (e(x) for x in i(ent) if p(x))

    def __getattr__(pa, attr):
        return Path(lambda ent: getattr(pa.x['e'](ent), attr),
                    pa.x['i'],
                    lambda ent: pa.x['p'](ent) and hasattr(ent, attr))

    def __getitem__(pa, idx):
        return Path(lambda ent: pa.x['e'](ent)[idx],
                    pa.x['i'],
                    lambda ent: pa.x['p'](ent) and hasattr(ent, '__getitem__'))

    def __or__(pa, pb):
        return Path(lambda ent: pa.x['p'](ent)
                                and pa.x['e'](ent)
                                or pb.x['e'](ent),
                    lambda ent: chain(pa.x['i'](ent), pb.x['i'](ent)),
                                # this chaining may be awful.
                    lambda ent: pa.x['p'](ent) or pb.x['p'](ent))

    def __div__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for x in pa.search(ent)
                                 for r in x.children(pb.x['p'])))

    def __floordiv__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for x in pa.search(ent)
                                 for r in x.deep(pb.x['p'])))

    def __sub__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: ent.before(pb.x['p']))

    def __mul__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: ent.parent and pb.x['p'](ent.parent)
                                and (ent.parent,)
                                or tuple())

    def __pow__(pa, pb):
        return Path(pb.x['e'],
                    lambda ent: ent.above(pb.x['p']))

    def __rdiv__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: pa.children(pb.x['p'])).search(pa)

    def __rfloordiv__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: (r
                                 for r in pa.deep(pb.x['p']))).search(pa)

    def __rsub__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: ent.before(pb.x['p'])).search(pa)

    def __rmul__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: ent.parent and pb.x['p'](ent.parent)
                                and (ent.parent,)
                                or tuple()).search(pa)

    def __rpow__(pb, pa):
        return Path(pb.x['e'],
                    lambda ent: ent.above(pb.x['p'])).search(pa)

    def __neg__(pa):
        p = pa.x['p']

        def _p(ent):
            if p(ent):
                raise NotWanted()
            return True
        return Path(pa.x['e'],
                    pa.x['i'],
                    _p)


def _entrail_get(e):
    ename = e
    e = '_' + e

    def _(self):
        x = getattr(self, e)
#        if isinstance(x, tuple):
#            return RProxyTuple(ename, x)
#        elif isinstance(x, list):
#            return RProxyList(ename, x)
        return x

    return _


def _entrail_set(e):
    e = '_' + e

    def _(self, v):
        if type(v) in (list, tuple):
            for x in v:
                if isinstance(x, Rentity):
                    x.set_parent(self)
        elif isinstance(v, Rentity):
            v.set_parent(self)
        setattr(self, e, v)
        #print "set entrail", e, v, getattr(self, '_' + e)
        return v

    return _


class Rentrail(property, Path):

    def __init__(self, cls, name):
        property.__init__(self, _entrail_get(name), _entrail_set(name))
        Path.__init__(self,
                      lambda ent: getattr(ent, name),
                      lambda ent: (ent,),
                      lambda ent: isinstance(ent, cls) and hasattr(ent, name))
        #self.owner = None
        self.name = name
        self.cls = cls

    #def before(self):
    #    p = self.owner.previous
    #    while p:
    #        yield p
    #        p = p.previous

    #def above(self):
    #    p = self.owner.parent
    #    while p:
    #        yield p
    #        p = p.parent

    def children(self, pred):
        return (x for x in self if pred(x))

    def deep(self, pred):
        return (x
                for c in self
                for x in c.search_iter(pred)
                if isinstance(c, Rentity))

    def _expr(self, x):
        return getattr(x, self.name)

    def _validate(self, x):
        return type(x) is self.cls


___indent = 0


def call_dumper(cls, name):
    m = getattr(cls, name)

    def _ret(*a, **kw):
        global ___indent
        print >> sys.stderr, "%sCalling %s.%s" % (' ' * ___indent,
                                                  cls.__name__, name), a, kw
        ___indent += 2
        ret = m(*a, **kw)
        ___indent -= 2
        print >> sys.stderr, "%s=>" % (' ' * ___indent), ret
        return ret
    _ret.__name__ = name
    return _ret


__shield = set()


def shield(iterable):
    global __shield
    __shield.update(id(x) for x in iterable)


def shield_against_return_self(f):

    def _f(self, *a, **kw):
        ret = f(self, *a, **kw)
        if ret is self:
            print type(self).__name__, f.__name__, "returns self !"
            raise Exception("{return self} not allowed !")
        if id(ret) in __shield:
            print type(self).__name__, f.__name__, "returns shielded entity !"
            raise Exception("{return shielded} not allowed !")
        return ret
    _f.__name__ = f.__name__
    return _f


class RentityMeta(type, Path):
    registry = {}

    def __init__(cls, name, bases, dic):
        Path.__init__(cls,
                      lambda e: e,
                      lambda e: (e,),
                      lambda e: isinstance(e, cls))
        RentityMeta.registry[name.lower()] = cls
        for e in cls.entrails:
            setattr(cls, e, Rentrail(cls, e))
        setattr(cls, 'eval_to', call_dumper(cls, "eval_to"))
        setattr(cls, 'resolve', call_dumper(cls, "resolve"))
        setattr(cls, 'eval_to', shield_against_return_self(cls.eval_to))
        setattr(cls, 'resolve', shield_against_return_self(cls.resolve))

    def _expr(self, x):
        return x

    def _validate(self, x):
        return type(x) is self


def __path_str(p):
    if len(p) == 0:
        return ['']
    if len(p) == 1:
        return [type(p[0]).__name__, '(', p[0].pp(), ')']
    parent = p[0]
    child = p[1]
    ret = [type(parent).__name__]
    for ent in parent.entrails:
        e = getattr(parent, ent)
        if e is child:
            ret.append('.')
            ret.append(ent)
        elif type(e) in (list, tuple):
            try:
                i = e.index(child)
                ret.append('.')
                ret.append(ent)
                ret.append('[')
                ret.append(str(i))
                ret.append(']')
            except:
                pass
    ret.append('.')
    ret.extend(path_str(p[1:]))
    return ret


def path_str(p):
    return ''.join(__path_str(p))


locked_parents = False


class Rentity(object):
    __metaclass__ = RentityMeta
    entrails = []

    def __set_p(self, p):
        if locked_parents:
            raise Exception("Read-only parent !")
        self.__p = p

    def __get_p(self):
        return self.__p

    parent = property(__get_p, __set_p)

    def __new__(cls, *a, **kw):
        if kw and not a:
            return Path.__call__(cls, **kw)
        return object.__new__(cls)

    def __eq__(self, a):
        return False

    def __init__(self, ast):
        self.ast = ast
        for e in self.entrails:
            setattr(self, '_' + e, None)
            #getattr(self, e).owner = self
        self.filename = RContext.current_file[-1]
        self.parent = None
        self.previous = None
        #for e in self.entrails:
        #    setattr(self, e, None)

    def copy(self):
        ret = type(self)(map(lambda x: isinstance(x, Rentity)
                                       and x.copy()
                                       or x, self.ast))
        ret.previous = self.previous
        ret.parent = self.parent
        return ret

    def set_parent(self, p):
        self.parent = p

    def eval_name(self, n):
        return None

    def __repr__(self):
        if type(self).__str__ is object.__str__:
            return object.__repr__(self)
        return str(self)

    def search_iter(self, predicate, forbid=[]):
        if type(self) in forbid:
            return
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
                    for result in k.search_iter(predicate, forbid):
                        yield result
            elif isinstance(x, Rentity):
                for result in x.search_iter(predicate, forbid):
                    yield result

    def children(self, pred):
        return (x
                for e in self.entrails
                for ent in (getattr(self, e),)
                for x in (isinstance(ent, Rentity) and (ent,) or ent)
                if pred(x))

    def deep(self, pred):
        return (self.search_iter(pred))

    def before(self, pred):
        p = self.previous
        while p:
            if pred(p):
                yield p
            p = p.previous

    def above(self, pred):
        p = self.parent
        while p:
            if pred(p):
                yield p
            p = p.parent

    def get_filename(self):
        if hasattr(self, 'filename'):
            return self.filename
        elif self.parent:
            return self.parent.get_filename()

    def eval_to(self):
        return self.copy()

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
            #print self, "has names and has", name, self.names[name]
            return self.names[name][-1].eval_to().copy()
        return None

    def pp(self):
        return '<entity ' + str(self) + '>'

    def __iter__(self):
        for x in self.entrails:
            e = getattr(self, x)
            if isinstance(e, Rentity):
                yield e
            for k in e:
                yield k

#    def __div__(self, what):
#        return [x
#                for c in self.children(lambda x: True)
#                for x in what.search(c)]

#    def __floordiv__(self, what):
#        return [x for c in self.deep(lambda x: True) for x in what.search(c)]

#    def __sub__(self, what):
#        return [x
#                for c in self.before(lambda x: True)
#                for x in what.search(c)]

#    def __mul__(self, what):
#        return self.parent and [x for x in what.search(self.parent)] or []

#    def __pow__(self, what):
#        return [x for p in self.above(lambda x: True) for x in what.search(p)]


Any = Path(lambda e: e, lambda e: (e,), lambda e: True)


class RProxy(Rentity):

    def __init__(self, name):
        Rentity.__init__(self, ast)
        self._name = name


class RProxyList(list, RProxy):

    def __init__(self, name, l):
        list.__init__(self, l)
        RProxy.__init__(self, name)


class RProxyTuple(tuple, RProxy):

    def __new__(cls, name, t):
        return tuple.__new__(cls, t)

    def __init__(self, name, t):
        tuple.__init__(self)
        RProxy.__init__(self, name)


class Renv(object):

    def __init__(self):
        self.names = {}

    def reg_name(self, name, value):
        if name in self.names:
            self.names[name].append(value)
        else:
            self.names[name] = [value]

    def resolve(self, name):
        #print "resolution of", name, "in", self.names
        if name in self.names:
            return self.names[name][-1].copy()
        return None


class RContext(object):
    current_file = ['']             # implementing reentrant parses
    current_text = ['']             # //   //         //      //
    current_dir = [os.getcwd()]     # //   //         //      //
    parse = None                    # shameful hack to prevent hard
                                    # circular dependency.
    call_resolution = []            # implementing call stack


class Statement(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self, ast)


class AllIndices(Rentity):

    def __str__(self):
        return "AllIndices"


def wrap_previous(get_target):

    def _set(s, v):
        try:
            t = get_target(s)
            if t is not None:
                t.previous = v
        except:
            pass

    def _get(s):
        try:
            t = get_target(s)
            return t and t.previous
        except:
            return None

    return property(_get, _set)


def extract_list(ast):
    ret = []
    on_comma = True
    #print "extract_list", ast
    for a in ast:
        #print "extract_list on", a
        if type(a) is tuple:
            if a[0] == 'COMMA':
                if on_comma:
                    ret.append(AllIndices(tuple()))
                else:
                    on_comma = True
            #else:
            #    print "extract_list on tuple", a
        else:
            on_comma = False
            ret.append(a)
    return ret


def chain_ifelse(ifelse, smthg):
    ret = ifelse
    while type(ifelse) is IfElse and ifelse.els_:
        ifelse = ifelse.els_
    if type(ifelse) is IfElse:
        ifelse.els_ = smthg
    return ret


class Name(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        if isinstance(ast, str):
            self.name = ast
            self.visibility = None
            self.namespace = None
        elif len(ast) == 4:
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
        if self.visibility is not None or self.name in R_base_names:
            print "routine from external package or R base:: package.",
            print self.pp()
            return self.copy()
        pathass = Assign(lhs=lambda x: type(x) is Name and x == self)
        # discard None's
        defs = filter(lambda x: x is not None,
                      (x.resolve(self)
                       for x in self - (pathass | If // pathass)
                       if x))
        # retain all IfElse's and only one previous eval (possible final else).
        defs = reduce(lambda accum, d:
                      accum[0] and (type(d) is IfElse, accum[1] + [d])
                                or accum,
                      defs,
                      (True, []))[1]
        # now chain if's as much as can do
        #print "defs", defs
        if len(defs) > 1:
            #print "tmp", reduce(chain_ifelse, defs)
            #return strip_common_path(*defs)
            return reduce(chain_ifelse, defs)
        if len(defs) == 0 or defs[0] is None:
            return self.copy()
        return defs[0]

    def resolve(self, n):
        if self is n:
            return self.copy()
        return None

    def __eq__(self, a):
        if type(a) is type(self):
            return (self.namespace == a.namespace and self.name == a.name)
        else:
            return False

    def __hash__(self):
        return hash(self.namespace) + hash(self.name)

    def pp(self):
        if self.visibility:
            return ''.join((self.namespace, self.visibility, self.name))
        return self.name


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
        Statement.__init__(self, ast)
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

    def ppop(self):
        return {'LEFT_ARROW': '<-',
                'RIGHT_ARROW': '->',
                'LEFT_ARROW2': '<<-',
                'RIGHT_ARROW2': '->>',
                'EQUAL': '='}[self.assign]

    def pp(self):
        return self.lhs.pp() + ' ' + self.ppop() + ' ' + self.rhs.pp()


class If(Statement):
    entrails = ['condition', 'then', 'els_']

    def __get_previous(self):
        return self.condition and self.condition.previous

    def __set_previous(self, p):
        if self.condition:
            self.condition.previous = p

    #previous = property(__get_previous, __set_previous)
    previous = wrap_previous(lambda s: s.condition)

    def __init__(self, ast):
        Statement.__init__(self, ast)
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
                    return IfElse(self, cond.expression,
                                  els_, None)
                else:
                    return IfElse(self, Negation(cond),
                                  els_, None)
            return IfElse(self, cond, then, els_)

    def eval_to(self):
        cond = self.condition.eval_to()
        #print "[eval_to] If eval cond to", cond
        if isinstance(cond, Immed):
            if cond.value():
                return self.then.eval_to()
            elif self.els_:
                return self.els_.eval_to()
        else:
            return IfElse(self, cond,
                          self.then.eval_to(),
                          self.els_ and self.els_.eval_to())


class IfElse(If):

    def __init__(self, ref, cond, then, els_):
        #print "IfElse", prev, cond, then, els_
        if isinstance(cond, bool):
            raise Exception()
        #print "cond", cond
        #print "then", then
        #print "els_", els_
        If.__init__(self, (None, None, None, cond,
                           None, then, None, els_))
        self.previous = ref.previous
        self.parent = ref.parent

    def copy(self):
        return IfElse(self,
                      self.condition.copy(),
                      self.then.copy(),
                      self.els_ and self.els_.copy())


class Immed(Rentity):

    def __init__(self, ast):
        Rentity.__init__(self, ast)
        if (isinstance(ast, int)
                or isinstance(ast, float)
                or isinstance(ast, long)):
            self.typ = 'NUM'
            self.val = str(ast)
        elif isinstance(ast, str):
            self.typ = 'STRING'
            self.val = ast
        else:
            self.typ = ast[1][0]
            self.val = ast[1][1]

    def __str__(self):
        return str(self.typ) + '(' + str(self.val) + ')'

    def value(self):
        if self.typ == "STRING":
            return self.val[1:-1]  # strip quotes
        elif self.typ == "NUM":
            return float(self.val)

    def pp(self):
        return self.val
