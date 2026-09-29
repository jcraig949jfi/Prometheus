"""PORTABILITY-01 regression under contract v0.2.1 with the FROZEN v0.2 adapters (85d648447). Preserved evidence + one bounded replay.
    python -m archaeon.causal_lens.regress_v02 [archaeon|bee|bee_arch|npe|pte ...]   (default: all)
Writes archaeon/causal_lens/out_v02/*.json. Light and bounded: BEE uses 3 workers (Bellerophon's campaign holds M2).
"""
from __future__ import annotations

import gzip
import json
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from archaeon.causal_lens import adapters_v02 as A2
from archaeon.causal_lens import schema as S1
from archaeon.causal_lens.upgrade_v01 import upgrade

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "archaeon/causal_lens/out_v02"
EV1 = Path(r"C:\Prometheus-data\evidence\portability01_2026-09-26")
EV2 = Path(r"C:\Prometheus-data\evidence\contract_v02_2026-09-27")
EG2 = Path(r"C:\Prometheus-data\evidence\envgate02_2026-09-26")


def dump(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")


# ------------------------------------------------------------------------------------------------ ARCHAEON
def archaeon():
    from archaeon.causal_lens import fossils_archaeon as F
    t0 = time.time(); rep = {"upgraded_v01_graphs": {}}
    for name, fn in (("A1", F.a1_autonomous), ("A2", F.a2_inserted), ("A3", F.a3_block15_panel)):
        w, _ = fn(); g1 = F.graph_of(w, name); g2, ur = upgrade(g1)
        rep["upgraded_v01_graphs"][name] = {"violations": g2.check()[:5], "report": ur, "contributors_preserved": all(g2.contributors_hu(t) == g1.contributors_hu(t) for t in g1.of_kind("TRANSFORMATION"))}
    g1 = S1.Graph.from_json(json.loads((EV1 / "archaeon/A4_block13.graph.v2.json").read_text(encoding="utf-8")))
    t1 = time.time(); g2, ur = upgrade(g1); up_s = time.time() - t1
    rep["upgraded_v01_graphs"]["A4_block13"] = {"violations": g2.check()[:5], "report": ur, "upgrade_s": round(up_s, 2), "nodes": len(g2.nodes),
                                                "establishments": g2.establishments()}
    ev = json.loads((EV1 / "archaeon/A4_block13_events.json").read_text(encoding="utf-8"))["watched"]
    t1 = time.time(); reads = [A2.archaeon_event(e) for e in ev]; light_s = time.time() - t1
    c = Counter(); tie = Counter()
    for e, r in zip(ev, reads):
        c[(r["autonomy_material"], r["autonomy_write"], r["autonomy_exec"], "cont=" + (r["hu_continuity"] if r["hu_continuity"] in ("ILL_POSED", "NOT_IDENTIFIABLE", "NONE") else "decided"))] += 1
        if r["hu_continuity"] == "ILL_POSED": tie[(e["mechanism"], e["template"])] += 1
    rep["block13_v02_roles"] = {" | ".join(k): v for k, v in c.most_common()}
    rep["block13_ill_posed_vs_native_tiebreak"] = {" | ".join(k): v for k, v in tie.items()}
    rep["block13_light_us_per_event"] = round(1e6 * light_s / len(ev), 2)
    res = json.loads((EG2 / "RESULTS.json").read_text(encoding="utf-8"))
    cf = A2.envgate02_cf_graph(res)
    rep["envgate02_cf"] = {"violations": cf.check(), "tests": {n: {k: cf.nodes[n][k] for k in ("cf_kind", "intervention", "outcome", "result", "totals")} for n in cf.of_kind("CF_TEST")}}
    rep["wall_s"] = round(time.time() - t0, 1); dump("ARCHAEON_V02.json", rep); return rep


# ------------------------------------------------------------------------------------------------ BEE
def _bee_one(rid):
    from archaeon.causal_lens.adapters import bee as B1
    cfg = json.loads((B1.RUNS / rid / "config.json").read_text(encoding="utf-8")); L = B1.L_of(cfg); p = B1.Pass(cfg)
    joint = Counter(); t_v1 = t_v2 = 0.0; n = 0
    for r in B1.rows(rid):
        a = time.perf_counter(); e1 = p.step(r); b = time.perf_counter(); e2 = A2.bee_row(r, L); c = time.perf_counter()
        t_v1 += b - a; t_v2 += c - b; n += 1
        joint[(e1["lens_class"], r[6], "sr%d" % r[11], "M=%s" % e2["autonomy_material"], "W=%s" % e2["autonomy_write"], "E=%s" % e2["autonomy_exec"],
               "cont=%s" % (e2["hu_continuity"] if e2["hu_continuity"] in ("NOT_IDENTIFIABLE", "ILL_POSED", "NONE", "occupant") else "writer"))] += 1
    return rid, {"births": n, "joint": {"|".join(k): v for k, v in joint.items()}, "v1_s": t_v1, "v2_s": t_v2}


def bee(workers=3):
    from archaeon.causal_lens.adapters import bee as B1
    rids = sorted(p.name[:-9] for p in B1.BIRTHS.glob("*.jsonl.gz")); t0 = time.time()
    tot = Counter(); v1 = v2 = 0.0; n = 0
    with ProcessPoolExecutor(workers) as ex:
        for rid, r in ex.map(_bee_one, rids, chunksize=8):
            for k, v in r["joint"].items(): tot[k] += v
            v1 += r["v1_s"]; v2 += r["v2_s"]; n += r["births"]
    rep = {"runs": len(rids), "births": n, "joint": dict(tot.most_common()), "adapter_cost_us_per_birth": {"v0.1": round(1e6 * v1 / n, 2), "v0.2": round(1e6 * v2 / n, 2)},
           "wall_s": round(time.time() - t0, 1)}
    # dispositions of the v0.1 disagreements
    def s(pred): return sum(v for k, v in tot.items() if pred(k.split("|")))
    rep["AN1_DECOUPLED"] = {"total": s(lambda k: k[0] == "DECOUPLED"),
                            "own_code_governed_writes(W=YES)": s(lambda k: k[0] == "DECOUPLED" and k[4] == "W=YES"),
                            "foreign_code_governed_writes(W=NO)": s(lambda k: k[0] == "DECOUPLED" and k[4] == "W=NO"),
                            "write_governance_NI": s(lambda k: k[0] == "DECOUPLED" and k[4] == "W=NOT_IDENTIFIABLE"),
                            "native_SR_and_W=YES": s(lambda k: k[0] == "DECOUPLED" and k[2] == "sr1" and k[4] == "W=YES"),
                            "native_SR_and_W!=YES": s(lambda k: k[0] == "DECOUPLED" and k[2] == "sr1" and k[4] != "W=YES")}
    rep["FF27_AUTONOMOUS_target"] = {"total": s(lambda k: k[0] == "AUTONOMOUS" and k[1] == "target"),
                                     "v02_continuity_writer": s(lambda k: k[0] == "AUTONOMOUS" and k[1] == "target" and k[6] == "cont=writer")}
    rep["UNRESOLVED_v01"] = {"total": s(lambda k: k[0] == "UNRESOLVED"), "v02_still_NI": s(lambda k: k[0] == "UNRESOLVED" and k[6] == "cont=NOT_IDENTIFIABLE")}
    rep["W=NO_anywhere"] = s(lambda k: k[4] == "W=NO"); rep["W=NO_and_M=YES"] = s(lambda k: k[4] == "W=NO" and k[3] == "M=YES")
    dump("BEE_V02.json", rep); return rep


def bee_arch(rid="r000001"):
    from archaeon.causal_lens.adapters import bee as B1
    tp = json.loads((EV2 / ("bee_%s_tapes.json" % rid)).read_text(encoding="utf-8"))
    cfg = json.loads((B1.RUNS / rid / "config.json").read_text(encoding="utf-8")); L = B1.L_of(cfg); p = B1.Pass(cfg)
    rows = list(B1.rows(rid)); assert len(rows) == len(tp["rows"]), "replay/trace length mismatch"
    align = sum(1 for r, t in zip(rows, tp["rows"]) if r[1] == t[1]); c = Counter(); mism = 0
    for r, t in zip(rows, tp["rows"]):
        e1 = p.step(r); e2 = A2.bee_row(r, L)
        child = bytes.fromhex(t[2]); wpre = bytes.fromhex(t[3])
        arch = A2.bee_arch(child, wpre)
        c[(e1["lens_class"], r[6], "fidW<.9" if r[4] < 0.9 else "fidW>=.9", "arch=%s" % arch)] += 1
    rep = {"rid": rid, "births": len(rows), "writer_id_alignment": align, "replay_wall_s": tp["wall_s"],
           "joint": {" | ".join(k): v for k, v in c.most_common()}}
    def s(pred): return sum(v for k, v in c.items() if pred(k))
    rep["AN7_AUTONOMOUS_target"] = {"total": s(lambda k: k[0] == "AUTONOMOUS" and k[1] == "target"),
                                   "arch_exact": s(lambda k: k[0] == "AUTONOMOUS" and k[1] == "target" and k[3] == "arch=exact"),
                                   "arch_rotation": s(lambda k: k[0] == "AUTONOMOUS" and k[1] == "target" and k[3] == "arch=rotation"),
                                   "arch_NI": s(lambda k: k[0] == "AUTONOMOUS" and k[1] == "target" and k[3] == "arch=NOT_IDENTIFIABLE")}
    rep["AUTONOMOUS_writer_arch"] = {a: s(lambda k, a=a: k[0] == "AUTONOMOUS" and k[1] == "writer" and k[3] == "arch=" + a) for a in ("exact", "rotation", "NOT_IDENTIFIABLE")}
    dump("BEE_ARCH_V02.json", rep); return rep


# ------------------------------------------------------------------------------------------------ NPE
def npe():
    t0 = time.time(); evs = []; viol = {}; per = {}
    for pth in sorted((EV1 / "npe").glob("*__s*__*.replay.json")):
        rec = json.loads(pth.read_text(encoding="utf-8")); g, out = A2.npe_graph(rec)
        v = g.check()
        if v: viol[pth.name] = v[:5]
        arm = pth.name.rsplit("__", 1)[1][:-len(".replay.json")]
        for o in out: o["arm"] = arm
        evs += out; per[pth.name] = len(out)
    c = Counter(); an3 = Counter()
    for o in evs:
        cf = o["cf"]
        c[("cont=%s" % ("decided" if o["hu_continuity"] not in ("NOT_IDENTIFIABLE", "ILL_POSED", "NONE") else o["hu_continuity"]),
           "N_real=%s" % cf.get("N_real"), "S_rebuild=%s" % cf.get("S_rebuild"), "S_author=%s" % cf.get("S_author"), "N_random=%s" % cf.get("N_random"))] += 1
        # host-conditioned signature (v0.2): donor material factually flows in situ, donor writes necessary in situ, donor NOT sufficient on a random victim
        factual = o["donor_material_share"] not in ("NOT_IDENTIFIABLE",) and (o["donor_material_share"] or 0) > 0
        an3[("factual_donor_material=%s" % factual, "N_real=%s" % cf.get("N_real"), "S_rebuild=%s" % cf.get("S_rebuild"))] += 1
    body = Counter(o["body_continuity"] for o in evs)
    shares = sorted(o["donor_material_share"] for o in evs if isinstance(o["donor_material_share"], (int, float)))
    fid = sorted(o["fid_init"] for o in evs if o["fid_init"] is not None)
    rep = {"runs": len(per), "pair_births": len(evs), "graph_violations": viol, "classes": {" | ".join(k): v for k, v in c.most_common()},
           "host_conditioned_signature": {" | ".join(k): v for k, v in an3.most_common()}, "body_continuity": dict(body),
           "donor_material_share": {"n": len(shares), "min": shares[0] if shares else None, "median": shares[len(shares) // 2] if shares else None, "max": shares[-1] if shares else None,
                                    "gt_half": sum(1 for x in shares if x > 0.5)},
           "fid_init": {"median": fid[len(fid) // 2] if fid else None, "max": fid[-1] if fid else None},
           "spontaneous_by_arm": {"%s|%s" % k: v for k, v in Counter((o["arm"], o["spontaneous"]) for o in evs).items()},
           "events": evs, "wall_s": round(time.time() - t0, 1)}
    dump("NPE_V02.json", rep); return rep


# ------------------------------------------------------------------------------------------------ PTE
def pte():
    import numpy as np
    from archaeon.causal_lens.adapters import ananke as A1
    row = None
    with gzip.open(A1.ROWS, "rt") as fh:
        for l in fh:
            r = json.loads(l)
            if r["kind"] == "evolve": row = r; break
    t0 = time.time(); small = {"pop": 16, "gens": 6, "M": 2, "M_final": 2, "M_held": 4}
    ph, env, log, genomes, same = A2.pte_instrumented_evolve(row, small)
    evo_s = time.time() - t0
    zero = np.zeros_like(next(iter(genomes.values()))); genomes["ZERO_CONTROL"] = zero
    t1 = time.time(); sig = A2.pte_behavior(ph, env, genomes); beh_s = time.time() - t1
    L = A2.pte_lens(log, sig, sig["ZERO_CONTROL"])
    sigs = Counter(v for k, v in sig.items() if k != "ZERO_CONTROL")
    rep = {"cell_id": row["cell_id"], "small_spec": small, "determinism": same, "ops": Counter(e["op"] for e in log), "genomes": len(genomes) - 1,
           "distinct_behavior_signatures": len(sigs), "largest_signature_class": sigs.most_common(1)[0][1] if sigs else 0,
           "zero_control_signature": sig["ZERO_CONTROL"], "crossover_classes": L["classes"], "crossover_rows": L["rows"],
           "evolve_s": round(evo_s, 1), "behavior_s": round(beh_s, 1)}
    dump("PTE_V02.json", rep); return rep


def main(argv=None):
    argv = (sys.argv[1:] if argv is None else argv) or ["archaeon", "npe", "pte", "pte_arch", "bee_arch", "bee"]
    for k in argv:
        r = globals()[k]()
        print(k, json.dumps({kk: vv for kk, vv in r.items() if kk not in ("events", "joint", "crossover_rows", "rows")}, default=str)[:3000], flush=True)



def pte_arch(group="1455015bd05a", n_children=24, seed=20260927):
    """Non-degenerate specimen for the B1/AN6 architecture test: native C1 champions sharing physics+env, crossed with PTE's own
    crossover (mask logged by the identical draw), behavior signatures by the FROZEN criterion (A2.pte_behavior)."""
    import hashlib
    import numpy as np
    from prometheus.ananke import search as S, envs
    from prometheus.ananke.physics import Physics
    from archaeon.causal_lens.adapters import ananke as A1
    from archaeon.causal_lens.schema_v02 import continuity
    champs = []; row0 = None
    with gzip.open(A1.ROWS, "rt") as fh:
        for l in fh:
            r = json.loads(l)
            if r["kind"] != "evolve": continue
            key = hashlib.sha256(json.dumps([r["physics"], r["env"]], sort_keys=True).encode()).hexdigest()[:12]
            if key != group: continue
            res = r.get("result") or {}; ch = res.get("champion") or (r.get("extra") or {}).get("genome")
            if ch is not None: champs.append((r["cell_id"], (res.get("held") or {}).get("acc"), np.array(ch))); row0 = row0 or r
    champs.sort(key=lambda x: -(x[1] or 0))
    ph = Physics.from_dict(row0["physics"]); env = envs.EnvSpec(**row0["env"]); rng = np.random.default_rng(seed)
    pairs = [(champs[0], champs[1]), (champs[2], champs[3])] if len(champs) >= 4 else [(champs[0], champs[1])]
    genomes = {"ZERO_CONTROL": np.zeros_like(champs[0][2])}; rows = []
    for (ca, a), (cb, b) in [((x[0], x[2]), (y[0], y[2])) for x, y in pairs]:
        genomes["P:" + ca] = a; genomes["P:" + cb] = b
        for k in range(n_children):
            m = rng.random(a.shape[:2]) < 0.5; c = np.where(m[..., None], a, b)               # == search.crossover, with the mask kept
            cid = "C:%s:%s:%d" % (ca[:6], cb[:6], k); genomes[cid] = c
            rows.append({"child": cid, "a": "P:" + ca, "b": "P:" + cb, "from_a": int(m.sum()), "total": int(m.size)})
    t0 = time.time(); sig = A2.pte_behavior(ph, env, genomes); beh = time.time() - t0
    out = Counter(); det = []
    for r in rows:
        c = continuity({"a": r["from_a"] / r["total"], "b": 1 - r["from_a"] / r["total"]}, A2.MAJ_ILL)
        sc, sa, sb = sig[r["child"]], sig[r["a"]], sig[r["b"]]
        arch = "same_as_a" if sc == sa and sc != sb else ("same_as_b" if sc == sb and sc != sa else ("same_as_both" if sc == sa == sb else "new_class"))
        cont = c["hu_continuity"]; agree = (cont == "a" and arch == "same_as_a") or (cont == "b" and arch == "same_as_b")
        out[("cont=%s" % cont, "arch=%s" % arch, "cont_matches_arch=%s" % agree)] += 1
        det.append(dict(r, hu_continuity=cont, arch=arch, degenerate=sc == sig["ZERO_CONTROL"]))
    rep = {"group": group, "parents": [(p[0][0], p[0][1], p[1][0], p[1][1]) for p in pairs], "parent_signatures_distinct": {r: sig[r] for r in genomes if r.startswith("P:")},
           "zero_control": sig["ZERO_CONTROL"], "classes": {" | ".join(k): v for k, v in out.most_common()}, "rows": det, "behavior_s": round(beh, 1)}
    dump("PTE_ARCH_V02.json", rep); return rep


if __name__ == "__main__":
    main()
