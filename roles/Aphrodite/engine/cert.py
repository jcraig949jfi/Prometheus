"""Campaign-local CLASS CERTIFICATES (AMENDMENT 12 ADDENDUM 3, frozen at
a2ba379aa before this was written).

behavior_id is a provisional bucket (GLOBAL_BEHAVIOR_IDENTITY = FAIL). A
bucket may influence science only if every member agrees on BOTH the fresh
valid-domain battery B_CERT and the threshold-adversarial battery A(S), whose
generator is fixed here and uses program structure (each member's own
ceiling-crossing boundary) but never the certificate outcome.
"""
import random
from typing import Dict, List, Sequence, Tuple

import basis_v4 as G
import identity as I

B_CERT_N = 20_000
A_CAP = 60_000
QS = (1, 2, 3, 7, 32, 33, 96, 97)
LAST_VARIANTS = (2, 3, 29, 30)

_BCERT = None
_BASES = None


def b_cert() -> List[List[int]]:
    global _BCERT
    if _BCERT is None:
        _BCERT = I.build_b2_v3(B_CERT_N, "APHRODITE/S1/CERT/v1")
    return _BCERT


def bases() -> List[List[int]]:
    global _BASES
    if _BASES is None:
        rng = random.Random(I._seed("APHRODITE/S1/ADV/v1"))
        out = [[c] * 200 for c in range(2, 31)]
        for _ in range(40):
            a, b = rng.randint(2, 30), rng.randint(2, 30)
            out.append([a if k % 2 == 0 else b for k in range(200)])
        for _ in range(40):
            out.append([rng.randint(2, 30) for _ in range(200)])
        _BASES = out
    return _BASES


def _fails(p, inp) -> bool:
    return G.run_program(p, list(inp), True) is None


def adversarial(members: Sequence[Tuple]) -> List[List[int]]:
    """A(S): for each member, each base and each query, bracket the smallest
    domain length L* at which the member FAILS on base[:L] + [q]."""
    lengths = I.TASK_LENGTHS
    out = []
    for p in members:
        for base in bases():
            for q in QS:
                Ls = None
                for k, L in enumerate(lengths):
                    if _fails(p, base[:L] + [q]):
                        Ls = k
                        break
                if Ls is None:
                    continue
                for kk in (Ls - 1, Ls, Ls + 1):
                    if 0 <= kk < len(lengths):
                        out.append(base[:lengths[kk]] + [q])
                L = lengths[Ls]
                for lv in LAST_VARIANTS:
                    out.append(base[:L - 1] + [lv] + [q])
                for qq in range(1, 98):
                    out.append(base[:L] + [qq])
    out = I._dedupe(out)
    if len(out) > A_CAP:
        rng = random.Random(I._seed("APHRODITE/S1/ADV-CAP/v1"))
        out = rng.sample(out, A_CAP)
    assert all(I.in_task_domain(x) for x in out)
    return out


def certify(members: Sequence[Tuple], anchor: Tuple = None) -> Dict:
    """PASS iff all members agree on B1 u B_CERT u A(S). On a split, the
    sub-buckets are returned, and the anchor's sub-bucket is named."""
    members = [tuple(m) for m in dict.fromkeys(tuple(m) for m in members)]
    adv = adversarial(members)
    bat = list(I.B1) + b_cert() + adv
    sig = {}
    for m in members:
        sig.setdefault(I.values(m, True, bat), []).append(list(m))
    buckets = list(sig.values())
    rec = {"members": len(members), "adversarial_inputs": len(adv),
           "b_cert_inputs": len(b_cert()), "sub_buckets": len(buckets),
           "PASS": len(buckets) == 1}
    if not rec["PASS"]:
        rec["split"] = [b[:6] for b in buckets]
        if anchor is not None:
            rec["anchor_bucket"] = next(b for b in buckets if list(tuple(anchor)) in b)
    return rec
