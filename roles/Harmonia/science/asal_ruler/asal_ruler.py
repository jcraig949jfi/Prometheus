"""Harmonia ASAL legitimate-search ruler. Preregistration: PREREG_ASAL_LEGIT_SEARCH_2026-09-18.md.

Run in Techne's isolated env (read-only use):
  <asal107 python> asal_ruler.py --stage fixture   # F, C-METRIC, C-NEG-BLANK, C-CHEAT-SCORE, C-POS-SEARCH -> thresholds.json
  <asal107 python> asal_ruler.py --stage search    # S0 catalogue scan, S1 random envelope, S2 local; refuses without a passing fixture
Imports Techne's numpy Lenia port and CLIP observer BY PATH (techne/scripts/techne107_asal_observer.py) as a
descendant instrument; re-implements the score independently for C-METRIC.
"""
import argparse, hashlib, importlib.util, json, math, os, platform, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TECHNE_SCRIPT = os.path.join(REPO, "techne", "scripts", "techne107_asal_observer.py")
TECHNE_RECEIPT = os.path.join(REPO, "techne", "acquisition", "poet_alife", "TECHNE107_RECEIPT_2026-09-17.json")
ANIMALS = os.path.join(HERE, "fixtures", "animals.json")
ANIMALS_SHA = "09cf0a831c1ef8a73ebfaa9126257fbe076108362b706a98d88650ca9848d206"
OUT = os.path.join(HERE, "out")
WORLD, STEPS, TF = 128, 256, 8
GARBAGE_MEAN, GARBAGE_SD, GARBAGE_MIN, ORBIUM = 0.816686, 0.008363, 0.807538, 0.847246
B_DOMAIN = ["1", "1/2,1", "1,1/3", "1,1,1", "3/4,1,1", "1,1", "1,3/4,1/2,1/4", "1,2/3,1/3,2/3"]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load_techne():
    spec = importlib.util.spec_from_file_location("t107", TECHNE_SCRIPT)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def my_score(z):
    """Independent re-implementation of asal_metrics.py:53 semantics: for each frame i>0, max cosine to any earlier frame; mean over ALL frames (frame 0 contributes 0)."""
    T = z.shape[0]; vals = np.zeros(T)
    for i in range(1, T):
        vals[i] = max(float(z[i] @ z[j]) for j in range(i))
    return float(vals.mean())


def parse_b(bs):
    return [float(eval(x)) for x in bs.split(",")]


