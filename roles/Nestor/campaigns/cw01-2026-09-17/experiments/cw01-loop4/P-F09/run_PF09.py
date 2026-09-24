"""P-F09 (serendipity cross; T-X15 read in e06's TAPE and TREE genomes).

Evolved bodies (solo_tape / solo_tree arms, rates .5 and 1.0, 3 ids, 80 generations; the final
populations) damaged blind at FIXED k (2 instructions / 2 internal-node contractions) and
FRACTION-MATCHED (.15), 4 draws; score loss = (score_orig - score_damaged) / score_orig on one shared
item set (per-organism evaluate, no sharing). TAPE: NOP-PAD (append inert instructions writing a dead
register) and DUPLICATE (append a copy) then the same damage. Regressions of loss on log size, live
registers (TAPE), tree depth (TREE).
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
sys.path.insert(0, str(HERE.parents[1] / "cw01-loop3" / "P-E06"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import run_PE06 as E6          # noqa: E402  (contract_tree)

W6 = E6.W6
E6.MODE["arm"] = "none"
PID, TID = "P-F09", "T-X15"
IDS, RATES, GENS, DRAWS, FR = ["cw01-loop4-PF09-%d" % i for i in range(3)], (0.5, 1.0), 80, 4, 0.15


def tree_depth(node):
    return 0 if node[0] == "in" else 1 + max(tree_depth(node[1]), tree_depth(node[2]))


def damage_tape(prog, k, r):
    k = min(k, len(prog) - 1)
    picks = set(int(x) for x in r.choice(len(prog), size=k, replace=False)) if k > 0 else set()
    return [ins for i, ins in enumerate(prog) if i not in picks]


def damage_tree(body, k, r):
    n_int = W6.tree_nodes(body) - (W6.tree_nodes(body) + 1) // 2
    k = min(k, n_int)
    if k <= 0:
        return body
    picks = sorted((int(x) for x in r.choice(n_int, size=k, replace=False)), reverse=True)
    for t in picks:
        body = E6.contract_tree(body, t, [0])
    return body


def pad_tape(prog, cfg):
    dead = cfg["substrates"]["TAPE"]["n_registers"] - 1
    return list(prog) + [("add", dead, dead, dead)] * len(prog)


def job(j):
    aid, rate = j["aid"], j["rate"]
    cfg = L.load_cfg("cw01-e06", aid)
    cfg["ecology"]["recombination_rate"] = rate
    targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
    irng = np.random.Generator(np.random.PCG64(S.seed(aid, "assay-items", 0)))
    items = W6.make_items(cfg, irng, targets)
    rows = []
    for arm, sub in (("solo_tape", "TAPE"), ("solo_tree", "TREE")):
        run = W6.evolve(cfg, arm, GENS, 96, S.seed, "%s|%s|r%.1f" % (aid, arm, rate), freq_first=1.0, target=targets)
        seen = set()
        for gi, g in enumerate(run["final_pop"]):
            key = json.dumps(g["body"], default=str)
            if key in seen:
                continue
            seen.add(key)
            oid = "%s|%.1f|%s|%d" % (aid, rate, sub, gi)
            s0 = W6.evaluate(g, cfg, items)["score"]
            variants = {"original": g}
            if sub == "TAPE":
                if 2 * len(g["body"]) <= 2 * cfg["substrates"]["TAPE"]["max_instructions"]:
                    variants["pad"] = dict(g, body=pad_tape(g["body"], cfg))
                    variants["duplicate"] = dict(g, body=list(g["body"]) + list(g["body"]))
            for vname, v in variants.items():
                sv = W6.evaluate(v, cfg, items)["score"]
                rec = {"oid": oid, "aid": aid, "rate": rate, "substrate": sub, "variant": vname, "size": W6.structural_units(v), "live_regs": W6.registers_used(v),
                       "depth": tree_depth(v["body"]) if sub == "TREE" else None, "score0": sv, "identical": abs(sv - s0) < 1e-12}
                for mode in ("k2", "f"):
                    losses = []
                    for d in range(DRAWS):
                        r = np.random.Generator(np.random.PCG64(S.seed(aid, "dmg|%s|%s|%s|%d" % (arm, vname, mode, d), len(rows))))
                        k = 2 if mode == "k2" else max(1, int(round(FR * W6.structural_units(v))))
                        dv = dict(v, body=(damage_tape(v["body"], k, r) if sub == "TAPE" else damage_tree(v["body"], k, r)))
                        sd = W6.evaluate(dv, cfg, items)["score"]
                        losses.append((sv - sd) / sv if sv > 0 else 0.0)
                    rec["loss_" + mode] = float(np.mean(losses))
                rows.append(rec)
    return rows


def perm_reg(X, y, n=2000, seed=0):
    ok = np.isfinite(y)
    X, y = X[ok], y[ok]
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    rng = np.random.Generator(np.random.PCG64(seed))
    null = np.array([np.linalg.lstsq(X, rng.permutation(y), rcond=None)[0] for _ in range(n)])
    return {"coef": [float(x) for x in b], "p05": [float(x) for x in np.percentile(null, 5, axis=0)], "p95": [float(x) for x in np.percentile(null, 95, axis=0)], "n": int(ok.sum())}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-E06", "T-E07"], "claim_type": "serendipity-cross",
                         "bodies": "final populations of solo_tape / solo_tree at rates .5 / 1.0, 3 ids, 80 gens (deduplicated)", "damage": {"fixed": "k=2 units", "fraction": FR, "draws": DRAWS},
                         "ruler": "relative score loss on a shared item set, per-organism evaluate (no sharing)", "manipulations": "TAPE: pad (dead-register instructions appended; identity checked) and duplicate",
                         "analysis": "per substrate: loss ~ 1 + log size + (live regs | depth), standardised, 2000-permutation bands, for fixed-k and fraction-matched; pad/duplicate paired contrasts (fixed-k and fraction)",
                         "predictions": {"CROSS_SUBSTRATE": "fixed-k loss falls with size in TAPE (coef below p05) and the pad/duplicate pattern matches P-F01's", "REPRESENTATION_IS_A_COORDINATE": "TAPE and TREE disagree in sign", "NOT_PORTABLE": "no size coefficient clears its band"},
                         "material_rule": "any size / registers / depth coefficient outside its band, or a pad/duplicate contrast outside its band", "continuation": ["registers-only damage", "depth-matched trees"]})
    jobs = [{"aid": a, "rate": r} for a in IDS for r in RATES]
    with ProcessPoolExecutor(max_workers=6) as ex:
        rows = [x for rs in ex.map(job, jobs) for x in rs]
    reg = {}
    for sub in ("TAPE", "TREE"):
        rs = [r for r in rows if r["substrate"] == sub and r["variant"] == "original"]
        if len(rs) < 10:
            continue
        cov = np.array([r["live_regs"] if sub == "TAPE" else r["depth"] for r in rs], float)
        X = np.column_stack([np.ones(len(rs)), np.log([r["size"] for r in rs]), cov])
        for c in (1, 2):
            X[:, c] = (X[:, c] - X[:, c].mean()) / (X[:, c].std() + 1e-9)
        for mode in ("k2", "f"):
            reg["%s|%s" % (sub, mode)] = perm_reg(X, np.array([r["loss_" + mode] for r in rs], float))
    pairs = {}
    orig = {r["oid"]: r for r in rows if r["variant"] == "original"}
    for v in ("pad", "duplicate"):
        for mode in ("k2", "f"):
            diffs, diffs_id = [], []
            for r in rows:
                if r["variant"] != v:
                    continue
                o = orig.get(r["oid"])
                if o is None:
                    continue
                diffs.append(r["loss_" + mode] - o["loss_" + mode])
                if r["identical"]:
                    diffs_id.append(r["loss_" + mode] - o["loss_" + mode])
            d = np.array(diffs)
            if len(d):
                rng = np.random.Generator(np.random.PCG64(0))
                null = np.array([(d * rng.choice([-1.0, 1.0], size=len(d))).mean() for _ in range(3000)])
                pairs["%s|%s" % (v, mode)] = {"mean": float(d.mean()), "n": len(d), "n_identical": len(diffs_id), "above_p95": bool(d.mean() > np.percentile(null, 95)), "below_p05": bool(d.mean() < np.percentile(null, 5))}
    sig = lambda r, i: not (r["p05"][i] <= r["coef"][i] <= r["p95"][i])   # noqa: E731
    tape_k = reg.get("TAPE|k2")
    tree_k = reg.get("TREE|k2")
    reading = []
    if tape_k and tape_k["coef"][1] < tape_k["p05"][1]:
        reading.append("SIZE_LOWERS_FIXED_K_LOSS_IN_TAPE")
    if tape_k and tree_k and np.sign(tape_k["coef"][1]) != np.sign(tree_k["coef"][1]) and (sig(tape_k, 1) or sig(tree_k, 1)):
        reading.append("REPRESENTATION_IS_A_COORDINATE")
    if not any(sig(r, i) for r in reg.values() for i in (1, 2)):
        reading.append("NOT_PORTABLE")
    material = bool(any(sig(r, i) for r in reg.values() for i in (1, 2)) or any(v["above_p95"] or v["below_p05"] for v in pairs.values()))
    n_ident = sum(1 for r in rows if r["variant"] == "pad" and r["identical"])
    out = {"perturbation_id": PID, "parent": TID, "reading": reading or ["UNRESOLVED"], "regressions": reg, "pad_duplicate_contrasts": pairs, "pad_identity_share": n_ident / max(1, sum(1 for r in rows if r["variant"] == "pad")),
           "n_bodies": {s: sum(1 for r in rows if r["substrate"] == s and r["variant"] == "original") for s in ("TAPE", "TREE")}, "mean_loss": {"%s|%s" % (s, m): float(np.mean([r["loss_" + m] for r in rows if r["substrate"] == s and r["variant"] == "original"])) for s in ("TAPE", "TREE") for m in ("k2", "f")},
           "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=L.js), encoding="utf-8")
    L.append_evidence(TID, PID, "T-X15 in e06 bodies: reading %s; regressions (coef log size, covariate; bands) %s; pad/duplicate %s; pad identity share %.2f; mean loss %s"
                      % (out["reading"], {k: ([round(x, 3) for x in v["coef"][1:]], [round(x, 3) for x in v["p05"][1:]], [round(x, 3) for x in v["p95"][1:]]) for k, v in reg.items()},
                         {k: (round(v["mean"], 3), v["n"], v["above_p95"], v["below_p05"]) for k, v in pairs.items()}, out["pad_identity_share"], {k: round(v, 3) for k, v in out["mean_loss"].items()}), material, detail={"reg": reg, "pairs": pairs})
    L.append_evidence("T-E06", PID, "cross: damage loss vs body size in evolved TAPE/TREE bodies: %s" % out["reading"], material)
    print("DONE material=%s reading=%s (%.0f s) %s | pairs %s" % (material, out["reading"], time.time() - t0, {k: [round(x, 3) for x in v["coef"][1:]] for k, v in reg.items()}, {k: round(v["mean"], 3) for k, v in pairs.items()}))


if __name__ == "__main__":
    main()
