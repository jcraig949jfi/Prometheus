"""Basis registry and canonical-order control (frozen)."""
import random

from . import s1_tpc, s2_flat, s3_trs, s4_rev

BASES = {"S1": s1_tpc, "S2": s2_flat, "S3": s3_trs, "S4": s4_rev}
ORDER_SPACES = {
    "S1": (s1_tpc.NSLOT, s1_tpc.NARG),
    "S2": (s2_flat.NOPS, s2_flat.NARG),
    "S3": (s3_trs.NKIND, s3_trs.NPAY),
    "S4": (s4_rev.NOPS, s4_rev.NREG),
}
ORDER_PERM_RNG_BASE = 101


def set_order(basis, order_id):
    """Order 0 is the identity permutation; orders 1,2 are fixed shuffles."""
    n1, n2 = ORDER_SPACES[basis]
    p1, p2 = list(range(n1)), list(range(n2))
    if order_id != 0:
        rng = random.Random(ORDER_PERM_RNG_BASE + order_id + 7919 * (ord(basis[1]) - 48))
        rng.shuffle(p1)
        rng.shuffle(p2)
    BASES[basis].set_order(p1, p2)
    return {"perm_op": p1, "perm_arg": p2}


def get(basis):
    return BASES[basis]
