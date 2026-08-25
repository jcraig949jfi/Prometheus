"""Charon's INDEPENDENT gate-fire probe on Ergon's packet invariants, 2026-08-25.

Ergon's own gate-fire suite is evidence about his implementation, not about his specification.
This probe is written by the kill authority, does not import his test suite, and attacks the
invariants with perturbations HE DID NOT INSTANTIATE, chosen from the defect classes this
campaign has actually been burned by plus two he has not been burned by yet.

A check that has never failed is an untested function whose return value happens to be True.
That is his own sentence; this applies it to the artifact he wrote to close it.

Each world plants ONE defect and asserts the invariants FAIL. A world that plants a defect and
still passes is a hole, and is reported as such.

    python charon/probe/charon_gate_fire_2026-08-25.py
"""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ergon.probe.packet_invariants import check_task, slug_bands_not_separable  # noqa: E402

CARRY = ["F-null", "F-generic", "F-prom-retrieved", "F-hint", "F-null+hint", "F-prom+hint"]
FORBIDDEN = ["true", "false", "correct answer", "the answer is"]


def live_packets():
    import ergon.probe.campaign as C
    rows = C.manifest()
    gold = {r["uid"]: r["gold_int"] for r in rows}
    arms = C.Arms(rows, gold)
    out = []
    for r in rows:
        try:
            p = {a: arms.prompt(a, r["uid"]) for a in ["F0"] + CARRY}
        except Exception:
            continue
        out.append((r["uid"], p, gold[r["uid"]]))
        if len(out) >= 40:
            break
    return out


GATES = ("base_identical", "template_conformance", "slug_pool_shared",
         "sparsity_arm_invariant", "nontreatment_identical_across_arms",
         "no_forbidden_tokens", "no_verbatim_gold")


def passes(prompts, gold):
    return check_task(prompts, gold, CARRY, FORBIDDEN)["all_pass"]


def failing(prompts, gold):
    r = check_task(prompts, gold, CARRY, FORBIDDEN)
    return [k for k in GATES if not r[k]]


def world(name, mutate, expect_fail=True):
    """Plant one defect across live packets; report whether the gate notices."""
    pk = live_packets()
    assert pk, "no packets"
    clean = all(passes(p, g) for _, p, g in pk)
    fired = 0
    which = set()
    for uid, p, g in pk:
        q = copy.deepcopy(p)
        mutate(q, uid)
        f = failing(q, g)
        if f:
            fired += 1
            which.update(f)
    ok = (fired > 0) if expect_fail else (fired == 0)
    print(f"  [{'PASS' if ok else 'HOLE'}] {name}: clean_baseline={clean} "
          f"fired_on {fired}/{len(pk)}  via={sorted(which) or '-'}")
    return {"world": name, "clean_baseline": clean, "fired": fired, "n": len(pk),
            "caught_by": sorted(which), "verdict": "PASS" if ok else "HOLE"}


