"""Run the failure convergence probe and print the table. Hermes, 2026-09-11.

    python roles/Hermes/science/convergence/probe.py

Reads observations.json, computes every signature strategy over every
observation, and reports for each case how many DISTINCT keys the observers
would independently have produced. The number that matters is:

    keys == 1   the second observer would have found the first
    keys == n   every observer opens its own record (today's behaviour)

Also emits, per case, the operator's classification:

    EXACT             one key with no normalization (s0)
    NORMALIZABLE      one key after the named deterministic rules (s2/s3)
    RELATED-NOT-SAME  the case is one family, and the signatures correctly
                      keep it as several incidents
    UNSIGNABLE        the point-of-failure evidence cannot establish identity
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import signature as S                                            # noqa: E402

SEATS = S.seat_names()


def keys_for(case, strategy):
    fn = S.STRATEGIES[strategy]
    out = {}
    for o in case["observations"]:
        obs = o["observed"]
        k = fn(obs, seats=SEATS) if strategy in ("s2_normalized", "s3_normalized_plus_input") else fn(obs)
        out.setdefault(k, []).append(o["observer"])
    return out


def scored_observations(case):
    """Rows whose point-of-failure text actually survives. A paraphrase is
    not an observation; counting it would flatter the result."""
    return [o for o in case["observations"] if not o.get("paraphrased")]


def classify(case):
    scored = scored_observations(case)
    n = len(scored)
    if n < 2:
        return "UNSIGNABLE", "fewer than two point-of-failure records survive ({} of {})".format(
            n, len(case["observations"]))
    sub = {"id": case["id"], "observations": scored}
    raw = keys_for(sub, "s0_raw")
    norm = keys_for(sub, "s2_normalized")
    with_input = keys_for(sub, "s3_normalized_plus_input")
    if not case["same_underlying_failure"]:
        if len(with_input) == n:
            return "RELATED-NOT-SAME", ("s3 keeps all {} apart, which is correct: one family, "
                                        "different failures".format(n))
        return "RELATED-NOT-SAME", ("WARNING: s3 merges {} of {} distinct failures -- an "
                                    "over-merge".format(n - len(with_input) + 1, n))
    # SPECIFICITY GATE, added after the first run classified CASE-E as EXACT.
    # Sensitivity without specificity is the trap: a key that also matches a
    # non-failure is not an identity, however perfectly the observers agree.
    hit = collides_with_a_control(case)
    if hit and hit["control_kind"] == "non_failure":
        return "UNSIGNABLE", ("{} observers converge, but the key also matches {}, which is not a "
                              "failure at all -- sensitivity without specificity".format(n, hit["id"]))
    if hit and hit["control_kind"] == "different_failure":
        return "UNSIGNABLE", ("false merge: the key also matches {}, a different failure".format(hit["id"]))
    if len(raw) == 1:
        return "EXACT", "{} observers, one key with no normalization".format(n)
    if len(norm) == 1:
        scope = ""
        if hit and hit["control_kind"] == "different_cause_same_symptom":
            scope = ("; SYMPTOM-SCOPED -- {} shows this key names a symptom with more than one "
                     "cause, so the incident must keep observations independent and be "
                     "splittable".format(hit["id"]))
        return "NORMALIZABLE", "{} raw keys -> 1 after N1+N2+N3+N4{}".format(len(raw), scope)
    return "UNSIGNABLE", "{} observers still produce {} keys after normalization".format(n, len(norm))


def collides_with_a_control(case):
    """True when some control row that is NOT an instance of this case
    produces one of the case's keys."""
    ctl = json.loads((Path(__file__).resolve().parent / "controls.json").read_text(
        encoding="utf-8"))["controls"]
    scored = scored_observations(case)
    k2 = {S.s2_normalized(o["observed"], seats=SEATS) for o in scored}
    k3 = {S.s3_normalized_with_missing_input(o["observed"], seats=SEATS) for o in scored}
    worst = None
    order = {"non_failure": 0, "different_failure": 1, "different_cause_same_symptom": 2}
    for c in ctl:
        if c["must_not_match"] != case["id"]:
            continue
        if (S.s2_normalized(c["observed"], seats=SEATS) in k2
                or S.s3_normalized_with_missing_input(c["observed"], seats=SEATS) in k3):
            if worst is None or order[c["control_kind"]] < order[worst["control_kind"]]:
                worst = c
    return worst


