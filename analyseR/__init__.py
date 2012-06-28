from parseR import parse
from entities import *
from call_graph import *


def __check(e, r):
    if e.parent is not r:
        print "BAD PARENT", e.parent, "EXPECTED",
        print r, "IN", path_str(e.get_path())
    if e.previous is None:
        pstr = path_str(e.get_path())
        #if not ('Function.params' in pstr
        #        or pstr.startswith('Script.statements[0].')):
        print e.previous, pstr
    check(e)


def check(r):
    if r is None:
        return
    for ent in r.entrails:
        e = getattr(r, ent)
        if isinstance(e, Rentity):
            __check(e, r)
        elif type(e) in (list, tuple):
            for k in e:
                __check(k, r)
