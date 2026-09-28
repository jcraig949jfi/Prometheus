"""POST-HOC exploratory (not in the frozen score): WIN-B/WIN-V at iti 2, where
stale waves arrive inside the C1 window, so the broken arm is NOT identical
(closer to the real C1 M3 case)."""
import dataclasses, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import wk, checks
E2 = dataclasses.replace(wk.RELAY_DA, iti=2)
out = {}
for fx in wk.fixtures():
    if fx.fid not in ("WIN-B", "WIN-V"):
        continue
    fx = dataclasses.replace(fx, fid=fx.fid + "-iti2", env=E2)
    g = wk.genome_of(fx)
    n = fx.harness.run(fx.ph, g, fx.env, wk.NORMAL, record=fx.arm.var)
    a = fx.harness.run(fx.ph, g, fx.env, fx.arm, record=fx.arm.var)
    base = {"n": n, "a": a, "reading": wk.reading(n, a)}
    row = {"reading": base["reading"], "checks": {}}
    for k, fn in checks.CHECKS.items():
        try:
            row["checks"][k] = fn(fx, base)
        except Exception as e:
            row["checks"][k] = {"status": "ERROR", "why": repr(e)}
    print(fx.fid, base["reading"]["reading"], base["reading"]["normal"][0], base["reading"]["arm"][0],
          " ".join(f"{k}:{v['status'][0]}" for k, v in row["checks"].items()),
          "reach", row["checks"]["K1"].get("reach"), "applied", row["checks"]["K4c"].get("applied_tick_worlds"), flush=True)
    out[fx.fid] = row
json.dump(out, open(os.path.join(os.path.dirname(__file__), "out", "posthoc_win_iti2.json"), "w"), indent=1, default=float)
