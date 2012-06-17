__all__ = ['cpp_scanner']
from jupyLR import Scanner
from itertools import imap

int_suffix = "(?:L|LL|U|UL|ULL)?"
int_hex = "0x[a-fA-F0-9]+" + int_suffix

num1 = r"[0-9]+(?:[.][0-9]*)?"
num2 = r"[.][0-9]+"
expo = r"(?:[eE]-?[0-9]+\.?[0-9]*)?[uUlLdf]*"
number = '(?:(?:' + num1 + '|' + num2 + ')' + expo + '|' + int_hex + ')'

keywords = [
    'repeat', 'while', 'for', 'if', 'else', 'source', 'return', 'function',
    'in',
]


def kw_to_dic(kw):
    raw_kw = kw
    if kw.startswith('__'):
        kw = kw[2:]
    if kw.endswith('__'):
        kw = kw[:-2]
    return kw.upper(), raw_kw

kw_dic = {}

for kw in keywords:
    name, value = kw_to_dic(kw)
    if name in kw_dic:
        kw_dic[name] += '|'
    else:
        kw_dic[name] = ''
    kw_dic[name] += value

for k, v in kw_dic.iteritems():
    if '|' in v:
        kw_dic[k] = r'\b(?:%s)\b' % v
    else:
        kw_dic[k] = r'\b' + v + r'\b'


misc = dict(PLUS='+', MINUS='-', STAR='*', SLASH='/',
            INF='<', SUP='>',
            AMPERSAND='&', PIPE='|', TILDE='~', CIRCONFLEX='^',
            EXCLAMATION='!',
            SHL='<<', SHR='>>',
            LE='<=', GE='>=', EQ='==', NE='!=',
            LOG_AND="&&", LOG_OR="||",
            COMMA=',',
            EQUAL='=',
            COLON=':',
            SCOPE='::',
            HIDDEN_SCOPE=':::',
            SEMICOLON=';',
            DOLLAR='$',
            OPEN_PAR='(',
            CLOSE_PAR=')',
            OPEN_CURLY='{',
            CLOSE_CURLY='}',
            PERCENT='%',
            OPEN_SQ='[',
            CLOSE_SQ=']',
            #ELLIPSIS='...',
            RIGHT_ARROW='->',
            RIGHT_ARROW2='->>',
            LEFT_ARROW='<-',
            LEFT_ARROW2='<<-',
            QUESTION='?',
           )

one_char = dict((k, v) for k, v in misc.iteritems() if len(v) == 1)
two_char = dict((k, v) for k, v in misc.iteritems() if len(v) == 2)
three_char = dict((k, v) for k, v in misc.iteritems() if len(v) == 3)


def escape(c):
    return c == '^' and r'\^' or c


for k, op in one_char.iteritems():
    #asserts = filter_asserts(op, two_char)
    #asserts += filter_asserts(op, three_char)
    #tokens[k] = mk_op_re(op, asserts)
    one_char[k] = '[%s]' % ']['.join(imap(escape, op))

for k, op in two_char.iteritems():
    #tokens[k] = mk_op_re(op, filter_asserts(op, three_char))
    two_char[k] = '[%s]' % ']['.join(imap(escape, op))

for k, op in three_char.iteritems():
    #tokens[k] = mk_op_re(op, filter_asserts(op, three_char))
    three_char[k] = '[%s]' % ']['.join(imap(escape, op))

#tokens.update(three_char)

#tokens['number'] = number
#tokens['symbol'] = symbol_assert + r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'

discard_them_all = ['WS', 'comment']

r_scanner = (Scanner(**kw_dic)
                #.add(NEWLINE="[\n]")
                .add(**three_char)
                .add(**two_char)
                .add(**one_char)
                .add(SYM=r'\b[.a-zA-Z_][.a-zA-Z0-9_]*\b')
                .add(NUM=number)
                .add(STRING=r'L?"(?:\\["bntr]|[^\\"])*"')
                .add(CHAR=r"L?'(?:\\['bntr\\]|[^\\'])'")
                #.add(WS='[ \t]+')
                .add(WS='[ \t\r\n]+')
                .add(comment='[#][^\n]*')
                .add(discard_names=discard_them_all))
