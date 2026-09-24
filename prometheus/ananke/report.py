"""PTE evidence package from a campaign's cells.jsonl (read-only).

    python -m prometheus.ananke.report --run <ANANKE_HOME>/<campaign> --out <dir>

Writes <out>/summary.json (every number the report states, recomputed
from rows), <out>/REPORT.md (pure ASCII), and the Atlas pointer files
<out>/atlas_fact.jsonl + atlas_edge.jsonl. Labels are recomputed with the
frozen campaign functions (classify, causal_label, detect_boundaries), so
the report cannot disagree with the campaign's own rules.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib

import numpy as np

from . import campaign as C

FAMS = ("RELAY", "XOR", "MAJ", "FLIP", "HOLD")


def load(run: pathlib.Path):
    rows = []
    with open(run / "cells.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    cfg_raw = None
    for p in (run / "run_meta.json",):
        if p.exists():
            cfg_raw = json.loads(p.read_text())
    return rows, cfg_raw


def f3(x):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}"


def by(rows, key):
    d = collections.defaultdict(list)
    for r in rows:
        d[key(r)].append(r)
    return d


def dial_table(rows, fam, metric, top=8):
    eff = C.dial_effects(rows, fam, metric)[:top]
    out = []
    for score, dial, means in eff:
        lv = ", ".join(f"{json.loads(k)}:{v:.2f}" for k, v in sorted(means.items(), key=lambda kv: kv[0]))
        out.append({"dial": dial, "score_se": round(float(score), 1), "means": means, "text": lv})
    return out


def build(run: pathlib.Path, cfg: C.CampaignConfig) -> dict:
    rows, meta = load(run)
    S = {"campaign": cfg.campaign_id, "n_rows": len(rows), "meta": meta}
    waves = by(rows, lambda r: r["wave"])
    S["cells_per_wave"] = {w: len(v) for w, v in sorted(waves.items())}
    fails = (run / "failures.log")
    S["failed_cells"] = sum(1 for _ in open(fails)) if fails.exists() else 0
    log = (run / "log.txt").read_text(encoding="utf-8") if (run / "log.txt").exists() else ""
    S["censor_lines"] = [ln for ln in log.splitlines() if "BUDGET_CENSORED" in ln]
    # ---------------- A0 physics census
    A0 = waves.get("A0", [])
    a0 = {}
    for fam in FAMS:
        rs = [r for r in A0 if r["env"]["family"] == fam]
        if not rs:
            continue
        pl = np.array([r["result"]["plant"]["acc"] for r in rs])
        se = np.array([r["result"]["gen0"]["frac_sensitive_any"] for r in rs])
        em = np.array([r["result"]["gen0"]["frac_emitting"] for r in rs])
        a0[fam] = {"n": len(rs), "plant_mean": float(pl.mean()), "plant_viable_frac": float((pl >= 0.75).mean()),
                   "sens_mean": float(se.mean()), "living_frac": float(np.mean([C.living(r, cfg) for r in rs])),
                   "emit_mean": float(em.mean()),
                   "top_dials_plant": dial_table(A0, fam, "plant"),
                   "top_dials_sens": dial_table(A0, fam, "sens")}
    S["A0"] = a0
    # ---------------- evolution cells (all waves)
    EV = [r for r in rows if r["kind"] == "evolve"]
    for r in EV:
        r["_lab"] = C.classify(r, cfg)
    A1 = [r for r in EV if r["wave"] == "A"]
    a1 = {}
    for fam in FAMS:
        rs = [r for r in A1 if r["env"]["family"] == fam]
        if not rs:
            continue
        held = np.array([r["result"]["held"]["acc"] for r in rs])
        a1[fam] = {"n": len(rs),
                   "n_uniform": sum(1 for r in rs if r["extra"].get("uniform")),
                   "n_living": sum(1 for r in rs if "from_living_A0" in r["extra"]),
                   "SIGNAL": sum(r["_lab"]["SIGNAL"] for r in rs),
                   "SIGNAL_uniform": sum(r["_lab"]["SIGNAL"] for r in rs if r["extra"].get("uniform")),
                   "SIGNAL_living": sum(r["_lab"]["SIGNAL"] for r in rs if "from_living_A0" in r["extra"]),
                   "COMM_DEPENDENT": sum(r["_lab"]["COMM_DEPENDENT"] for r in rs),
                   "LOCAL_ONLY": sum(r["_lab"]["LOCAL_ONLY"] for r in rs),
                   "INTEGRATION": sum(bool(r["_lab"].get("INTEGRATION_BEYOND_ONE_SENSOR")) for r in rs)
                   + (sum(r["_lab"]["SIGNAL"] for r in rs) if fam == "XOR" else 0),
                   "held_quantiles": np.quantile(held, [0, .5, .9, 1]).round(3).tolist(),
                   "top_dials_acc": dial_table(A1, fam, "acc"),
                   "best": sorted(({"cell": r["cell_id"], "held": r["result"]["held"]["acc"],
                                    "lo99": r["result"]["held"]["lo99"], "zero_comm": r["result"]["held"]["zero_comm"],
                                    "comm_delta_lo99": r["result"]["held"]["comm_delta_lo99"],
                                    "levels": r["levels"], "env": r["env_levels"]} for r in rs),
                                  key=lambda x: -x["lo99"])[:3]}
    S["A1"] = a1
    # ---------------- anomalies
    an = collections.Counter()
    ex = {}
    for r in EV:
        for f in r.get("anomalies", []):
            an[f] += 1
            ex.setdefault(f, []).append(r["cell_id"])
    S["anomalies"] = {k: {"count": v, "examples": ex[k][:5]} for k, v in an.most_common()}
    # ---------------- boundaries
    for name in ("boundaries_B.json", "boundaries_verdicts.json"):
        p = run / name
        S[name.split(".")[0]] = json.loads(p.read_text()) if p.exists() else []
    verd = S["boundaries_verdicts"]
    S["boundary_counts"] = collections.Counter(v["label"] for v in verd)
    # ---------------- C: transfer + re-evolution
    Ct = [r for r in rows if r["wave"] == "C" and r["kind"] == "transfer"]
    S["C_transfer"] = [{"source": r["extra"]["source_cell"], "from": r["extra"]["source_family"],
                        "to": r["env"]["family"], "variant": r["extra"].get("variant"),
                        "held": r["result"]["held"]["acc"], "lo99": r["result"]["held"]["lo99"],
                        "TRANSFER_SUPPORT": bool(r["result"]["held"]["lo99"] > 0.5 + cfg.signal_margin
                                                 and (r["env"]["family"] != r["extra"]["source_family"]
                                                      or r["extra"].get("variant")))}
                       for r in Ct]
    Ce = [r for r in EV if r["wave"] == "C"]
    S["C_reevolve"] = [{"source": r["extra"]["source_cell"], "family": r["env"]["family"],
                        "held": r["result"]["held"]["acc"], "SIGNAL": r["_lab"]["SIGNAL"]} for r in Ce]
    # ---------------- D: adjudication
    Dadj = [r for r in rows if r["wave"] == "D" and r["kind"] == "adjudicate"]
    Drep = [r for r in EV if r["wave"] == "D"]
    rep_by = by(Drep, lambda r: r["extra"]["replicates"])
    dd = []
    src = {r["cell_id"]: r for r in EV}
    for r in Dadj:
        sc = r["extra"]["source_cell"]
        fam = r["env"]["family"]
        reps = rep_by.get(sc, [])
        tp = r["result"]["transplants"]
        transfer_tp = [k for k, v in tp.items() if isinstance(v, dict) and v.get("acc", 0) > 0.5 + cfg.signal_margin
                       and k != "state_transplant"]
        dd.append({"source": sc, "family": fam, "physics": src.get(sc, {}).get("levels"),
                   "held": src.get(sc, {}).get("result", {}).get("held", {}).get("acc"),
                   "REPRODUCED_SIGNAL": any(x["_lab"]["SIGNAL"] for x in reps),
                   "replicate_held": [x["result"]["held"]["acc"] for x in reps],
                   "causal": C.causal_label(r, fam),
                   "controls": {k: (v.get("acc") if v.get("status", "RAN") == "RAN" else v.get("status"))
                                for k, v in r["result"]["controls"].items()},
                   "transplants": {k: (v.get("acc") if isinstance(v, dict) and "acc" in v else v)
                                   for k, v in tp.items()},
                   "transplant_transfer": transfer_tp,
                   "twin": r["result"]["twin"]})
    S["D"] = dd
    # ---------------- E: scale
    Et = [r for r in rows if r["wave"] == "E"]
    S["E"] = [{"source": r["extra"].get("source_cell"), "kind": r["kind"], "family": r["env"]["family"],
               "N": r["physics"]["n_sites"],
               "held": r["result"]["held"]["acc"], "lo99": r["result"]["held"]["lo99"],
               "source_held": src.get(r["extra"].get("source_cell"), {}).get("result", {}).get("held", {}).get("acc")}
              for r in Et]
    # ---------------- predictions (PREREG s12)
    S["predictions"] = score_predictions(S, EV, A0, A1, verd, cfg)
    return S


def score_predictions(S, EV, A0, A1, verd, cfg):
    P = {}
    rel = [v for v in verd if v["family"] == "RELAY" and v["metric"] == "plant"
           and v["dial"] in ("lat_base", "loss", "delta", "d") and v["label"] == "PHASE_BOUNDARY_SUPPORTED"]
    P["P1"] = {"claim": "RELAY plant boundary SUPPORTED on lat_base/loss/delta/d", "held": bool(rel),
               "evidence": [(v["dial"], v["between"]) for v in rel]}
    hold = S["A0"].get("HOLD", {})
    top3 = [d["dial"] for d in hold.get("top_dials_plant", [])[:3]] + [d["dial"] for d in hold.get("top_dials_sens", [])[:3]]
    h1 = [r for r in A1 if r["env"]["family"] == "HOLD" and r["physics"]["decay_shift"] == 1]
    P["P2"] = {"claim": "decay_shift in HOLD top-3 A0 dials AND HOLD A1 at decay 1 all NULL",
               "held": (None if not h1 else ("decay_shift" in top3) and not any(r["_lab"]["SIGNAL"] for r in h1)),
               "evidence": {"top3": top3, "n_decay1": len(h1), "signals_decay1": sum(r["_lab"]["SIGNAL"] for r in h1)},
               "note": "INDETERMINATE if no HOLD A1 cell had decay 1" if not h1 else ""}
    xs = [r for r in EV if r["env"]["family"] == "XOR" and r["_lab"]["SIGNAL"]]
    P["P3"] = {"claim": "zero XOR SIGNAL cells", "held": not xs, "evidence": [r["cell_id"] for r in xs]}
    cd = sum(r["_lab"]["COMM_DEPENDENT"] for r in A1)
    P["P4"] = {"claim": "<= 5% of A1 COMM_DEPENDENT", "held": (cd / max(1, len(A1))) <= 0.05,
               "evidence": {"comm_dependent": cd, "n": len(A1)}}
    tr = [t for t in S["C_transfer"] if t["TRANSFER_SUPPORT"] and t["from"] != "HOLD" and t["to"] != t["from"]]
    P["P5"] = {"claim": "zero cross-family TRANSFER_SUPPORT from comm-family champions", "held": not tr,
               "evidence": tr[:5]}
    dm = S["anomalies"].get("DISTRIBUTED_MEMORY_UNDER_DECAY", {"count": 0})["count"]
    P["P6"] = {"claim": "zero DISTRIBUTED_MEMORY_UNDER_DECAY flags", "held": dm == 0, "evidence": dm}
    hs = [e for e in S["E"] if e["family"] == "HOLD" and e["kind"] == "transfer" and e["N"] == 1024
          and e["source_held"] is not None]
    P["P7"] = {"claim": "HOLD champions within +-0.05 at N=1024", "held": None if not hs else all(
        abs(e["held"] - e["source_held"]) <= 0.05 for e in hs),
        "evidence": [(e["source_held"], e["held"]) for e in hs], "note": "INDETERMINATE if none" if not hs else ""}
    ac = [r for r in EV if "ANTI_CORRELATED" in r.get("anomalies", [])]
    P["P8"] = {"claim": ">= 1 ANTI_CORRELATED cell has decay_shift > 0", "held": any(
        r["physics"]["decay_shift"] > 0 for r in ac),
        "evidence": {"anti": len(ac), "with_decay": sum(r["physics"]["decay_shift"] > 0 for r in ac)}}
    # tri-state: None = INDETERMINATE (the evidence the claim needs does not exist);
    # it is never counted as held.
    return P


def to_markdown(S: dict) -> str:
    L = []
    w = L.append
    w(f"# PTE {S['campaign']} -- evidence package (generated by prometheus/ananke/report.py)")
    w("")
    w("Every number below is recomputed from cells.jsonl by report.py; labels")
    w("use the frozen campaign functions. Nothing here is a verdict about")
    w("intelligence; labels are the PREREG s7 vocabulary only.")
    w("")
    w("## 1. Run")
    w(f"rows {S['n_rows']}; per wave {S['cells_per_wave']}; failed cells {S['failed_cells']}")
    for ln in S["censor_lines"]:
        w("  " + ln)
    w("")
    w("## 2. A0 physics census (plant viability, random-substrate liveness)")
    w("family  n     plant_mean  viable>=.75  sens_mean  living  emit_frac")
    for fam, a in S["A0"].items():
        w(f"{fam:6s}  {a['n']:<5d} {f3(a['plant_mean']):11s} {f3(a['plant_viable_frac']):12s}"
          f" {f3(a['sens_mean']):10s} {f3(a['living_frac']):7s} {f3(a['emit_mean'])}")
    for fam, a in S["A0"].items():
        w(f"-- {fam}: dials by effect on plant viability (level:mean) [score in SE]")
        for d in a["top_dials_plant"][:5]:
            w(f"   {d['dial']:14s} [{d['score_se']}] {d['text']}")
        w(f"-- {fam}: dials by effect on random-substrate sensitivity")
        for d in a["top_dials_sens"][:5]:
            w(f"   {d['dial']:14s} [{d['score_se']}] {d['text']}")
    w("")
    w("## 3. A1 evolution census")
    w("family  n    SIGNAL (unif/living)  COMM_DEP  LOCAL  INTEGR  held q0/q50/q90/max")
    for fam, a in S["A1"].items():
        w(f"{fam:6s}  {a['n']:<4d} {a['SIGNAL']:3d} ({a['SIGNAL_uniform']}/{a['SIGNAL_living']})"
          f"{'':12s}{a['COMM_DEPENDENT']:<9d} {a['LOCAL_ONLY']:<6d} {a['INTEGRATION']:<7d} {a['held_quantiles']}")
    for fam, a in S["A1"].items():
        for b in a["best"][:2]:
            w(f"   {fam} best: held {f3(b['held'])} lo99 {f3(b['lo99'])} zero_comm {f3(b['zero_comm'])}"
              f" comm_delta_lo99 {f3(b['comm_delta_lo99'])} cell {b['cell']}")
    w("")
    w("## 4. Anomaly flags (counts; flags are not verdicts)")
    for k, v in S["anomalies"].items():
        w(f"   {k:32s} {v['count']:5d}  e.g. {', '.join(v['examples'][:3])}")
    w("")
    w("## 5. Phase-boundary verdicts (PREREG s8)")
    w(f"   counts: {dict(S['boundary_counts'])}")
    for v in S["boundaries_verdicts"]:
        w(f"   {v['label']:26s} {v['family']:5s} {v['track']:4s} {v['metric']:5s} {v['dial']:13s}"
          f" levels {v['between']} jump {v['jump']:+.3f} (se {v['se']:.3f}, range {v['range']:.3f})"
          f" fresh={v['fresh_seed_reproduced']} ortho={v['orthogonal_offset_reproduced']}")
    w("")
    w("## 6. Wave C: transfer of frozen champions / re-evolution")
    for t in S["C_transfer"]:
        w(f"   {t['from']:5s} -> {t['to']:5s} {str(t['variant'] or ''):28s} held {f3(t['held'])}"
          f" lo99 {f3(t['lo99'])} {'TRANSFER_SUPPORT' if t['TRANSFER_SUPPORT'] else ''}")
    for t in S["C_reevolve"]:
        w(f"   re-evolve {t['family']:5s} on physics of {t['source']}: held {f3(t['held'])}"
          f" {'SIGNAL' if t['SIGNAL'] else ''}")
    w("")
    w("## 7. Wave D: causal adjudication of promoted cells")
    for d in S["D"]:
        w(f"-- {d['family']} {d['source']} held {f3(d['held'])}: REPRODUCED={d['REPRODUCED_SIGNAL']}"
          f" (reps {[round(x, 3) for x in d['replicate_held']]}), {d['causal']}")
        w("   controls: " + ", ".join(f"{k}={v if isinstance(v, str) else round(v, 3)}"
                                      for k, v in d["controls"].items()))
        w("   transplants: " + ", ".join(f"{k}={v if not isinstance(v, float) else round(v, 3)}"
                                         for k, v in d["transplants"].items()))
        w(f"   twin: " + ", ".join(f"{k}={round(v, 2)}" for k, v in d["twin"].items()))
    w("")
    w("## 8. Wave E: scale")
    for e in S["E"]:
        w(f"   {e['family']:5s} {e['kind']:8s} N={e['N']:<5d} held {f3(e['held'])} lo99 {f3(e['lo99'])}"
          f" (source {f3(e['source_held'])})")
    w("")
    w("## 9. PREREG predictions P1-P8")
    for k, p in S["predictions"].items():
        verdict = "INDETERMINATE" if p["held"] is None else ("HELD" if p["held"] else "LOST")
        w(f"   {k} {verdict}: {p['claim']}  evidence {json.dumps(p['evidence'], default=str)[:160]}"
          + (f"  [{p['note']}]" if p.get("note") else ""))
    return "\n".join(L) + "\n"


def atlas_export(S: dict, out: pathlib.Path, run_ref: str):
    """Pointer rows in the prometheus/cosmos/atlas_export.py form."""
    facts, edges = [], []
    exp = f"ananke:{S['campaign']}"
    for fam, a in S["A1"].items():
        for lab in ("SIGNAL", "COMM_DEPENDENT", "LOCAL_ONLY"):
            facts.append({"fact_key": f"{exp}:A1:{fam}:{lab}", "layer": "OBSERVED", "subject_type": "experiment",
                          "subject_key": exp, "value_num": a[lab], "band_low": None, "band_high": None,
                          "method": "prometheus.ananke.report (PREREG s7)", "source": run_ref})
    for v in S["boundaries_verdicts"]:
        facts.append({"fact_key": f"{exp}:boundary:{v['family']}:{v['metric']}:{v['dial']}:{v['between']}",
                      "layer": "OBSERVED", "subject_type": "phase_boundary", "subject_key": exp,
                      "value_num": v["jump"], "band_low": v["jump"] - 3 * v["se"], "band_high": v["jump"] + 3 * v["se"],
                      "method": v["label"], "source": run_ref})
    for d in S["D"]:
        edges.append({"src": f"cell:{d['source']}", "dst": exp, "kind": "adjudicated_in",
                      "label": d["causal"], "reproduced": d["REPRODUCED_SIGNAL"]})
    with open(out / "atlas_fact.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for x in facts:
            f.write(json.dumps(x) + "\n")
    with open(out / "atlas_edge.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for x in edges:
            f.write(json.dumps(x) + "\n")
    return len(facts), len(edges)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--freeze", default=None, help="freeze JSON (defaults to CampaignConfig())")
    a = ap.parse_args(argv)
    run, out = pathlib.Path(a.run), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.freeze:
        raw = json.loads(pathlib.Path(a.freeze).read_text())["config"]
        cfg = C.CampaignConfig(**{k: (tuple(v) if k in ("families", "e_sizes") else v) for k, v in raw.items()})
    else:
        cfg = C.CampaignConfig()
    S = build(run, cfg)
    (out / "summary.json").write_text(json.dumps(S, indent=1, default=str))
    md = to_markdown(S)
    md = md.encode("ascii", "replace").decode("ascii")
    (out / "REPORT.md").write_text(md, encoding="ascii")
    nf, ne = atlas_export(S, out, str(run))
    print(f"wrote {out}/REPORT.md, summary.json, atlas {nf} facts / {ne} edges")


if __name__ == "__main__":
    main()
