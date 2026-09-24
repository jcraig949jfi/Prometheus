"""THE S2 GATE, G-S2.1 .. G-S2.6 (AMENDMENT 13 s4, frozen at 4a6bbf55d).

Runs only after S1_PASS. Writes S2_GATE_2026-09-23.json.
"""
import json
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G           # noqa: E402
import conformance as CF       # noqa: E402
import engine as E             # noqa: E402
import fair as FR              # noqa: E402
import identity as I           # noqa: E402
import tier3c as T3C           # noqa: E402

R = 8
FAMILIES = ["md_a_sum_times_last", "md_c_prod_minus_first"]


def _log(m):
    print("[s2] " + m, flush=True)


def _t3c_libs():
    art = json.loads((HERE / "TIER3C_ARTIFACT_2026-09-22.json").read_text(encoding="utf-8"))
    res = json.loads((HERE / "TIER3C_RESULTS_2026-09-22.json").read_text(encoding="utf-8"))
    mem = [dict(e) for e in art["evolved_entries"]]
    assert art["selected_operator"] == "memorise" and not art["schemas"] and not art["op_schemas"]
    abstract = []
    for e in mem:
        e2 = dict(e)
        if e2["name"] == "memorised":
            e2["name"] = "abstracted"
            e2["schemas"], e2["op_schemas"] = [], []
        abstract.append(e2)
    sizes = {f: res["generator_qualification"][f]["size"] for f in FAMILIES}
    return FR.KLib(mem), FR.KLib(abstract), sizes


