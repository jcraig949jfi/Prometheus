"""Stage 1: fixture acceptance (specimen readings only; no check is scored)."""
import json, sys, time
sys.path.insert(0, ".")
import wk

out = {}
for fx in wk.fixtures():
    t = time.time()
    g = wk.genome_of(fx)
    n = fx.harness.run(fx.ph, g, fx.env, wk.NORMAL)
    a = fx.harness.run(fx.ph, g, fx.env, fx.arm)
    r = wk.reading(n, a)
    r["wall"] = round(time.time() - t, 1)
    out[fx.fid] = r
    print(fx.fid, fx.truth, r["reading"], "normal %.3f [%.3f,%.3f]" % r["normal"],
          "arm %.3f" % r["arm"][0], "diff %.3f [%.3f,%.3f]" % r["diff"], r["wall"], flush=True)
json.dump(out, open(__import__("os").path.join(__import__("os").path.dirname(__file__), "out", "accept.json"), "w"), indent=1)
