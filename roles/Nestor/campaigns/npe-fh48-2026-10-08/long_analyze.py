"""X-DIR-LONG reducer: architecture trajectory of the dominant competent genome (every STEP epochs).
Per run: robustness (all / routine) over time, Hamming to CT_UA, detector (bytes 16-19) intact?, final CS.
Classification input: end-of-run dominant routine robustness vs CT_UA's 0.382."""
import gzip, json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arch, fh
CT = fh.PLANTS["CT_UA"]
STEP = 500


def main(exp="X-DIR-LONG"):
    d = HERE / "runs" / exp
    res = {}
    for p in sorted(d.glob("*.json")):
        if p.name.endswith(".detail.json.gz") or p.name.startswith(("RECEIPT", "REDUCED", "LONG_REDUCED")):
            continue
        r = json.loads(p.read_text())
        det = json.load(gzip.open(d / ("%s_%d.detail.json.gz" % (r["arm"], r["seed"])), "rt"))
        traj = []
        for x in det["dom_series"]:
            if x["e"] % STEP == 0:
                g = bytes.fromhex(x["g"])
                rb = arch.robustness(g)
                traj.append({"e": x["e"], "rob_all": rb["all"], "rob_routine": rb["by_region"]["routine"],
                             "ham": sum(g[j] != CT[j] for j in range(64)),
                             "detector_intact": g[16:20] == CT[16:20], "families": x["families"], "dom_n": x["n"]})
        res.setdefault(r["arm"], []).append({"seed": r["seed"], "CS": r["CS"], "traj": traj})
    out = {}
    for arm, runs in res.items():
        maint = [x for x in runs if x["CS"] >= 0.10 and x["traj"]]
        end_rob = [x["traj"][-1]["rob_routine"] for x in maint]
        out[arm] = {"runs": runs, "maintained": len(maint),
                    "end_routine_robustness": end_rob,
                    "runs_rob_gain_ge_0.10": sum(v - 0.3822 >= 0.10 for v in end_rob),
                    "runs_rob_gain_ge_0.05": sum(v - 0.3822 >= 0.05 for v in end_rob),
                    "detector_lost_at_end": sum(not x["traj"][-1]["detector_intact"] for x in maint)}
        print(arm, "maintained", len(maint), "end routine robustness", end_rob,
              "gain>=0.10:", out[arm]["runs_rob_gain_ge_0.10"], "gain>=0.05:", out[arm]["runs_rob_gain_ge_0.05"],
              "detector lost:", out[arm]["detector_lost_at_end"])
        for x in maint:
            print("   ", x["seed"], [(t["e"], t["rob_routine"], t["ham"], int(t["detector_intact"])) for t in x["traj"]])
    (d / "LONG_REDUCED.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*(sys.argv[1:2] or []))
