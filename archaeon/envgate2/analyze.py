"""ENVGATE-02 analysis -- frozen with the preregistration (sha256 in PREREG.json). Reads runs/block_XX.json, writes RESULTS.json.

Endpoint: INDEPENDENT_GENETIC_ESTABLISHMENT (archaeon.lineage.core.World.genetic_establishments): a genetic lineage (glin) of random
origin (random_inflow arrival or originated from random material; never inserted) whose material reproduced outside the chamber, alive
at root_end + 3 x max_age, with peak >= 0.25 N or genetic generation depth >= 10. Host labels amplifying one glin count ONCE.

PRIMARY UNIT = BLOCK (the ENVGATE-01 lesson: arrivals inside one world are not independent). Y[b][arm] = genetic establishments.
  P1  U > BAND0         exact one-sided sign test over blocks
  P2  RRIGHT > R128     exact one-sided sign test over blocks
  P3  RRIGHT > RWEAK    exact one-sided sign test over blocks
  Holm-Bonferroni over P1..P3 at family alpha 0.05.
  PO  ordering: Page's L trend test for the frozen predicted order U > RRIGHT > RWEAK > R128 > BAND0 (within-block ranks, midranks for
      ties); p by 200,000 within-block permutations from a fixed seed; significant at 0.05.
Reported, not decisive: arrival-level paired McNemar on genetic establishments (established glin root arrival), parent-chain counts
(to show whether results depend on labels), takeover share.

PHASE C GATE (all required): attribution tests pass (recorded in PREREG), preflight PASS without waiver, INFORMATIVE (U total >= 10 and
RRIGHT+RWEAK+R128 total >= 6), PO significant, P1 Holm-significant, (P2 or P3) Holm-significant, no instrument failure.
Verdict: WINDOW_SUPPORTED (gate passes) / WINDOW_PARTIAL (P1 and PO pass, P2 and P3 fail) / WINDOW_NOT_SUPPORTED (PO not significant or
R128 >= RRIGHT in total) / UNINFORMATIVE / DESIGN_OR_INSTRUMENT_FAILURE.
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

from archaeon.envgate2 import mechanism as M

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
ORDER = ["U", "RRIGHT", "RWEAK", "R128", "BAND0"]


def tail(k, n):
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def sign(Y, X, Z):
    d = [Y[b][X] - Y[b][Z] for b in sorted(Y)]; pos = sum(x > 0 for x in d); neg = sum(x < 0 for x in d)
    return {"X": X, "Y": Z, "total_X": sum(Y[b][X] for b in Y), "total_Y": sum(Y[b][Z] for b in Y), "block_diffs": d, "pos": pos, "neg": neg, "p": tail(pos, pos + neg)}


def holm(ps, alpha=0.05):
    order = sorted(ps, key=lambda k: ps[k]); out = {}; stop = False
    for i, k in enumerate(order):
        if not stop and ps[k] <= alpha / (len(order) - i): out[k] = True
        else: stop = True; out[k] = False
    return out


def ranks(vals):
    s = sorted(range(len(vals)), key=lambda i: vals[i]); r = [0.0] * len(vals); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and vals[s[j + 1]] == vals[s[i]]: j += 1
        for k in range(i, j + 1): r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def page(Y, n_perm=200_000, seed=20260924):
    weights = list(range(len(ORDER), 0, -1))                                  # predicted rank: U highest
    rows = [ranks([Y[b][a] for a in ORDER]) for b in sorted(Y)]
    L = sum(w * r for row in rows for w, r in zip(weights, row))
    rng = random.Random(seed); ge = 0
    for _ in range(n_perm):
        Lp = 0.0
        for row in rows:
            p = row[:]; rng.shuffle(p); Lp += sum(w * r for w, r in zip(weights, p))
        ge += Lp >= L - 1e-9
    return {"L": L, "p": (ge + 1) / (n_perm + 1), "n_perm": n_perm, "seed": seed}


def analyze(blocks, expected, attribution_tests_pass: bool, preflight_pass: bool):
    fail = []
    if len(blocks) != expected: fail.append("blocks %d of %d" % (len(blocks), expected))
    Y = {}; PC = {}; arr = defaultdict(set); takeover = 0; tk_est = 0; lin = []
    for b in blocks:
        if len(set(b["pairing_sha256"].values())) != 1: fail.append("pairing mismatch block %s" % b["block"])
        Y[b["block"]] = {}; PC[b["block"]] = {}
        for a, s in b["arms"].items():
            Y[b["block"]][a] = len(s["genetic_established"]); PC[b["block"]][a] = len(s["parent_chain_established_arrivals"])
            for g in s["genetic_established"]:
                st = s["glins"][str(g)] if str(g) in s["glins"] else s["glins"][g]
                lin.append(dict(st, block=b["block"], arm=a, glin=g))
                if st.get("arrival") is not None: arr[a].add((b["block"], st["arrival"]))
            if s["final_ecology_pop"] >= 0.9 * 128: takeover += 1; tk_est += len(s["genetic_established"])
    tot = {a: sum(Y[b][a] for b in Y) for a in ORDER}
    P = {"P1_U_gt_BAND0": sign(Y, "U", "BAND0"), "P2_RRIGHT_gt_R128": sign(Y, "RRIGHT", "R128"), "P3_RRIGHT_gt_RWEAK": sign(Y, "RRIGHT", "RWEAK")} if Y else {}
    sig = holm({k: v["p"] for k, v in P.items()}) if P else {}
    for k in P: P[k]["holm_significant"] = sig[k]
    PO = page(Y) if Y else {"p": 1.0}
    informative = tot["U"] >= 10 and (tot["RRIGHT"] + tot["RWEAK"] + tot["R128"]) >= 6
    mc = {}
    for X, Z in (("U", "BAND0"), ("RRIGHT", "R128"), ("RRIGHT", "RWEAK")):
        n10 = len(arr[X] - arr[Z]); n01 = len(arr[Z] - arr[X]); mc["%s_vs_%s" % (X, Z)] = {"discordant": [n10, n01], "p": tail(n10, n10 + n01)}
    gate = {"1_attribution_tests_pass": attribution_tests_pass, "2_preflight_pass_no_waiver": preflight_pass, "3_informative": informative,
            "4_ordering_consistent_PageL": PO["p"] < 0.05, "5_BAND0_suppressed_P1": bool(P and P["P1_U_gt_BAND0"]["holm_significant"]),
            "6_RRIGHT_beats_R128_or_RWEAK": bool(P and (P["P2_RRIGHT_gt_R128"]["holm_significant"] or P["P3_RRIGHT_gt_RWEAK"]["holm_significant"])),
            "7_no_instrument_failure": not fail}
    falsifiers = {"R128_rescues_as_strongly_as_RRIGHT": tot["R128"] >= tot["RRIGHT"], "RRIGHT_and_RWEAK_similar": bool(P) and not P["P3_RRIGHT_gt_RWEAK"]["holm_significant"],
                  "BAND0_like_U": bool(P) and not P["P1_U_gt_BAND0"]["holm_significant"],
                  "ordering_dominated_by_takeovers": sum(tot.values()) > 0 and tk_est / max(1, sum(tot.values())) > 0.5,
                  "label_dependence": {a: {"genetic": tot[a], "parent_chain": sum(PC[b][a] for b in PC)} for a in ORDER}}
    if fail or not attribution_tests_pass or not preflight_pass: verdict = "DESIGN_OR_INSTRUMENT_FAILURE"
    elif not informative: verdict = "UNINFORMATIVE"
    elif all(gate.values()): verdict = "WINDOW_SUPPORTED"
    elif PO["p"] >= 0.05 or tot["R128"] >= tot["RRIGHT"]: verdict = "WINDOW_NOT_SUPPORTED"
    elif gate["5_BAND0_suppressed_P1"]: verdict = "WINDOW_PARTIAL"
    else: verdict = "WINDOW_NOT_SUPPORTED"
    return {"schema": "archaeon.envgate2.results.v1", "verdict": verdict, "phase_c_gate": gate, "phase_c_gate_passed": all(gate.values()), "failures": fail,
            "totals_genetic": tot, "per_block": {str(b): Y[b] for b in sorted(Y)}, "primary": P, "ordering_page": PO, "arrival_level_mcnemar": mc,
            "takeover_worlds": takeover, "establishments_in_takeover_worlds": tk_est, "falsifiers": falsifiers, "predictions": M.predictions(), "established_glins": lin}


def main(argv=None) -> int:
    pre = json.loads((HERE / "PREREG.json").read_text(encoding="utf-8")); pf = json.loads((HERE / "PREFLIGHT.json").read_text(encoding="utf-8"))
    blocks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(RUNS.glob("block_*.json"))]
    res = analyze(blocks, len(pre["blocks"]), pre["attribution_tests"]["passed"], pf["verdict"] == "PASS")
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: res[k] for k in ("verdict", "phase_c_gate_passed", "totals_genetic")}))
    print(json.dumps(res["phase_c_gate"])); print(json.dumps({k: {x: v[x] for x in ("pos", "neg", "p", "holm_significant")} for k, v in res["primary"].items()}), res["ordering_page"]["p"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
