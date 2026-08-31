"""Frozen mutation physics for RM-D5. Spec: PREREG-PREFLIGHT.md section 2.
All randomness flows through a caller-supplied random.Random instance."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'substrate'))
from rm_vm import OPS, OP_LIST, NREG, MAX_LEN, PALETTE

MUT_CLASSES = ['OP_REPLACE', 'ARG_TWEAK', 'INSERT', 'DELETE', 'SWAP', 'DUP_BLOCK']


def _rand_b(op, rng):
    kind = OPS[op]
    if kind == 'reg':
        return rng.randrange(NREG)
    if kind == 'const':
        return rng.randrange(len(PALETTE))
    if kind == 'jump':
        return rng.randint(1, 8)
    return 0


def random_instruction(rng):
    op = OP_LIST[rng.randrange(len(OP_LIST))]
    return (op, rng.randrange(NREG), _rand_b(op, rng))


def _applicable(prog, cls):
    if cls == 'INSERT':
        return len(prog) < MAX_LEN
    if cls == 'DELETE':
        return len(prog) > 1
    if cls == 'SWAP':
        return len(prog) >= 2
    if cls == 'DUP_BLOCK':
        return len(prog) < MAX_LEN
    return True


def mutate(prog, rng, allowed=None):
    """One mutation event; returns a new program. allowed: subset of MUT_CLASSES
    (used only by the PF4 ablation assay)."""
    classes = [c for c in (allowed or MUT_CLASSES) if _applicable(prog, c)]
    cls = classes[rng.randrange(len(classes))]
    p = list(prog)
    if cls == 'OP_REPLACE':
        i = rng.randrange(len(p))
        op = OP_LIST[rng.randrange(len(OP_LIST))]
        p[i] = (op, p[i][1], _rand_b(op, rng))
    elif cls == 'ARG_TWEAK':
        i = rng.randrange(len(p))
        op, a, b = p[i]
        if OPS[op] == 'none' or rng.random() < 0.5:
            p[i] = (op, rng.randrange(NREG), b)
        else:
            p[i] = (op, a, _rand_b(op, rng))
    elif cls == 'INSERT':
        p.insert(rng.randrange(len(p) + 1), random_instruction(rng))
    elif cls == 'DELETE':
        del p[rng.randrange(len(p))]
    elif cls == 'SWAP':
        i = rng.randrange(len(p) - 1)
        p[i], p[i + 1] = p[i + 1], p[i]
    elif cls == 'DUP_BLOCK':
        blk = rng.randint(1, min(3, len(p), MAX_LEN - len(p)))
        i = rng.randrange(len(p) - blk + 1)
        j = rng.randrange(len(p) + 1)
        p[j:j] = p[i:i + blk]
    return tuple(p)


def crossover(p1, p2, rng):
    c1 = rng.randint(0, len(p1))
    c2 = rng.randint(0, len(p2))
    child = tuple(p1[:c1]) + tuple(p2[c2:])
    return child[:MAX_LEN] if child else (('MOV', 0, 0),)


# Frozen starting repertoire (PREREG-PREFLIGHT 1.4): 16 literal programs.
SEED_REPERTOIRE = [
    (('MOV', 0, 0),),                            # identity
    *[(('SET', 0, c),) for c in range(10)],      # the 10 palette constants
    (('ADD', 0, 0),),                            # doubling
    (('MUL', 0, 0),),                            # squaring
    (('XOR', 0, 1),),                            # x xor r1(=0): identity variant
    (('SET', 1, 1), ('SHR', 0, 1)),              # halving
    (('SET', 1, 1), ('ADD', 0, 1)),              # increment
]
assert len(SEED_REPERTOIRE) == 16