def main():
    t0 = time.perf_counter()
    s1 = json.loads((HERE / "S1_GATE_RUN3_2026-09-24.json").read_text(encoding="utf-8"))
    if s1.get("OUTCOME") != "S1_PASS":
        print("S1 has not passed -- S2 does not run")
        return 2
    rep = {"amendment": "AMENDMENT_13 @ 4a6bbf55d", "R": R, "families": FAMILIES,
           "started_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    mem, abstract, sizes = _t3c_libs()
    base = FR.pristine()
    cells = [FR.Cell(T3C, f, r, sizes[f]) for f in FAMILIES for r in range(R)]

    # G-S2.1 identical content, different names -- the Tier-3C case rebuilt
    cm = [c.cost(mem)[0] for c in cells]
    ca = [c.cost(abstract)[0] for c in cells]
    rep["G_S2_1_identical_content"] = {
        "content_equal": mem.content() == abstract.content(),
        "canonical_differs": mem.canonical() != abstract.canonical(),
        "costs_memorise": cm, "costs_abstract": ca,
        "tier3c_recorded": "memorise 13,479 vs abstract 51,018 (per-arm seeding)",
        "PASS": cm == ca and mem.content() == abstract.content()}
    _log("G-S2.1 PASS=%s" % rep["G_S2_1_identical_content"]["PASS"])

    # G-S2.2 order invariance
    rng = random.Random(7)
    perm = []
    for e in mem.entries:
        e2 = {k: (list(v) if isinstance(v, list) else v) for k, v in e.items()}
        for k in ("inits", "bodies", "finals"):
            if k in e2:
                rng.shuffle(e2[k])
        perm.append(e2)
    permuted = FR.KLib(perm)
    cp = [c.cost(permuted)[0] for c in cells]
    rep["G_S2_2_order_invariance"] = {"costs_permuted": cp, "PASS": cp == cm}
    _log("G-S2.2 PASS=%s" % rep["G_S2_2_order_invariance"]["PASS"])

    # G-S2.3 arm invariance: the recipient cell is built from (family, i) only
    arm_rows = {}
    for arm in ("EVOLVED", "PRISTINE", "SHAM_3"):
        rc = [FR.Cell(T3C, f, i, sizes[f], label="T3D-rx") for f in FAMILIES for i in range(4)]
        arm_rows[arm] = [c.cost(mem)[0] for c in rc]
    rep["G_S2_3_arm_invariance"] = {"rows": arm_rows,
                                    "PASS": len({json.dumps(v) for v in arm_rows.values()}) == 1}
    _log("G-S2.3 PASS=%s" % rep["G_S2_3_arm_invariance"]["PASS"])

    # G-S2.4 charge conservation vs a direct enumeration
    checks, bad = 0, []
    for c in cells:
        for lib in (mem, base):
            charges, prog = c.cost(lib)
            pos = None
            for k, (p, _coord) in enumerate(lib.candidates(c.seed), start=1):
                if k > FR.ESCROW:
                    break
                if all(G.run_program(p, n, True) is not None and str(G.run_program(p, n, True)) == g
                       for n, g in c.parsed):
                    pos = k
                    break
            want = pos if pos is not None else FR.ESCROW
            checks += 1
            if want != charges:
                bad.append({"family": c.family, "r": c.r, "charges": charges, "direct": want})
    rep["G_S2_4_charge_conservation"] = {"checks": checks, "mismatches": bad, "PASS": not bad}
    _log("G-S2.4 PASS=%s" % rep["G_S2_4_charge_conservation"]["PASS"])

    # G-S2.5 pairing is informative (reported, not thresholded)
    cb = [c.cost(base)[0] for c in cells]
    other = [FR.Cell(T3C, f, r, sizes[f], label="S2-unpaired") for f in FAMILIES for r in range(R)]
    cm_unpaired = [c.cost(mem)[0] for c in other]
    dp = [b - m for b, m in zip(cb, cm)]
    du = [b - m for b, m in zip(cb, cm_unpaired)]
    rep["G_S2_5_pairing"] = {"pristine": cb, "memorise_paired": cm, "memorise_unpaired": cm_unpaired,
                             "var_paired_diff": statistics.pvariance(dp),
                             "var_unpaired_diff": statistics.pvariance(du),
                             "paired_summary_memorise_vs_pristine": FR.paired_summary(cb, cm),
                             "PASS": True}
    _log("G-S2.5 var paired %.0f vs unpaired %.0f" % (rep["G_S2_5_pairing"]["var_paired_diff"],
                                                     rep["G_S2_5_pairing"]["var_unpaired_diff"]))

    # G-S2.6 conformance (both parts) and S1 identity unchanged
    std = CF.check()
    smp = random.Random(I._seed("APHRODITE/S2/CONF/v1"))
    progs = [("fold", smp.choice(G.INIT_SPACE), smp.choice(G.BODY_SPACE), smp.choice(G.FINAL_SPACE))
             for _ in range(40)]
    p2 = [CF.check_whole_program(p, bat, 2) for p in progs for bat in (I.B1, I.B1_BOUNDARY)]
    p2m = sum(len(x["mismatches"]) for x in p2)
    rep["G_S2_6_conformance"] = {"part1_GREEN": std["GREEN"], "part1_checked": std["checked"],
                                 "part2_programs": len(progs),
                                 "part2_checked": sum(x["checked"] for x in p2),
                                 "part2_mismatches": p2m,
                                 "B1_sha256_unchanged": I.B1_SHA == s1["B1_sha256"],
                                 "PASS": std["GREEN"] and p2m == 0 and I.B1_SHA == s1["B1_sha256"]}
    _log("G-S2.6 PASS=%s" % rep["G_S2_6_conformance"]["PASS"])

    gates = ["G_S2_1_identical_content", "G_S2_2_order_invariance", "G_S2_3_arm_invariance",
             "G_S2_4_charge_conservation", "G_S2_6_conformance"]
    rep["OUTCOME"] = "S2_PASS" if all(rep[g]["PASS"] for g in gates) else "S2_FAIL"
    rep["failed_gates"] = [g for g in gates if not rep[g]["PASS"]]
    rep["seconds"] = round(time.perf_counter() - t0, 1)
    (HERE / "S2_GATE_2026-09-23.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n",
                                                   encoding="utf-8")
    _log("OUTCOME %s %s (%.0fs)" % (rep["OUTCOME"], rep["failed_gates"], rep["seconds"]))
    return 0 if rep["OUTCOME"] == "S2_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
