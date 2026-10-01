"""W2-G: independent re-derivation of PTE-C1 / C1b / harvest numbers from raw rows.

Does NOT import prometheus.ananke.report or campaign (no reuse of the report
aggregation). Labels are recomputed from the PREREG s7 thresholds written out
here (SIGNAL: held lo99 > 0.55; COMM_DEPENDENT: SIGNAL and comm_delta_lo99 > 0.03).
CPU only, no torch. Run from the worktree root:

    python roles/Ananke/research/harvest/wave2/W2-G/rederive_c1.py

Writes derived.json next to this file.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import math
import os
import pathlib
import statistics

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PTE = ROOT / "roles/Ananke/pte"
ROWS = PTE / "c1_rows/cells.jsonl.gz"
C1B = PTE / "c1b/c1b_rows/rows.jsonl.gz"
HP = ROOT / "roles/Ananke/research/harvest/H-PLANT"
FAMS = ("RELAY", "XOR", "MAJ", "FLIP", "HOLD")
SIG_LO = 0.55
COMM_LO = 0.03


def load(p):
    with gzip.open(p, "rt") as f:
        return [json.loads(l) for l in f]


R = load(ROWS)
BYID = {r["cell_id"]: r for r in R}
P8 = {r["cell_id"][:8]: r for r in R}
EV = [r for r in R if r["kind"] == "evolve"]
TR = [r for r in R if r["kind"] == "transfer"]
ADJ = [r for r in R if r["kind"] == "adjudicate"]
A0 = [r for r in R if r["wave"] == "A0"]
A1 = [r for r in EV if r["wave"] == "A"]
D = {}


def sig(r):
    return r["result"]["held"]["lo99"] > SIG_LO


def cdep(r):
    return sig(r) and r["result"]["held"]["comm_delta_lo99"] > COMM_LO


def fam(r):
    return r["env"]["family"]


def held(r):
    return r["result"]["held"]["acc"]


def physkey(r, with_env=True):
    o = [r["physics"]] + ([r["env"]] if with_env else [])
    return hashlib.sha1(json.dumps(o, sort_keys=True).encode()).hexdigest()[:10]


def hops(r):
    """Forward hop count sensor->actuator implied by the env placement rule.
    ring/torus: geometric distance d with neighbourhood radius r -> ceil(d/r);
    smallworld/random: d is BFS hops already (envs.dist_matrix); global: 1."""
    p, d = r["physics"], r["env"]["d"]
    t = p["topology"]
    if t == "global":
        return "global"
    if t in ("ring", "torus"):
        return max(1, math.ceil(d / p["radius"]))
    return d  # BFS hops (smallworld base is a radius-1 torus; random is directed)


def r3(x):
    return None if x is None else round(float(x), 3)


# ------------------------------------------------------------------ run-level
D["n_rows"] = len(R)
D["per_wave"] = dict(sorted(collections.Counter(r["wave"] for r in R).items()))
D["per_wave_kind"] = {f"{w}/{k}": n for (w, k), n in sorted(collections.Counter((r["wave"], r["kind"]) for r in R).items())}
fin = sorted(r["receipt"]["finished_at"] for r in R if r.get("receipt", {}).get("finished_at"))
D["finished_at_min_max"] = [fin[0], fin[-1]]
log = (PTE / "c1_rows/log.txt").read_text(encoding="utf-8")
D["log_first_line"] = log.splitlines()[0][:80]
D["censor_lines"] = [l for l in log.splitlines() if "BUDGET_CENSORED" in l]
D["log_fail_lines"] = [l for l in log.splitlines() if "fail" in l.lower()][:5]
D["code_sha_set"] = sorted({r["receipt"]["code_sha"][:9] for r in R})
D["freeze_sha_set"] = sorted({r["receipt"]["freeze_sha256"][:12] for r in R})
a = A1[0]
D["n_physics_dials"] = len(a["levels"])
D["n_env_dials"] = len(a["env_levels"])
D["A_search"] = a["search"]
D["A_cell_wall_mean_s"] = r3(statistics.mean(r["result"]["cell_wall_s"] for r in A1))
D["A_cell_wall_median_s"] = r3(statistics.median(r["result"]["cell_wall_s"] for r in A1))

# ------------------------------------------------------------------ A0 census
a0 = {}
for f in FAMS:
    rs = [r for r in A0 if fam(r) == f]
    pl = [r["result"]["plant"]["acc"] for r in rs]
    sens = [r["result"]["gen0"]["frac_sensitive_any"] for r in rs]
    cpos = [r["result"]["gen0"]["frac_contrast_pos"] for r in rs]
    L1 = sum(s >= 0.30 for s in sens)
    L2 = sum(c >= 2 / 64 for c in cpos)
    L2p = sum(p >= 0.75 for p in pl)
    living = sum((p >= 0.75) or (s >= 0.30) for p, s in zip(pl, sens))
    both = sum((c >= 2 / 64) and (p >= 0.75) for c, p in zip(cpos, pl))
    a0[f] = {"n": len(rs), "plant_mean": r3(statistics.mean(pl)), "viable_ge_.75": L2p,
             "L1_sens_ge_.30": L1, "L2_contrast_ge_2of64": L2, "L2p_and_L2": both,
             "living(plant>=.75 or sens>=.30)": living}
D["A0"] = a0
# RELAY plant viability by level (A0_FINDINGS s3 / C1_REPORT s2 "0/253")
rel0 = [r for r in A0 if fam(r) == "RELAY"]
byl = {}
for dial in ("loss", "decay_shift", "economy", "delta"):
    c = collections.defaultdict(lambda: [0, 0])
    for r in rel0:
        lv = r["levels"].get(dial, r["env_levels"].get(dial))
        c[str(lv)][0] += r["result"]["plant"]["acc"] >= 0.75
        c[str(lv)][1] += 1
    byl[dial] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(c.items())}
D["A0_RELAY_viable_by_level"] = byl
maj0 = [r for r in A0 if fam(r) == "MAJ"]
D["A0_MAJ_viable_at_decay_3_or_6"] = "%d/%d" % (
    sum(r["result"]["plant"]["acc"] >= 0.75 for r in maj0 if r["physics"]["decay_shift"] in (3, 6)),
    sum(1 for r in maj0 if r["physics"]["decay_shift"] in (3, 6)))
D["A0_MAJ_viable_any"] = "%d/%d" % (sum(r["result"]["plant"]["acc"] >= 0.75 for r in maj0), len(maj0))

# ------------------------------------------------------------------ evolve cells (all waves)
ev = {}
for f in FAMS:
    rs = [r for r in EV if fam(r) == f]
    ev[f] = {"n": len(rs), "SIGNAL": sum(map(sig, rs)), "COMM_DEPENDENT": sum(map(cdep, rs)),
             "n_by_wave": dict(collections.Counter(r["wave"] for r in rs)),
             "SIGNAL_by_wave": dict(collections.Counter(r["wave"] for r in rs if sig(r))),
             "distinct_phys_env_all": len({physkey(r) for r in rs}),
             "distinct_phys_env_SIGNAL": len({physkey(r) for r in rs if sig(r)}),
             "distinct_physics_SIGNAL": len({physkey(r, False) for r in rs if sig(r)})}
D["evolve_all_waves"] = ev
# stored labels agree with recomputed?
D["stored_label_mismatch"] = sum(1 for r in EV + TR if (r.get("labels") or {}).get("SIGNAL") not in (None, sig(r)))

# A1
a1 = {}
for f in FAMS:
    rs = [r for r in A1 if fam(r) == f]
    uni = [r for r in rs if r["extra"].get("uniform")]
    liv = [r for r in rs if "from_living_A0" in r["extra"]]
    hs = sorted(held(r) for r in rs)
    a1[f] = {"n": len(rs), "SIGNAL": sum(map(sig, rs)), "COMM_DEPENDENT": sum(map(cdep, rs)),
             "LOCAL_ONLY": sum(1 for r in rs if sig(r) and not cdep(r)),
             "uniform": f"{sum(map(sig, uni))}/{len(uni)}", "living": f"{sum(map(sig, liv))}/{len(liv)}",
             "held_max": r3(hs[-1]), "held_median": r3(statistics.median(hs))}
    if f == "MAJ":
        a1[f]["INTEGRATION_lo99_gt_.70"] = sum(r["result"]["held"]["lo99"] > 0.70 for r in rs)
D["A1"] = a1
D["A1_COMM_DEPENDENT_total"] = f"{sum(map(cdep, A1))}/{len(A1)}"
D["A1_COMM_DEPENDENT_comm_families_only"] = f"{sum(cdep(r) for r in A1 if fam(r) != 'HOLD')}/{sum(1 for r in A1 if fam(r) != 'HOLD')}"
D["A1_SIGNAL_comm_families"] = f"{sum(sig(r) for r in A1 if fam(r) != 'HOLD')}/{sum(1 for r in A1 if fam(r) != 'HOLD')}"
D["A1_HOLD_decay1"] = "%d SIGNAL of %d" % (sum(sig(r) for r in A1 if fam(r) == "HOLD" and r["physics"]["decay_shift"] == 1),
                                           sum(1 for r in A1 if fam(r) == "HOLD" and r["physics"]["decay_shift"] == 1))

# ------------------------------------------------------------------ zero_comm identity (harvest #1)
zc = {}
for f in FAMS:
    for kind, rs in (("evolve", EV), ("transfer", TR)):
        z = [r["result"]["held"]["zero_comm"] for r in rs if fam(r) == f]
        zc[f"{f}/{kind}"] = f"{sum(1 for x in z if x == 0.5)}/{len(z)}"
    z = [r["result"]["held"]["zero_comm"] for r in EV + TR if fam(r) == f]
    zc[f"{f}/evolve+transfer"] = f"{sum(1 for x in z if x == 0.5)}/{len(z)}"
D["zero_comm_exact_half"] = zc
D["comm_dependent_equals_signal"] = {f: [ev[f]["SIGNAL"], ev[f]["COMM_DEPENDENT"]] for f in FAMS}
# D-wave adjudication zero_comm / max_loss
D["D_zero_comm_maxloss_comm_fams"] = sorted({(r3(a["result"]["controls"]["zero_comm"]["acc"]), r3(a["result"]["controls"]["max_loss"]["acc"]))
                                             for a in ADJ if fam(a) != "HOLD"})

# ------------------------------------------------------------------ one-hop (harvest #2)
oh = {}
for f in ("RELAY", "MAJ", "XOR", "FLIP"):
    for waves, tag in ((("A",), "A1"), (("A", "B", "B2", "C", "D", "E"), "all")):
        rs = [r for r in EV if fam(r) == f and r["wave"] in waves]
        c = collections.defaultdict(lambda: [0, 0])
        for r in rs:
            h = hops(r)
            topo = r["physics"]["topology"]
            k = "global" if h == "global" else (f"random_d{h}" if topo == "random" else ("1hop" if h == 1 else "multihop"))
            c[k][0] += sig(r)
            c[k][1] += 1
        oh[f"{f}/{tag}"] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(c.items())}
D["signal_by_hop_class"] = oh
rs = [r for r in EV if fam(r) == "RELAY" and sig(r)]
D["RELAY_SIGNAL_topology_radius_d"] = {f"{t}|r{rad}|d{d}": n for (t, rad, d), n in sorted(collections.Counter(
    (r["physics"]["topology"], r["physics"]["radius"], r["env"]["d"]) for r in rs).items())}
D["RELAY_SIGNAL_multihop_cells"] = [(r["cell_id"][:8], r["wave"], r["physics"]["topology"], r["env"]["d"], r3(held(r)), r3(r["result"]["held"]["lo99"]))
                                    for r in rs if hops(r) not in (1, "global")]
rs = [r for r in EV if fam(r) == "MAJ" and sig(r)]
D["MAJ_SIGNAL_topology_radius_d"] = {f"{t}|r{rad}|d{d}": n for (t, rad, d), n in sorted(collections.Counter(
    (r["physics"]["topology"], r["physics"]["radius"], r["env"]["d"]) for r in rs).items())}


# d9cc physics point (H-SCI F3): ring 144 r3 fanout 8 pw 2 saturate cap 2 sync period 2
def is_d9cc(r):
    p = r["physics"]
    return (p["topology"] == "ring" and p["radius"] == 3 and p["fanout"] == 8 and p["payload_width"] == 2
            and p["collision"] == "saturate" and p["cap"] == 2 and p["update_mode"] == "sync"
            and p["update_period"] == 2 and p["lat_base"] == 1 and p["lat_hop"] == 1 and p["lat_jitter"] == 1
            and p["plastic_route"] == 1 and p["wimm"] == 1)


D["RELAY_SIGNAL_at_d9cc_point"] = f"{sum(is_d9cc(r) for r in EV if fam(r) == 'RELAY' and sig(r))}/{ev['RELAY']['SIGNAL']}"
D["RELAY_SIGNAL_at_d9cc_point_wave"] = dict(collections.Counter(r["wave"] for r in EV if fam(r) == "RELAY" and sig(r) and is_d9cc(r)))


# lineage: does every RELAY SIGNAL above .8 descend from A1 86fc0105?
def ancestry(r):
    seen = []
    cur = r
    for _ in range(10):
        e = cur["extra"]
        nxt = e.get("base_cell") or e.get("source_cell") or e.get("replicates") or (cur.get("parent") if isinstance(cur.get("parent"), str) else None)
        if not nxt or nxt not in BYID:
            break
        seen.append(nxt[:8])
        cur = BYID[nxt]
    return seen


hi = [r for r in EV if fam(r) == "RELAY" and held(r) > 0.8]
D["RELAY_held_gt_.8"] = [(r["cell_id"][:8], r["wave"], r3(held(r)), ancestry(r)) for r in hi]
sigrel = [r for r in EV if fam(r) == "RELAY" and sig(r)]
D["RELAY_SIGNAL_descend_from_86fc0105"] = f"{sum('86fc0105' in ancestry(r) or r['cell_id'].startswith('86fc0105') for r in sigrel)}/{len(sigrel)}"
D["RELAY_SIGNAL_roots"] = dict(collections.Counter((ancestry(r) or [r["cell_id"][:8]])[-1] for r in sigrel))

# ------------------------------------------------------------------ C transfers
ct = [r for r in TR if r["wave"] == "C"]
out = []
for r in ct:
    src = r["extra"]["source_family"]
    tsup = r["result"]["held"]["lo99"] > SIG_LO and (fam(r) != src or r["extra"].get("variant"))
    out.append((src, fam(r), json.dumps(r["extra"].get("variant")), r3(held(r)), r3(r["result"]["held"]["lo99"]), bool(tsup)))
D["C_transfer_n"] = len(ct)
D["C_TRANSFER_SUPPORT_cross_family"] = sum(1 for o in out if o[5] and o[0] != o[1])
D["C_TRANSFER_SUPPORT_HOLD_variants"] = sum(1 for o in out if o[5] and o[0] == o[1] == "HOLD")
D["C_RELAY_within_family"] = [o for o in out if o[0] == o[1] == "RELAY"]
D["C_cross_family_max_lo99"] = max((o for o in out if o[0] != o[1]), key=lambda o: o[4])
ce = [r for r in EV if r["wave"] == "C"]
D["C_reevolve"] = f"{sum(map(sig, ce))} SIGNAL of {len(ce)}"
D["C_reevolve_SIGNAL"] = [(r["cell_id"][:8], fam(r), r3(held(r)), r["extra"]["source_cell"][:8]) for r in ce if sig(r)]

# ------------------------------------------------------------------ D adjudication
rep = collections.defaultdict(list)
for r in EV:
    if r["wave"] == "D":
        rep[r["extra"]["replicates"]].append(r)
dd = {}
for a in ADJ:
    sc = a["extra"]["source_cell"]
    c = a["result"]["controls"]
    g = lambda k: (r3(c[k]["acc"]) if c.get(k, {}).get("status", "RAN") == "RAN" and "acc" in c.get(k, {}) else c.get(k, {}).get("status"))
    n = c["normal"]["acc"]
    ok_perm = 0.40 <= c["env_permutation"]["acc"] <= 0.60
    if fam(a) == "HOLD":
        lab = "CAUSAL_SUPPORT" if (c["memory_ablation"].get("status", "RAN") == "RAN" and c["memory_ablation"]["acc"] <= n - 0.10 and ok_perm) else "NOT_SUPPORTED"
    else:
        ran = all(c[k].get("status", "RAN") == "RAN" for k in ("zero_comm", "packet_ablation"))
        lab = ("CAUSAL_SUPPORT" if c["zero_comm"]["acc"] <= 0.55 and c["packet_ablation"]["acc"] <= n - 0.10 and ok_perm
               else "NOT_SUPPORTED") if ran else "INCONCLUSIVE"
    tp = a["result"]["transplants"]
    dd[sc[:8]] = {"family": fam(a), "held": r3(held(BYID[sc])), "held_lo99": r3(BYID[sc]["result"]["held"]["lo99"]),
                  "reps": [r3(held(x)) for x in rep[sc]], "reps_SIGNAL": [sig(x) for x in rep[sc]],
                  "causal": lab, "controls": {k: g(k) for k in c},
                  "transplants": {k: (r3(v["acc"]) if isinstance(v, dict) and "acc" in v else (v.get("status") if isinstance(v, dict) else v)) for k, v in tp.items()},
                  "twin": a["result"]["twin"], "adj_cell": a["cell_id"][:8],
                  "n_sites": BYID[sc]["physics"]["n_sites"], "topology": BYID[sc]["physics"]["topology"]}
D["D"] = dd
relD = {k: v for k, v in dd.items() if v["family"] == "RELAY"}
D["RELAY_D_causal"] = f"{sum(v['causal'] == 'CAUSAL_SUPPORT' for v in relD.values())}/{len(relD)}"
D["RELAY_D_reproduced"] = f"{sum(any(v['reps_SIGNAL']) for v in relD.values())}/{len(relD)}"
D["RELAY_D_both_reps_SIGNAL"] = f"{sum(all(v['reps_SIGNAL']) for v in relD.values())}/{len(relD)}"
D["RELAY_D_topology_random"] = {k: v["transplants"].get("topology->random") for k, v in relD.items()}
D["RELAY_D_ranges"] = {key: [min(v["controls"][key] for v in relD.values()), max(v["controls"][key] for v in relD.values())]
                       for key in ("zero_comm", "max_loss", "shuffle_dest", "shuffle_time", "randomize_payload", "env_permutation")}
D["RELAY_D_transplant_ranges"] = {key: [min(v["transplants"][key] for v in relD.values()), max(v["transplants"][key] for v in relD.values())]
                                  for key in ("loss+0.2", "latency+1", "jitter+2", "size_x2.25", "async0.7", "noise+32")}
D["RELAY_D_n_sites"] = {k: v["n_sites"] for k, v in relD.items()}

# ------------------------------------------------------------------ E scale
E = [r for r in R if r["wave"] == "E"]
D["E"] = [(r["kind"], fam(r), r["physics"]["n_sites"], r3(held(r)), r3(r["result"]["held"]["lo99"]),
           (r["extra"].get("source_cell") or "")[:8],
           r3(held(BYID[r["extra"]["source_cell"]])) if r["extra"].get("source_cell") in BYID else None,
           BYID[r["extra"]["source_cell"]]["physics"]["n_sites"] if r["extra"].get("source_cell") in BYID else None)
          for r in E]
D["E_RELAY_sources"] = sorted({e[5] for e in D["E"] if e[1] == "RELAY"})
D["E_HOLD_transfer_1024"] = [(e[6], e[3]) for e in D["E"] if e[1] == "HOLD" and e[0] == "transfer" and e[2] == 1024]

# ------------------------------------------------------------------ anomalies (recomputed independently)
an = collections.Counter()
mism = 0
for r in EV:
    h, tel, tw = r["result"]["held"], r["result"].get("held_tel", {}), r["result"].get("twin", {})
    f = []
    if h["acc"] > 0.6 and tel.get("emit_rate", 1) < 0.01 and fam(r) != "HOLD":
        f.append("SILENT_COMPETENCE")
    if h["acc"] > 0.6 and h["comm_delta"] < 0.02 and fam(r) in ("RELAY", "XOR", "MAJ"):
        f.append("COMPETENT_WITHOUT_COMM")
    if tw.get("persist", 0) > 3 * r["env"]["delta"] and tw.get("div_frac_readout", 0) > 0.25 and h["acc"] <= 0.55:
        f.append("MEMORY_WITHOUT_USE")
    if h["acc"] > 0.6 and r["physics"]["loss"] >= 0.3:
        f.append("ROBUST_UNDER_LOSS")
    if h["acc"] > 0.6 and r["levels"].get("economy") == "high":
        f.append("COMPETENT_UNDER_COST")
    if h["acc"] < 0.45:
        f.append("ANTI_CORRELATED")
    if r["result"].get("champ_train_final", 0.5) - h["acc"] > 0.15:
        f.append("TRAIN_HELD_GAP")
    if fam(r) == "HOLD" and h["acc"] > 0.6 and r["physics"]["decay_shift"] in (1, 3) and h["comm_delta"] > 0.05:
        f.append("DISTRIBUTED_MEMORY_UNDER_DECAY")
    an.update(f)
    mism += sorted(f) != sorted(r.get("anomalies", []))
D["anomalies_recomputed"] = dict(an)
D["anomalies_stored_mismatch_rows"] = mism
D["MEMORY_WITHOUT_USE_by_family"] = dict(collections.Counter(fam(r) for r in EV if "MEMORY_WITHOUT_USE" in r.get("anomalies", [])))

# ------------------------------------------------------------------ boundaries (recount the stored verdicts; recompute RELAY plant means from B rows)
bv = json.loads((PTE / "c1_rows/boundaries_verdicts.json").read_text())
D["boundary_counts"] = dict(collections.Counter(v["label"] for v in bv))
sup = [v for v in bv if v["label"] == "PHASE_BOUNDARY_SUPPORTED"]
D["SUPPORTED_by_family_metric"] = dict(collections.Counter(f"{v['family']}/{v['track']}/{v['metric']}/{v['dial']}" for v in sup))
D["SUPPORTED_evo_track"] = sum(v["track"] == "evo" for v in sup)
bb = [r for r in R if r["wave"] == "B" and r["kind"] == "census" and fam(r) == "RELAY"]
chk = {}
for v in bv:
    if v["family"] != "RELAY" or v["metric"] != "plant" or v["track"] != "phys":
        continue
    rs = [r for r in bb if r["extra"].get("transect") == v["dial"] and r["extra"].get("base") == v["base"]]
    m = collections.defaultdict(list)
    for r in rs:
        m[r["extra"]["level_index"]].append(r["result"]["plant"]["acc"])
    means = [statistics.mean(m[i]) for i in sorted(m)]
    i, j = v["between"]
    chk[f"{v['dial']}@base{v['base']}"] = {"recomputed_means": [r3(x) for x in means], "stored_means": [r3(x) for x in v["means"]],
                                          "recomputed_jump": r3(means[j] - means[i]) if len(means) > j else None, "stored_jump": r3(v["jump"])}
D["RELAY_plant_boundary_recheck"] = chk

# ------------------------------------------------------------------ predictions
D["P3_XOR_SIGNAL"] = f"{ev['XOR']['SIGNAL']}/{ev['XOR']['n']}"
D["P4"] = D["A1_COMM_DEPENDENT_total"]
D["P4_pct"] = round(100 * sum(map(cdep, A1)) / len(A1), 2)
D["P6_DMUD"] = an.get("DISTRIBUTED_MEMORY_UNDER_DECAY", 0)
D["P8_ANTI"] = an.get("ANTI_CORRELATED", 0)
D["XOR_FLIP_evolve_total"] = ev["XOR"]["n"] + ev["FLIP"]["n"]

# ------------------------------------------------------------------ post-hoc M2 (c1_posthoc)
ph = json.loads((PTE / "c1_posthoc/posthoc_adjudication.json").read_text())
cells = ph["cells"] if isinstance(ph["cells"], list) else list(ph["cells"].items())
phd = {}
for cid, c in cells:
    ctl = c.get("controls", {})
    phd[cid[:8]] = {"family": c["family"], "held": r3(c["held"]["acc"]),
                    "controls": {k: (r3(v["acc"]) if isinstance(v, dict) and "acc" in v else (v.get("status") if isinstance(v, dict) else v)) for k, v in ctl.items()}}
D["posthoc"] = phd

# ------------------------------------------------------------------ C1b
B = load(C1B)
D["c1b_n_rows"] = len(B)
D["c1b_status"] = dict(collections.Counter(r["status"] for r in B))
D["c1b_done"] = json.loads((PTE / "c1b/c1b_rows/DONE.json").read_text())
D["c1b_raw_sha256_16"] = hashlib.sha256(gzip.open(C1B).read()).hexdigest()[:16]
s1 = {}
for r in B:
    if r["stage"] != "S1":
        continue
    s1[r["cell"][:8]] = {"label": r["label"], "arms": {k: (r3(v["acc"][0]) if v.get("status") == "RAN" else v.get("status")) for k, v in r["arms"].items()},
                         "carryover": round(r["carryover"]["mean_inflight_at_onset"]), "carry_flag": r["carryover"]["CARRYOVER"],
                         "census": {k: r3(r["census"][k]) for k in ("acc", "perm_p")} if r.get("census") else None,
                         "rule_predicts": r3(r["rule_predicts"]["acc"]) if r.get("rule_predicts") else None,
                         "c1_window_lo99": r3(r["booleans"].get("_positive_components", {}).get("c1_window_lo99")) if r["mechanism"] == "M3" else None}
D["c1b_S1"] = s1
D["c1b_S2"] = [(r["mechanism"], r["replicates"][:8], r["k"], r3(r["held"]["acc"]), r["signal"], r.get("label"),
                {k: r3(v["acc"][0]) for k, v in r.get("arms", {}).items() if k in ("normal", "drop_window_c1", "drop_readout_tick_only", "latency_plus1", "flush_inflight", "reset_all_nonpacket") and v.get("status") == "RAN"})
               for r in B if r["stage"] == "S2"]
D["c1b_S3"] = {r["cell"][:8]: {k: r3(v["acc"][0]) for k, v in r["arms"].items()} | {"frozen_routing_C1": r["frozen_routing_C1"]}
               for r in B if r["stage"] == "S3"}
m2 = [x for x in D["c1b_S2"] if x[0] == "M2"]
D["c1b_M2_fresh_SIGNAL"] = f"{sum(x[4] for x in m2)}/{len(m2)}"
D["c1b_M2_fresh_flush_kills_among_SIGNAL"] = f"{sum(1 for x in m2 if x[4] and x[6].get('flush_inflight', 1) <= 0.55)}/{sum(x[4] for x in m2)}"

# ------------------------------------------------------------------ H-PLANT light-cone census split by row kind
lc = json.loads((HP / "out/lc_census.json").read_text())
split = collections.defaultdict(lambda: [0, 0])
for o in lc["rows"]:
    k = BYID[o["cell"]]["kind"]
    split[f"{o['family']}/{k}"][0] += o["bound"] < 0.60
    split[f"{o['family']}/{k}"][1] += 1
    if BYID[o["cell"]]["wave"] == "A" and k == "evolve":
        split[f"{o['family']}/A1-evolve"][0] += o["bound"] < 0.60
        split[f"{o['family']}/A1-evolve"][1] += 1
D["lightcone_capped_by_kind"] = {k: f"{v[0]}/{v[1]} ({v[0] / v[1]:.3f})" for k, v in sorted(split.items())}
D["lightcone_summary_as_published"] = lc["summary"]

# ------------------------------------------------------------------ cells cited in docs whose kind is not 'evolve'
D["kind_of_cited_cells"] = {k: (P8[k]["wave"], P8[k]["kind"], fam(P8[k]), r3(P8[k]["result"].get("held", {}).get("acc")),
                                (P8[k]["extra"].get("source_cell") or "")[:8])
                            for k in ("fac4aaa2", "1b26026f", "ef77ef2e", "d64656f2", "6f82f9c7", "f7e62fe3", "aa2b8d68",
                                      "4ab2ba01", "86fc0105", "bbef66a1", "925caa3a", "882525a9", "613162a3")}

(HERE / "derived.json").write_text(json.dumps(D, indent=1, default=str) + "\n")
print("wrote", HERE / "derived.json", "keys", len(D))
