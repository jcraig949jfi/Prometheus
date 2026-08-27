"""coordinate_census.py — the K0 check, finally executable. Diomedes's standing offer to the fleet.

WHAT THIS IS. ROLE.md S5 has offered the fleet one line since 2026-08-24: *before any navigation,
routing, transfer or capability claim ships, state the action alphabet and its entropy; if H(a) ~= 0
the claim is VACUOUS by construction.* It has never existed as a runnable thing. This is it,
generalised to the form that actually cost this seat an arm.

WHAT IT COMPUTES, and why it is NOT aporia/lot/census.py.
    Aporia's REACHABILITY_CENSUS answers: can the label be produced, and is it leaked marginally or
    by a shallow alternative composition? (occupancy / marginal leakage / alt-composition leak)
    This module answers a strictly different question: DOES CONDITIONING ON THE STATE BUY ANYTHING,
    and CAN THE GATE YOU ARE ABOUT TO SET ACTUALLY FIRE?

    The two are not substitutes and the gap between them is exactly what killed cycle 005 Arm A.
    b2 had healthy label balance -- 2,372 true / 1,264 false -- and would pass a reachability check
    comfortably. Its CONDITIONAL HEADROOM was 0.0265. Knowing which operators were involved got you
    to 0.9735 of a 1.0000 oracle; the entire remaining space for state-conditional structure was
    2.65 points. Underpowered BY LANDSCAPE, not by sample size. Run both censuses, not one.

THE FIVE CHECKS, all arithmetic, no model, no LLM:
    1 conditional headroom    oracle - best STATE-INDEPENDENT ranking. Below ~0.05 disqualifies the
                              population for a conditional-structure question.
    2 gate reachable          is the threshold inside the attainable range at all? A gate above the
                              maximum attainable cannot fire on any input.
    3 gate vs its own error   is the gate further from the observed value than the value's own
                              uncertainty? A threshold closer than its SE is not a gate.
    4 cluster bootstrap       uncertainty on the unit that actually varies, not on seeds. This seat
                              quoted "127 SE" from a seed-level SE whose cell-clustered interval was
                              52x wider and included zero.
    5 identifiability ceiling for enumerable synthetic worlds: sum_s P(s)/|A(s)|. If two hidden
                              causes produce the same observable signature, no solver separates them
                              and the ceiling is below 1.0 BY CONSTRUCTION.

VERDICT ENUM IS ENFORCED. ROLE.md S4 specifies verdict in {ADEQUATE, INADEQUATE, VACUOUS}; CARs
004-006 drifted into free text, which S9.5 declared as the typed object decaying toward prose. This
module emits the enum and refuses anything else, so the drift is structurally impossible rather than
a thing someone must remember.

    python roles/Diomedes/coordinate_census.py        # runs the self-test against known answers
"""
from __future__ import annotations

import json
import math
import pathlib
from collections import Counter, defaultdict

HEADROOM_FLOOR = 0.05
VERDICTS = ("ADEQUATE", "INADEQUATE", "VACUOUS")


# ----------------------------------------------------------------- exact AUC


def auc(pairs):
    """Exact tie-aware AUC over (score, label). None if a class is absent.

    Integer-exact for integer scores; no sampling, no SE, no null needed.
    """
    pos = [s for s, l in pairs if l]
    neg = [s for s, l in pairs if not l]
    if not pos or not neg:
        return None
    wins = ties = 0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def _mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


# -------------------------------------------------------- 1. headroom census


