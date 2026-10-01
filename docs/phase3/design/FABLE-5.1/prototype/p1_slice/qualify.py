"""P1 calibration slice: the qualification gate, as code.

    python qualify.py            # runs everything, writes RECEIPT_qualify.json
                                 # exit 0 only if the gate is satisfied

What it shows, in miniature (REQUIREMENTS.md ids in brackets):

  A  the BUILD ruler sorts the calibration set: graded positives, the negative
     and the impostors [MEAS-02, section 1.3]
  B  known-answer recovery at graded effect sizes, and the ruler's sensitivity
     at this sample size [SCI-05, MEAS-01]
  C  the causal rulers recover a known carrier and reject a known bystander
     and a sham [CAUS-01, CAUS-03]
  D  the harness really controls the stores [ORG-02]
  E  the world does not leak [WLD-05]
  F  every control above can FAIL: fire tests [MEAS-02]
  G  measured throughput of this kernel [COMP-01]

EXPECTED below was written before the first run and committed in its own
commit (see PREREG.md). The gate compares what happened with it. A mismatch
anywhere fails the gate; nothing is "explained" afterwards.
"""
import hashlib
import json
import pathlib
import platform
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction

import numba
import numpy as np

import organisms as org
import rulers as ru
import wm_mini as wm
from rulers import FAIL, INDETERMINATE, PASS

HERE = pathlib.Path(__file__).resolve().parent
ALPHA = Fraction(1, 10 ** 6)
DELTA = Fraction(1, 20)
VERSION = 2              # v1 failed its gate: see PREREG_v2.md
N_LIVES = 2400           # sealed lives for section A (v1: 1200)
N_PAIRS = 500            # sealed life pairs for interchange (v1: 250)
BASE = ru.SEALED_BASE + 5_000_000    # v2 uses sealed lives that v1 never touched
MIN_POWER = Fraction(99, 100)        # every preregistered verdict must be attainable with this power
SPLIT = 4                # episode boundary at which interventions happen
TRAIN_LIFE_OF_LOOKUP = 7

# ------------------------------------------------------------------ preregistered expectations
EXPECTED = {
    "A_build": {
        "builder(8)": PASS, "builder(6)": PASS, "builder(4)": PASS, "builder(2)": PASS,
        "builder(0)": FAIL, "holder(8)": FAIL, "constant": FAIL, "lookup": FAIL, "leak_reader": FAIL,
    },
    "A_hold": {
        "builder(8)": PASS, "builder(6)": PASS, "builder(4)": PASS, "builder(2)": PASS,
        "builder(0)": FAIL, "holder(8)": PASS, "constant": FAIL, "lookup": FAIL, "leak_reader": FAIL,
    },
    "A_novel": "PASS for every organism",
    "B_known_answer": "probes with s < m all correct; probes with s >= m consistent with 1/R; "
                      "certified lower bound never above the true value m/K + (1 - m/K)/R",
    "C_interchange": {"builder(8)": "FLIP", "holder(8)": "NO-EFFECT", "builder(8) sham": "NO-EFFECT"},
    "C_lesion": {"builder(8) used cells": FAIL, "builder(8) unused cells": PASS},
    "D_reset_equivalence": {"builder(8)": PASS, "holder(8)": PASS},
    "E_leak_probe": PASS,
    "F_fire_tests": "all fire",
}


def c_pairs():
    return [(BASE + 200_000 + 2 * i, BASE + 200_001 + 2 * i) for i in range(N_PAIRS)]


def c_lives():
    return range(BASE + 300_000, BASE + 300_000 + 2 * N_PAIRS)


