"""P-J08 [T-ARCH5; serendipity; requires P-J02]: REPRESENTATION AS AN ACCESSIBILITY COORDINATE. The sampled
one-operator neighbourhood of the 6 plateau genomes under grammar B vs grammar v0.4 (paired: same genomes,
2000 mutants each, same held-out set) on A' (xor 1) and A (xor 15): shares hit / beneficial / neutral /
deleterious, best mutant, operators of the beneficial mutants. Computational scope: integer programs on a
bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L
try:
    from archaeon.campaign5.repb import grammar_b as GB
    GB_OK = True
except Exception:      # noqa: BLE001
    GB, GB_OK = None, False

PID, TID = "P-J08", "T-ARCH5"
N_SAMPLE, MARGIN, MARGIN4, CONFIRM_CAP = 2000, 0.0625, 0.05, 300


def classify(f, f0, thr):
    return "hit" if f >= thr else "beneficial" if f > f0 + MARGIN else "deleterious" if f < f0 - MARGIN else "neutral"


def sample(m, grammar, sets, f0, thr, seed):
    rng = A.SplitMix64(A.seed_from("nestor.pj08", A.LOOP_SEED, grammar, seed))
    rows = []
    for _ in range(N_SAMPLE):
        c, op = m, None
        for _try in range(8):
            try:
                c, rec = (GB.mutate_b(m, rng, None, None) if grammar == "B" else A.GR.mutate(m, rng, mate=None, name=None))
                op = rec["operator"]
                break
            except Exception:      # noqa: BLE001
                continue
        r = {"op": op, "m": c}
        for w, s in sets.items():
            f = CE.held_reward(c, s[:2])
            r[w] = f
            r[w + "_class"] = classify(f, f0[w], thr)
        rows.append(r)
    return rows


def job(j):
    m = j["m"]
    sets = {"xor1": CE.held_sets("A", j["seed"], xor=1), "xor15": CE.held_sets("A", j["seed"], xor=15)}
    thr = CE.THRESH["A"]
    f0_4 = {w: CE.held_reward(m, s) for w, s in sets.items()}
    f0 = {w: CE.held_reward(m, s[:2]) for w, s in sets.items()}          # baseline on the SAME 2 sets as the mutants
    out = {"seed": j["seed"], "rank": j["rank"], "f0_4set": f0_4, "f0_2set": f0}
    for grammar in ("B", "v0.4"):
        rows = sample(m, grammar, sets, f0, thr, j["seed"] * 10 + j["rank"])
        d = {}
        for w in sets:
            cls = Counter(r[w + "_class"] for r in rows)
            d[w] = {k: cls.get(k, 0) / len(rows) for k in ("hit", "beneficial", "neutral", "deleterious")}
            d[w]["best"] = max(r[w] for r in rows)
            d[w]["mean"] = float(np.mean([r[w] for r in rows]))
            d[w]["beneficial_ops"] = dict(Counter(r["op"] for r in rows if r[w + "_class"] in ("beneficial", "hit")))
            cand = [r for r in rows if r[w + "_class"] in ("beneficial", "hit")][:CONFIRM_CAP]
            conf = [CE.held_reward(r["m"], sets[w]) for r in cand]
            d[w]["confirmed_beneficial"] = sum(1 for f in conf if f > f0_4[w] + MARGIN4) / len(rows)
            d[w]["confirmed_hit"] = sum(1 for f in conf if f >= thr) / len(rows)
            d[w]["best4"] = max(conf, default=None)
        d["ops"] = dict(Counter(r["op"] for r in rows))
        out[grammar] = d
    return out


def main():
    t0 = time.time()
    tops = json.load(open(HERE.parent / "P-I01" / "tops.json", encoding="utf-8"))
    jobs = [{"m": r["tops"][k]["m"], "seed": r["seed"], "rank": k} for r in tops if r["world"] == "A" and r["control"] is None for k in (0, 1)]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-J02"], "scope": CM.SCOPE, "claim_type": "serendipity-representation", "grammar_b_available": GB_OK, "genomes": [(j["seed"], j["rank"]) for j in jobs],
                         "design": "paired: %d one-operator mutants per genome under grammar B and under v0.4, 2 held-out sets with the baseline on the same sets, beneficial / hits confirmed on 4 (cap %d), A' (xor 1) and A (xor 15)" % (N_SAMPLE, CONFIRM_CAP),
                         "material_rule": "material if the grammars differ in hit share, or in beneficial share by > 2x with >= 10 beneficial mutants pooled", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    if not GB_OK:
        L.append_evidence(TID, PID, "grammar B not importable: NOT_RUNNABLE", False)
        return
    with A.pool(6) as ex:
        rows = list(ex.map(job, jobs))
    summary = {}
    for grammar in ("B", "v0.4"):
        summary[grammar] = {w: {k: float(np.mean([r[grammar][w][k] for r in rows])) for k in ("hit", "beneficial", "neutral", "deleterious", "best", "mean", "confirmed_beneficial", "confirmed_hit")} for w in ("xor1", "xor15")}
        summary[grammar]["beneficial_ops_pooled"] = {w: dict(sum((Counter(r[grammar][w]["beneficial_ops"]) for r in rows), Counter())) for w in ("xor1", "xor15")}
    nb = {w: sum(summary[g][w]["confirmed_beneficial"] + summary[g][w]["confirmed_hit"] for g in ("B", "v0.4")) * N_SAMPLE * len(rows) for w in ("xor1", "xor15")}
    material = any(summary["B"][w]["confirmed_hit"] != summary["v0.4"][w]["confirmed_hit"] for w in ("xor1", "xor15")) or any(
        nb[w] >= 10 and (max(summary["B"][w]["confirmed_beneficial"], summary["v0.4"][w]["confirmed_beneficial"]) > 2 * max(1e-9, min(summary["B"][w]["confirmed_beneficial"], summary["v0.4"][w]["confirmed_beneficial"]))) for w in ("xor1", "xor15"))
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": rows, "material": bool(material), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "grammar B vs v0.4 one-op neighbourhood of the plateau (6 genomes x %d): %s" % (N_SAMPLE, {g: {w: {k: round(v, 4) for k, v in summary[g][w].items()} for w in ("xor1", "xor15")} for g in ("B", "v0.4")}), bool(material), detail=summary)
    L.append_evidence("T-R01", PID, "cross: representation as an accessibility coordinate: hit shares B %s v0.4 %s; beneficial shares B %s v0.4 %s" % (
        [round(summary["B"][w]["hit"], 4) for w in ("xor1", "xor15")], [round(summary["v0.4"][w]["hit"], 4) for w in ("xor1", "xor15")], [round(summary["B"][w]["beneficial"], 4) for w in ("xor1", "xor15")], [round(summary["v0.4"][w]["beneficial"], 4) for w in ("xor1", "xor15")]), bool(material))
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps(summary, default=CM.js)[:1500])


if __name__ == "__main__":
    main()
