"""D-VM: deterministic, bounded, typed, homoiconic stack machine.

One value universe: Int (python int) and Block (tuple of instructions).
An instruction is an opcode name (str) or a literal push ('P', value).
Programs ARE Blocks; the meta tier edits Blocks as data.

No clocks, no randomness, no host introspection. Every failure is a typed
numeric error (code, ip, depth) — failure geometry, not English.
"""

import hashlib

MOD = 97  # object-tier arithmetic modulus

# ---- caps (fixed physics; frozen with the grammar) ----
MAX_STACK = 16
MAX_BLOCK = 64
MAX_INT = 1 << 20
OBJ_MAX_STEPS = 64

# ---- error codes ----
E_UNDERFLOW = 1
E_TYPE = 2
E_BLOCK_CAP = 3
E_STACK_CAP = 4
E_STEP_CAP = 5
E_BADOP = 6
E_INT_CAP = 7


class VMError(Exception):
    def __init__(self, code, ip, depth):
        self.code = code
        self.ip = ip
        self.depth = depth
        super().__init__((code, ip, depth))

    def descriptor(self):
        return (self.code, self.ip, self.depth)


def is_block(v):
    return isinstance(v, tuple)


# ---- canonical serialization / hashing ----

def ser(v):
    if isinstance(v, bool):  # guard: bools are ints in python; forbid
        raise TypeError("bool is not a D-VM value")
    if isinstance(v, int):
        return str(v)
    return "{" + " ".join(ser_instr(i) for i in v) + "}"


def ser_instr(i):
    if isinstance(i, str):
        return i
    if isinstance(i, tuple) and len(i) == 2 and i[0] == "P":
        return "[" + ser(i[1]) + "]"
    raise TypeError("not a D-VM instruction: %r" % (i,))


def block_hash(b):
    return hashlib.sha256(ser(b).encode("utf-8")).hexdigest()


# ---- object tier ----
# o0 add mod MOD | o1 mul mod MOD | o2 dup | o3 swap
# o4 skipz: pop int; if zero, skip the next instruction
OBJECT_OPS = ("o0", "o1", "o2", "o3", "o4")


def exec_object(block, stack, max_steps=OBJ_MAX_STEPS):
    """Execute an object-tier artifact against an int stack.

    Returns the final stack (tuple). Raises VMError on any bound/type breach.
    """
    st = list(stack)
    ip = 0
    steps = 0
    n = len(block)
    while ip < n:
        steps += 1
        if steps > max_steps:
            raise VMError(E_STEP_CAP, ip, len(st))
        instr = block[ip]
        if isinstance(instr, tuple):  # ('P', v)
            st.append(instr[1])
            if len(st) > MAX_STACK:
                raise VMError(E_STACK_CAP, ip, len(st))
            ip += 1
            continue
        if instr == "o0" or instr == "o1":
            if len(st) < 2:
                raise VMError(E_UNDERFLOW, ip, len(st))
            b, a = st.pop(), st.pop()
            if is_block(a) or is_block(b):
                raise VMError(E_TYPE, ip, len(st))
            st.append((a + b) % MOD if instr == "o0" else (a * b) % MOD)
        elif instr == "o2":
            if not st:
                raise VMError(E_UNDERFLOW, ip, len(st))
            st.append(st[-1])
            if len(st) > MAX_STACK:
                raise VMError(E_STACK_CAP, ip, len(st))
        elif instr == "o3":
            if len(st) < 2:
                raise VMError(E_UNDERFLOW, ip, len(st))
            st[-1], st[-2] = st[-2], st[-1]
        elif instr == "o4":
            if not st:
                raise VMError(E_UNDERFLOW, ip, len(st))
            a = st.pop()
            if is_block(a):
                raise VMError(E_TYPE, ip, len(st))
            if a == 0:
                ip += 2
                continue
        else:
            raise VMError(E_BADOP, ip, len(st))
        ip += 1
    return tuple(st)


# ---- meta tier ----
# Learner-visible token IDs are arbitrary; semantics documented for humans.
META_OPS = (
    "d00",  # dup    (a -> a a)
    "d01",  # swap   (a b -> b a)
    "d02",  # drop   (a -> )
    "d03",  # nil    ( -> B) empty block
    "d04",  # cat    (B B -> B)
    "d05",  # len    (B -> I)
    "d06",  # splt   (B I -> B B) split at clamped index; left below right
    "d07",  # qlit   (B -> B) one-instruction block that pushes the argument
    "d08",  # zero   ( -> I)
    "d09",  # succ   (I -> I)
    "d10",  # add    (I I -> I)
    "d11",  # half   (I -> I) floor div 2
)


