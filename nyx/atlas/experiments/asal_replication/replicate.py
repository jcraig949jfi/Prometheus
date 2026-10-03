"""ASAL full-domain replication, executor (operator directive 2026-09-19 s4; operator directive 2026-10-03 N1).

Preregistration: nyx/atlas/experiments/asal_replication/PREREG_ASAL_REPLICATION_001.md
Packet:          nyx/atlas/predictions/MECH-ASAL-REPLICATION-001.json (+ .FREEZE)

The INSTRUMENT is Harmonia's (roles/Harmonia/science/asal_ruler/asal_ruler.py), imported by path and used
UNMODIFIED: rollout(), observables(), classify(), my_score(), to_rgb(), witness(), stage_fixture(). The executor
is Techne's EXTENDED numpy Lenia port (techne/scripts/techne107_asal_observer.py, extended at 593d57096: kn 1-4,
gn 1-3, fractional rings). Run with Techne's asal107 env python (torch CLIP; read-only use).

Stages, in order; each refuses to run unless its predecessor's record exists and passed:
  domain       enumerate the intended domain, instantiate EVERY member on the executor, write DOMAIN.json.
               No score. Refuses (exit 3) if any refusal is not covered by the declared exclusion rule.
  fixture      Harmonia's fixture + controls on this host and port; thresholds must reproduce the 09-18
               thresholds.json (the frozen threshold semantics) to 1e-12.
  determinism  (a) SAMPLED: all 395 rollouts executed on 09-18, regenerated, uint8 frames equal to the delivered
               frames128_manifest.json hashes; (b) ADVERSARIAL: a rule-chosen subset run twice, once in a fresh
               subprocess in reversed order, byte-identical frames. No score.
  search       REFUSES unless the packet FREEZE exists and matches the packet bytes. Torch column (the original
               observer of 09-18) on M3. Writes rows.jsonl, readouts.json, trajectories64.npz, embeddings16.npz,
               and the uint8 frames of every scored rollout OUTSIDE the repository plus their manifest IN it.
  selfcheck    torch path of techne/scripts/harm55_flax_score.py re-scores the exported uint8 frames; every
               score must equal the search's to 1e-6 (the frames are the frames that were scored).

Keys: S0 rollouts are keyed by the POSITION of the entry in animals.json ("S0_p<pos>"), never by its code
(63 codes are duplicated, Harmonia #479). S1 "S1_<i>", S2 "S2_<j*40+k>" as in 09-18.

    <asal107 python> -m nyx.atlas.experiments.asal_replication.replicate --stage domain
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RULER_DIR = os.path.join(REPO, "roles", "Harmonia", "science", "asal_ruler")
RUN0918 = os.path.join(RULER_DIR, "out", "run_2026-09-18")
OUT = os.path.join(HERE, "out")
PACKET = os.path.join(REPO, "nyx", "atlas", "predictions", "MECH-ASAL-REPLICATION-001.json")
FRAMES_DEST = r"C:\Prometheus-vault\nyx\asal_replication_001_frames128"   # outside git, like HARM-55's delivery

S1_SEED = 20261003          # fresh draws: NOT the 09-18 seed (a replication on new points, not a re-run)
S1_N, S2_STARTS, S2_STEPS = 300, 5, 40   # the 09-18 budget, unchanged
FROZEN_THRESHOLDS_SHA256 = None          # filled from the 09-18 file at import; compared in the fixture stage
EXCLUSION_RULE = "pattern_larger_than_world_128"   # the ONLY admissible reason a domain member is not executed


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


sys.dont_write_bytecode = True           # never write bytecode next to an imported instrument or body
AR = _load("asal_ruler_harmonia", os.path.join(RULER_DIR, "asal_ruler.py"))


def sha256_file(p):
    return AR.sha256_file(p)


def sha256_lf(p):
    return hashlib.sha256(open(p, "rb").read().replace(b"\r\n", b"\n")).hexdigest()


# ------------------------------------------------------------------------------------------ the domain
def catalogue():
    """[(pos, entry)] for every 2D catalogue lifeform: a dict with params and cells, cells free of the 3D/4D
    delimiters %#@ (Techne's lenia_port_acceptance.py rule). pos = index in animals.json: the stable identity."""
    animals = json.load(open(AR.ANIMALS, encoding="utf-8"))
    out = []
    for pos, e in enumerate(animals):
        if isinstance(e, dict) and "params" in e and "cells" in e and not any(ch in str(e["cells"]) for ch in "%#@"):
            out.append((pos, e))
    return out


