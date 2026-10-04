"""Pre-freeze supply screen (T49, standing V2-B requirement).

Three of four consecutive ARC3 assays failed on supply or design, not on the mechanism:
- A20: UNTESTABLE (supply);
- A21: INVALID_DESIGN_DEFECT;
- A22: UNTESTABLE (5/8 < 6).
v2b makes the screen a PRECONDITION. An experiment's freeze record must carry a SupplyReceipt showing that the
deterministic role-assignment rule fills at least `quota` replicates FROM THE ACTUAL QUALIFIED FOUNDRY ROWS, before
any donor runs. If the screen fails, the experiment closes SUPPLY_LIMITED, and it is never run and called NO.
"""
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Callable, List


class SupplyLimited(Exception):
    pass


@dataclass
class SupplyReceipt:
    experiment: str
    replicates_planned: int
    replicates_fillable: int
    quota: int
    passed: bool
    unfilled: List[int]
    rows_sha256: str

    def as_dict(self):
        return asdict(self)


def screen(experiment, rows, assign: Callable, replicates: int, quota: int) -> SupplyReceipt:
    """assign(rows, r) -> (families, ok): the experiment's own deterministic role rule, unmodified."""
    fill, unfilled = 0, []
    for r in range(replicates):
        _fams, ok = assign(rows, r)
        if ok:
            fill += 1
        else:
            unfilled.append(r)
    h = hashlib.sha256(json.dumps(sorted(x["name"] for x in rows)).encode()).hexdigest()[:16]
    return SupplyReceipt(experiment, replicates, fill, quota, fill >= quota, unfilled, h)


def require(receipt: SupplyReceipt):
    if not receipt.passed:
        raise SupplyLimited("%s: %d/%d replicates fillable < quota %d (unfilled %s)" % (
            receipt.experiment, receipt.replicates_fillable, receipt.replicates_planned, receipt.quota,
            receipt.unfilled))
    return receipt


# ---------------------------------------------------------------- extensional distinctness (v2b-2, after T02)
def interchangeable(fa, fb, version="v1a"):
    """True iff each family's witness BODY, placed in the other family's (init, final), is tribunal-qualified on
    the other family. Both directions are required. That makes the two families extensional duplicates for
    reuse counting (T02: A23 CON1/CON8 G1 SAME pairs). fa/fb are dicts with name, body, init, final."""
    import a17
    import tribunal_t4 as T4
    import tribunal_t4_v1a as T4a
    prov = a17.Prov({fa["name"]: (fa["body"], fa["final"], fa["init"]), fb["name"]: (fb["body"], fb["final"], fb["init"])})
    T4.use_provider(prov)
    pa = ("fold", fa["init"], fa["body"], fa["final"])
    pb = ("fold", fb["init"], fb["body"], fb["final"])
    ab = T4a.direct_score(("fold", fb["init"], fa["body"], fb["final"]), fb["name"], pb, version)["qualified"]
    ba = T4a.direct_score(("fold", fa["init"], fb["body"], fa["final"]), fa["name"], pa, version)["qualified"]
    return bool(ab and ba)


def distinct_classes(fams, version="v1a"):
    """Group families into extensional-interchangeability classes (greedy, deterministic in input order).
    Reuse 'across k families' must mean k CLASSES."""
    classes = []
    for f in fams:
        for c in classes:
            if interchangeable(c[0], f, version):
                c.append(f)
                break
        else:
            classes.append([f])
    return classes
