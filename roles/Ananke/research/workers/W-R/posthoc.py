"""W-R POST-HOC (not in PLAN; after seeing the negative control fail, LOG A11).
(a) leave-trial-out robustness: re-stratify from out/raw_<spec>.npz without trial 1 (and without
    trial 11) and report class / phase-effect changes vs the main analysis;
(b) effect sizes: max |dX| per spec (main analysis), vs the async trial-parity baseline.
python posthoc.py <spec> [...]  -> out/posthoc_<spec>.json"""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import specs
import numpy as np
import fork


def load_raw(name):
    z = np.load(HERE / f"out/raw_{name}.npz")
    d = json.loads((HERE / f"out/strat_{name}.json").read_text())
    offs = d["offsets"]
    g = lambda k: {o: z[f"{o}__{k}"] for o in offs}
    return d, z["normal"], z["normal_s0"], z["scored"], g("site"), g("chan"), g("s0_site"), g("s0_chan")


def run(name):
    d, normal, ns0, scored, site, chan, s0s, s0c = load_raw(name)
    main = d["offsets_res"]
    out = {"spec": name, "max_abs_d": None, "drop": {}}
    ds = [abs(r["diff"][f"d{x}"]) for r in main.values() if r.get("diff") for x in "SCN"]
    ds_eff = [abs(r["diff"][f"d{x}"]) for o, r in main.items() if r.get("diff") and int(o) >= 1 for x in "SCN"]
    out["max_abs_d"] = max(ds) if ds else None
    out["max_abs_d_o_ge_1"] = max(ds_eff) if ds_eff else None
    for drop in (1, 11):
        trials = [k for k in d["trials"] if k != drop]
        res = fork.stratified(normal, ns0, scored, site, chan, s0s, s0c, trials, d["offsets"], d["Pd"],
                              d["strat_period"], n_boot=1000)
        rows = {}
        for o, r in res.items():
            m = main[str(o)]
            rows[str(o)] = {"classes": [r["pooled"]["class"], r["q0"]["class"], r["q1"]["class"]],
                            "main_classes": [m["pooled"]["class"], m["q0"]["class"], m["q1"]["class"]],
                            "effect": r.get("phase_effect"), "main_effect": m.get("phase_effect"),
                            "resolution": r.get("resolution"), "main_resolution": m.get("resolution"),
                            "diff": r.get("diff")}
        out["drop"][str(drop)] = {
            "effect_offsets": [o for o, r in rows.items() if r["effect"]],
            "class_changes_vs_main": [o for o, r in rows.items() if r["classes"] != r["main_classes"]],
            "resolution_changes_vs_main": [o for o, r in rows.items() if r["resolution"] != r["main_resolution"]],
            "rows": rows}
    (HERE / f"out/posthoc_{name}.json").write_text(json.dumps(out, indent=1, default=float))
    print(name, "max|d|", round(out["max_abs_d"] or 0, 3), "o>=1", round(out["max_abs_d_o_ge_1"] or 0, 3),
          {k: {kk: v[kk] for kk in ("effect_offsets", "class_changes_vs_main", "resolution_changes_vs_main")}
           for k, v in out["drop"].items()}, flush=True)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        run(n)