def rollout(t107, params, ic, seed=None):
    """Return frames128 (8,128,128) grey, masses (9,), alive flag."""
    p = dict(params); p["b"] = str(p["b"])
    sim = t107.Lenia2D(WORLD, p)
    if ic["kind"] == "cells":
        A = sim.place(t107.rle2arr_2d(ic["cells"]))
    elif ic["kind"] == "blob":
        yy, xx = np.mgrid[0:WORLD, 0:WORLD]; A = np.exp(-(((xx - 64) ** 2 + (yy - 64) ** 2) / (2 * 8.0 ** 2)))
    elif ic["kind"] == "zero":
        A = np.zeros((WORLD, WORLD))
    else:
        raise ValueError(ic)
    frames, mass = [], []
    sample_at = [(STEPS // TF) * i for i in range(TF)]
    for t in range(STEPS):
        if t in sample_at:
            frames.append(A.copy()); mass.append(float(A.sum()))
        A = sim.step(A)
    mass.append(float(A.sum()))
    alive = all(1.0 <= m <= 0.5 * WORLD * WORLD for m in mass)
    return np.stack(frames), np.array(mass), alive


def observables(frames128, z):
    F = frames128
    d_pix = float(np.mean([np.linalg.norm(F[i + 1] - F[i]) / WORLD for i in range(TF - 1)]))
    d_clip = float(np.mean([1.0 - float(z[i + 1] @ z[i]) for i in range(TF - 1)]))
    cohs, disps = [], []
    yy, xx = np.mgrid[0:WORLD, 0:WORLD]
    for i in range(TF - 1):
        a, b = F[i] - F[i].mean(), F[i + 1] - F[i + 1].mean()
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-9 or nb < 1e-9:
            cohs.append(0.0)
        else:
            xc = np.real(np.fft.ifft2(np.fft.fft2(a) * np.conj(np.fft.fft2(b))))
            cohs.append(float(xc.max() / (na * nb)))
        ma, mb = F[i].sum(), F[i + 1].sum()
        if ma > 1e-9 and mb > 1e-9:
            ca = np.array([(yy * F[i]).sum() / ma, (xx * F[i]).sum() / ma]); cb = np.array([(yy * F[i + 1]).sum() / mb, (xx * F[i + 1]).sum() / mb])
            disps.append(float(np.linalg.norm(cb - ca)))
    masses = F.reshape(TF, -1).sum(axis=1)
    mass_cv = float(masses.std() / masses.mean()) if masses.mean() > 1e-9 else float("inf")
    return {"d_pix": d_pix, "d_clip": d_clip, "coh": float(np.mean(cohs)), "disp": float(np.mean(disps)) if disps else float("nan"), "mass_cv": mass_cv}


def classify(o, alive, th):
    if not alive:
        return "NOT_ALIVE"
    if o["coh"] >= 0.8 * th["coh_O"] and o["d_pix"] >= 0.5 * th["d_pix_O"] and o["mass_cv"] <= 0.5:
        return "GENUINE_DYNAMICAL_NOVELTY"
    if o["coh"] < 0.5 * th["coh_O"] and o["d_pix"] >= th["d_pix_O"]:
        return "METRIC_EXPLOIT"
    if o["d_pix"] < 0.5 * th["d_pix_O"] and o["d_clip"] >= 0.8 * th["d_clip_H"]:
        return "OBSERVER_EXPLOIT"
    return "UNCLASSIFIED"


def to_rgb(t107, frames128):
    return np.stack([t107.grey_to_rgb(f) for f in frames128])


def witness(obs):
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    import torch
    return {"host": platform.node(), "python": sys.version.split()[0], "executable": sys.executable, "torch": torch.__version__,
            "numpy": np.__version__, "clip_weights_sha256": obs.weights_sha256, "pip_freeze_sha256": hashlib.sha256(freeze.encode()).hexdigest(),
            "pip_freeze_n": len(freeze.splitlines()), "techne_script_sha256": sha256_file(TECHNE_SCRIPT), "techne_receipt_sha256": sha256_file(TECHNE_RECEIPT),
            "animals_sha256": sha256_file(ANIMALS), "ruler_sha256": sha256_file(os.path.abspath(__file__))}


def save_contact(t107, frames128, path):
    from PIL import Image
    sheet = np.concatenate([t107.resize_bilinear(np.repeat(f[:, :, None], 3, axis=2), 112) for f in frames128], axis=1)
    Image.fromarray((np.clip(sheet, 0, 1) * 255).astype(np.uint8)).save(path)


# ------------------------------------------------------------------ fixture stage
def stage_fixture(out):
    t107 = load_techne(); obs = t107.Observer()
    assert sha256_file(ANIMALS) == ANIMALS_SHA, "animals.json hash"
    rec = json.load(open(TECHNE_RECEIPT)); R = rec["arms"]
    animals = json.load(open(ANIMALS, encoding="utf-8")); orb = next(e for e in animals if isinstance(e, dict) and e.get("code") == "O2u")
    res = {"stage": "fixture", "witness": witness(obs), "F": {}, "controls": {}}
    lenia128, mass, alive = rollout(t107, orb["params"], {"kind": "cells", "cells": orb["cells"]})
    lenia = to_rgb(t107, lenia128)
    arms = {"LENIA": lenia, "STATIC": np.repeat(lenia[:1], TF, axis=0),
            "CYCLE2": np.stack([lenia[0] if i % 2 == 0 else lenia[4] for i in range(TF)]),
            "HUECYCLE": np.stack([t107.tint(lenia[0], i / TF) for i in range(TF)]),
            "DRIFT_SYN": np.stack([t107.blob_frame(6 * i) for i in range(TF)])}
    embs, scores = {}, {}
    for k, fr in arms.items():
        z = obs.embed(fr); embs[k] = z; scores[k] = t107.open_endedness_score(z)
    for nm, gen in (("NOISE", lambda rng: np.stack([rng.random((224, 224, 3)) for _ in range(TF)])),
                    ("GARBAGE", lambda rng: np.stack([t107.ellipse_scene(rng) for _ in range(TF)]))):
        vals = []
        for i in range(5):
            z = obs.embed(gen(np.random.default_rng(1000 + i))); embs[f"{nm}_seed{i}"] = z; vals.append(t107.open_endedness_score(z))
            scores[f"{nm}_seed{i}"] = vals[-1]
        scores[nm] = float(np.mean(vals))
    cheat_fr = np.repeat(t107.ellipse_scene(np.random.default_rng(7))[None], TF, axis=0)
    z = obs.embed(cheat_fr); embs["CHEAT"] = z; scores["CHEAT"] = t107.open_endedness_score(z)
    # F: compare to receipt
    Fok = True; F = {}
    for k in ("LENIA", "STATIC", "CYCLE2", "HUECYCLE", "DRIFT_SYN"):
        d = scores[k] - R[k]["score"]; ok = abs(d) <= 0.002; Fok &= ok; F[k] = {"mine": scores[k], "techne": R[k]["score"], "delta": d, "pass": ok}
    d = scores["CHEAT"] - R["CHEAT_identical_as_distinct"]["score"]; ok = abs(d) <= 0.002; Fok &= ok; F["CHEAT"] = {"mine": scores["CHEAT"], "techne": R["CHEAT_identical_as_distinct"]["score"], "delta": d, "pass": ok}
    for nm in ("NOISE", "GARBAGE"):
        d = scores[nm] - R[nm]["mean"]; ok = abs(d) <= 2 * R[nm]["sd"]; Fok &= ok; F[nm] = {"mine_mean": scores[nm], "techne_mean": R[nm]["mean"], "techne_sd": R[nm]["sd"], "delta": d, "pass": ok}
    res["F"] = F; res["controls"]["F_fixture"] = {"pass": bool(Fok)}
    # C-METRIC
    # AMENDMENT_A (2026-09-18, interventions_unseen=true): embeddings are float32; the two implementations
    # differ by float32 rounding (3.1e-7 observed). Tolerance 1e-6 replaces the preregistered 1e-9; the
    # float64 comparison below must agree to 1e-12 (the semantic check the prereg meant).
    md = max(abs(my_score(z) - t107.open_endedness_score(z)) for z in embs.values())
    md64 = max(abs(my_score(z.astype(np.float64)) - t107.open_endedness_score(z.astype(np.float64))) for z in embs.values())
    res["controls"]["C-METRIC"] = {"max_abs_diff_float32": md, "max_abs_diff_float64": md64, "pass": md <= 1e-6 and md64 <= 1e-12}
    # C-NEG-BLANK
    z128, zm, zalive = rollout(t107, orb["params"], {"kind": "zero"})
    zs = t107.open_endedness_score(obs.embed(to_rgb(t107, z128)))
    res["controls"]["C-NEG-BLANK"] = {"score": zs, "alive": zalive, "pass": abs(zs - 0.875) < 1e-3 and not zalive}
    # C-CHEAT-SCORE: frames replaced by GARBAGE seed 0 scenes regardless of params
    # AMENDMENT_A: one generator per SEQUENCE (as Techne's script); the first draft made a new generator per
    # frame, producing 8 identical scenes and a score of 0.875 -- a construction defect of the control.
    g0 = np.random.default_rng(1000)
    gz = obs.embed(np.stack([t107.ellipse_scene(g0) for _ in range(TF)]))
    gs = t107.open_endedness_score(gz)
    res["controls"]["C-CHEAT-SCORE"] = {"score": gs, "expected": R["GARBAGE_seed0"]["score"], "pass": abs(gs - R["GARBAGE_seed0"]["score"]) <= 0.002}
    # C-POS-SEARCH on the free-image domain: seed is the parameter
    rng = np.random.default_rng(20260918); best = 1.0; best_seed = None; log = []
    seeds = [int(s) for s in rng.integers(0, 10 ** 6, 30)]
    def scenes(seed):  # AMENDMENT_A: one generator per sequence
        g = np.random.default_rng(seed); return np.stack([t107.ellipse_scene(g) for _ in range(TF)])
    for s in seeds:
        v = t107.open_endedness_score(obs.embed(scenes(s)))
        log.append((s, v))
        if v < best: best, best_seed = v, s
    cur, curv = best_seed, best
    for i in range(20):
        s2 = int((cur + int(rng.integers(1, 1000))) % 10 ** 6)
        v = t107.open_endedness_score(obs.embed(scenes(s2)))
        log.append((s2, v))
        if v < curv: cur, curv = s2, v
    res["controls"]["C-POS-SEARCH"] = {"best": curv, "threshold": GARBAGE_MEAN, "pass": curv <= GARBAGE_MEAN, "evals": len(log)}
    # thresholds from the fixture (before S0)
    oO = observables(lenia128, embs["LENIA"])
    hue128 = lenia128[:1].repeat(TF, axis=0)  # HUECYCLE pixels (grey) do not move; its d_clip comes from the tinted embeddings
    oH = observables(hue128, embs["HUECYCLE"])
    th = {"coh_O": oO["coh"], "d_pix_O": oO["d_pix"], "disp_O": oO["disp"], "mass_cv_O": oO["mass_cv"], "d_clip_O": oO["d_clip"],
          "d_pix_H": oH["d_pix"], "d_clip_H": oH["d_clip"], "orbium_alive": bool(alive), "orbium_mass": [float(m) for m in mass]}
    res["thresholds"] = th
    allpass = all(v["pass"] for v in res["controls"].values())
    res["all_controls_pass"] = bool(allpass)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "fixture.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    json.dump(th, open(os.path.join(out, "thresholds.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    save_contact(t107, lenia128, os.path.join(out, "fixture_LENIA_contact.png"))
    print(json.dumps({k: v for k, v in res.items() if k != "witness"}, indent=1))
    print("ALL_CONTROLS_PASS", allpass)
    return allpass


# ------------------------------------------------------------------ search stage
def stage_search(out):
    fx = json.load(open(os.path.join(out, "fixture.json")))
    assert fx["all_controls_pass"], "fixture stage did not pass; search refused"
    th = json.load(open(os.path.join(out, "thresholds.json")))
    t107 = load_techne(); obs = t107.Observer()
    animals = json.load(open(ANIMALS, encoding="utf-8"))
    orb = next(e for e in animals if isinstance(e, dict) and e.get("code") == "O2u")
    cat = [e for e in animals if isinstance(e, dict) and "params" in e and "cells" in e and "x" not in str(e.get("code", ""))]
    rows = []; rows_f = open(os.path.join(out, "rows.jsonl"), "w", encoding="utf-8", newline="\n")
    traj = {}; t0 = time.time()

    def evaluate(stage, idx, params, ic, ic_label, seed=None):
        try:
            f128, mass, alive = rollout(t107, params, ic, seed)
        except Exception as e:  # a parameter draw the port cannot simulate is recorded, not hidden
            r = {"stage": stage, "idx": idx, "params": params, "ic": ic_label, "seed": seed, "error": repr(e)[:200], "alive": False, "class": "NOT_ALIVE", "score": None}
            rows.append(r); rows_f.write(json.dumps(r) + "\n"); rows_f.flush(); return r
        z = obs.embed(to_rgb(t107, f128)); s = t107.open_endedness_score(z)
        o = observables(f128, z); cls = classify(o, alive, th)
        r = {"stage": stage, "idx": idx, "params": {k: (v if not isinstance(v, np.generic) else v.item()) for k, v in params.items()}, "ic": ic_label, "seed": seed,
             "score": s, "alive": bool(alive), "mass": [float(m) for m in mass], "class": cls, **o}
        rows.append(r); rows_f.write(json.dumps(r) + "\n"); rows_f.flush()
        key = f"{stage}_{idx}"
        traj[key] = {"frames64": (np.clip(np.stack([t107.resize_bilinear(np.repeat(f[:, :, None], 3, axis=2), 64)[:, :, 0] for f in f128]), 0, 1) * 255).astype(np.uint8),
                     "z16": z.astype(np.float16), "frames128": f128.astype(np.float32)}
        if len(rows) % 25 == 0:
            print(f"{len(rows)} rollouts, {time.time() - t0:.0f} s, best alive so far {min((x['score'] for x in rows if x['alive'] and x['score'] is not None), default=None)}", flush=True)
        return r

    # S0 catalogue scan
    for i, e in enumerate(cat):
        evaluate("S0", i, dict(e["params"]), {"kind": "cells", "cells": e["cells"]}, f"IC-CAT:{e.get('code')}")
    # S1 random envelope
    rng = np.random.default_rng(20260918)
    for i in range(300):
        p = {"R": int(rng.integers(6, 31)), "T": int(rng.choice([5, 10, 20])), "m": float(rng.uniform(0.05, 0.50)),
             "s": float(np.exp(rng.uniform(np.log(0.005), np.log(0.10)))), "b": str(rng.choice(B_DOMAIN)), "kn": int(rng.choice([1, 2, 3, 4])), "gn": int(rng.choice([1, 2, 3]))}
        if rng.random() < 0.5:
            ic, lab = {"kind": "blob"}, "IC-BLOB"
        else:
            ic, lab = {"kind": "cells", "cells": orb["cells"]}, "IC-ORB"
        evaluate("S1", i, p, ic, lab, seed=20260918)
    # S2 local search from the 5 best alive
    alive_rows = sorted([r for r in rows if r["alive"] and r["score"] is not None], key=lambda r: r["score"])[:5]
    for j, base in enumerate(alive_rows):
        rng2 = np.random.default_rng(20260918 + j + 1); cur, curv = dict(base["params"]), base["score"]
        ic = {"kind": "blob"} if base["ic"] == "IC-BLOB" else ({"kind": "cells", "cells": orb["cells"]} if base["ic"] == "IC-ORB" else {"kind": "cells", "cells": next(e["cells"] for e in cat if f"IC-CAT:{e.get('code')}" == base["ic"])})
        for k in range(40):
            cand = dict(cur); cand["m"] = float(np.clip(cur["m"] + rng2.normal(0, 0.02), 0.05, 0.50)); cand["s"] = float(np.clip(cur["s"] + rng2.normal(0, 0.005), 0.005, 0.10))
            cand["R"] = int(np.clip(round(cur["R"] + rng2.normal(0, 1)), 6, 30))
            r = evaluate("S2", j * 40 + k, cand, ic, base["ic"], seed=20260918)
            if r["alive"] and r["score"] is not None and r["score"] < curv:
                cur, curv = cand, r["score"]
    rows_f.close()
    # readouts
    alive_all = [r for r in rows if r["alive"] and r["score"] is not None]
    best = min(alive_all, key=lambda r: r["score"]) if alive_all else None
    def stage_stats(st):
        rs = [r for r in rows if r["stage"] == st]; al = [r for r in rs if r["alive"] and r["score"] is not None]
        hist = {}
        for r in rs: hist[r["class"]] = hist.get(r["class"], 0) + 1
        return {"n": len(rs), "n_alive": len(al), "best": min((r["score"] for r in al), default=None), "frac_below_garbage_mean": (sum(1 for r in al if r["score"] < GARBAGE_MEAN) / len(al)) if al else None, "class_histogram": hist}
    readouts = {"n_rollouts": len(rows), "n_alive": len(alive_all), "best_legit": best, "delta_vs_orbium": (best["score"] - ORBIUM) if best else None,
                "delta_vs_garbage_mean": (best["score"] - GARBAGE_MEAN) if best else None, "delta_vs_garbage_min": (best["score"] - GARBAGE_MIN) if best else None,
                "crossing_2sd": (best["score"] < GARBAGE_MEAN - 2 * GARBAGE_SD) if best else None, "crossing_mean": (best["score"] < GARBAGE_MEAN) if best else None,
                "per_stage": {st: stage_stats(st) for st in ("S0", "S1", "S2")}, "indeterminate": [] if len([r for r in rows if r["stage"] in ("S0", "S1") and r["alive"]]) >= 20 else ["fewer than 20 ALIVE rollouts in S0 u S1"],
                "top20_alive": sorted(alive_all, key=lambda r: r["score"])[:20], "seconds": round(time.time() - t0, 1), "thresholds": th}
    json.dump(readouts, open(os.path.join(out, "readouts.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True, default=float)
    # preserve trajectories
    np.savez_compressed(os.path.join(out, "trajectories64.npz"), **{k: v["frames64"] for k, v in traj.items()})
    np.savez_compressed(os.path.join(out, "embeddings16.npz"), **{k: v["z16"] for k, v in traj.items()})
    os.makedirs(os.path.join(out, "top20"), exist_ok=True)
    for r in readouts["top20_alive"]:
        key = f"{r['stage']}_{r['idx']}"
        np.save(os.path.join(out, "top20", key + "_frames128.npy"), traj[key]["frames128"])
        save_contact(t107, traj[key]["frames128"], os.path.join(out, "top20", key + "_contact.png"))
    print(json.dumps({k: v for k, v in readouts.items() if k not in ("top20_alive", "thresholds")}, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", choices=["fixture", "search"], required=True); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(OUT, "run_2026-09-18")
    if a.stage == "fixture":
        ok = stage_fixture(out); sys.exit(0 if ok else 2)
    else:
        stage_search(out)
