"""HARM-55 input: regenerate the 128x128 greyscale frames of every EXECUTED rollout of run_2026-09-18
from its recorded (params, ic, seed) -- the Lenia rollout is deterministic and needs no CLIP -- and hand
them to Techne OUTSIDE git (uint8, 8x128x128 per rollout) with a sha256 manifest committed IN git.

Controls (both must pass or nothing is delivered):
  C-TOP20   for the 20 rollouts whose float32 frames were stored, uint8(clip(x)*255) of the regenerated
            frames equals uint8 of the stored frames byte for byte
  C-TRAJ64  the 64x64 downsample (same PIL path as the search) of every regenerated rollout equals the
            committed trajectories64.npz entry byte for byte
The uint8 128 grey frame is exactly what reached CLIP: grey_to_rgb() converts to uint8 at 128 before the
bilinear resize to 224, so nothing is lost relative to the search's own input.
"""
import argparse, hashlib, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import asal_ruler as AR

RUN = os.path.join(HERE, "out", "run_2026-09-18", "search")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dest", default=r"C:\Prometheus-vault\harmonia\asal_001_frames128")
    ap.add_argument("--port", default=None, help="path to the techne107_asal_observer.py version to regenerate with (default: the tree's)")
    ap.add_argument("--diff-report", default=None, help="write per-rollout max |diff| vs stored frames to this JSON (diagnostic; no delivery)")
    a = ap.parse_args()
    if a.port:
        AR.TECHNE_SCRIPT = os.path.abspath(a.port)
    t107 = AR.load_techne(); os.makedirs(a.dest, exist_ok=True)
    diffs = {}
    animals = json.load(open(AR.ANIMALS, encoding="utf-8")); orb = next(e for e in animals if isinstance(e, dict) and e.get("code") == "O2u")
    cat = {f"IC-CAT:{e.get('code')}": e["cells"] for e in animals if isinstance(e, dict) and "params" in e and "cells" in e}
    rows = [json.loads(l) for l in open(os.path.join(RUN, "rows.jsonl")) if '"error"' not in l]
    traj = np.load(os.path.join(RUN, "trajectories64.npz"))
    manifest = {"schema": "harmonia.frames128/1", "run": "run_2026-09-18/search", "dest": a.dest, "dtype": "uint8", "shape": [8, 128, 128],
                "note": "uint8(clip(x,0,1)*255) of the 128x128 greyscale Lenia frames; this is the exact intermediate grey_to_rgb() fed to CLIP",
                "port_sha256": AR.sha256_file(AR.TECHNE_SCRIPT), "rollouts": {}, "controls": {}}
    top20_ok = top20_n = traj_ok = 0; t0 = time.time()
    for r in rows:
        key = f"{r['stage']}_{r['idx']}"
        ic = {"kind": "blob"} if r["ic"] == "IC-BLOB" else {"kind": "cells", "cells": orb["cells"] if r["ic"] == "IC-ORB" else cat[r["ic"]]}
        f128, mass, alive = AR.rollout(t107, r["params"], ic)
        u8 = (np.clip(f128, 0, 1) * 255).astype(np.uint8)
        # C-TRAJ64: same downsample path as the search
        d64 = (np.clip(np.stack([t107.resize_bilinear(np.repeat(f[:, :, None], 3, axis=2), 64)[:, :, 0] for f in f128]), 0, 1) * 255).astype(np.uint8)
        eq64 = bool(np.array_equal(d64, traj[key])); traj_ok += eq64
        p20 = os.path.join(RUN, "top20", key + "_frames128.npy")
        if os.path.exists(p20):
            stored = np.load(p20); eq = bool(np.array_equal(u8, (np.clip(stored, 0, 1) * 255).astype(np.uint8)))
            top20_n += 1; top20_ok += eq
            diffs[key] = {"traj64_equal": eq64, "frames128_equal": eq, "max_abs_diff_128": float(np.abs(f128 - stored).max()), "params": r["params"], "ic": r["ic"]}
        elif not eq64:
            diffs[key] = {"traj64_equal": False, "max_abs_diff_64": int(np.abs(d64.astype(int) - traj[key].astype(int)).max()), "params": r["params"], "ic": r["ic"]}
        path = os.path.join(a.dest, key + ".npy"); np.save(path, u8)
        manifest["rollouts"][key] = {"sha256": AR.sha256_file(path), "score_torch": r["score"], "class": r["class"], "alive": r["alive"],
                                     "mass_regenerated_equals_recorded": bool(np.allclose(mass, r["mass"]))}
    manifest["controls"] = {"C-TOP20": {"n": top20_n, "ok": top20_ok, "pass": top20_ok == top20_n == 20},
                            "C-TRAJ64": {"n": len(rows), "ok": traj_ok, "pass": traj_ok == len(rows)}}
    manifest["n_rollouts"] = len(rows); manifest["seconds"] = round(time.time() - t0, 1)
    manifest["delivered"] = manifest["controls"]["C-TOP20"]["pass"] and manifest["controls"]["C-TRAJ64"]["pass"]
    if a.diff_report:
        json.dump({"port_sha256": manifest["port_sha256"], "controls": manifest["controls"], "differing": diffs}, open(a.diff_report, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
        print("differing rollouts:", len([k for k, v in diffs.items() if not v.get("frames128_equal", v.get("traj64_equal"))]))
    mp = os.path.join(HERE, "out", "run_2026-09-18", "frames128_manifest.json")
    json.dump(manifest, open(mp, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in manifest.items() if k != "rollouts"}, indent=1))
    if not manifest["delivered"]:
        for f in os.listdir(a.dest): os.remove(os.path.join(a.dest, f))
        print("CONTROL FAILED: delivery directory emptied"); sys.exit(2)


if __name__ == "__main__":
    main()