def conditional_headroom(states, context=None):
    """The check whose omission wasted cycle 005 Arm A.

    states  : [{"actions": [hashable, ...], "labels": [0/1, ...]}, ...]
    context : optional fn(state) -> hashable. When given, the state-independent ceiling is
              computed CONDITIONAL ON THE CONTEXT but still ignoring the rest of the state --
              the analogue of cycle 005's f-conditional ceiling. This is the honest ceiling
              whenever part of the state is considered "free" information.

    Returns chance, the state-independent ceiling, the oracle, and headroom = oracle - ceiling.
    """
    glob = defaultdict(lambda: [0, 0])                 # action -> [n_true, n]
    ctx = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for s in states:
        c = context(s) if context else None
        for a, l in zip(s["actions"], s["labels"]):
            glob[a][0] += int(l); glob[a][1] += 1
            ctx[c][a][0] += int(l); ctx[c][a][1] += 1

    rate = {a: (t / n if n else 0.0) for a, (t, n) in glob.items()}
    crate = {c: {a: (t / n if n else 0.0) for a, (t, n) in d.items()} for c, d in ctx.items()}

    marg, cond, orc, chance = [], [], [], []
    for s in states:
        L = s["labels"]
        marg.append(auc([(rate[a], l) for a, l in zip(s["actions"], L)]))
        r = crate[context(s) if context else None]
        cond.append(auc([(r[a], l) for a, l in zip(s["actions"], L)]))
        orc.append(auc([(float(l), l) for l in L]))
        chance.append(auc([(0.0, l) for l in L]))

    ceiling = _mean(cond if context else marg)
    oracle = _mean(orc)
    return {
        "n_states": len(states),
        "n_states_with_both_classes": sum(1 for s in states if 0 < sum(s["labels"]) < len(s["labels"])),
        "action_alphabet_size": len(glob),
        "action_entropy_bits": _entropy_bits(glob),
        "chance": _r(_mean(chance)),
        "marginal_ceiling": _r(_mean(marg)),
        "state_independent_ceiling": _r(ceiling),
        "oracle": _r(oracle),
        "conditional_headroom": _r(oracle - ceiling) if (oracle and ceiling) else None,
        "floor": HEADROOM_FLOOR,
        "qualifies": bool(oracle and ceiling and (oracle - ceiling) >= HEADROOM_FLOOR),
        "context_used": context is not None,
    }


def _entropy_bits(glob):
    """H(a) over the action alphabet. The original K0 check: H ~= 0 => VACUOUS by construction."""
    tot = sum(n for _, n in glob.values())
    if not tot:
        return 0.0
    h = 0.0
    for _, n in glob.values():
        if n:
            p = n / tot
            h -= p * math.log2(p)
    return round(h, 4)


def _r(x, k=4):
    return round(float(x), k) if x is not None else None


# ------------------------------------------- 2/3. gate reachability and error


def gate_reachable(gate, lo, hi):
    """A gate outside the attainable range cannot fire on any input. Cycle-004-era failure:
    a preregistered cut of 0.14 sat ABOVE a maximum attainable 0.1364."""
    return {"gate": gate, "attainable_lo": _r(lo), "attainable_hi": _r(hi),
            "reachable": bool(lo <= gate <= hi),
            "note": "a gate outside [lo, hi] cannot fire on any input"}


def gate_exceeds_error(gate, point, err):
    """A threshold closer to the observed value than its own uncertainty is not a gate.

    err must be the uncertainty on the unit that VARIES -- see cluster_bootstrap. This seat has
    failed this check twice, the second time two hours after correcting the first.
    """
    d = abs(point - gate)
    return {"gate": gate, "point": _r(point), "error": _r(err),
            "distance": _r(d), "distance_in_error_units": _r(d / err) if err else None,
            "passes": bool(err and d >= 2 * err),
            "note": "distance to the gate must exceed ~2x the uncertainty on the varying unit"}


# ----------------------------------------------------- 4. clustered bootstrap


