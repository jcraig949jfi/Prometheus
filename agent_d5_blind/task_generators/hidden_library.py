"""Hidden structure library H (generator-side ONLY; never learner-visible).

Each unary primitive: (name, pyfunc, template) where template is RM-D5 code
transforming r0 in place, clobbering only r1-r2. Predicates write 0/1 to r3,
read the saved input from r4, clobber r1-r2. Spec: PREREG-TASKS.md section 2.

Register discipline (compiler contract):
  r0 value | r1-r2 primitive scratch | r3 predicate out | r4 saved input
  r5 branch scratch | r6-r7 loop counter/constant or alien-family scratch
"""
M = 0xFFFF
# palette values usable via SET (index -> value): see rm_vm.PALETTE
PAL = [0, 1, 2, 3, 5, 7, 11, 13, 16, 255]
PIDX = {v: i for i, v in enumerate(PAL)}


def _c(reg, val):
    """SET reg to a palette VALUE."""
    return ('SET', reg, PIDX[val])


def _unary(name, c, py, tmpl):
    return {'name': f'{name}{c}', 'py': py, 'tmpl': tmpl}


def make_H(poison=False):
    """The frozen hidden pool. poison=True yields H' (NEGXFER): each constant
    is replaced by the next palette value up (frozen bijection), so machinery
    shaped on H is surface-similar but wrong."""
    def pz(c):
        if not poison:
            return c
        nz = [v for v in PAL if v != 0]          # keep constants nonzero
        return nz[(nz.index(c) + 1) % len(nz)] if c in nz else c

    H = []
    for c in (1, 3, 5, 7, 11, 13, 255):
        cc = pz(c)
        H.append(_unary('ADDC', c, lambda x, k=cc: (x + k) & M,
                        [_c(1, cc), ('ADD', 0, 1)]))
        H.append(_unary('SUBC', c, lambda x, k=cc: (x - k) & M,
                        [_c(1, cc), ('SUB', 0, 1)]))
        H.append(_unary('XORC', c, lambda x, k=cc: x ^ k,
                        [_c(1, cc), ('XOR', 0, 1)]))
    for c in (2, 3, 5, 7):
        cc = pz(c)
        H.append(_unary('MULC', c, lambda x, k=cc: (x * k) & M,
                        [_c(1, cc), ('MUL', 0, 1)]))
    for c in (7, 11, 13, 255):
        cc = pz(c)
        H.append(_unary('ANDC', c, lambda x, k=cc: x & k,
                        [_c(1, cc), ('AND', 0, 1)]))
        H.append(_unary('MODC', c, lambda x, k=cc: x % k,
                        [_c(1, cc), ('MOD', 0, 1)]))
    for c in (1, 2, 5, 16):
        cc = pz(c)
        H.append(_unary('ORC', c, lambda x, k=cc: x | k,
                        [_c(1, cc), ('OR', 0, 1)]))
    for s in (1, 2, 3):
        ss = pz(s) if pz(s) in (1, 2, 3) else s   # shifts stay small
        H.append(_unary('SHLC', s, lambda x, k=ss: (x << k) & M,
                        [_c(1, ss), ('SHL', 0, 1)]))
        H.append(_unary('SHRC', s, lambda x, k=ss: x >> k,
                        [_c(1, ss), ('SHR', 0, 1)]))
    H.append({'name': 'SQ', 'py': lambda x: (x * x) & M, 'tmpl': [('MUL', 0, 0)]})
    for c in (1, 3, 5):
        cc = pz(c)
        H.append(_unary('SQC', c, lambda x, k=cc: (x * x + k) & M,
                        [('MUL', 0, 0), _c(1, cc), ('ADD', 0, 1)]))
    # SWAP3: swap the two 3-bit halves of a 6-bit field (F4 flavor)
    H.append({'name': 'SWAP3',
              'py': lambda x: ((x >> 3) | ((x & 7) << 3)) & M,
              'tmpl': [('MOV', 2, 0), _c(1, 3), ('SHR', 0, 1), _c(1, 7),
                       ('AND', 2, 1), _c(1, 3), ('SHL', 2, 1), ('OR', 0, 2)]})
    return H


# Predicates: write 0/1 into r3; read saved input from r4; clobber r1-r2.
def make_PREDS():
    preds = []
    preds.append({'name': 'PARITY', 'py': lambda x: x & 1,
                  'tmpl': [('MOV', 3, 4), _c(1, 1), ('AND', 3, 1)]})
    for t in (3, 7, 13, 16):
        preds.append({'name': f'GT{t}', 'py': lambda x, k=t: 1 if x > k else 0,
                      'tmpl': [_c(3, 1), ('MOV', 2, 4), _c(1, t),
                               ('SKG', 2, 1), _c(3, 0)]})
    for k in (1, 2, 3):
        preds.append({'name': f'BIT{k}',
                      'py': lambda x, b=k: (x >> b) & 1,
                      'tmpl': [('MOV', 3, 4), _c(1, k), ('SHR', 3, 1),
                               _c(1, 1), ('AND', 3, 1)]})
    return preds


# Binary combiners (ALIEN family): combine r0 (=hB(y)) with r6 (=hA(x)).
COMBINERS = [
    {'name': 'CADD', 'py': lambda u, v: (u + v) & M, 'tmpl': [('ADD', 0, 6)]},
    {'name': 'CXOR', 'py': lambda u, v: u ^ v, 'tmpl': [('XOR', 0, 6)]},
    {'name': 'CSUB', 'py': lambda u, v: (v - u) & M, 'tmpl': [('SUB', 0, 6)]},
    {'name': 'CMAX', 'py': lambda u, v: max(u, v),
     'tmpl': [('SKG', 0, 6), ('MOV', 0, 6)]},
]
