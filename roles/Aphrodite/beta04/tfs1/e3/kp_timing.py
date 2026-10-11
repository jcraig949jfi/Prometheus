"""E3-KP timing (amendment A1, item 5 of the SUBSTRATE task): core-seconds per family per stage, measured on EXPOSED
pilot worlds, and a projection for the production E3-KP (15 admitted R3/R4 families x primary + 4 secondary rows, and
the OE-repair re-run). Reads only <out>/KPA1_<world>.json caches (no search is run here).

  python -m tfs1.e3.kp_timing --root foundry/pilot_v2 --worlds W1d5301d0,W0467897d [--out tfs1/e3/runs]

COST ACCOUNTING. Every search record carries its own process CPU (time.process_time, one process, OMP_NUM_THREADS=1).
  standalone row cost  = the sum over every search the row USES (as if the row ran alone, cold cache);
  incremental row cost = the sum over the searches the row adds to the shared cache, given the rows before it (in the
                         order the rows are listed) already ran.
Per family: r1 = the attempts of its constituent units (a shared unit is attributed to every family that uses it,
so per-family r1 sums exceed the per-world unit total), chain, scratch.

PROJECTION (production; no production data is read). Structural counts are the prereg's / red team's published ones:
15 admitted families in 7 worlds, about 17 acquisition units, at most 2 R1 families per unit in the id_map (pilot: 2).
The per-search costs are the pilot measurements: a censored search (no hit at 1e6) costs the measured mean for its
stage; a hit costs (measured CPU per charge) x charge, bounded above by the censored cost. The UPPER bound assumes
every R1 attempt is censored (2 per unit), every chain and scratch search censored; the EXPECTED line uses the red
team's prediction (10 / 17 units high-risk: both attempts censored; the rest: one hit at about half budget).
"""
import argparse
import json
from pathlib import Path
from statistics import mean

from tfs1.e3 import e3_known_positive as KP

HERE = Path(__file__).resolve().parent
OE_SCRATCH_CAP_S = 900.0
ROWS = [("primary", KP.Config()), ("fallback_off", KP.Config(fallback=False)),
        ("foundry_primitives", KP.Config(source="foundry")), ("seed1", KP.Config(seed=1)),
        ("seed2", KP.Config(seed=2)), ("all_acquired", KP.Config(scope="all")), ("oe_repair", KP.Config(oe=True))]
PROD = {"families": 15, "worlds": 7, "units": 17, "r1_per_unit_max": 2, "high_risk_units": 10,
        "extra_units_all_acquired_est": 11, "fallback_dependent_units_est": 5, "fallback_dependent_families_est": 5}


def row_searches(kp, d, cfg):
    """search keys used by a row (re-derived from its records; same keys as KP.search_key)."""
    row = d["rows"].get(cfg.key())
    if not row:
        return None
    keys = {}
    for m, u in row["units"].items():
        for a in u.get("attempts", []):
            keys[KP.search_key(a["family_id"], None, cfg)] = ("r1", m, a["family_id"])
    for f, c in row["chain"].items():
        if c.get("library_sha256"):
            k = "%s|seed=%d|lib=%s|oe=%d|B=%d|max=%d" % (f, cfg.seed, c["library_sha256"][:16], cfg.oe, cfg.budget,
                                                         KP.MAX_SIZE)
            keys[k] = ("chain", None, f)
    for f in row["scratch"]:
        keys[KP.search_key(f, None, cfg)] = ("scratch", None, f)
    return keys


def measure(root, worlds, out):
    res = {"label": KP._label(root), "worlds": {}, "rows": {}}
    stage_samples, sampled = {}, set()
    for w in worlds:
        kp = KP.KP(root, w)
        d = KP._load(out, w)
        seen = set()
        wres = {}
        for name, cfg in ROWS:
            keys = row_searches(kp, d, cfg)
            if keys is None:
                continue
            S = d["searches"]
            stand = sum(S[k]["cpu_s"] for k in keys)
            inc = sum(S[k]["cpu_s"] for k in keys if k not in seen)
            seen |= set(keys)
            by_stage = {}
            for k, (st, _m, _f) in keys.items():
                by_stage[st] = round(by_stage.get(st, 0) + S[k]["cpu_s"], 2)
                tag = ("oe_repair" if cfg.oe else "base", st)
                if (w, k) not in sampled:
                    sampled.add((w, k))
                    stage_samples.setdefault(tag, []).append((S[k]["hit"], S[k]["charges"], S[k]["cpu_s"]))
            desc = kp.describe(d, cfg)
            wres[name] = {"standalone_cpu_s": round(stand, 2), "incremental_cpu_s": round(inc, 2),
                          "by_stage_cpu_s": by_stage,
                          "families": [{"family_id": f["family_id"], **f["cpu_s"], "chain": f["chain_status"],
                                        "link": f["first_failing_link"], "detail": f["link_detail"]}
                                       for f in desc["families"]],
                          "units": [{"mechanism": u["mechanism"], "status": u["status"], "cpu_s": u["cpu_s"],
                                     "link": u["link"], "n_attempts": u["n_attempts"]} for u in desc["units"]]}
        res["worlds"][w] = wres
    # per-search cost parameters
    par = {}
    for (kind, st), xs in stage_samples.items():
        cens = [c for h, _n, c in xs if not h]
        hits = [(n, c) for h, n, c in xs if h]
        par["%s/%s" % (kind, st)] = {
            "n": len(xs), "censored_mean_cpu_s": round(mean(cens), 2) if cens else None,
            "censored_max_cpu_s": max(cens) if cens else None,
            "cpu_per_1e6_charges_hits": round(1e6 * sum(c for _n, c in hits) / max(1, sum(n for n, _c in hits)), 1)
            if hits else None}
    res["per_search_parameters"] = par
    res["projection"] = project(par)
    return res


