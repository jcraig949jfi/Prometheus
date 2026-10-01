"""P1: CVT-R (Artemis certs unchanged, via Artemis's adapter as driven by W2-16 _env) for the 17 side-1 copiers
(side 1) and the 18 W2-16 s4 side-0 copiers (side 0), under STOCK (W2-7 DENSE), HARV_HALT, HARV_WRAP.
The step's p11.interact receives the arm's VM, so interaction and child readout share physics.
Also: per-interaction good-copy rate (60 victims, sha256 'W2-16' as s4) and P-11 competence (ST4)."""
import json, pathlib, random, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
from _env import A, ROWS, certs, FRESH, shabytes  # noqa: E402
import _harv as H  # noqa: E402
import alien_pair as AP  # noqa: E402
import p11  # noqa: E402

t0 = time.time()
ARMS = ("STOCK", "HARV_HALT", "HARV_WRAP")
side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
s0 = [r for r in ROWS if r["P11"]["certified_sides"] == [0] and r["vm"] == "DENSE"]
s0 = [r for r in s0 if not r["CVTR_accept"]] + [r for r in s0 if r["CVTR_accept"]][:12]
assert len(side1) == 17 and len(s0) == 18
out = {"genomes": [], "summary": {}}
for r in side1 + s0:
    side = 1 if r in side1 else 0
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"])
    assert (P["n"], P["tape_len"], P["budget"], P["mask"]) == (64, 128, 300, 0x2A), P
    rec = {"key": r["key"], "side": side, "record_cvtr_side": r["CVT"][str(side)]["CVTR"]["accept"]}
    for arm in ARMS:
        z = H.dense(arm)
        sc = A.cvt_side(z, G, P["n"], P["tape_len"], P["budget"], P["mask"], side, r["hex"])
        rec[arm] = {"CVT": [sc[c]["n"] for c in ("CVT1", "CVT2", "CVTR")], "accept": sc["CVTR"]["accept"]}
        if arm == "STOCK":
            rec["stock_identical_to_record"] = all(sc[c] == r["CVT"][str(side)][c] for c in ("CVT1", "CVT2", "CVTR"))
        good = 0; hits = 0
        for j in range(60):
            vb = shabytes("W2-16", r["key"], j, n=64)
            ga, gb = (G, vb) if side == 0 else (vb, G)
            z._HITS[0] = 0
            tape, _, _, _ = p11.interact(z, n=64, tape_len=128, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH, budget=300,
                                         ops_mask=0x2A, cmr=0.0, rng=random.Random(0))
            v0 = 64 if side == 0 else 0
            good += p11.fidelity(G, bytes(tape[v0:v0 + 64])) >= 0.9
            hits += z._HITS[0] > 0
        rec[arm]["good_60"] = good
        rec[arm]["interactions_with_harv_hit"] = hits
        if side == 1:
            rec[arm]["p11_competent"] = AP.competent(z, G)
    out["genomes"].append(rec)
    print(r["key"], side, {a: (rec[a]["accept"], rec[a]["good_60"]) for a in ARMS}, rec["stock_identical_to_record"],
          round(time.time() - t0), flush=True)
for s in (0, 1):
    sel = [g for g in out["genomes"] if g["side"] == s]
    out["summary"]["side%d" % s] = {
        "n": len(sel), "record_accept": sum(g["record_cvtr_side"] for g in sel),
        "stock_identical_to_record": sum(g["stock_identical_to_record"] for g in sel),
        **{a: {"accept": sum(g[a]["accept"] for g in sel), "good_60_sum": sum(g[a]["good_60"] for g in sel),
               "p11_competent": sum(g[a].get("p11_competent", False) for g in sel) if s == 1 else None}
           for a in ARMS}}
out["seconds"] = round(time.time() - t0, 1)
print(json.dumps(out["summary"], indent=1))
HERE.joinpath("p1_cvtr.json").write_text(json.dumps(out, indent=1))
