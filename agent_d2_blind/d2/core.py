"""D-2 core: values, terms, hashing, structural predicates.

Val ::= Sym(str) | List(tuple of Val)
A program IS a Val. There is no separate AST type anywhere in this system.
"""
import hashlib

# ---------------------------------------------------------------- values

def is_sym(v):
    return type(v) is str

def is_list(v):
    return type(v) is tuple


def ser(v):
    """Canonical serialisation of a Val (used only for hashing / ledgers)."""
    if type(v) is str:
        return v
    return "(" + " ".join(ser(u) for u in v) + ")"


def vhash(v):
    return hashlib.sha1(ser(v).encode()).hexdigest()[:16]


def hash_many(items):
    h = hashlib.sha1()
    for it in items:
        h.update(str(it).encode())
        h.update(b"\x00")
    return h.hexdigest()[:16]


# ------------------------------------------------- structural predicates
# These are used ONLY by the human-side census classifiers. No learner ever
# sees them.

def nodes(v):
    """Val-node count."""
    if type(v) is str:
        return 1
    return 1 + sum(nodes(u) for u in v)


def subterms(v):
    yield v
    if type(v) is tuple:
        for u in v:
            yield from subterms(u)


def contains(o, p):
    """p occurs as a subterm of o."""
    if o == p:
        return True
    if type(o) is tuple:
        for u in o:
            if contains(u, p):
                return True
    return False


def count_occ(o, p):
    n = 1 if o == p else 0
    if type(o) is tuple:
        for u in o:
            n += count_occ(u, p)
    return n


def proper_subterm(o, p):
    """o is a proper subterm of p."""
    if o == p:
        return False
    return contains(p, o)


def skeleton(v):
    """Tree shape with all symbols erased."""
    if type(v) is str:
        return "*"
    return tuple(skeleton(u) for u in v)


def leaves(v):
    if type(v) is str:
        return [v]
    out = []
    for u in v:
        out.extend(leaves(u))
    return out


def depth(v):
    if type(v) is str:
        return 0
    if not v:
        return 1
    return 1 + max(depth(u) for u in v)
