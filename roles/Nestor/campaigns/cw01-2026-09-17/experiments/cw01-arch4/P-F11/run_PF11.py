"""P-F11 (anti-gravity deformation cross; T-X17 x T-X15 x T-ARCH4/M1): DOES DAMAGE CHANGE THE TEMPORAL
RESPONSE? The raw 7-vector (ticks.response_vector) of every program before and after fixed-k and
fraction-matched deletion (2 draws each) and after the NOP-pad / duplicate / persist-none
manipulations; stratified by the damage outcome (reward lost or not). Computational scope: integer
programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manip as MP             # noqa: E402
import ticks as TK             # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops   # noqa: E402

PID, TID = "P-F11", "T-X17"


def cls(v):
    """Cycle-3 class rule on the K2 components (index 4 = between_puts, 5 = before_first_ask)."""
    bp, ba = v[4], v[5]
    if not (bp == bp and ba == ba):
        return "silent"
    if bp < 0.1 and ba >= 0.1:
        return "ask_time_bound"
    if bp >= 0.1 and ba < 0.1:
        return "schedule_bound"
    if bp < 0.1 and ba < 0.1:
        return "immune"
    return "both"


def d(a, b):
    a, b = np.array(a, float), np.array(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    return float(np.mean(np.abs(a[ok] - b[ok]))) if ok.any() else float("nan")


def job(j):
    p = j["program"]
    env = p["env"]
    eps = A.episodes(env)
    pm = A.canonical(p["manifest"])
    base = TK.response_vector(pm)["vector"]
    r0 = A.evaluate(pm, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    out = {"pid": p["organism_id"], "set": p["stratum"], "base": base, "class": cls(base), "variants": []}
    for name, mk in (("pad", MP.pad), ("duplicate", MP.duplicate), ("persist_none", MP.persist_none)):
        m = mk(pm)
        if m is None:
            continue
        try:
            v = TK.response_vector(m)["vector"]
            rw = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
        except A.ManifestError:
            continue
        out["variants"].append({"kind": name, "vector": v, "class": cls(v), "dist": d(v, base), "reward_delta": rw - r0, "lost": bool(rw < r0 - A.C1.BAND)})
    for mode, val in (("k", 4), ("f", 0.15)):
        for dr in (1, 2):
            rng = A.SplitMix64(A.seed_from("nestor.pf11", A.LOOP_SEED, p["organism_id"], mode, val, dr))
            m = MP.damage_k(pm, "delete", int(val), 1, rng) if mode == "k" else MP.damage_fraction(pm, "delete", float(val), rng)
            if m is None:
                continue
            v = TK.response_vector(m)["vector"]
            rw = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
            out["variants"].append({"kind": "delete_%s%s" % (mode, val), "vector": v, "class": cls(v), "dist": d(v, base), "reward_delta": rw - r0, "lost": bool(rw < r0 - A.C1.BAND)})
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(c - h), float(c + h))


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X15", "T-ARCH4/M1"], "scope": CM.SCOPE, "claim_type": "deformation-cross",
                         "vector": TK.VECTOR_KEYS, "class_rule": "on K2 components: ask_time_bound (between_puts < .1, before_first_ask >= .1) | schedule_bound (>= .1, < .1) | immune | both | silent",
                         "variants": ["pad", "duplicate", "persist_none", "delete k4 x2 draws", "delete f.15 x2 draws"], "programs": "viable parents, walker-16, C4-08 tops",
                         "readouts": "class-preservation share per variant (Wilson), stratified by reward lost / kept; mean L1 distance to the base vector; whether persist_none collapses vectors to immunity",
                         "predictions": {"STRUCTURAL": "class preserved in >= 2/3 of damaged programs that LOST reward", "FUNCTIONAL": "class preserved in < 1/3 of those", "ENTANGLED_WITH_LENGTH": "pad or duplicate change the class in >= 1/3", "ONE_NODE": "persist_none collapses >= 2/3 of vectors to immune (T-X15 and T-X17 share the coordinate)"},
                         "material_rule": "any prediction's threshold met with its Wilson band clear of the complementary threshold", "continuation": ["class of D7 children", "class along no_growth walks"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        rows = list(ex.map(job, [{"program": p} for p in programs]))
    summ = {}
    for kind in ("pad", "duplicate", "persist_none", "delete_k4", "delete_f0.15"):
        vs = [(r, v) for r in rows for v in r["variants"] if v["kind"] == kind and r["class"] not in ("silent",)]
        for strat, sel in (("all", lambda r, v: True), ("lost", lambda r, v: v["lost"]), ("kept", lambda r, v: not v["lost"])):
            xs = [(r, v) for r, v in vs if sel(r, v)]
            n = len(xs)
            k = sum(1 for r, v in xs if v["class"] == r["class"])
            summ["%s|%s" % (kind, strat)] = {"n": n, "class_preserved": k / n if n else None, "wilson": wilson(k, n), "mean_dist": float(np.nanmean([v["dist"] for r, v in xs])) if n else None,
                                             "to_immune": sum(1 for r, v in xs if v["class"] == "immune") / n if n else None}
    base_classes = {}
    for r in rows:
        base_classes.setdefault(r["set"], {}).setdefault(r["class"], 0)
        base_classes[r["set"]][r["class"]] += 1
    reading = []
    lost = [summ.get("delete_k4|lost"), summ.get("delete_f0.15|lost")]
    if any(x and x["n"] >= 8 and x["wilson"][0] > 2 / 3 for x in lost):
        reading.append("STRUCTURAL")
    if any(x and x["n"] >= 8 and x["wilson"][1] < 1 / 3 for x in lost):
        reading.append("FUNCTIONAL")
    if any(summ["%s|all" % k]["n"] >= 8 and summ["%s|all" % k]["class_preserved"] is not None and (1 - summ["%s|all" % k]["class_preserved"]) >= 1 / 3 and wilson(int(round((1 - summ["%s|all" % k]["class_preserved"]) * summ["%s|all" % k]["n"])), summ["%s|all" % k]["n"])[0] > 1 / 3 for k in ("pad", "duplicate")):
        reading.append("ENTANGLED_WITH_LENGTH")
    pn = summ["persist_none|all"]
    if pn["n"] >= 8 and pn["to_immune"] is not None and wilson(int(round(pn["to_immune"] * pn["n"])), pn["n"])[0] > 2 / 3:
        reading.append("ONE_NODE")
    if not reading:
        reading.append("UNRESOLVED")
    material = reading != ["UNRESOLVED"]
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "summary": summ, "base_classes_by_set": base_classes, "n_programs": len(rows), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "temporal class after damage/manipulation: reading %s; base classes %s; class preserved %s"
                      % (reading, base_classes, {k: (v["n"], round(v["class_preserved"], 2) if v["class_preserved"] is not None else None, round(v["mean_dist"], 3) if v["mean_dist"] is not None else None, round(v["to_immune"], 2) if v["to_immune"] is not None else None) for k, v in summ.items()}),
                      material, detail={"summary": summ, "base_classes": base_classes})
    L.append_evidence("T-X15", PID, "cross: persist_none sends %s of programs to immunity; pad/duplicate preserve the class in %s / %s" % (round(pn["to_immune"], 2) if pn["to_immune"] is not None else None, round(summ["pad|all"]["class_preserved"], 2) if summ["pad|all"]["class_preserved"] is not None else None, round(summ["duplicate|all"]["class_preserved"], 2) if summ["duplicate|all"]["class_preserved"] is not None else None), material)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, reading, time.time() - t0, {k: (v["n"], v["class_preserved"], v["to_immune"]) for k, v in summ.items()}))


if __name__ == "__main__":
    main()