def power_gate(P):
    """MEAS-08 as a gate. From the schedules alone (no organism), count the
    eligible trials of every preregistered verdict and compute the exact
    probability of obtaining that verdict if the organism is what it was
    designed to be. Refuse to run if any is below MIN_POWER.

    For the graded builders the count is treated as Binomial(n, p(m)). The true
    count has a fixed part and so a smaller variance, which makes this
    conservative.
    """
    cen = ru.census_types(P, BASE, N_LIVES)
    n_inter = ru.census_interchange(P, c_pairs(), SPLIT)
    n_les = ru.census_lesion(P, c_lives(), SPLIT)
    chance = Fraction(1, P.R)

    def pm(m):
        return Fraction(m, P.K) + (1 - Fraction(m, P.K)) * chance

    true_build = {"builder(8)": pm(8), "builder(6)": pm(6), "builder(4)": pm(4), "builder(2)": pm(2),
                  "builder(0)": chance, "holder(8)": chance, "constant": chance, "lookup": chance,
                  "leak_reader": chance}
    true_hold = dict(true_build)
    true_hold["holder(8)"] = Fraction(1)
    rows = []
    for name, exp in EXPECTED["A_build"].items():
        rows.append(("A build " + name, cen["probe"], exp, true_build[name]))
    for name, exp in EXPECTED["A_hold"].items():
        rows.append(("A hold " + name, cen["repeat"], exp, true_hold[name]))
    lab = {"FLIP": PASS, "NO-EFFECT": FAIL}
    inter_true = {"builder(8)": Fraction(1), "holder(8)": chance, "builder(8) sham": chance}
    for name, exp in EXPECTED["C_interchange"].items():
        rows.append(("C interchange " + name, n_inter, lab[exp], inter_true[name]))
    les_true = {"builder(8) used cells": chance, "builder(8) unused cells": Fraction(1)}
    for name, exp in EXPECTED["C_lesion"].items():
        rows.append(("C lesion " + name, n_les, exp, les_true[name]))
    table, ok = [], True
    cache = {}
    for name, n, exp, p in rows:
        key = (n, exp, p)
        if key not in cache:
            cache[key] = ru.power(n, P.R, exp, p, ALPHA, DELTA)
        pw = cache[key]
        ok &= pw >= MIN_POWER
        table.append({"cell": name, "eligible": n, "expected": exp, "designed_true_rate": float(p),
                      "power": float(pw), "adequate": bool(pw >= MIN_POWER)})
    return {"census": cen, "interchange_eligible": n_inter, "lesion_eligible": n_les,
            "min_power_required": float(MIN_POWER), "table": table}, bool(ok)


def calibration_set(P):
    return {
        "builder(8)": (org.builder(8), org.empty_store(P.S)),
        "builder(6)": (org.builder(6), org.empty_store(P.S)),
        "builder(4)": (org.builder(4), org.empty_store(P.S)),
        "builder(2)": (org.builder(2), org.empty_store(P.S)),
        "builder(0)": (org.builder(0), org.empty_store(P.S)),
        "holder(8)": (org.holder(8), org.empty_store(P.S)),
        "constant": (org.constant(), org.empty_store(P.S)),
        "lookup": (org.lookup(), org.lookup_store(P.seed, TRAIN_LIFE_OF_LOOKUP, P.K, P.R, P.S)),
        "leak_reader": (org.leak_reader(), org.empty_store(P.S)),
    }


def section_a(P, ruler_R=None, **kw):
    """BUILD and HOLD verdicts for the calibration set on sealed lives.
    ruler_R lets a fire test hand the ruler a wrong null (R it does not have)."""
    R = P.R if ruler_R is None else ruler_R
    out = {}
    for name, (prog, st) in calibration_set(P).items():
        ev = ru.evaluate(prog, st, P, BASE, N_LIVES, **kw)
        c = ev["counts"]
        out[name] = {
            "build": ru.class_exclusion(int(c[wm.T_PROBE, 0]), int(c[wm.T_PROBE, 1]), R, ALPHA, DELTA),
            "hold": ru.class_exclusion(int(c[wm.T_REPEAT, 0]), int(c[wm.T_REPEAT, 1]), R, ALPHA, DELTA),
            "novel": ru.novel_sanity(int(c[wm.T_NOVEL, 0]), int(c[wm.T_NOVEL, 1]), R, ALPHA),
            "probe_accuracy": float(c[wm.T_PROBE, 1]) / max(1, int(c[wm.T_PROBE, 0])),
        }
    return out


