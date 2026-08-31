"""G1 LISPY basis.

  V ::= x | nil | (q S) | (head V) | (tail V) | (self V) | (cons V V) | (if B V V)
  B ::= true | false | (atom V) | (null V) | (not B) | (eq V V)

A program is a Val. Artifacts and transforms are the same objects run by the same
evaluator: E(artifact, input) and E(transform, artifact) differ only in what is
passed as x.
"""
from .core import is_list

NAME = "G1_LISPY"

SYMS = ("a", "b", "c", "d", "x", "nil", "true", "false", "q",
        "head", "tail", "self", "cons", "if", "atom", "null", "not", "eq")

V_TERMS = ["x", "nil"] + [("q", s) for s in SYMS]     # 20
B_TERMS = ["true", "false"]                            # 2

V_FORMS = ["head", "tail", "self", "cons", "if"]
B_FORMS = ["atom", "null", "not", "eq"]

ARITY = {"head": 1, "tail": 1, "self": 1, "cons": 2, "if": 3,
         "atom": 1, "null": 1, "not": 1, "eq": 2, "q": 1}


# ------------------------------------------------------------------ size

def size(t):
    """Grammar-production count (the enumeration's own length measure)."""
    if type(t) is str:
        return 1
    if t[0] == "q":
        return 1
    return 1 + sum(size(u) for u in t[1:])


# ------------------------------------------------------------ validation

def valid_V(t):
    if type(t) is str:
        return t in ("x", "nil")
    if type(t) is not tuple or not t:
        return False
    h = t[0]
    if type(h) is not str:
        return False
    if h == "q":
        return len(t) == 2 and type(t[1]) is str and t[1] in SYMS
    if h in ("head", "tail", "self"):
        return len(t) == 2 and valid_V(t[1])
    if h == "cons":
        return len(t) == 3 and valid_V(t[1]) and valid_V(t[2])
    if h == "if":
        return len(t) == 4 and valid_B(t[1]) and valid_V(t[2]) and valid_V(t[3])
    return False


def valid_B(t):
    if type(t) is str:
        return t in ("true", "false")
    if type(t) is not tuple or not t:
        return False
    h = t[0]
    if h in ("atom", "null"):
        return len(t) == 2 and valid_V(t[1])
    if h == "not":
        return len(t) == 2 and valid_B(t[1])
    if h == "eq":
        return len(t) == 3 and valid_V(t[1]) and valid_V(t[2])
    return False


# ------------------------------------------------------------- evaluator

class Err(Exception):
    __slots__ = ("kind", "path", "step", "depth")

    def __init__(self, kind, step, depth):
        self.kind = kind
        self.step = step
        self.depth = depth
        self.path = []


def run(prog, xval, limit=4000, dmax=24, trace=False):
    """Deterministic, total-under-budget. Returns ('ok', val) or ('err', kind).

    trace=True additionally returns executable failure geometry with no semantic
    labels: (kind, node path, step index, recursion depth).
    """
    ctr = [0]

    def ev(t, xv, dep):
        c = ctr[0] + 1
        ctr[0] = c
        if c > limit:
            raise Err("budget", c, dep)
        if type(t) is str:
            if t == "x":
                return xv
            if t == "nil":
                return ()
            if t == "true":
                return True
            return False                      # 'false'
        h = t[0]
        if h == "q":
            return t[1]
        if h == "cons":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            try:
                b = ev(t[2], xv, dep)
            except Err as e:
                e.path.append(2); raise
            if type(b) is not tuple:
                raise Err("cons_atom", ctr[0], dep)
            return (a,) + b
        if h == "head":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            if type(a) is not tuple:
                raise Err("head_atom", ctr[0], dep)
            if not a:
                raise Err("head_nil", ctr[0], dep)
            return a[0]
        if h == "tail":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            if type(a) is not tuple:
                raise Err("tail_atom", ctr[0], dep)
            if not a:
                raise Err("tail_nil", ctr[0], dep)
            return a[1:]
        if h == "if":
            try:
                c0 = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            k = 2 if c0 else 3
            try:
                return ev(t[k], xv, dep)
            except Err as e:
                e.path.append(k); raise
        if h == "self":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            if dep + 1 > dmax:
                raise Err("depth", ctr[0], dep)
            return ev(prog, a, dep + 1)
        if h == "atom":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            return type(a) is str
        if h == "null":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            return a == ()
        if h == "not":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            return not a
        if h == "eq":
            try:
                a = ev(t[1], xv, dep)
            except Err as e:
                e.path.append(1); raise
            try:
                b = ev(t[2], xv, dep)
            except Err as e:
                e.path.append(2); raise
            return a == b
        raise Err("malformed", ctr[0], dep)

    try:
        v = ev(prog, xval, 0)
    except Err as e:
        if trace:
            return ("err", e.kind, tuple(reversed(e.path)), e.step, e.depth, ctr[0])
        return ("err", e.kind)
    except RecursionError:
        if trace:
            return ("err", "hostdepth", (), ctr[0], -1, ctr[0])
        return ("err", "hostdepth")
    if trace:
        return ("ok", v, (), ctr[0], 0, ctr[0])
    return ("ok", v)