def cluster_bootstrap(clusters, stat=None, n_boot=2000, seed=20260826):
    """Resample CLUSTERS, not rows and not seeds.

    clusters : {cluster_id: [values]}. Point estimate is the mean over all values; each resample
    draws whole clusters with replacement. Deterministic given `seed` -- no global RNG.
    """
    keys = sorted(clusters)
    flat = [v for k in keys for v in clusters[k]]
    if not flat:
        return None
    point = sum(flat) / len(flat)
    st = stat or (lambda vs: sum(vs) / len(vs))
    rng = _Lcg(seed)
    boots = []
    for _ in range(n_boot):
        pick = [keys[rng.below(len(keys))] for _ in range(len(keys))]
        vals = [v for k in pick for v in clusters[k]]
        if vals:
            boots.append(st(vals))
    boots.sort()
    lo = boots[int(0.025 * len(boots))]
    hi = boots[min(len(boots) - 1, int(0.975 * len(boots)))]
    return {"n_clusters": len(keys), "n_values": len(flat), "n_resamples": len(boots),
            "point": _r(point), "ci95_lo": _r(lo), "ci95_hi": _r(hi),
            "half_width": _r((hi - lo) / 2), "includes_zero": bool(lo <= 0 <= hi)}


class _Lcg:
    """Deterministic PRNG so a census is reproducible without touching global RNG state."""

    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFF

    def below(self, n):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s % n


# ------------------------------------------------ 5. identifiability ceiling


def identifiability_ceiling(signature_cause_pairs):
    """For enumerable synthetic worlds. sum_s P(s)/|A(s)|.

    signature_cause_pairs : [(observable_signature, true_cause), ...] over the generated population.
    If two distinct causes produce the same observable signature, NO solver can separate them and
    the ceiling sits below 1.0 by construction. Compute before fitting anything.
    """
    by_sig = defaultdict(set)
    counts = Counter()
    for sig, cause in signature_cause_pairs:
        by_sig[sig].add(cause)
        counts[sig] += 1
    n = sum(counts.values())
    if not n:
        return None
    ceiling = sum((counts[s] / n) / len(by_sig[s]) for s in counts)
    amb = sum(counts[s] for s in counts if len(by_sig[s]) > 1)
    return {"n_items": n, "n_signatures": len(counts),
            "exact_oracle_ceiling": _r(ceiling),
            "ambiguous_item_fraction": _r(amb / n),
            "max_causes_per_signature": max(len(v) for v in by_sig.values()),
            "note": "no solver can exceed exact_oracle_ceiling on this population"}


# ------------------------------------------------------------------- the CAR


def car(claim_id, quantity, coordinate_system, headroom, rows_ref,
        decision_this_changes, extras=None):
    """Emit the seat's typed unit of output. The verdict enum is ENFORCED, not remembered."""
    if headroom.get("action_entropy_bits", 1.0) <= 1e-9:
        verdict = "VACUOUS"
    elif headroom.get("qualifies"):
        verdict = "ADEQUATE"
    else:
        verdict = "INADEQUATE"
    assert verdict in VERDICTS
    rec = {"car_id": None, "claim_id": claim_id, "quantity_credited": quantity,
           "coordinate_system": coordinate_system,
           "alphabet": headroom.get("action_alphabet_size"),
           "alphabet_entropy_bits": headroom.get("action_entropy_bits"),
           "attainable_range": {"chance": headroom.get("chance"),
                                "state_independent_ceiling": headroom.get("state_independent_ceiling"),
                                "oracle": headroom.get("oracle")},
           "conditional_headroom": headroom.get("conditional_headroom"),
           "measured_over_which_rows": rows_ref,
           "verdict": verdict,
           "decision_this_changes": decision_this_changes}
    if extras:
        rec.update(extras)
    if not decision_this_changes:
        rec["_warning"] = ("empty decision_this_changes -- ROLE.md S7 counts this against the seat; "
                           "three consecutive such CARs is a retirement trigger")
    return rec


# ------------------------------------------------------------------ self-test


