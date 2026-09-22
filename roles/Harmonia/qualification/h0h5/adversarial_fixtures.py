"""Nine adversarial fixtures every H0-H5 lane must pass.  AF-1.1.0  2026-09-18.

Each fixture GENERATES a run record carrying one known defect, and each
detector is a mechanical predicate over that record. No LLM verdict appears
anywhere: every detector is an equality, a count, a sign, or a rate.

    F1 planted leak            the arm answers without consulting the oracle
    F2 wrong artifact          consumed bytes are not the sealed bytes
    F3 invalid witness         a claimed counterexample does not falsify
    F4 swapped labels          arm labels exchanged
    F5 exhausted run           budget exhaustion dropped from the denominator
    F6 no-effect synthetic     identical arms must not read as support
    F7 degenerate replicate    bit-identical replays offered as replicates       (AF-1.1.0)
    F8 structural floor        a corpus whose units sit on the attainable bound   (AF-1.1.0)
    F9 non-exchangeable rows   a trended region read against an i.i.d. null       (AF-1.1.0)

AF-1.1.0 (HARM-04, Harmonia[m2-ca1148a0]) adds F7-F9, each run TWICE: once with
the defect (must fire) and once on a clean control (must be silent). A detector
that fires on everything detects nothing; the silence is half the fixture.

WHY F4 NEEDS A SIGNED POSITIVE CONTROL, and this is the load-bearing point.
Swapping labels on a NO-EFFECT dataset is undetectable in principle -- that is
exactly what an exchangeability null asserts. So a symmetric fixture cannot
catch F4, and a battery built only from symmetric fixtures would pass while
blind to it. F4 is therefore run against a fixture with a PLANTED EFFECT OF
DECLARED SIGN, and the detector fires on sign reversal. This is the same
asymmetry the NK/CA packet applies when it refuses a symmetric negative
fixture, and the same one-sidedness that makes an invariance null prove a
defect on failure but never prove capability on success.
"""
from __future__ import annotations

import hashlib
import random

from qualification_rules import (SUPPORTED, paired_contrast, h0_estimands)

FIXTURES_VERSION = "AF-1.1.0"


