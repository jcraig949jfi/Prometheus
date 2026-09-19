"""Generate the seven-arm control anchor frame sets EXACTLY as asal_ruler.stage_fixture does (same functions,
same seeds, same Orbium rollout), as float32 224x224x3 in [0,1], for scoring through the native observer
(HARM-56 AMENDMENT_A, section A). Writes <dest>/<ARM>.npy + MANIFEST_anchors.json with sha256 and the torch
fixture score of each arm (from out/run_2026-09-18/fixture.json). Cheat control: the torch observer in this env
re-scores every written array and must reproduce fixture.json to 1e-6, else nothing is delivered.
"""
import hashlib, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import asal_ruler as AR


def main(dest):
    t107 = AR.load_techne(); obs = t107.Observer()
    fx = json.load(open(os.path.join(HERE, "out", "run_2026-09-18", "fixture.json")))
    animals = json.load(open(AR.ANIMALS, encoding="utf-8")); orb = next(e for e in animals if isinstance(e, dict) and e.get("code") == "O2u")
    lenia128, mass, alive = AR.rollout(t107, orb["params"], {"kind": "cells", "cells": orb["cells"]}); lenia = AR.to_rgb(t107, lenia128)
    TF = AR.TF
    arms = {"LENIA": lenia, "STATIC": np.repeat(lenia[:1], TF, axis=0),
            "CYCLE2": np.stack([lenia[0] if i % 2 == 0 else lenia[4] for i in range(TF)]),
            "HUECYCLE": np.stack([t107.tint(lenia[0], i / TF) for i in range(TF)]),
            "DRIFT_SYN": np.stack([t107.blob_frame(6 * i) for i in range(TF)])}
    # NOISE/GARBAGE: one generator per SEQUENCE, seeds 1000+i, exactly as the fixture
    for i in range(5):
        g = np.random.default_rng(1000 + i); arms[f"NOISE_seed{i}"] = np.stack([g.random((224, 224, 3)) for _ in range(TF)])
    for i in range(5):
        g = np.random.default_rng(1000 + i); arms[f"GARBAGE_seed{i}"] = np.stack([t107.ellipse_scene(g) for _ in range(TF)])
    arms["CHEAT"] = np.repeat(t107.ellipse_scene(np.random.default_rng(7))[None], TF, axis=0)
    os.makedirs(dest, exist_ok=True)
    man = {"schema": "harmonia.anchors224/1", "dtype": "float32", "shape": [8, 224, 224, 3], "range": "[0,1]", "feed": "directly to the observer (no grey->RGB, no quantisation), as the torch fixture did",
           "orbium_mass": [float(m) for m in mass], "arms": {}, "torch_fixture_ref": "out/run_2026-09-18/fixture.json F block"}
    ref = {"LENIA": fx["F"]["LENIA"]["mine"], "STATIC": fx["F"]["STATIC"]["mine"], "CYCLE2": fx["F"]["CYCLE2"]["mine"], "HUECYCLE": fx["F"]["HUECYCLE"]["mine"],
           "DRIFT_SYN": fx["F"]["DRIFT_SYN"]["mine"], "CHEAT": fx["F"]["CHEAT"]["mine"]}
    ok = True
    for name, fr in arms.items():
        arr = np.ascontiguousarray(fr.astype(np.float32)); p = os.path.join(dest, name + ".npy"); np.save(p, arr)
        s = t107.open_endedness_score(obs.embed(arr.astype(np.float64)))
        row = {"sha256": AR.sha256_file(p), "score_torch_rescored_here": float(s)}
        if name in ref:
            row["score_torch_fixture"] = ref[name]; row["match"] = abs(s - ref[name]) <= 1e-6; ok &= row["match"]
        man["arms"][name] = row
    for nm in ("NOISE", "GARBAGE"):
        vals = [man["arms"][f"{nm}_seed{i}"]["score_torch_rescored_here"] for i in range(5)]
        man["arms"][nm] = {"mean_rescored": float(np.mean(vals)), "sd_rescored": float(np.std(vals)), "fixture_mean": fx["F"][nm]["mine_mean"]}
        ok &= abs(float(np.mean(vals)) - fx["F"][nm]["mine_mean"]) <= 1e-6
    man["cheat_control_pass"] = bool(ok)
    json.dump(man, open(os.path.join(dest, "MANIFEST_anchors.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    json.dump(man, open(os.path.join(HERE, "out", "run_2026-09-18", "anchors_manifest.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    print(json.dumps({k: (v.get("match", v.get("mean_rescored")) if isinstance(v, dict) else v) for k, v in man["arms"].items()}, indent=1)); print("CHEAT_CONTROL_PASS", ok)
    if not ok:
        for f in os.listdir(dest): os.remove(os.path.join(dest, f))
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else r"C:\Prometheus-vault\harmonia\asal_001_anchors224")