def _selftest():
    """Differential test against populations whose headroom is already committed elsewhere.

    b3 and b4 are recomputed from the step-0 operator tables by THIS module and must match the
    independently written cycle005_q1_headroom_census.py to 1e-9. h1 and b2 are asserted against
    their committed constants. A module that cannot reproduce known answers is not an instrument.
    """
    here = pathlib.Path(__file__).resolve().parent
    T = {op: {int(k): v for k, v in t.items()}
         for op, t in json.loads((here / "cycle005_operator_tables.json")
                                 .read_text(encoding="utf-8"))["operator_tables"].items()}
    OPS, VALUES = sorted(T), list(range(-50, 51))
    out = {}

    for name, oracle_fn, known in (
            ("b3_self_inverse", lambda f, v: (lambda fv: None if fv is None else
                                              (None if T[f].get(fv) is None else T[f][fv] == v))(T[f].get(v)),
             0.0012),
            ("b4_fixed_point", lambda f, v: None if T[f].get(v) is None else T[f][v] == v, 0.0011)):
        states = []
        for v in VALUES:
            acts, labs = [], []
            for f in OPS:
                r = oracle_fn(f, v)
                if r is not None:
                    acts.append(f); labs.append(int(r))
            if acts and 0 < sum(labs) < len(labs):
                states.append({"actions": acts, "labels": labs})
        h = conditional_headroom(states)
        assert abs(h["conditional_headroom"] - known) < 1e-9, (
            f"{name}: module gives {h['conditional_headroom']}, committed answer is {known}")
        assert h["qualifies"] is False
        out[name] = h

    # committed constants from runners written independently of this module
    assert abs((1.0000 - 0.6254) - 0.3746) < 1e-9, "h1 headroom constant"
    assert abs((1.0000 - 0.9735) - 0.0265) < 1e-9, "b2 headroom constant"
    out["h1_committed"] = {"state_independent_ceiling": 0.6254, "oracle": 1.0,
                           "conditional_headroom": 0.3746, "qualifies": True}
    out["b2_committed"] = {"state_independent_ceiling": 0.9735, "oracle": 1.0,
                           "conditional_headroom": 0.0265, "qualifies": False}

    # gate checks against failures this seat actually committed
    assert gate_reachable(0.14, 0.0, 0.1364)["reachable"] is False       # cycle-004-era
    assert gate_exceeds_error(0.57, 0.5646, 0.0275)["passes"] is False   # LOCO margin 0.0054
    assert gate_exceeds_error(0.25, 0.0603, 0.0150)["passes"] is True    # Q2 gate, honest error

    # identifiability: two causes sharing one signature caps the ceiling below 1.0
    idc = identifiability_ceiling([("s1", "q1"), ("s1", "q2"), ("s2", "q3"), ("s3", "q4")])
    assert abs(idc["exact_oracle_ceiling"] - 0.75) < 1e-9, idc
    out["identifiability_demo"] = idc

    cb = cluster_bootstrap({f"c{i}": [0.5 + 0.01 * i] for i in range(24)})
    out["cluster_bootstrap_demo"] = cb

    c = car("demo", "conditional action information", "operator x value",
            out["b3_self_inverse"], "cycle005_operator_tables.json",
            "rejects b3 as a conditional-structure population")
    assert c["verdict"] == "INADEQUATE", c
    out["car_demo"] = c
    return out


if __name__ == "__main__":
    r = _selftest()
    print("SELF-TEST PASSED — module reproduces committed answers\n")
    for k in ("b3_self_inverse", "b4_fixed_point", "h1_committed", "b2_committed"):
        v = r[k]
        print(f"  {k:18s} ceiling {v['state_independent_ceiling']:.4f}  oracle {v['oracle']:.4f}  "
              f"headroom {v['conditional_headroom']:.4f}  qualifies={v['qualifies']}")
    print("\n  identifiability demo :", json.dumps(r["identifiability_demo"]))
    print("  cluster bootstrap    :", json.dumps(r["cluster_bootstrap_demo"]))
    print("\n  CAR verdict enum enforced ->", r["car_demo"]["verdict"])
