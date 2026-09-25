"""P-D08 [T-X05, fossil-ablation]: the e08 fossils (256 representatives, 4 arms x 8 lineages x 8): for each,
(i) the rank profile SCRAMBLED at identical total bond width with the cores re-drawn at the substrate's
init, (ii) the read mask scrambled at identical bit count, (iii) both; held64 of the original vs each
ablation, per arm. Is the low-burden / high-capability association carried by WHICH bonds are wide, or
only by size? Computational scope: tensor-train policies in a bounded encounter world."""
from __future__ import annotations

import base64
import json
import pathlib
import sys
import time
import zlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[2]
E08 = CAMP / "experiments" / "cw01-e08"
sys.path.insert(0, str(CAMP / "loop"))
sys.path.insert(0, str(E08))
import looprun as L            # noqa: E402
import world_e08 as W          # noqa: E402

PID, TID = "P-D08", "T-X05"
SCOPE = "Computational artificial-life research: tensor-train policies evolved in a bounded encounter world; no biological content."


def load_fossils(cfg, spec):
    f = json.loads((E08 / "fossils" / "representatives.json").read_text(encoding="utf-8"))
    raw = zlib.decompress(base64.b64decode(f["records_zlib_base64"]))
    B = np.frombuffer(raw, np.uint8).reshape(f["n_records"], f["record_nbytes"])
    return W.unpack(B, cfg, spec), f["meta"]


def random_profile(rng, total, n, R):
    """A uniform-ish random composition of `total` into n parts in [1, R] (random increments with cap)."""
    rk = np.ones(n, np.int64)
    left = int(total - n)
    while left > 0:
        j = int(rng.integers(0, n))
        if rk[j] < R:
            rk[j] += 1
            left -= 1
    return rk


def ablate(pop, cfg, spec, rng, ranks=False, masks=False):
    out = W.copy_pop(pop)
    d, R, A, Wd = W.dims(cfg, spec)
    P = out["rk"].shape[0]
    if ranks:
        fresh = W.init_population(cfg, spec, rng, P)
        for key in ("al", "G", "Wo"):
            out[key] = fresh[key]
        out["rk"] = np.stack([random_profile(rng, int(out["rk"][p].sum()), d + 1, R) for p in range(P)])
    if masks:
        mk = np.zeros_like(out["mk"])
        for p in range(P):
            k = int(out["mk"][p].sum())
            idx = rng.choice(out["mk"].shape[1], size=k, replace=False)
            mk[p, idx] = True
        out["mk"] = mk
    return W.enforce_pad(out, cfg, spec)


def held64(pop, cfg, spec):
    hs = W.held_seeds(cfg)
    ro = W.rollout(spec, pop, hs)
    return ro["fit"] / len(hs)


def main(pid=PID, arms=(("ranks", True, False), ("masks", False, True), ("both", True, True)), seed=808):
    t0 = time.time()
    cfg = json.loads((E08 / "WORLD.json").read_text(encoding="utf-8"))
    spec = W.world_spec(cfg)
    pop, meta = load_fossils(cfg, spec)
    floor = cfg["assay"]["competence_floor_held64"]
    ph = L.prereg(HERE, {"perturbation_id": pid, "parent": TID, "scope": SCOPE, "claim_type": "fossil-ablation", "fossils": "cw01-e08/fossils/representatives.json (256)", "arms": [a[0] for a in arms],
                         "ablations": {"ranks": "rank profile re-drawn as a random composition of the same total bond width; cores re-drawn at init", "masks": "read mask re-drawn at the same bit count", "both": "both"},
                         "readout": "held64 (tax-free held-out) of the original vs each ablation, per e08 arm; share above the competence floor %.2f" % floor, "material_rule": "material if any ablation keeps >= half the original's excess over the floor on average in any e08 arm"})
    rng = np.random.default_rng(seed)
    h0 = held64(pop, cfg, spec)
    res = {"original": h0}
    for name, rk, mk in arms:
        res[name] = held64(ablate(pop, cfg, spec, rng, ranks=rk, masks=mk), cfg, spec)
    B = W.burden(pop, cfg, spec)
    e08_arms = sorted({m["arm"] for m in meta})
    table = {}
    for arm in e08_arms:
        idx = [i for i, m in enumerate(meta) if m["arm"] == arm]
        table[arm] = {k: {"mean": float(np.mean(v[idx])), "above_floor": float(np.mean(v[idx] > floor))} for k, v in res.items()}
        table[arm]["bond_mean"] = float(np.mean(B["bond"][idx]))
        table[arm]["bits_mean"] = float(np.mean(B["bits"][idx]))
        for name, _, _ in arms:
            ex0 = np.maximum(res["original"][idx] - floor, 0)
            table[arm]["retained_excess_" + name] = float(np.sum(np.maximum(res[name][idx] - floor, 0)) / max(np.sum(ex0), 1e-9))
    comp = res["original"] > floor
    corr = {name: float(np.corrcoef(res["original"], res[name])[0, 1]) for name, _, _ in arms}
    material = any(table[a]["retained_excess_" + n] >= 0.5 for a in e08_arms for n, _, _ in arms)
    out = {"perturbation_id": pid, "parent": TID, "n": int(len(meta)), "floor": floor, "n_competent_original": int(comp.sum()), "table": table, "corr_with_original": corr,
           "per_rep": [{"arm": m["arm"], "lineage": m["lineage"], "rep": m["rep"], **{k: float(v[i]) for k, v in res.items()}} for i, m in enumerate(meta)], "material": bool(material), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, pid, "e08 fossil ablation (%s): per-arm held64 %s; retained excess over the floor %s; corr with original %s" % (
        [a[0] for a in arms], {a: {k: round(table[a][k]["mean"], 1) for k in res} for a in e08_arms}, {a: {n: round(table[a]["retained_excess_" + n], 3) for n, _, _ in arms} for a in e08_arms}, {k: round(v, 3) for k, v in corr.items()}), bool(material), detail={"table": table, "corr": corr})
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps({a: {k: round(table[a][k]["mean"], 1) for k in res} for a in e08_arms}), json.dumps({a: {n: round(table[a]["retained_excess_" + n], 3) for n, _, _ in arms} for a in e08_arms}))


if __name__ == "__main__":
    main()