def main():
    cases = S.load_cases()
    print("FAILURE CONVERGENCE PROBE -- Hermes 2026-09-11")
    print("=" * 78)
    print("seat roster size used by N2: {}".format(len(SEATS)))
    print()
    summary = []
    for c in cases:
        scored = scored_observations(c)
        print("{}  [{}]".format(c["id"], c["class"]))
        print("  {}".format(c["title"]))
        print("  observers: {} total, {} with a surviving point-of-failure record".format(
            len(c["observations"]), len(scored)))
        print("  {:<28} {:>6}  {}".format("strategy", "keys", "grouping"))
        for name in ("s0_raw", "s1_type_only", "s2_normalized", "s3_normalized_plus_input"):
            g = keys_for({"observations": scored}, name)
            groups = " | ".join(",".join(v) for v in g.values())
            print("  {:<28} {:>6}  {}".format(name, len(g), groups[:120]))
        verdict, why = classify(c)
        print("  VERDICT: {} -- {}".format(verdict, why))
        print()
        summary.append((c["id"], c["class"], verdict, len(scored)))
    print("=" * 78)
    print("{:<9} {:<34} {:<18} {}".format("case", "class", "verdict", "scored observers"))
    for cid, cls, v, n in summary:
        print("{:<9} {:<34} {:<18} {}".format(cid, cls[:33], v, n))
    out = Path(__file__).resolve().parent / "probe_results.json"
    out.write_text(json.dumps(
        {"generated": "2026-09-11", "roster_size": len(SEATS),
         "cases": [{"id": cid, "class": cls, "verdict": v, "scored_observers": n}
                   for cid, cls, v, n in summary]}, indent=2), encoding="utf-8")
    print("\nrows written to {}".format(out.relative_to(S.REPO).as_posix()))


# ------------------------------------------------------ SPECIFICITY ---------
# Sensitivity alone rewards a signature that merges everything (s1_type_only
# converges every case above and is worthless). These rows ask the other
# question: does the key also match something that is NOT this failure?

def specificity():
    import json as _j
    ctl = _j.loads((Path(__file__).resolve().parent / "controls.json").read_text(encoding="utf-8"))["controls"]
    cases = {c["id"]: c for c in S.load_cases()}
    print()
    print("SPECIFICITY -- does the key also match a non-instance?")
    print("=" * 78)
    print("{:<7} {:<9} {:<34} {}".format("ctl", "vs case", "what it is", "s2 / s3 collision"))
    rows = []
    for c in ctl:
        case = cases[c["must_not_match"]]
        scored = scored_observations(case)
        case_keys_s2 = {S.s2_normalized(o["observed"], seats=SEATS) for o in scored}
        case_keys_s3 = {S.s3_normalized_with_missing_input(o["observed"], seats=SEATS) for o in scored}
        k2 = S.s2_normalized(c["observed"], seats=SEATS)
        k3 = S.s3_normalized_with_missing_input(c["observed"], seats=SEATS)
        hit2, hit3 = k2 in case_keys_s2, k3 in case_keys_s3
        expected = c.get("expected_collision", False)
        mark = "COLLIDES" if (hit2 or hit3) else "clean"
        flag = "" if (hit2 or hit3) == expected else "  <-- UNEXPECTED"
        if expected and (hit2 or hit3):
            mark += " (expected, and it is the finding)"
        print("{:<7} {:<9} {:<34} {}{}".format(c["id"], c["must_not_match"], c["title"][:33], mark, flag))
        rows.append({"id": c["id"], "vs": c["must_not_match"], "s2_collision": hit2,
                     "s3_collision": hit3, "expected": expected})
    print()
    unexpected = [r for r in rows if (r["s2_collision"] or r["s3_collision"]) != r["expected"]]
    print("unexpected results: {}".format(len(unexpected) if unexpected else "none"))
    out = Path(__file__).resolve().parent / "specificity_results.json"
    out.write_text(json.dumps({"generated": "2026-09-11", "controls": rows}, indent=2), encoding="utf-8")
    print("rows written to {}".format(out.relative_to(S.REPO).as_posix()))
    return rows


if __name__ == "__main__":
    main()
    specificity()