def table_matches(a):
    ok = True
    for name, v in a.items():
        ok &= v["build"]["verdict"] == EXPECTED["A_build"][name]
        ok &= v["hold"]["verdict"] == EXPECTED["A_hold"][name]
        ok &= v["novel"]["verdict"] == PASS
    return bool(ok)


def section_b(P, a):
    """Known-answer recovery with graded positives, and the ruler's sensitivity."""
    res, ok = {}, True
    for m in (0, 2, 4, 6, 8):
        n_lo = k_lo = n_hi = k_hi = 0
        for life in range(BASE + 100_000, BASE + 100_300):
            L = ru.Life(org.builder(m), org.empty_store(P.S), life, P).run(P.E)
            for (_, _, ttype, s, _, corr) in L.rows:
                if ttype == wm.T_PROBE:
                    if s < m:
                        n_lo += 1
                        k_lo += corr
                    else:
                        n_hi += 1
                        k_hi += corr
        stored_all_correct = (k_lo == n_lo)
        p0 = Fraction(1, P.R)
        guess_consistent = (n_hi == 0) or (ru.tail_ge(n_hi, k_hi, p0) > Fraction(1, 1000)
                                           and ru.tail_le(n_hi, k_hi, p0) > Fraction(1, 1000))
        true_p = Fraction(m, P.K) + (1 - Fraction(m, P.K)) * p0
        lb = a["builder(%d)" % m]["build"].get("lower_bound", 0.0)
        sound = lb <= float(true_p) + 1e-12
        res["m=%d" % m] = {
            "stored_probes": [n_lo, k_lo], "unstored_probes": [n_hi, k_hi],
            "predicted_accuracy": float(true_p),
            "observed_accuracy_sectionA": a["builder(%d)" % m]["probe_accuracy"],
            "certified_lower_bound": lb,
            "stored_all_correct": stored_all_correct, "guess_consistent_with_chance": bool(guess_consistent),
            "bound_sound": bool(sound),
        }
        ok &= stored_all_correct and guess_consistent and sound
    # sensitivity of the BUILD ruler at the section-A sample size
    n = a["builder(8)"]["build"]["eligible"]
    p0 = Fraction(1, P.R)
    lo, hi = 0, n
    while hi - lo > 1:                      # smallest k with P(X >= k | chance) <= alpha
        mid = (lo + hi) // 2
        if ru.tail_ge(n, mid, p0) <= ALPHA:
            hi = mid
        else:
            lo = mid
    k_star = hi
    lo, hi = 256, 1024                      # smallest p (grid 1/1024) detected with power >= 0.8
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ru.tail_ge(n, k_star, Fraction(mid, 1024)) >= Fraction(4, 5):
            hi = mid
        else:
            lo = mid
    mde = hi / 1024.0
    res["sensitivity"] = {"eligible": n, "pass_threshold_k": k_star, "pass_threshold_accuracy": k_star / n,
                          "minimum_detectable_accuracy_power_0.8": mde, "chance": float(p0),
                          "false_positive_rate_bound": float(ALPHA)}
    return res, bool(ok)


def section_c(P):
    pairs, lives = c_pairs(), c_lives()
    e = org.empty_store(P.S)
    inter = {
        "builder(8)": ru.interchange(org.builder(8), e, P, pairs, SPLIT),
        "holder(8)": ru.interchange(org.holder(8), e, P, pairs, SPLIT),
        "builder(8) sham": ru.interchange(org.builder(8), e, P, pairs, SPLIT, sham=True),
    }
    les = {
        "builder(8) used cells": ru.lesion(org.builder(8), e, P, lives, SPLIT, range(0, P.K)),
        "builder(8) unused cells": ru.lesion(org.builder(8), e, P, lives, SPLIT, range(P.K, P.S)),
    }
    ok = all(inter[k]["label"] == v for k, v in EXPECTED["C_interchange"].items())
    ok &= all(les[k]["verdict"] == v for k, v in EXPECTED["C_lesion"].items())
    return {"interchange": inter, "lesion": les}, bool(ok)