def exec_meta(prog, stack):
    """Execute a straight-line meta program (tuple of meta/introducer tokens).

    `introducers` semantics are supplied by the grammar via TOKEN_BLOCKS.
    Returns final stack (list copied to tuple). Raises VMError.
    """
    st = list(stack)

    def pop_block(ip):
        if not st:
            raise VMError(E_UNDERFLOW, ip, len(st))
        v = st.pop()
        if not is_block(v):
            raise VMError(E_TYPE, ip, len(st))
        return v

    def pop_int(ip):
        if not st:
            raise VMError(E_UNDERFLOW, ip, len(st))
        v = st.pop()
        if is_block(v):
            raise VMError(E_TYPE, ip, len(st))
        return v

    def push(v, ip):
        st.append(v)
        if len(st) > MAX_STACK:
            raise VMError(E_STACK_CAP, ip, len(st))

    for ip, op in enumerate(prog):
        if op == "d00":
            if not st:
                raise VMError(E_UNDERFLOW, ip, len(st))
            push(st[-1], ip)
        elif op == "d01":
            if len(st) < 2:
                raise VMError(E_UNDERFLOW, ip, len(st))
            st[-1], st[-2] = st[-2], st[-1]
        elif op == "d02":
            if not st:
                raise VMError(E_UNDERFLOW, ip, len(st))
            st.pop()
        elif op == "d03":
            push((), ip)
        elif op == "d04":
            b = pop_block(ip)
            a = pop_block(ip)
            r = a + b
            if len(r) > MAX_BLOCK:
                raise VMError(E_BLOCK_CAP, ip, len(st))
            push(r, ip)
        elif op == "d05":
            b = pop_block(ip)
            push(len(b), ip)
        elif op == "d06":
            i = pop_int(ip)
            b = pop_block(ip)
            k = max(0, min(len(b), i))
            push(b[:k], ip)
            push(b[k:], ip)
        elif op == "d07":
            b = pop_block(ip)
            push((("P", b),), ip)
        elif op == "d08":
            push(0, ip)
        elif op == "d09":
            v = pop_int(ip) + 1
            if v > MAX_INT:
                raise VMError(E_INT_CAP, ip, len(st))
            push(v, ip)
        elif op == "d10":
            b = pop_int(ip)
            a = pop_int(ip)
            v = a + b
            if v > MAX_INT:
                raise VMError(E_INT_CAP, ip, len(st))
            push(v, ip)
        elif op == "d11":
            push(pop_int(ip) // 2, ip)
        elif op in TOKEN_BLOCKS:
            push(TOKEN_BLOCKS[op], ip)
        else:
            raise VMError(E_BADOP, ip, len(st))
    return tuple(st)


# introducer tokens: each pushes a fixed length-1 Block of one object opcode
TOKEN_BLOCKS = {
    "t0": ("o0",),
    "t1": ("o1",),
    "t2": ("o2",),
    "t3": ("o3",),
    "t4": ("o4",),
}


# ---- abstract typing for enumeration ----
# type stack symbols: 'I', 'B'. Returns new tuple or None if the op cannot
# apply (underflow / type mismatch / guaranteed cap breach is NOT modeled —
# caps are runtime, typing is shape-only).

META_TYPE = {
    "d03": ((), ("B",)),
    "d04": (("B", "B"), ("B",)),
    "d05": (("B",), ("I",)),
    "d06": (("B", "I"), ("B", "B")),
    "d07": (("B",), ("B",)),
    "d08": ((), ("I",)),
    "d09": (("I",), ("I",)),
    "d10": (("I", "I"), ("I",)),
    "d11": (("I",), ("I",)),
}
for _t in TOKEN_BLOCKS:
    META_TYPE[_t] = ((), ("B",))


def type_step(tstack, op):
    """Apply one token to an abstract type stack; None if ill-typed."""
    if op == "d00":
        if not tstack:
            return None
        return tstack + (tstack[-1],)
    if op == "d01":
        if len(tstack) < 2:
            return None
        return tstack[:-2] + (tstack[-1], tstack[-2])
    if op == "d02":
        if not tstack:
            return None
        return tstack[:-1]
    sig = META_TYPE.get(op)
    if sig is None:
        return None
    ins, outs = sig
    n = len(ins)
    if n and (len(tstack) < n or tstack[len(tstack) - n:] != ins):
        return None
    if len(tstack) - n + len(outs) > MAX_STACK:
        return None
    return tstack[: len(tstack) - n] + outs