def project(par):
    def cens(kind, st, fallback):
        p = par.get("%s/%s" % (kind, st), {})
        return p.get("censored_mean_cpu_s") or fallback
    r1, ch, sc = cens("base", "r1", 65.0), cens("base", "chain", 60.0), cens("base", "scratch", 60.0)
    # chain censored cost is unmeasured if no pilot chain was censored in that row; fall back to scratch-like cost
    U, F = PROD["units"], PROD["families"]
    hi_units = PROD["high_risk_units"]
    prim_upper = U * PROD["r1_per_unit_max"] * r1 + F * ch + F * sc
    prim_exp = hi_units * 2 * r1 + (U - hi_units) * 0.5 * r1 + F * ch + F * sc
    rows = {
        "primary": {"upper_s": prim_upper, "expected_s": prim_exp},
        "fallback_off (incremental)": {"upper_s": PROD["fallback_dependent_units_est"] * r1
                                       + PROD["fallback_dependent_families_est"] * ch},
        "foundry_primitives (incremental: chains only)": {"upper_s": F * ch},
        "seed1 + seed2": {"upper_s": 2 * prim_upper, "expected_s": 2 * prim_exp},
        "all_acquired (incremental)": {"upper_s": PROD["extra_units_all_acquired_est"] * PROD["r1_per_unit_max"] * r1
                                       + F * ch * 1.3},
    }
    # OE: every pilot OE R1 / chain search hit (no censored measurement); the censored OE cost is taken as the
    # largest measured censored OE search (a scratch search), and an OE scratch search on a List-output family is
    # charged the 900 s process cap (one of 7 pilot OE scratch searches was killed at the 900 s wall cap)
    p_oe = par.get("oe_repair/scratch", {})
    o_max = p_oe.get("censored_max_cpu_s")
    if o_max:
        rows["oe_repair re-run (primary config, OE on; standalone)"] = {
            "upper_s": U * PROD["r1_per_unit_max"] * o_max + F * o_max + F * OE_SCRATCH_CAP_S,
            "expected_s": hi_units * 1 * o_max + F * 60.0 + F * (0.5 * o_max + 0.5 * OE_SCRATCH_CAP_S)}
    o_r1 = o_ch = o_sc = o_max
    tot_u = sum(v["upper_s"] for k, v in rows.items() if not k.startswith("oe_repair"))
    out = {k: {kk: round(vv / 3600, 2) for kk, vv in v.items()} for k, v in rows.items()}
    out = {k: {kk.replace("_s", "_core_h"): vv for kk, vv in v.items()} for k, v in out.items()}
    out["primary + 4 secondaries, upper_core_h"] = round(tot_u / 3600, 2)
    out["assumptions"] = dict(PROD, censored_cpu_s={"r1": r1, "chain": ch, "scratch": sc},
                              oe_censored_cpu_s={"r1": o_r1, "chain": o_ch, "scratch": o_sc},
                              oe_scratch_list_family_cap_s=OE_SCRATCH_CAP_S,
                              oe_expected="10 high-risk units: one OE R1 search at the censored cost; chains ~60 s; half "
                                          "the scratch searches at the cap",
                              all_acquired_chain_slowdown=1.3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--worlds", required=True)
    ap.add_argument("--out", default=str(HERE / "runs"))
    a = ap.parse_args()
    res = measure(a.root, a.worlds.split(","), a.out)
    p = Path(a.out) / "KPA1_TIMING.json"
    p.write_text(json.dumps(res, indent=1, sort_keys=True))
    print(json.dumps({"per_search_parameters": res["per_search_parameters"], "projection": res["projection"]},
                     indent=1))
    for w, rows in res["worlds"].items():
        for name, r in rows.items():
            print(w, name, "standalone", r["standalone_cpu_s"], "incremental", r["incremental_cpu_s"], r["by_stage_cpu_s"])
            for f in r["families"]:
                print("   ", f)


if __name__ == "__main__":
    main()