def section_d(P):
    lives = range(BASE + 400_000, BASE + 400_100)
    e = org.empty_store(P.S)
    res = {"builder(8)": ru.reset_equivalence(org.builder(8), e, P, lives, SPLIT),
           "holder(8)": ru.reset_equivalence(org.holder(8), e, P, lives, SPLIT)}
    return res, all(res[k]["verdict"] == v for k, v in EXPECTED["D_reset_equivalence"].items())


def section_e(P):
    res = ru.leak_probe(P, range(0, 400), range(BASE + 500_000, BASE + 500_400))
    return res, res["verdict"] == EXPECTED["E_leak_probe"]


def section_f(P, a_clean):
    """Fire tests. Each breaks one thing on purpose and records whether the
    control built to catch it did."""
    e = org.empty_store(P.S)
    f = {}

    # FT1 a harness that does not reset fast memory. The BUILD ruler alone is fooled
    # (the holder now passes); the reset-equivalence check must catch the harness.
    ev = ru.evaluate(org.holder(8), e, P, BASE, N_LIVES, reset_fmem=False)
    c = ev["counts"]
    fooled = ru.class_exclusion(int(c[wm.T_PROBE, 0]), int(c[wm.T_PROBE, 1]), P.R, ALPHA, DELTA)
    chk = ru.reset_equivalence(org.holder(8), e, P, range(BASE + 400_000, BASE + 400_100),
                               SPLIT, reset_fmem=False)
    f["FT1_broken_reset"] = {"build_ruler_on_holder": fooled["verdict"], "reset_equivalence": chk,
                             "fired": fooled["verdict"] == PASS and chk["verdict"] == FAIL,
                             "note": "the ruler alone says PASS here; only the harness check exposes it"}

    # FT2 a world whose observation is the answer.
    ev = ru.evaluate(org.leak_reader(), e, P, BASE, N_LIVES, leaky=True)
    c = ev["counts"]
    nov = ru.novel_sanity(int(c[wm.T_NOVEL, 0]), int(c[wm.T_NOVEL, 1]), P.R, ALPHA)
    probe = ru.leak_probe(P, range(0, 400), range(BASE + 500_000, BASE + 500_400), leaky=True)
    f["FT2_leaky_world"] = {"novel_sanity": nov, "leak_probe": probe,
                            "fired": nov["verdict"] == FAIL and probe["verdict"] == FAIL}

    # FT3 reporting on a life the organism was built from (selection on the evaluation set).
    try:
        ru.evaluate(org.lookup(), org.lookup_store(P.seed, TRAIN_LIFE_OF_LOOKUP, P.K, P.R, P.S),
                    P, TRAIN_LIFE_OF_LOOKUP, 1)
        refused = False
    except ru.SealedSetViolation:
        refused = True
    try:
        ru.require_unsealed(ru.SEALED_BASE, 1)
        refused2 = False
    except ru.SealedSetViolation:
        refused2 = True
    bypass = ru.evaluate(org.lookup(), org.lookup_store(P.seed, TRAIN_LIFE_OF_LOOKUP, P.K, P.R, P.S),
                         P, TRAIN_LIFE_OF_LOOKUP, 1, sealed=False)["counts"]
    f["FT3_sealed_guard"] = {"report_on_training_life_refused": refused, "search_on_sealed_life_refused": refused2,
                             "if_bypassed_novel_trials": [int(bypass[wm.T_NOVEL, 0]), int(bypass[wm.T_NOVEL, 1])],
                             "fired": refused and refused2,
                             "note": "bypassing the guard gives 8 of 8 on never-seen stimuli in the training life"}

    # FT4 a ruler handed the wrong null (it believes there are 8 responses, so chance is 1/8).
    wrong = section_a(P, ruler_R=8)
    f["FT4_wrong_null"] = {"constant_build_verdict_under_wrong_null": wrong["constant"]["build"]["verdict"],
                           "calibration_table_matches": table_matches(wrong),
                           "fired": not table_matches(wrong)}

    # FT5 a loader that admits nothing must not read as a pass.
    empty = ru.class_exclusion(0, 0, P.R, ALPHA, DELTA)
    f["FT5_empty_input"] = {"verdict": empty["verdict"], "fired": empty["verdict"] == INDETERMINATE}

    # FT6 channel test: fabricated records straight into the ruler; all three verdicts attainable.
    ch = [ru.class_exclusion(4000, k, P.R, ALPHA, DELTA)["verdict"] for k in (4000, 1000, 1100)]
    f["FT6_channel"] = {"records_k_of_4000": [4000, 1000, 1100], "verdicts": ch,
                        "fired": ch == [PASS, FAIL, INDETERMINATE]}

    # FT7 the store affordance switched off: the positive control must stop passing.
    ev = ru.evaluate(org.builder(8), e, P, BASE, N_LIVES, aff_store=False)
    c = ev["counts"]
    off = ru.class_exclusion(int(c[wm.T_PROBE, 0]), int(c[wm.T_PROBE, 1]), P.R, ALPHA, DELTA)
    f["FT7_affordance_off"] = {"builder8_build_verdict_without_store_writes": off["verdict"],
                               "fired": off["verdict"] == FAIL and a_clean["builder(8)"]["build"]["verdict"] == PASS}

    # FT8 the power gate itself must be able to refuse. The eligible counts of the v1 design
    # (the run whose gate failed) are fed to it: it must call all three bounded cells underpowered.
    chance = Fraction(1, P.R)
    v1 = {"interchange NO-EFFECT (n=2785)": 2785, "hold FAIL (n=2879)": 2879, "lesion FAIL (n=3670)": 3670}
    pw = {k: float(ru.power(n, P.R, FAIL, chance, ALPHA, DELTA)) for k, n in v1.items()}
    f["FT8_power_gate_refuses_v1"] = {"power_at_v1_sample_sizes": pw,
                                      "fired": all(v < float(MIN_POWER) for v in pw.values())}

    return f, all(v["fired"] for v in f.values())


