"""T-H3-P11. The reservoir ancestry certificate walks only P-11-causal pair edges.

Operator ruling 2026-09-24 (C9-D11): every hereditary PAIR_EXECUTION edge the certificate
traverses must itself be P-11 causal; a predecessor-only pair edge breaks it.

Chains are built directly in a real Runner's lineage (founder born in the easy niche 0,
a logged migration 0 -> 2, crossing in hard niche 2), then certified:

  1. fully P-11-causal chain                          PASS (certificate)
  2. identical chain, final edge non-P-11             FAIL (no certificate)
  3. mixed chain, one non-causal edge in the middle   FAIL

FAIL-ON-OLD-CODE: the pre-repair certificate is restored from source into a private copy
and cases 2 and 3 must then be ACCEPTED by it - otherwise the test could not tell the
repaired code from the old.

Also T-H3-B (C9-D13): arm B keeps the RESERVOIR structure (identical migration physics)
and differs from arm A only in the easy-niche modifier. Injection: rev B's arm B
(NICHES_HIGH_MIG, migration 0.08 vs 0.02) must be caught.

Run:  python tests/test_h3_p11_ancestry.py     Exit 0 all demonstrated, 1 otherwise.
"""
from __future__ import annotations

import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import manifest as M     # noqa: E402
import world             # noqa: E402

CELL = dict(M.H3_CELLS[0][1])
P11_PASS = {"pass": True, "C2": True, "C4": True, "C5": True}
P11_FAIL = {"pass": False, "C2": False, "C4": False, "C5": True}


def runner(module=world, **kw):
    r = module.Runner(CELL, 1, tier="S", max_epochs=1, **kw)
    r.lineage, r.birth_niche, r.lineage_complete = [], {1: 0}, True
    return r


def chain(r, causal_flags):
    """founder 1 (easy niche) -> 2 -> ... ; the first child migrates 0 -> 2; the last
    node is the crossing organism. causal_flags[i] is the P-11 status of edge i."""
    oid = 1
    for i, ok in enumerate(causal_flags):
        r.epoch = 10 * (i + 1)
        child = oid + 1
        r._lin_birth(child, oid, 0 if i == 0 else 2, 0.97, r.L, ok,
                     causal_pred=True, p11_rec=(P11_PASS if ok else P11_FAIL))
        if i == 0:
            r._lin_migration(child, 0, 2)
        oid = child
    return oid


def certify(r, crossing):
    parent, _cp, birth_niche, moves = r._lineage_graph()
    return r.ancestry_certificate(crossing, birth_niche, parent, moves)


def old_world():
    """The pre-repair module: the noncausal-pair check removed from the certificate."""
    src = (ROOT / "world.py").read_text()
    a = '''        noncausal_pair = {e["child"] for e in self.lineage
                          if e["kind"] == "birth" and "p11" in e and not e["causal"]}
'''
    b = '''            if cur in noncausal_pair and cur in parent:
                return None
'''
    assert src.count(a) == 1 and src.count(b) == 1, "repair not found: injection would be VACUOUS"
    src = src.replace(a, "").replace(b, "")
    mod = types.ModuleType("world_prerepair")
    mod.__file__ = str(ROOT / "world.py")
    exec(compile(src, "world_prerepair", "exec"), mod.__dict__)
    return mod


CASES = [("fully P-11-causal chain", [True, True], True),
         ("identical chain, final edge non-P-11", [True, False], False),
         ("mixed chain, one non-causal edge", [True, False, True], False)]


def main():
    ok = True

    def rec(label, good, detail):
        nonlocal ok
        ok &= good
        print("%-7s %-52s %s" % ("PASS" if good else "FAIL", label, detail))

    print("REPAIRED certificate")
    print("-" * 100)
    for name, flags, want in CASES:
        r = runner()
        c = certify(r, chain(r, flags))
        rec(name + (": certificate" if want else ": none"), (c is not None) == want,
            "cert=%s" % (None if c is None else "lineage_len %d" % c["lineage_len"]))

    print()
    print("FAIL-ON-OLD-CODE - the pre-repair certificate must ACCEPT the non-causal chains")
    print("-" * 100)
    old = old_world()
    for name, flags, want in CASES[1:]:
        r = runner(module=old)
        c = certify(r, chain(r, flags))
        rec("old code accepts: " + name, c is not None,
            "old cert=%s -> the repaired test above distinguishes the two" % (c is not None))

    print()
    print("T-H3-B arm B: identical migration physics, easy niche off (C9-D13)")
    print("-" * 100)
    b = [a for a in M.h3_bundles(1)[0]["arms"]]
    arm = {a["arm"]: a for a in b}
    A, B, Cc = arm["A_easy_plus_migration"], arm["B_homogeneous_same_migration"], arm["C_easy_no_migration"]
    ra = world.Runner(A["cell"], 1, tier="S", **A["kwargs"])
    rb = world.Runner(B["cell"], 1, tier="S", **B["kwargs"])
    same_struct = A["cell"]["structure"] == B["cell"]["structure"] == "RESERVOIR"
    same_rest = {k: v for k, v in A["cell"].items()} == {k: v for k, v in B["cell"].items()}
    ea = ra._apply_niche_modifier(ra.spec, 0)
    eb = rb._apply_niche_modifier(rb.spec, 0)
    rec("B keeps RESERVOIR structure (migration 0.02)", same_struct and same_rest,
        "A=%s B=%s cells identical=%s" % (A["cell"]["structure"], B["cell"]["structure"], same_rest))
    rec("A niche 0 is easy, B niche 0 is not",
        (ea.read_order, ea.bridge) == ("FORCED_READ", "NEUTRAL_BRIDGE") and eb == rb.spec,
        "A=(%s,%s) B=(%s,%s)" % (ea.read_order, ea.bridge, eb.read_order, eb.bridge))
    rec("C keeps the easy niche, migration disabled",
        Cc["kwargs"].get("migration_disabled") is True and not Cc["kwargs"].get("easy_niche_disabled"),
        str(Cc["kwargs"]))
    revb = dict(A["cell"], structure="NICHES_HIGH_MIG")
    rec("injected rev-B arm B is caught", not (revb["structure"] == A["cell"]["structure"]),
        "rev B structure %s != RESERVOIR" % revb["structure"])

    print()
    print("OPEN (C9-D14, not a gate): a certificate with ZERO lineage edges")
    print("-" * 100)
    r = runner()
    r._lin_migration(1, 0, 2)
    c = certify(r, 1)
    print("        founder = crossing organism, no hereditary edge: cert=%s" %
          (None if c is None else "FORMED, lineage_len %d" % c["lineage_len"]))

    print("-" * 100)
    print("T-H3-P11:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