def steps_of(prog, xval, limit=4000, dmax=24):
    r = run(prog, xval, limit, dmax, trace=True)
    return r[5]


def apply_transform(t, term, limit=4000, dmax=24):
    """Meta use. Returns ('ok', prog') | ('invalid', val) | ('err', kind)."""
    r = run(t, term, limit, dmax)
    if r[0] == "err":
        return ("err", r[1])
    v = r[1]
    if type(v) is bool:
        return ("invalid", v)
    if valid_V(v):
        return ("ok", v)
    return ("invalid", v)


# ------------------------------------------------------------ enumeration

class Enum:
    """Size-major typed enumeration under an explicit token/form ordering.

    Ordering is a first-class experimental variable (see PREREG-CENSUS CG-F):
    an ordering is a permutation of the terminal lists and of the form lists.
    Minimal SIZE is invariant under ordering by construction; RANK is not.
    """

    def __init__(self, vterm_perm=None, bterm_perm=None,
                 vform_perm=None, bform_perm=None, store_max=5):
        self.vterms = [V_TERMS[i] for i in (vterm_perm or range(len(V_TERMS)))]
        self.bterms = [B_TERMS[i] for i in (bterm_perm or range(len(B_TERMS)))]
        self.vforms = [V_FORMS[i] for i in (vform_perm or range(len(V_FORMS)))]
        self.bforms = [B_FORMS[i] for i in (bform_perm or range(len(B_FORMS)))]
        self.store_max = store_max
        self.V = {1: list(self.vterms)}
        self.B = {1: list(self.bterms)}
        for n in range(2, store_max + 1):
            self.V[n] = list(self._gen_V(n))
            self.B[n] = list(self._gen_B(n))

    def _gen_V(self, n):
        V, B = self.V, self.B
        for f in self.vforms:
            if f in ("head", "tail", "self"):
                for a in V[n - 1]:
                    yield (f, a)
            elif f == "cons":
                for i in range(1, n - 1):
                    j = n - 1 - i
                    if j < 1:
                        continue
                    for a in V[i]:
                        for b in V[j]:
                            yield ("cons", a, b)
            elif f == "if":
                for i in range(1, n - 2):
                    for j in range(1, n - 1 - i):
                        k = n - 1 - i - j
                        if k < 1:
                            continue
                        for c in B[i]:
                            for a in V[j]:
                                for b in V[k]:
                                    yield ("if", c, a, b)

    def _gen_B(self, n):
        V, B = self.V, self.B
        for f in self.bforms:
            if f in ("atom", "null"):
                for a in V[n - 1]:
                    yield (f, a)
            elif f == "not":
                for a in B[n - 1]:
                    yield ("not", a)
            elif f == "eq":
                for i in range(1, n - 1):
                    j = n - 1 - i
                    if j < 1:
                        continue
                    for a in V[i]:
                        for b in V[j]:
                            yield ("eq", a, b)

    def gen(self, n):
        if n in self.V:
            return iter(self.V[n])
        return self._gen_V(n)

    def stream(self, nmax):
        """Canonical stream: size-major, then ordering-major. Yields (rank, term)."""
        r = 0
        for n in range(1, nmax + 1):
            for t in self.gen(n):
                yield r, t
                r += 1


valid_transform = valid_V


def raw_apply(t, term, limit=4000, dmax=24):
    """Meta application WITHOUT object-language validation (used by ST1)."""
    r = run(t, term, limit, dmax)
    return r
