"""Register machine with reversible primitives, counted ERASE/EXPORT, and a backward-run certificate.

Every trace entry stores the op and its operand NAMES / env positions / the function, never the
value it wrote, so the inverse must be recomputed from the register file and the environment at
that point (a genuine check). ERASE has no inverse: a backward run that meets one fails.
Control flow in the backward run follows the recorded op sequence (disclosed in AMENDMENTS_P2 A5).
"""


class Irreversible(Exception):
    pass


class RM:
    def __init__(self, env):
        self.env = env  # 1-indexed symbol array (harness copy of the environment's past)
        self.v = {}
        self.w = {}
        self.stack = []  # agent-held garbage/history stack: (value, width)
        self.stack_bits = 0
        self.exp = []  # export tape (outside the agent)
        self.exp_bits = 0
        self.trace = []
        self.ops = 0
        self.reads = 0
        self.erased = 0
        self.reg_bits = 0
        self.peak = 0

    # ----- bookkeeping -----
    def _peak(self):
        b = self.reg_bits + self.stack_bits
        if b > self.peak:
            self.peak = b

    def bits(self):
        return self.reg_bits + self.stack_bits

    def alloc(self, n, w):
        assert n not in self.v, n
        self.v[n] = 0
        self.w[n] = w
        self.reg_bits += w
        self._peak()
        self.trace.append(("alloc", n, w))

    def free(self, n):
        assert self.v[n] == 0, (n, self.v[n])
        self.reg_bits -= self.w[n]
        del self.v[n]
        del self.w[n]
        self.trace.append(("free", n))

    def charge(self, ops, reads=0):
        """Ops of a sub-computation that computes and uncomputes a value inside one step, with no
        net effect on the register file (e.g. a synchronisation scan). Counted, not traced."""
        self.ops += ops
        self.reads += reads

    # ----- reversible primitives -----
    def xc(self, n, c):
        self.v[n] ^= c
        self.ops += 1
        self.trace.append(("xc", n, c))

    def xr(self, d, s):
        assert d != s
        self.v[d] ^= self.v[s]
        self.ops += 1
        self.trace.append(("xr", d, s))

    def tab(self, d, fn, srcs=(), envpos=(), cost=1):
        """v[d] ^= fn(*regs, *env symbols). Bijective because d is not a source."""
        assert d not in srcs
        val = fn(*([self.v[s] for s in srcs] + [int(self.env[p]) for p in envpos]))
        self.v[d] ^= val
        self.ops += cost
        self.reads += len(envpos)
        self.trace.append(("tab", d, fn, tuple(srcs), tuple(envpos), cost))

    def perm(self, r, P, keysrc=None, envpos=None, Pinv=None):
        key = self.v[keysrc] if keysrc is not None else int(self.env[envpos])
        self.v[r] = P[key][self.v[r]]
        self.ops += 1
        if envpos is not None:
            self.reads += 1
        self.trace.append(("perm", r, P, Pinv, keysrc, envpos))

    def swap(self, a, b):
        self.v[a], self.v[b] = self.v[b], self.v[a]
        assert self.w[a] == self.w[b]
        self.ops += 1
        self.trace.append(("swap", a, b))

    def push(self, r):
        self.stack.append((self.v[r], self.w[r]))
        self.stack_bits += self.w[r]
        self.v[r] = 0
        self.ops += 1
        self._peak()
        self.trace.append(("push", r))

    def export(self, r):
        self.exp.append(self.v[r])
        self.exp_bits += self.w[r]
        self.v[r] = 0
        self.ops += 1
        self.trace.append(("export", r))

    def deliver(self, r, t):
        """W = 0 transfer: the environment moves x_t into a zero register and keeps no copy."""
        assert self.v[r] == 0
        self.v[r] ^= int(self.env[t])
        self.ops += 1
        self.trace.append(("deliver", r, t))

    # ----- irreversible primitive -----
    def erase(self, r):
        self.erased += self.w[r]
        self.v[r] = 0
        self.ops += 1
        self.trace.append(("erase", r))

    def erase_bit(self, r, k):
        self.erased += 1
        self.v[r] &= ~(1 << k)
        self.ops += 1
        self.trace.append(("erase", r))

    # ----- certificate -----
    def backward_certificate(self):
        """Undo the trace from the final state. True iff every register is freed at the end, the
        stack and export tape are empty, and no ERASE was met. The initial register file is empty."""
        v = dict(self.v)
        w = dict(self.w)
        stack = list(self.stack)
        exp = list(self.exp)
        env = self.env
        try:
            for op in reversed(self.trace):
                k = op[0]
                if k == "alloc":
                    n = op[1]
                    if v.get(n, None) != 0:
                        return False
                    del v[n]
                    del w[n]
                elif k == "free":
                    # re-create the zero register; width recovered from the alloc (not needed for check)
                    v[op[1]] = 0
                    w[op[1]] = None
                elif k == "xc":
                    v[op[1]] ^= op[2]
                elif k == "xr":
                    v[op[1]] ^= v[op[2]]
                elif k == "tab":
                    _, d, fn, srcs, envpos, _c = op
                    v[d] ^= fn(*([v[s] for s in srcs] + [int(env[p]) for p in envpos]))
                elif k == "perm":
                    _, r, P, Pinv, keysrc, envpos = op
                    key = v[keysrc] if keysrc is not None else int(env[envpos])
                    v[r] = Pinv[key][v[r]]
                elif k == "swap":
                    v[op[1]], v[op[2]] = v[op[2]], v[op[1]]
                elif k == "push":
                    if v[op[1]] != 0:
                        return False
                    val, _w = stack.pop()
                    v[op[1]] = val
                elif k == "export":
                    if v[op[1]] != 0:
                        return False
                    v[op[1]] = exp.pop()
                elif k == "deliver":
                    _, r, t = op
                    if v[r] != int(env[t]):
                        return False
                    v[r] = 0
                elif k == "erase":
                    raise Irreversible()
                else:
                    raise ValueError(k)
        except Irreversible:
            return False
        except (KeyError, IndexError):
            return False
        return len(v) == 0 and len(stack) == 0 and len(exp) == 0
