"""Smoke: one T-003 run, short horizon, observed vs plain: value identity on every interaction + identical lineage hash."""
import hashlib, json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pin"))
import observe as O                                   # noqa: E402
import pin_reproduce as P                             # noqa: E402
import world as W                                     # noqa: E402
EP = int(sys.argv[1]) if len(sys.argv) > 1 else 60
IDX = int(sys.argv[2]) if len(sys.argv) > 2 else 0
jobs = P.job_list(O.Z, P.REPO / P.PATHS[2])
job = jobs[IDX]
kw = dict(job["kwargs"]); kw.pop("implant_source", None); hx = kw.pop("implant_hex", None)
if hx: kw["implant_bytes"] = bytes.fromhex(hx)
kw["max_epochs"] = EP
def lh(r): return hashlib.sha256(json.dumps(r.lineage, sort_keys=True, default=str).encode()).hexdigest()
t0 = time.time(); r0 = W.Runner(job["cell"], job["seed"], tier=job["tier"], **kw); r0.run(); t_plain = time.time() - t0
cnt = {"n": 0, "births": 0}
def sink(runner, iid, pre_oid, orgs, gs, regs, flags, sh, last_store, post, births, n):
    cnt["n"] += 1; cnt["births"] += len(births)
t0 = time.time(); r1 = O.Observed(job["cell"], job["seed"], tier=job["tier"], sink=sink, **kw); r1.run(); t_obs = time.time() - t0
print(json.dumps({"run": job["name"], "epochs": EP, "interactions": cnt["n"], "births": cnt["births"],
                  "shadow_checked": r1.shadow_checked, "lineage_equal": lh(r0) == lh(r1),
                  "t_plain_s": round(t_plain, 1), "t_observed_s": round(t_obs, 1)}))