def s1_draws():
    """The 300 S1 draws: the 09-18 rule (asal_ruler.py:297-305) verbatim, with the fresh seed."""
    animals = json.load(open(AR.ANIMALS, encoding="utf-8"))
    orb_pos = next(i for i, e in enumerate(animals) if isinstance(e, dict) and e.get("code") == "O2u")
    rng = np.random.default_rng(S1_SEED)
    draws = []
    for i in range(S1_N):
        p = {"R": int(rng.integers(6, 31)), "T": int(rng.choice([5, 10, 20])), "m": float(rng.uniform(0.05, 0.50)),
             "s": float(np.exp(rng.uniform(np.log(0.005), np.log(0.10)))), "b": str(rng.choice(AR.B_DOMAIN)),
             "kn": int(rng.choice([1, 2, 3, 4])), "gn": int(rng.choice([1, 2, 3]))}
        if rng.random() < 0.5:
            draws.append((i, p, "IC-BLOB", None))
        else:
            draws.append((i, p, "IC-ORB", orb_pos))
    return draws


def ic_of(label, pos, animals):
    if label == "IC-BLOB":
        return {"kind": "blob"}
    return {"kind": "cells", "cells": animals[pos]["cells"]}


def stage_domain(out):
    t107 = AR.load_techne()
    animals = json.load(open(AR.ANIMALS, encoding="utf-8"))
    res = {"stage": "domain", "executor": {"script": AR.TECHNE_SCRIPT, "sha256_lf": sha256_lf(AR.TECHNE_SCRIPT)},
           "animals_sha256": sha256_file(AR.ANIMALS), "classes": {}, "catalogue": {}, "s1": {}}

    def instantiate(p, A0=None, world=64):
        sim = t107.Lenia2D(world, dict(p, b=str(p["b"])))
        if A0 is None:
            A = np.zeros((world, world)); A[world // 2 - 4:world // 2 + 4, world // 2 - 4:world // 2 + 4] = 1.0
        else:
            A = sim.place(A0)
        for _ in range(3):
            A = sim.step(A)
        if not np.isfinite(A).all():
            raise ValueError("non_finite")

    base = {"R": 13, "T": 10, "m": 0.15, "s": 0.015, "b": "1", "kn": 1, "gn": 1}
    cls_ref = 0
    for name, values in (("b", AR.B_DOMAIN), ("kn", [1, 2, 3, 4]), ("gn", [1, 2, 3]), ("R", [6, 30]), ("T", [5, 10, 20]),
                         ("m", [0.05, 0.50]), ("s", [0.005, 0.10])):
        for v in values:
            try:
                instantiate(dict(base, **{name: v})); res["classes"][f"{name}={v}"] = "ACCEPTED"
            except Exception as e:  # noqa: BLE001
                res["classes"][f"{name}={v}"] = "REFUSED: " + repr(e)[:120]; cls_ref += 1
    # every kn x gn combination (the extension's own claim), at the base point
    for kn in (1, 2, 3, 4):
        for gn in (1, 2, 3):
            try:
                instantiate(dict(base, kn=kn, gn=gn)); res["classes"][f"kn={kn},gn={gn}"] = "ACCEPTED"
            except Exception as e:  # noqa: BLE001
                res["classes"][f"kn={kn},gn={gn}"] = "REFUSED: " + repr(e)[:120]; cls_ref += 1
    rows, excluded, refused = [], [], []
    for pos, e in catalogue():
        row = {"pos": pos, "code": e.get("code"), "b": str(e["params"].get("b")), "kn": e["params"].get("kn", 1), "gn": e["params"].get("gn", 1),
               "R": e["params"].get("R"), "T": e["params"].get("T")}
        try:
            pat = t107.rle2arr_2d(e["cells"])
            row["shape"] = list(pat.shape)
            if pat.shape[0] > AR.WORLD or pat.shape[1] > AR.WORLD:
                row["status"] = "EXCLUDED"; row["reason"] = EXCLUSION_RULE; excluded.append(pos)
            else:
                instantiate(dict(e["params"]), pat, world=AR.WORLD); row["status"] = "ACCEPTED"
        except Exception as ex:  # noqa: BLE001
            row["status"] = "REFUSED"; row["reason"] = repr(ex)[:160]; refused.append(pos)
        rows.append(row)
    res["catalogue"] = {"members": len(rows), "accepted": sum(r["status"] == "ACCEPTED" for r in rows), "excluded": len(excluded),
                        "refused": len(refused), "excluded_positions": excluded, "refused_positions": refused, "rows": rows}
    s1_ref = []
    for i, p, lab, pos in s1_draws():
        try:
            instantiate(p, None if lab == "IC-BLOB" else t107.rle2arr_2d(animals[pos]["cells"]), world=AR.WORLD)
        except Exception as ex:  # noqa: BLE001
            s1_ref.append({"i": i, "params": p, "reason": repr(ex)[:160]})
    res["s1"] = {"seed": S1_SEED, "n": S1_N, "refused": len(s1_ref), "refused_rows": s1_ref,
                 "draws_sha256": hashlib.sha256(json.dumps([(i, p, lab, pos) for i, p, lab, pos in s1_draws()], sort_keys=True).encode()).hexdigest()}
    # 09-18 overlap, by position: which catalogue members were EXECUTED then (the old S0 indexed the "x"-filtered list)
    old_cat = [i for i, e in enumerate(animals) if isinstance(e, dict) and "params" in e and "cells" in e and "x" not in str(e.get("code", ""))]
    old_rows = [json.loads(l) for l in open(os.path.join(RUN0918, "search", "rows.jsonl"))]
    executed_old = sorted(old_cat[r["idx"]] for r in old_rows if r["stage"] == "S0" and "error" not in r)
    res["overlap_0918"] = {"catalogue_positions_executed_0918": executed_old, "n": len(executed_old),
                           "new_positions": sorted(set(r["pos"] for r in rows if r["status"] == "ACCEPTED") - set(executed_old))}
    res["overlap_0918"]["n_new"] = len(res["overlap_0918"]["new_positions"])
    res["executable"] = cls_ref == 0 and not refused and not s1_ref
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "DOMAIN.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    print(json.dumps({k: (v if k not in ("catalogue", "classes", "overlap_0918") else None) for k, v in res.items()}, default=str)[:600])
    print("classes refused:", cls_ref, "| catalogue", {k: res["catalogue"][k] for k in ("members", "accepted", "excluded", "refused")},
          "| S1 refused", len(s1_ref), "| new catalogue positions", res["overlap_0918"]["n_new"], "| EXECUTABLE", res["executable"])
    return res["executable"]


# ------------------------------------------------------------------------------------------ fixture
def stage_fixture(out):
    assert json.load(open(os.path.join(out, "DOMAIN.json")))["executable"], "domain stage not passed"
    ok = AR.stage_fixture(out)
    th_new = json.load(open(os.path.join(out, "thresholds.json")))
    th_old = json.load(open(os.path.join(RUN0918, "thresholds.json")))
    keys = ("coh_O", "d_pix_O", "d_clip_H", "d_clip_O", "disp_O", "mass_cv_O")
    diffs = {k: abs(th_new[k] - th_old[k]) for k in keys}
    same = all(d <= 1e-12 for d in diffs.values()) and th_new["orbium_alive"] == th_old["orbium_alive"]
    rec = {"fixture_controls_pass": bool(ok), "thresholds_0918_sha256": sha256_file(os.path.join(RUN0918, "thresholds.json")),
           "threshold_diffs": diffs, "thresholds_reproduce_0918": bool(same), "pass": bool(ok and same)}
    json.dump(rec, open(os.path.join(out, "FIXTURE_CHECK.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    print(json.dumps(rec, indent=1))
    return rec["pass"]


# ------------------------------------------------------------------------------------------ determinism
def _old_ic(r, animals, old_cat, cat_first):
    if r["ic"] == "IC-BLOB":
        return {"kind": "blob"}
    if r["ic"] == "IC-ORB":
        return {"kind": "cells", "cells": next(e for e in animals if isinstance(e, dict) and e.get("code") == "O2u")["cells"]}
    if r["stage"] == "S0":
        return {"kind": "cells", "cells": animals[old_cat[r["idx"]]]["cells"]}
    return {"kind": "cells", "cells": cat_first[r["ic"]]}


def adversarial_set():
    """Rule-chosen, score-blind: one catalogue member per (b, kn, gn) class the 09-18 port REFUSED (lowest position
    first); the largest accepted pattern; the max-R and min-T members; S1 draws at the domain edges (R 6 / 30, T 5,
    s at its two extremes, kn 4, gn 3), first by index."""
    dom = json.load(open(os.path.join(OUT, "DOMAIN.json")))
    acc = [r for r in dom["catalogue"]["rows"] if r["status"] == "ACCEPTED"]
    pick, seen = [], set()
    for r in sorted(acc, key=lambda r: r["pos"]):
        cls = (r["b"], r["kn"], r["gn"])
        refused_0918 = ("/" in r["b"]) or r["kn"] >= 3 or r["gn"] >= 3
        if refused_0918 and cls not in seen:
            seen.add(cls); pick.append(("S0", r["pos"]))
    by_area = max(acc, key=lambda r: r["shape"][0] * r["shape"][1]); pick.append(("S0", by_area["pos"]))
    pick.append(("S0", max(acc, key=lambda r: (r["R"] or 0, -r["pos"]))["pos"]))
    pick.append(("S0", min(acc, key=lambda r: (r["T"] or 99, r["pos"]))["pos"]))
    draws = s1_draws()
    for pred in (lambda p: p["R"] == 6, lambda p: p["R"] == 30, lambda p: p["T"] == 5, lambda p: p["kn"] == 4, lambda p: p["gn"] == 3,
                 lambda p: p["s"] < 0.006, lambda p: p["s"] > 0.09):
        hit = next((i for i, p, _, _ in draws if pred(p)), None)
        if hit is not None:
            pick.append(("S1", hit))
    out, s = [], set()
    for x in pick:
        if x not in s:
            s.add(x); out.append(x)
    return out


def frames_for(item, t107, animals):
    kind, k = item
    if kind == "S0":
        e = animals[k]; f128, _, _ = AR.rollout(t107, dict(e["params"]), {"kind": "cells", "cells": e["cells"]})
    else:
        i, p, lab, pos = s1_draws()[k]; f128, _, _ = AR.rollout(t107, p, ic_of(lab, pos, animals))
    return (np.clip(f128, 0, 1) * 255).astype(np.uint8)


def stage_determinism(out, child=None):
    t107 = AR.load_techne(); animals = json.load(open(AR.ANIMALS, encoding="utf-8"))
    if child:                                    # subprocess mode: run the adversarial set in REVERSED order
        items = list(reversed(adversarial_set()))
        hashes = {f"{a}_{b}": hashlib.sha256(frames_for((a, b), t107, animals).tobytes()).hexdigest() for a, b in items}
        json.dump(hashes, open(child, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True); return True
    assert json.load(open(os.path.join(out, "FIXTURE_CHECK.json")))["pass"], "fixture stage not passed"
    man = json.load(open(os.path.join(RUN0918, "frames128_manifest.json")))["rollouts"]
    old_cat = [i for i, e in enumerate(animals) if isinstance(e, dict) and "params" in e and "cells" in e and "x" not in str(e.get("code", ""))]
    cat_first = {}
    for i in old_cat:
        cat_first.setdefault(f"IC-CAT:{animals[i].get('code')}", animals[i]["cells"])
    rows = [json.loads(l) for l in open(os.path.join(RUN0918, "search", "rows.jsonl")) if '"error"' not in l]
    t0 = time.time(); ok = 0; bad = []
    for r in rows:
        key = f"{r['stage']}_{r['idx']}"
        f128, _, _ = AR.rollout(t107, r["params"], _old_ic(r, animals, old_cat, cat_first))
        u8 = (np.clip(f128, 0, 1) * 255).astype(np.uint8)
        import io
        buf = io.BytesIO(); np.save(buf, u8); h = hashlib.sha256(buf.getvalue()).hexdigest()
        if h == man[key]["sha256"]:
            ok += 1
        else:
            bad.append(key)
    sampled = {"n": len(rows), "identical_to_0918_delivery": ok, "differing": bad, "pass": ok == len(rows), "seconds": round(time.time() - t0, 1)}
    items = adversarial_set()
    first = {f"{a}_{b}": hashlib.sha256(frames_for((a, b), t107, animals).tobytes()).hexdigest() for a, b in items}
    tmp = os.path.join(out, "_adv_child.json")
    subprocess.run([sys.executable, "-B", "-m", "nyx.atlas.experiments.asal_replication.replicate", "--stage", "determinism", "--child", tmp],
                   cwd=REPO, check=True)
    second = json.load(open(tmp)); os.remove(tmp)
    adv = {"items": [f"{a}_{b}" for a, b in items], "n": len(items), "identical": sum(first[k] == second.get(k) for k in first),
           "differing": [k for k in first if first[k] != second.get(k)], "rule": adversarial_set.__doc__.strip()}
    adv["pass"] = adv["identical"] == adv["n"]
    rec = {"sampled_0918_rollouts": sampled, "adversarial_two_processes": adv, "pass": sampled["pass"] and adv["pass"],
           "executor_sha256_lf": sha256_lf(AR.TECHNE_SCRIPT)}
    json.dump(rec, open(os.path.join(out, "DETERMINISM.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    print(json.dumps({k: (v if k != "adversarial_two_processes" else {kk: vv for kk, vv in v.items() if kk != "rule"}) for k, v in rec.items()}, indent=1))
    return rec["pass"]


# ------------------------------------------------------------------------------------------ search (torch column)
def _packet_frozen():
    sys.path.insert(0, REPO)
    from nyx.atlas.predictions import schema as ps
    p = json.load(open(PACKET, encoding="utf-8"))
    fz = PACKET[:-5] + ".FREEZE"
    if not os.path.exists(fz):
        return False, "no FREEZE"
    h = open(fz, encoding="utf-8").read().split()[0]
    return h == ps.packet_hash(p), h


def stage_search(out):
    for f, k in (("DOMAIN.json", "executable"), ("FIXTURE_CHECK.json", "pass"), ("DETERMINISM.json", "pass")):
        assert json.load(open(os.path.join(out, f)))[k], f"{f} not passed; search refused"
    frozen, h = _packet_frozen()
    assert frozen, f"packet not frozen ({h}); search refused"
    th = json.load(open(os.path.join(out, "thresholds.json")))
    t107 = AR.load_techne(); obs = t107.Observer()
    animals = json.load(open(AR.ANIMALS, encoding="utf-8"))
    dom = json.load(open(os.path.join(out, "DOMAIN.json")))
    accepted = [r["pos"] for r in dom["catalogue"]["rows"] if r["status"] == "ACCEPTED"]
    sdir = os.path.join(out, "search"); os.makedirs(sdir, exist_ok=True); os.makedirs(FRAMES_DEST, exist_ok=True)
    rows = []; rows_f = open(os.path.join(sdir, "rows.jsonl"), "w", encoding="utf-8", newline="\n")
    traj = {}; manifest = {"schema": "harmonia.frames128/1", "run": "nyx asal_replication_001/search", "dest": FRAMES_DEST, "dtype": "uint8",
                           "shape": [8, 128, 128], "note": "uint8(clip(x,0,1)*255) of the 128x128 grey frames: exactly what grey_to_rgb() fed CLIP; "
                           "sha256 is of the .npy file bytes (binary: the blob hash)", "port_sha256_lf": sha256_lf(AR.TECHNE_SCRIPT),
                           "packet_freeze": h, "rollouts": {}}
    t0 = time.time()

    def evaluate(stage, idx, params, ic, ic_label, seed=None, pos=None):
        key = f"{stage}_{idx}"
        f128, mass, alive = AR.rollout(t107, params, ic, seed)           # no try: the domain stage proved every member executes
        z = obs.embed(AR.to_rgb(t107, f128)); s = t107.open_endedness_score(z)
        o = AR.observables(f128, z); cls = AR.classify(o, alive, th)
        r = {"stage": stage, "idx": idx, "key": key, "pos": pos, "params": {k: (v if not isinstance(v, np.generic) else v.item()) for k, v in params.items()},
             "ic": ic_label, "seed": seed, "score": s, "alive": bool(alive), "mass": [float(m) for m in mass], "class": cls, **o}
        rows.append(r); rows_f.write(json.dumps(r) + "\n"); rows_f.flush()
        u8 = (np.clip(f128, 0, 1) * 255).astype(np.uint8)
        fp = os.path.join(FRAMES_DEST, key + ".npy"); np.save(fp, u8)
        manifest["rollouts"][key] = {"sha256": sha256_file(fp), "score_torch": s, "class": cls, "alive": bool(alive)}
        traj[key] = {"frames64": (np.clip(np.stack([t107.resize_bilinear(np.repeat(f[:, :, None], 3, axis=2), 64)[:, :, 0] for f in f128]), 0, 1) * 255).astype(np.uint8),
                     "z16": z.astype(np.float16), "z32": z.astype(np.float32)}
        if len(rows) % 50 == 0:
            print(f"{len(rows)} rollouts, {time.time() - t0:.0f} s", flush=True)
        return r

    for pos in accepted:                                                  # S0: every accepted catalogue member, by position
        e = animals[pos]
        evaluate("S0", f"p{pos}", dict(e["params"]), {"kind": "cells", "cells": e["cells"]}, f"IC-CAT:p{pos}:{e.get('code')}", pos=pos)
    for i, p, lab, pos in s1_draws():                                     # S1: fresh seed
        evaluate("S1", i, p, ic_of(lab, pos, animals), lab, seed=S1_SEED)
    alive_rows = sorted([r for r in rows if r["alive"]], key=lambda r: r["score"])[:S2_STARTS]   # S2: the 09-18 rule
    for j, base in enumerate(alive_rows):
        rng2 = np.random.default_rng(S1_SEED + j + 1); cur, curv = dict(base["params"]), base["score"]
        if base["ic"] == "IC-BLOB":
            ic = {"kind": "blob"}
        elif base["ic"] == "IC-ORB":
            ic = {"kind": "cells", "cells": next(e for e in animals if isinstance(e, dict) and e.get("code") == "O2u")["cells"]}
        else:
            ic = {"kind": "cells", "cells": animals[base["pos"]]["cells"]}
        for k in range(S2_STEPS):
            cand = dict(cur); cand["m"] = float(np.clip(cur["m"] + rng2.normal(0, 0.02), 0.05, 0.50)); cand["s"] = float(np.clip(cur["s"] + rng2.normal(0, 0.005), 0.005, 0.10))
            cand["R"] = int(np.clip(round(cur["R"] + rng2.normal(0, 1)), 6, 30))
            r = evaluate("S2", j * S2_STEPS + k, cand, ic, base["ic"], seed=S1_SEED, pos=base["pos"])
            if r["alive"] and r["score"] < curv:
                cur, curv = cand, r["score"]
    rows_f.close()
    new_pos = set(dom["overlap_0918"]["new_positions"])
    for r in rows:
        r["stratum"] = "S0_OLD" if (r["stage"] == "S0" and r["pos"] not in new_pos) else ("S0_NEW" if r["stage"] == "S0" else r["stage"])
    with open(os.path.join(sdir, "rows.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    np.savez_compressed(os.path.join(sdir, "trajectories64.npz"), **{k: v["frames64"] for k, v in traj.items()})
    np.savez_compressed(os.path.join(sdir, "embeddings16.npz"), **{k: v["z16"] for k, v in traj.items()})
    np.savez_compressed(os.path.join(sdir, "embeddings32_torch.npz"), **{k: v["z32"] for k, v in traj.items()})
    manifest["n_rollouts"] = len(rows); manifest["seconds"] = round(time.time() - t0, 1); manifest["witness"] = AR.witness(obs)
    json.dump(manifest, open(os.path.join(out, "frames128_manifest.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    json.dump(readouts(rows), open(os.path.join(sdir, "readouts.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True, default=float)
    print(f"done: {len(rows)} rollouts in {time.time() - t0:.0f} s")


def readouts(rows):
    """Descriptive tables only. The packet's rows are adjudicated by Harmonia from rows.jsonl, not from this."""
    G = AR.GARBAGE_MEAN; G2 = AR.GARBAGE_MEAN - 2 * AR.GARBAGE_SD
    out = {}
    for st in ("S0_OLD", "S0_NEW", "S1", "S2", "NEW_ALL"):
        rs = [r for r in rows if (r["stratum"] == st) or (st == "NEW_ALL" and r["stratum"] in ("S0_NEW", "S1", "S2"))]
        al = [r for r in rs if r["alive"]]
        below = [r for r in al if r["score"] < G]
        hist = {}
        for r in rs:
            hist[r["class"]] = hist.get(r["class"], 0) + 1
        out[st] = {"n": len(rs), "n_alive": len(al), "min_alive": min((r["score"] for r in al), default=None),
                   "argmin_alive": min(al, key=lambda r: r["score"])["key"] if al else None,
                   "n_below_mean": len(below), "n_below_2sd": sum(r["score"] < G2 for r in al),
                   "classes_below_mean": {c: sum(r["class"] == c for r in below) for c in sorted({r["class"] for r in below})},
                   "class_histogram": hist}
    return {"strata": out, "garbage_mean": G, "garbage_2sd": G2}


# ------------------------------------------------------------------------------------------ self-check
def stage_selfcheck(out):
    res_p = os.path.join(out, "selfcheck_torch.json")
    subprocess.run([sys.executable, "-B", os.path.join(REPO, "techne", "scripts", "harm55_flax_score.py"), "--path", "torch", "--out", res_p,
                    "--manifest", os.path.join(out, "frames128_manifest.json"), "--frames-dir", FRAMES_DEST,
                    "--rows", os.path.join(out, "search", "rows.jsonl"), "--thresholds", os.path.join(out, "thresholds.json")], cwd=REPO, check=True)
    sc = json.load(open(res_p))["scores"]
    rows = {r["key"]: r for r in (json.loads(l) for l in open(os.path.join(out, "search", "rows.jsonl")))}
    d = max(abs(float(sc[k]) - rows[k]["score"]) for k in rows)
    # C-REPRO: S0_OLD positions against the 09-18 torch scores of the same catalogue entries (old S0 idx -> position)
    animals = json.load(open(AR.ANIMALS, encoding="utf-8"))
    old_cat = [i for i, e in enumerate(animals) if isinstance(e, dict) and "params" in e and "cells" in e and "x" not in str(e.get("code", ""))]
    old = {old_cat[r["idx"]]: r["score"] for r in (json.loads(l) for l in open(os.path.join(RUN0918, "search", "rows.jsonl")))
           if r["stage"] == "S0" and "error" not in r}
    rep = [abs(rows[f"S0_p{p}"]["score"] - s) for p, s in old.items() if f"S0_p{p}" in rows]
    repro = {"n": len(rep), "of": len(old), "max_abs_diff": max(rep) if rep else None, "pass": bool(rep) and len(rep) == len(old) and max(rep) <= 1e-6}
    rec = {"C-SELF": {"n": len(rows), "n_rescored": len(sc), "max_abs_diff": d, "pass": d <= 1e-6 and len(sc) == len(rows)}, "C-REPRO": repro}
    rec["pass"] = rec["C-SELF"]["pass"] and repro["pass"]
    json.dump(rec, open(os.path.join(out, "SELFCHECK.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    print(json.dumps(rec, indent=1))
    return rec["pass"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["domain", "fixture", "determinism", "search", "selfcheck"], required=True)
    ap.add_argument("--out", default=OUT); ap.add_argument("--child", default=None)
    a = ap.parse_args()
    fn = {"domain": stage_domain, "fixture": stage_fixture, "search": stage_search, "selfcheck": stage_selfcheck}
    if a.stage == "determinism":
        ok = stage_determinism(a.out, a.child)
    else:
        ok = fn[a.stage](a.out)
    sys.exit(0 if ok in (True, None) else 3)
