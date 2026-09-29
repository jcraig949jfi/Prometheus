"""W-R: print update-schedule-relevant physics dials + env for every spec."""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "roles/Ananke/research/workers/W-M"))
import torch
torch.set_num_threads(2)
import apply as WM
SPECS = ["2dccdaa5", "c16d5231", "78f3b0ec", "8c37f32e", "e06701a5", "369f5a5b", "4781b0a1", "E1", "E2"]
out = {}
for s in SPECS:
    ph, env, g, seeds, meta = WM.spec(s)
    d = ph.to_dict()
    out[s] = {"update_mode": d["update_mode"], "update_period": d["update_period"], "update_p": d["update_p"],
              "lm": ph.lm(), "env": env.to_dict(), "Pd": env.period(), "T": env.T(), "ro_off": WM.ro_off(env),
              "n_sites": d["n_sites"], "decay_shift": d["decay_shift"], "mut_site": d["mut_site"], "meta": meta}
    print(s, out[s]["update_mode"], "period", out[s]["update_period"], "p", out[s]["update_p"], "Pd", out[s]["Pd"],
          "ro_off", out[s]["ro_off"], "trials", env.trials, "N", d["n_sites"], "LM", ph.lm(), flush=True)
(HERE / "out/physics.json").write_text(json.dumps(out, indent=1, default=str))