def main():
    print("Charon independent gate-fire on ergon/probe/packet_invariants.py\n")
    res = []

    # W0 -- the null world. Unmutated packets must pass, or every result below is meaningless.
    res.append(world("W0 clean packets pass (positive control)",
                     lambda q, u: None, expect_fail=False))

    # W1 -- the ORIGINAL defect, re-planted: a per-arm lead line on two arms of six.
    def w1(q, u):
        for a in ("F-null", "F-prom-retrieved"):
            q[a] = "A prior attempt record:\n" + q[a]
    res.append(world("W1 per-arm lead line (the historical LABEL 1)", w1))

    # W2 -- an arm-varying suffix. His own 4.1 says conformance alone cannot catch this and
    # that INV 6c is what closes it. Test the claim rather than accept it.
    def w2(q, u):
        q["F-generic"] = q["F-generic"] + "\n[note: generic]"
    res.append(world("W2 per-arm trailing suffix (4.1's claimed hole)", w2))

    # W3 -- an ARM-INVARIANT addition INSIDE the residue region (before the shared F0 base).
    # Ergon 4.1 claims such an addition is absorbed silently and correctly, because an
    # arm-invariant suffix is not an arm label. Firing here would mean over-sensitivity.
    #
    # CORRECTION TO MY OWN PROBE: the first cut of W3 appended AFTER the base prompt, which
    # breaks base_identical -- a real and DIFFERENT defect. It reported a HOLE that was my
    # test's error, not his gate's. Fixed here; the mis-specified variant is kept as W3b so
    # the correction stays visible rather than being quietly dropped.
    def w3(q, u):
        base = q["F0"]
        for a in CARRY:
            assert q[a].endswith(base)
            q[a] = q[a][:-len(base)] + "[uniform note]\n" + base
    res.append(world("W3 arm-INVARIANT text inside residue must NOT fire "
                     "(over-sensitivity check)", w3, expect_fail=False))

    def w3b(q, u):
        for a in CARRY:
            q[a] = q[a] + "\n[uniform footer]"
    res.append(world("W3b arm-invariant text AFTER the shared base SHOULD fire "
                     "(breaks base identity)", w3b))

    # W4 -- a single whitespace difference on ONE arm. Byte-identity should catch what a
    # digit-erased envelope abstraction would not.
    def w4(q, u):
        q["F-hint"] = q["F-hint"].replace("\n", "\n", 1) + " "
    res.append(world("W4 one trailing space on one arm", w4))

    # W5 -- a defect class he has NOT been burned by: a per-arm UNICODE homoglyph swap that
    # leaves character counts, digit runs and line structure identical.
    def w5(q, u):
        if "o" in q["F-prom+hint"]:
            q["F-prom+hint"] = q["F-prom+hint"].replace("o", "ο", 1)  # Greek omicron
    res.append(world("W5 per-arm homoglyph swap (length-preserving, novel class)", w5))

    # W6 -- a per-arm ZERO-WIDTH character. Invisible in any rendered inspection.
    def w6(q, u):
        q["F-null+hint"] = q["F-null+hint"] + "​"
    res.append(world("W6 per-arm zero-width space (invisible to human review)", w6))

    # W7 -- population-scope: reintroduce a disjoint digit band in the slug (historical LABEL 2).
    # Per-task checks cannot see this by construction, so it is checked across the manifest.
    pk = live_packets()
    import re as _re
    slots_clean, slots_dirty = [], []
    for uid, p, g in pk:
        r = check_task(p, g, CARRY, FORBIDDEN)
        if r.get("_slots"):
            slots_clean.append(r["_slots"])
            d = copy.deepcopy(r["_slots"])
            for i, a in enumerate(CARRY):
                if a in d and isinstance(d[a], dict) and "slug" in d[a]:
                    d[a]["slug"] = _re.sub(r"\d+", str(10000 * (i + 1) + len(slots_dirty)),
                                           d[a]["slug"])
            slots_dirty.append(d)
    ok_clean, _ = slug_bands_not_separable(slots_clean)
    ok_dirty, det = slug_bands_not_separable(slots_dirty)
    hit = ok_clean and not ok_dirty
    print(f"  [{'PASS' if hit else 'HOLE'}] W7 replanted disjoint slug bands (LABEL 2): "
          f"clean={ok_clean} dirty={ok_dirty}")
    res.append({"world": "W7 replanted disjoint slug bands", "clean_baseline": ok_clean,
                "fired": (not ok_dirty), "n": len(slots_dirty),
                "verdict": "PASS" if hit else "HOLE"})

    holes = [r for r in res if r["verdict"] == "HOLE"]
    out = {"probe": "charon independent gate-fire",
           "target": "ergon/probe/packet_invariants.py",
           "n_worlds": len(res), "holes": len(holes), "worlds": res,
           "verdict": "GATES FIRE — no hole found by this probe" if not holes
                      else f"HOLES FOUND: {[h['world'] for h in holes]}"}
    print("\n" + out["verdict"])
    p = pathlib.Path(__file__).resolve().parent / "charon_gate_fire_2026-08-25.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", p.name)
    return 0 if not holes else 1


if __name__ == "__main__":
    sys.exit(main())