def throughput(P):
    prog, st = org.builder(8), org.empty_store(P.S)
    ru.evaluate(prog, st, P, BASE, 64)                              # compile
    runs = []
    for i in range(3):
        t = time.perf_counter()
        ev = ru.evaluate(prog, st, P, BASE + 1_000_000 + i * 400_000, 400_000)
        runs.append((time.perf_counter() - t, ev["instr"]))
    dt, instr = sorted(runs)[1]                                      # median of three
    return {"lives": 400_000, "instructions": instr, "seconds": round(dt, 3),
            "instructions_per_second": round(instr / dt), "lives_per_second": round(400_000 / dt),
            "threads": numba.get_num_threads(),
            "note": "organism instructions only; world stepping and scoring are included in the time"}


def source_hashes():
    out = {}
    for name in ("wm_mini.py", "oracle.py", "organisms.py", "rulers.py", "qualify.py", "differential_test.py"):
        data = (HERE / name).read_bytes().replace(b"\r\n", b"\n")
        out[name] = hashlib.sha256(data).hexdigest()
    return out


def main():
    P = ru.Params()
    t0 = time.perf_counter()
    pg, pg_ok = power_gate(P)
    print("0  power gate (computed from schedules alone, before any organism runs)")
    for row in pg["table"]:
        print("   %-38s n=%5d  expect %-13s power %.6f %s" % (
            row["cell"], row["eligible"], row["expected"], row["power"], "" if row["adequate"] else " <-- UNDERPOWERED"))
    print("   every preregistered verdict attainable with power >= %.2f: %s" % (float(MIN_POWER), pg_ok))
    if "--power-only" in sys.argv:
        return 0 if pg_ok else 2
    if not pg_ok:
        print("REFUSED: underpowered design. Nothing was run.")
        return 2
    a = section_a(P)
    a_ok = table_matches(a)
    b, b_ok = section_b(P, a)
    c, c_ok = section_c(P)
    d, d_ok = section_d(P)
    e, e_ok = section_e(P)
    f, f_ok = section_f(P, a)
    g = throughput(P)
    gate = a_ok and b_ok and c_ok and d_ok and e_ok and f_ok

    print("A  calibration set (%d sealed lives): BUILD / HOLD / novel-trial check" % N_LIVES)
    for name, v in a.items():
        print("   %-12s probes %4d/%4d = %.3f  BUILD %-13s HOLD %-13s novel %s%s" % (
            name, v["build"]["fired"], v["build"]["eligible"], v["probe_accuracy"],
            v["build"]["verdict"], v["hold"]["verdict"], v["novel"]["verdict"],
            "  certified >= %.3f (%.2f bits)" % (v["build"]["lower_bound"], v["build"]["certified_bits"])
            if v["build"]["verdict"] == PASS else ""))
    print("   table matches the preregistered table: %s" % a_ok)
    print("B  known-answer recovery")
    for m in (0, 2, 4, 6, 8):
        r = b["m=%d" % m]
        print("   m=%d predicted %.4f observed %.4f lower bound %.4f  stored %s  unstored %s  ok=%s" % (
            m, r["predicted_accuracy"], r["observed_accuracy_sectionA"], r["certified_lower_bound"],
            r["stored_probes"], r["unstored_probes"],
            r["stored_all_correct"] and r["guess_consistent_with_chance"] and r["bound_sound"]))
    s = b["sensitivity"]
    print("   sensitivity at n=%d: PASS needs accuracy >= %.4f; detects accuracy %.4f with power 0.8; chance %.2f" % (
        s["eligible"], s["pass_threshold_accuracy"], s["minimum_detectable_accuracy_power_0.8"], s["chance"]))
    print("C  causal rulers")
    for k, v in c["interchange"].items():
        print("   interchange %-16s %-10s followed donor %d of %d (own %d)" % (
            k, v["label"], v["followed_donor"], v["eligible"], v["followed_own"]))
    for k, v in c["lesion"].items():
        print("   lesion      %-24s still above bound: %-5s (%d of %d correct)" % (k, v["verdict"], v["fired"], v["eligible"]))
    print("D  reset equivalence: %s" % {k: (v["verdict"], v["fired"], v["eligible"]) for k, v in d.items()})
    print("E  leak probe (clean world): %s (%d of %d)" % (e["verdict"], e["fired"], e["eligible"]))
    print("F  fire tests")
    for k, v in f.items():
        print("   %-22s %s" % (k, "fires" if v["fired"] else "DID NOT FIRE"))
    print("G  throughput: %.1f M organism instructions/s, %d lives/s on %d threads" % (
        g["instructions_per_second"] / 1e6, g["lives_per_second"], g["threads"]))
    print("GATE:", "PASS" if gate else "FAIL", "(A %s, B %s, C %s, D %s, E %s, F %s)  %.1f s" % (
        a_ok, b_ok, c_ok, d_ok, e_ok, f_ok, time.perf_counter() - t0))

    receipt = {
        "what": "P1 calibration slice prototype: qualification gate",
        "version": VERSION, "amends": "v1 gate FAILED (C interchange holder: INDETERMINATE); see PREREG_v2.md",
        "power_gate": pg,
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": platform.python_version(),
        "numba": numba.__version__, "numpy": np.__version__,
        "params": P.as_dict(), "alpha": str(ALPHA), "delta": str(DELTA),
        "n_lives": N_LIVES, "n_pairs": N_PAIRS, "split": SPLIT,
        "source_sha256_lf": source_hashes(),
        "expected": EXPECTED,
        "A": a, "A_matches": a_ok, "B": b, "B_ok": b_ok, "C": c, "C_ok": c_ok,
        "D": d, "D_ok": d_ok, "E": e, "E_ok": e_ok, "F": f, "F_ok": f_ok, "G": g,
        "gate": "PASS" if gate else "FAIL",
    }

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple, range)):
            return [clean(v) for v in o]
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return o

    (HERE / "RECEIPT_qualify.json").write_text(json.dumps(clean(receipt), indent=1, sort_keys=True) + "\n",
                                               encoding="utf-8", newline="\n")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