def _digest(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ F1 leak

def f1_planted_leak(rng):
    """An arm that reads target labels solves tasks it never queried."""
    rows = []
    for i in range(40):
        honest = rng.random() < 0.35
        rows.append({"task": i, "arm": "control", "solved": honest,
                     "oracle_calls": rng.randint(1, 20),
                     "termination": "COMPLETE"})
    for i in range(40):
        rows.append({"task": i, "arm": "leaky", "solved": True,
                     "oracle_calls": 0,            # the tell
                     "termination": "COMPLETE"})
    return rows


def detect_f1(rows, exhaustive_ceiling=0.60):
    """Two independent mechanical tells; either fires."""
    hits = []
    solved_without_oracle = [r for r in rows if r["solved"] and r["oracle_calls"] == 0]
    if solved_without_oracle:
        hits.append("solved_with_zero_oracle_calls n=%d" % len(solved_without_oracle))
    for arm in sorted({r["arm"] for r in rows}):
        a = [r for r in rows if r["arm"] == arm]
        frac = sum(r["solved"] for r in a) / len(a)
        if frac > exhaustive_ceiling:
            hits.append("arm %s solve fraction %.3f exceeds attainable ceiling %.2f"
                        % (arm, frac, exhaustive_ceiling))
    return hits


# -------------------------------------------------------- F2 wrong artifact

def f2_wrong_artifact(rng):
    sealed = b"the-declared-component-library-bytes"
    served = b"a-different-library-entirely!!"
    return {"sealed_slot": {"name": "component_library",
                            "digest": _digest(sealed),
                            "expected_bytes": len(sealed)},
            "load_receipt": {"digest": _digest(served),
                             "actual_bytes": len(served)}}


def detect_f2(rec):
    hits = []
    s, r = rec["sealed_slot"], rec["load_receipt"]
    if s["digest"] != r["digest"]:
        hits.append("consumed digest %s != sealed digest %s"
                    % (r["digest"][:19], s["digest"][:19]))
    if s["expected_bytes"] != r["actual_bytes"]:
        hits.append("consumed %d bytes, sealed declares %d"
                    % (r["actual_bytes"], s["expected_bytes"]))
    return hits


# -------------------------------------------------------- F3 invalid witness

def _spec(x):                       # the task: 3-input parity
    return (x & 1) ^ ((x >> 1) & 1) ^ ((x >> 2) & 1)


def _candidate(x):                  # a wrong program: ignores bit 2
    return (x & 1) ^ ((x >> 1) & 1)


def f3_invalid_witness(rng):
    """A claimed counterexample that does not actually falsify, beside a real
    one. 'no witness alone is never solved', and a returned counterexample is
    independently revalidated."""
    return {"claims": [
        {"witness": 0b011, "claimed": "falsifies"},   # cand==spec here: INVALID
        {"witness": 0b100, "claimed": "falsifies"},   # genuinely falsifies
        {"witness": None, "claimed": "solved"},       # no witness -> not solved
    ]}


def detect_f3(rec):
    hits = []
    for c in rec["claims"]:
        w = c["witness"]
        if w is None:
            if c["claimed"] == "solved":
                hits.append("claim of SOLVED with no witness and no exhaustive check")
            continue
        if _candidate(w) == _spec(w):
            hits.append("witness %s claimed to falsify but candidate agrees with "
                        "spec (both %d) -- INVALID_WITNESS" % (bin(w), _spec(w)))
    return hits


# --------------------------------------------------------- F4 swapped labels

def f4_swapped_labels(rng, swap=True):
    """A POSITIVE control with a DECLARED SIGN: treatment is planted better."""
    blocks = []
    for _ in range(12):
        base = rng.uniform(0.25, 0.45)
        ctrl, trt = base, base + 0.20          # declared: treatment > control
        if swap:
            ctrl, trt = trt, ctrl              # the defect
        blocks.append({"control": ctrl + rng.gauss(0, .02),
                       "treatment": trt + rng.gauss(0, .02)})
    return {"blocks": blocks, "declared_sign": +1}


def detect_f4(rec, threshold=0.05):
    diffs = [b["treatment"] - b["control"] for b in rec["blocks"]]
    est = paired_contrast("positive_control", diffs, n_primary=1)
    hits = []
    if rec["declared_sign"] > 0 and est.hi < 0:
        hits.append("positive control recovered with REVERSED sign: "
                    "point %.3f CI [%.3f, %.3f], declared sign +1"
                    % (est.point, est.lo, est.hi))
    if rec["declared_sign"] > 0 and est.decide(threshold) != SUPPORTED:
        hits.append("positive control failed to read as SUPPORTED (%s)"
                    % est.decide(threshold))
    return hits


# -------------------------------------------------------- F5 exhausted run

def f5_exhausted_run(rng):
    """Budget-exhausted runs silently dropped from the denominator."""
    assigned = 50
    rows = []
    for i in range(assigned):
        if i < 12:
            rows.append({"task": i, "termination": "BUDGET_EXHAUSTED",
                         "solved": False, "reported": False})   # the defect
        else:
            rows.append({"task": i, "termination": "COMPLETE",
                         "solved": rng.random() < 0.4, "reported": True})
    return {"assigned": assigned, "rows": rows}


def detect_f5(rec):
    hits = []
    reported = [r for r in rec["rows"] if r["reported"]]
    if len(reported) != rec["assigned"]:
        hits.append("denominator %d != assigned %d; %d run(s) dropped"
                    % (len(reported), rec["assigned"], rec["assigned"] - len(reported)))
    censored = [r for r in rec["rows"] if r["termination"] == "BUDGET_EXHAUSTED"]
    scored_as_failure = [r for r in censored if r["solved"] is False and not r["reported"]]
    if scored_as_failure:
        hits.append("%d BUDGET_EXHAUSTED run(s) scored as failure and excluded; "
                    "exhaustion is CENSORED and stays in the denominator"
                    % len(scored_as_failure))
    naive = sum(r["solved"] for r in reported) / max(1, len(reported))
    honest = sum(r["solved"] for r in rec["rows"]) / rec["assigned"]
    if abs(naive - honest) > 1e-9:
        hits.append("solve fraction %.3f on the truncated denominator vs %.3f on "
                    "all assigned tasks (+%.1f pp inflation)"
                    % (naive, honest, 100 * (naive - honest)))
    return hits


# ------------------------------------------------------ F6 no-effect dataset

def f6_no_effect(rng, n_blocks=12):
    """Four identical cells. Must never read as SUPPORT above the alpha rate."""
    blocks = []
    for _ in range(n_blocks):
        base = rng.uniform(0.25, 0.55)
        blocks.append({c: base + rng.gauss(0, .04)
                       for c in ("S00", "S10", "S01", "S11")})
    return blocks


def detect_f6(trials=4000, n_blocks=12, thresholds=(0.0, 0.05), seed=11):
    """Calibration fixture: the FALSE-SUPPORT rate over many no-effect draws.
    A single run proves nothing, so this detector is a RATE, with its SE.

    RUN AT TWO THRESHOLDS, and this is a correction to my own first version.
    At the PRACTICAL threshold the rate is structurally ~0 -- 5 pp sits about
    3 SE from zero at 12 blocks -- so a 0.0000 there is FORCED by the geometry
    and demonstrates nothing about the detector. That is the degenerate control
    I shipped in SE-1: a check that cannot fire, passing.

    The load-bearing calibration is at threshold 0, where SUPPORT reduces to an
    ordinary one-sided interval and must fire at alpha/2 per contrast under
    Bonferroni (0.0125). Both are reported, and the SE-distance is reported
    beside the practical-threshold rate so nobody reads a forced zero as
    strength.
    """
    out = {}
    for thr in thresholds:
        rng = random.Random(seed)
        # AF-1.1.0 FIX: QR-1.1.0 (789ce4fdd, 09-10) renamed the estimand to
        # G_joint_treatment_S11_minus_S00 and this dict kept the QR-1.0.0 name, so
        # run_qualification.py raised KeyError here from 09-10 until 09-18; the
        # committed ledger h0h5_qualification.json (dd38720c0, 09-09) predates the
        # rename. Keyed on the estimand's own name now.
        cnt = {"G_joint_treatment_S11_minus_S00": 0, "interaction_I": 0}
        ses = {"G_joint_treatment_S11_minus_S00": [], "interaction_I": []}
        for _ in range(trials):
            g, i = h0_estimands(f6_no_effect(rng, n_blocks))
            for e in (g, i):
                ses[e.name].append(e.se)
                if e.decide(thr) == SUPPORTED:
                    cnt[e.name] += 1
        for k, v in cnt.items():
            r = v / trials
            mse = sum(ses[k]) / len(ses[k])
            out["thr=%.2f/%s" % (thr, k)] = {
                "false_support_rate": r,
                "binomial_se": math.sqrt(max(r, 1e-9) * (1 - r) / trials),
                "mean_se_of_estimate": mse,
                "threshold_distance_in_se": (thr / mse) if mse else float("inf"),
                "expected": (0.0125 if thr == 0.0 else None),
                "vacuous": thr / mse > 2.0 if mse else True,
            }
    return out


import math  # noqa: E402  (used by detect_f6)


# ------------------------------------------------------------------ battery

def run_battery(seed=20260908):
    rng = random.Random(seed)
    results = []

    def rec(name, hits, expect=True):
        detected = bool(hits)
        results.append({"fixture": name, "defect_present": expect,
                        "detected": detected, "evidence": hits,
                        "pass": detected == expect})

    rec("F1_planted_leak", detect_f1(f1_planted_leak(rng)))
    rec("F2_wrong_artifact", detect_f2(f2_wrong_artifact(rng)))
    rec("F3_invalid_witness", detect_f3(f3_invalid_witness(rng)))
    rec("F4_swapped_labels", detect_f4(f4_swapped_labels(rng, swap=True)))
    rec("F5_exhausted_run", detect_f5(f5_exhausted_run(rng)))

    # F4 control: the SAME detector on an UNSWAPPED positive control must be
    # silent. A detector that fires on everything detects nothing.
    rec("F4_control_unswapped", detect_f4(f4_swapped_labels(rng, swap=False)),
        expect=False)

    return results


# ======================================================= AF-1.1.0 fixtures

from qualification_rules import (PlanRefused, replay_attestation,        # noqa: E402
                                 refuse_replay_as_replicate)
from floor_precheck import floor_precheck, CorpusRefused                   # noqa: E402
from exchangeability import diagnose, VIOLATED, SUSPECT                    # noqa: E402


# --------------------------------------------- F7 degenerate replicate

def f7_degenerate_replicate(rng, replay=True):
    """Twelve units; with the defect, four of them are bit-identical replays of
    the same payload (same spec hash, same output bytes) offered as four
    independent units. Clean control: twelve distinct payloads."""
    rows = []
    for i in range(12):
        h = "sha256:%032x" % rng.getrandbits(128)
        rows.append({"unit": "u%02d" % i, "spec_hash": h,
                     "output_digest": "sha256:%032x" % rng.getrandbits(128),
                     "value": rng.uniform(0.2, 0.6)})
    if replay:
        for k in (3, 4, 5):                       # rows 3-5 become replays of row 2
            rows[k]["spec_hash"] = rows[2]["spec_hash"]
            rows[k]["output_digest"] = rows[2]["output_digest"]
            rows[k]["value"] = rows[2]["value"]
    return rows


def detect_f7(rows):
    hits = []
    att = replay_attestation(rows)
    for a in att:
        hits.append("payload %s appears %d times (%s); counts as %d unit"
                    % (a["payload_hash"][:19], a["n_rows"],
                       "bit-identical: attests determinism" if a["attests_determinism"]
                       else "outputs DIFFER: not deterministic, not a replicate either",
                       a["counts_as_units"]))
    try:
        refuse_replay_as_replicate(rows)
    except PlanRefused as e:
        hits.append("REFUSED as replicates: %s" % e)
    return hits


# ------------------------------------------------ F8 structural floor

def f8_structural_floor(rng, floor=True):
    """120 units. With the defect, 100 sit at the attainable bound 0.0 on every
    sample (C3-2's shape). Clean control: 120 non-degenerate units."""
    units = []
    for i in range(120):
        if floor and i < 100:
            units.append([0.0, 0.0, 0.0, 0.0])
        else:
            base = rng.uniform(0.2, 0.8)
            units.append([min(1.0, max(0.0, base + rng.gauss(0, 0.03))) for _ in range(4)])
    return units


def detect_f8(units):
    vals = [sum(s) / len(s) for s in units]
    try:
        rec = floor_precheck(vals, 0.0, 1.0, units)
    except CorpusRefused as e:
        return ["REFUSED: %s" % e]
    return [] if rec["label"] == "PASS" else ["label %s" % rec["label"]]


# --------------------------------------------- F9 non-exchangeable rows

def f9_non_exchangeable(rng, trended=True, n=12):
    """A region's rows in commit order. With the defect, a linear drift of the
    metric with committed_seq that a variance-ratio detector would read as
    dispersion. Clean control: exchangeable noise around a constant."""
    seqs = sorted(rng.sample(range(1000, 9000), n))
    if trended:
        metrics = [0.3 + 0.00005 * (s - seqs[0]) + rng.gauss(0, 0.01) for s in seqs]
    else:
        metrics = [0.4 + rng.gauss(0, 0.03) for _ in seqs]
    return seqs, metrics


def detect_f9(seqs_metrics):
    seqs, metrics = seqs_metrics
    rec = diagnose(seqs, metrics)
    if rec.label in (VIOLATED, SUSPECT):
        return ["%s: serial r %+.3f, trend explains %.0f%% of the variance, ratio inflation x%.2f; "
                "no i.i.d.-calibrated rate may be quoted for this region"
                % (rec.label, rec.serial_r, 100 * rec.trend_fraction, rec.inflation)]
    return []


def run_battery_1_1_0(seed=20260918):
    """The AF-1.0.0 battery, then F7-F9 each with its clean control."""
    results = run_battery(seed)
    rng = random.Random(seed + 1)

    def rec(name, hits, expect=True):
        detected = bool(hits)
        results.append({"fixture": name, "defect_present": expect,
                        "detected": detected, "evidence": hits,
                        "pass": detected == expect})

    rec("F7_degenerate_replicate", detect_f7(f7_degenerate_replicate(rng, replay=True)))
    rec("F7_control_distinct", detect_f7(f7_degenerate_replicate(rng, replay=False)), expect=False)
    rec("F8_structural_floor", detect_f8(f8_structural_floor(rng, floor=True)))
    rec("F8_control_clean", detect_f8(f8_structural_floor(rng, floor=False)), expect=False)
    rec("F9_non_exchangeable_rows", detect_f9(f9_non_exchangeable(rng, trended=True)))
    rec("F9_control_exchangeable", detect_f9(f9_non_exchangeable(rng, trended=False)), expect=False)
    return results
