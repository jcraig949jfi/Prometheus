"""HARM-55 -- score Harmonia's 395 preserved rollouts through an observer path and emit the directive-5 table.

Input (operator directive 2026-09-19 s1): the DELIVERED 128x128 uint8 greyscale frames
(C:\\Prometheus-vault\\harmonia\\asal_001_frames128\\<stage>_<idx>.npy, (8,128,128) uint8) and the committed
manifest roles/Harmonia/science/asal_ruler/out/run_2026-09-18/frames128_manifest.json (sha256 per rollout,
alive, class, score_torch). Nothing is regenerated here; every frame file is re-hashed against the manifest
before it is scored, and a mismatch stops the run.

Preprocessing contract (frozen; the seven-arm fixture and the search used it): uint8 grey -> float [0,1] ->
grey_to_rgb (3 channels, bilinear to 224) -> CLIP mean/std normalisation -> image features -> L2 norm.

Observer paths, both from the pinned ASAL body where it applies:
  --path flax    ASAL's OWN foundation_models/clip.py (FlaxCLIPModel openai/clip-vit-base-patch32) and ASAL's
                 OWN asal_metrics.calc_open_endedness_score, imported from the vault body (specimen
                 asal-sakana-2024). Needs jax/flax/transformers on an AVX host. THE HARM-55 DELIVERABLE.
  --path torch   the torch CLIP + numpy metric of techne107_asal_observer.py: the "original observer" column
                 recomputed from the delivered frames (self-check against the manifest's score_torch).

Output (keyed by stable stage_idx): original observer score (manifest), this path's score, abs and signed
difference, alive, class, threshold relationships for the catalogue (Orbium), mean-garbage and 2-sd
boundaries under both observers, d_clip and the re-derived class under this path, per-row frame sha256;
the pairwise discordance table in the preregistered +/-0.01 band around each boundary; the six directive
questions A-F; and "scores" = {key: score} so roles/Harmonia/science/asal_ruler/harm55_compare.py reads
the same file unchanged.
Run: <env python> techne/scripts/harm55_flax_score.py --path flax --out flax_scores.json
     [--frames-dir DIR] [--manifest FILE] [--rows rows.jsonl] [--thresholds thresholds.json] [--band 0.01]
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import platform
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve()
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE.parent))

RULER = REPO / "roles" / "Harmonia" / "science" / "asal_ruler" / "out" / "run_2026-09-18"
DEFAULT_MANIFEST = RULER / "frames128_manifest.json"
DEFAULT_ROWS = RULER / "search" / "rows.jsonl"
DEFAULT_THRESHOLDS = RULER / "search" / "thresholds.json"
# Boundaries as the frozen packet named them (Harmonia PREREG_ASAL_LEGIT_SEARCH_2026-09-18; TECHNE-107 receipt):
BOUNDARIES = {"catalogue": 0.8472459316253662,   # the Orbium reference (catalogue life, alive) -- TECHNE-107 LENIA arm
              "garbage_mean": 0.8167,             # GARBAGE 5-seed mean, the frozen convention (rule A7: a named cutoff)
              "garbage_2sd": 0.7999}              # 0.8167 - 2 * 0.0084
BAND = 0.01


def frames_to_rgb224(frames_u8: np.ndarray) -> np.ndarray:
    import techne107_asal_observer as port
    f = frames_u8.astype(np.float64) / 255.0
    return np.stack([port.grey_to_rgb(x) for x in f])


def d_clip_of(z: np.ndarray) -> float:
    """asal_ruler.py:76 -- mean over consecutive frames of (1 - z[i+1] . z[i])."""
    return float(np.mean([1.0 - float(z[i + 1] @ z[i]) for i in range(len(z) - 1)]))


def classify(o: dict, alive: bool, th: dict) -> str:
    """asal_ruler.py:96-105, verbatim logic (coh / d_pix / mass_cv are frame-based; only OBSERVER_EXPLOIT reads d_clip)."""
    if not alive:
        return "NOT_ALIVE"
    if o["coh"] >= 0.8 * th["coh_O"] and o["d_pix"] >= 0.5 * th["d_pix_O"] and o["mass_cv"] <= 0.5:
        return "GENUINE_DYNAMICAL_NOVELTY"
    if o["coh"] < 0.5 * th["coh_O"] and o["d_pix"] >= th["d_pix_O"]:
        return "METRIC_EXPLOIT"
    if o["d_pix"] < 0.5 * th["d_pix_O"] and o["d_clip"] >= 0.8 * th["d_clip_H"]:
        return "OBSERVER_EXPLOIT"
    return "UNCLASSIFIED"


# --------------------------------------------------------------------------- observers
def flax_observer():
    from techne.fossils import vault
    body = vault.body_dir("asal-sakana-2024") / "upstream" / "tree"
    sys.path.insert(0, str(body))
    import jax, jaxlib, flax, transformers          # noqa: F401  (AVX host only)
    import jax.numpy as jnp
    from foundation_models.clip import CLIP         # ASAL's wrapper, unmodified
    import asal_metrics                             # ASAL's metric, unmodified
    fm = CLIP()
    rec = json.loads((vault.specimen_dir("asal-sakana-2024") / "record.json").read_text(encoding="utf-8"))
    ident = {"path": "flax", "scorer": "ASAL foundation_models/clip.py CLIP.embed_img + asal_metrics.calc_open_endedness_score (body, unmodified)",
             "jax": jax.__version__, "jaxlib": jaxlib.__version__, "flax": flax.__version__, "transformers": transformers.__version__,
             "model": "openai/clip-vit-base-patch32 (FlaxCLIPModel)", "weights_files_sha256": _hf_snapshot_hashes("openai/clip-vit-base-patch32"),
             "body_commit": rec["source_origin"]["artifacts"][0].get("commit_resolved"), "body_tree_sha256": rec["hashes"]["tree_sha256"]}

    def embed(frames_rgb224: np.ndarray) -> np.ndarray:
        return np.asarray(jnp.stack([fm.embed_img(jnp.asarray(f, dtype=jnp.float32)) for f in frames_rgb224]))

    def score(z: np.ndarray) -> float:
        return float(asal_metrics.calc_open_endedness_score(jnp.asarray(z)))
    return ident, embed, score


def _hf_snapshot_hashes(repo_id: str) -> dict:
    try:
        from huggingface_hub import scan_cache_dir
        for r in scan_cache_dir().repos:
            if r.repo_id == repo_id:
                out = {}
                for rev in r.revisions:
                    for f in rev.files:
                        if f.file_name.endswith((".msgpack", ".safetensors", ".bin")):
                            out[f.file_name] = hashlib.sha256(open(f.file_path, "rb").read()).hexdigest()
                return out
    except Exception as e:                          # noqa: BLE001
        return {"error": str(e)[:100]}
    return {}


def torch_observer():
    import techne107_asal_observer as port
    obs = port.Observer()
    ident = {"path": "torch", "scorer": "techne107_asal_observer.py Observer (openai `clip` ViT-B/32) + numpy open_endedness_score -- the ORIGINAL observer of the search",
             "torch": obs.torch.__version__, "weights_sha256": obs.weights_sha256,
             "port_sha256_lf": hashlib.sha256(open(HERE.parent / "techne107_asal_observer.py", "rb").read().replace(b"\r\n", b"\n")).hexdigest()}
    return ident, obs.embed, port.open_endedness_score


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", choices=["flax", "torch"], required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST)); ap.add_argument("--frames-dir", default=None)
    ap.add_argument("--rows", default=str(DEFAULT_ROWS)); ap.add_argument("--thresholds", default=str(DEFAULT_THRESHOLDS))
    ap.add_argument("--band", type=float, default=BAND); ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    man = json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
    frames_dir = pathlib.Path(a.frames_dir or man["dest"])
    th = json.loads(pathlib.Path(a.thresholds).read_text(encoding="utf-8"))
    rows = {"%s_%s" % (r["stage"], r["idx"]): r for r in (json.loads(l) for l in open(a.rows, encoding="utf-8")) if "error" not in r}
    ident, embed, score = (flax_observer if a.path == "flax" else torch_observer)()
    ident.update({"host": platform.node(), "cpu": platform.processor(), "python": platform.python_version(),
                  "frames": {"manifest": str(pathlib.Path(a.manifest).relative_to(REPO)) if str(a.manifest).startswith(str(REPO)) else a.manifest,
                             "manifest_sha256_lf": hashlib.sha256(pathlib.Path(a.manifest).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
                             "dir": str(frames_dir), "dtype": man["dtype"], "shape": man["shape"], "regenerated_here": False,
                             "contract": "uint8 grey /255 -> grey_to_rgb bilinear 224 -> CLIP mean/std -> image features -> L2 (the seven-arm fixture's path)"},
                  "thresholds_file": th, "boundaries": BOUNDARIES, "band": a.band, "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    out_rows, scores, verified = {}, {}, 0
    keys = list(man["rollouts"])[: a.limit] if a.limit else list(man["rollouts"])
    t0 = time.time()
    for key in keys:
        m = man["rollouts"][key]
        p = frames_dir / (key + ".npy")
        b = p.read_bytes()
        h = hashlib.sha256(b).hexdigest()
        if h != m["sha256"]:
            raise SystemExit("FRAME HASH MISMATCH for %s: %s != manifest %s -- stopping (directive s1: never score altered frames)" % (key, h, m["sha256"]))
        verified += 1
        fr = np.load(p)
        z = embed(frames_to_rgb224(fr))
        s = score(z)
        scores[key] = s
        orig = float(m["score_torch"]) if m.get("score_torch") is not None else None
        r = rows.get(key, {})
        o = {"coh": r.get("coh"), "d_pix": r.get("d_pix"), "mass_cv": r.get("mass_cv"), "d_clip": d_clip_of(z)}
        cls_new = classify(o, bool(m["alive"]), th) if all(v is not None for v in (o["coh"], o["d_pix"], o["mass_cv"])) else "UNRESOLVED"
        out_rows[key] = {
            "stage": key.split("_")[0], "idx": key.split("_", 1)[1], "ic": r.get("ic"), "seed": r.get("seed"),
            "alive": bool(m["alive"]), "class": m["class"], "score_original": orig, "score_%s" % a.path: s,
            "abs_diff": (abs(s - orig) if orig is not None else None), "signed_diff": ((s - orig) if orig is not None else None),
            "crossings_original": {k: (orig < v) if orig is not None else None for k, v in BOUNDARIES.items()},
            "crossings_%s" % a.path: {k: (s < v) for k, v in BOUNDARIES.items()},
            "d_clip_original": r.get("d_clip"), "d_clip_%s" % a.path: o["d_clip"], "class_%s" % a.path: cls_new,
            "class_changed": (cls_new != m["class"]) if cls_new != "UNRESOLVED" else None,
            "frame_sha256": h}
    ident["seconds"] = round(time.time() - t0, 1); ident["n_scored"] = len(scores); ident["n_frames_verified"] = verified
    # ---- pairwise discordance in the preregistered band around each boundary (on the ORIGINAL score)
    disc = {}
    ok = [k for k in out_rows if out_rows[k]["score_original"] is not None and out_rows[k]["alive"]]
    for name, thv in BOUNDARIES.items():
        band_keys = [k for k in ok if abs(out_rows[k]["score_original"] - thv) <= a.band]
        pairs = list(itertools.combinations(band_keys, 2))
        table = []
        for i, j in pairs:
            oi, oj = out_rows[i]["score_original"], out_rows[j]["score_original"]
            ni, nj = scores[i], scores[j]
            same = (oi - oj) * (ni - nj) > 0
            table.append({"a": i, "b": j, "class_pair": sorted([out_rows[i]["class"], out_rows[j]["class"]]),
                          "original": [oi, oj], a.path: [ni, nj], "concordant": bool(same),
                          "max_dist_to_boundary": max(abs(oi - thv), abs(oj - thv))})
        n_disc = sum(1 for t in table if not t["concordant"])
        by_class = {}
        for t in table:
            cp = "|".join(t["class_pair"]); d = by_class.setdefault(cp, {"pairs": 0, "discordant": 0}); d["pairs"] += 1; d["discordant"] += (not t["concordant"])
        disc[name] = {"threshold": thv, "n_in_band": len(band_keys), "n_pairs": len(pairs), "n_discordant": n_disc,
                      "by_class_pair": by_class,
                      "by_distance": {"<%.4f" % d: sum(1 for t in table if not t["concordant"] and t["max_dist_to_boundary"] < d) for d in (0.0025, 0.005, 0.01)},
                      "pairs": table}
    # ---- the six questions (each answered on THIS path against the original; never averaged)
    g = BOUNDARIES["garbage_mean"]
    alive = [k for k in out_rows if out_rows[k]["alive"]]
    cat = [k for k in alive if out_rows[k]["stage"] == "S0"]
    genuine = [k for k in alive if out_rows[k]["class"] == "GENUINE_DYNAMICAL_NOVELTY"]
    exploit_low = [k for k in alive if out_rows[k]["class"] == "METRIC_EXPLOIT" and out_rows[k]["score_original"] is not None and out_rows[k]["score_original"] < g]
    deepest = sorted([k for k in alive if out_rows[k]["score_original"] is not None], key=lambda k: out_rows[k]["score_original"])[:10]
    def med(ks):
        v = [scores[k] for k in ks]; return float(np.median(v)) if v else None
    def med_o(ks):
        v = [out_rows[k]["score_original"] for k in ks if out_rows[k]["score_original"] is not None]; return float(np.median(v)) if v else None
    classes = ["GENUINE_DYNAMICAL_NOVELTY", "UNCLASSIFIED", "METRIC_EXPLOIT"]
    questions = {
        "A_catalogue_life_still_crosses_garbage": {"original": sorted(k for k in cat if out_rows[k]["score_original"] is not None and out_rows[k]["score_original"] < g),
                                                   a.path: sorted(k for k in cat if scores[k] < g)},
        "B_genuine_organisms_crossing": {"S2_135": {"in_corpus": "S2_135" in scores, "class": out_rows.get("S2_135", {}).get("class"),
                                                    "original": out_rows.get("S2_135", {}).get("score_original"), a.path: scores.get("S2_135")},
                                         "genuine_crossers_original": sorted(k for k in genuine if out_rows[k]["score_original"] is not None and out_rows[k]["score_original"] < g),
                                         "genuine_crossers_%s" % a.path: sorted(k for k in genuine if scores[k] < g)},
        "C_deepest_witnesses_still_cross": [{"key": k, "class": out_rows[k]["class"], "original": out_rows[k]["score_original"], a.path: scores[k], "crosses_%s" % a.path: scores[k] < g} for k in deepest],
        "D_low_score_exploits_preserved": {"n_original_below_garbage": len(exploit_low), "n_still_below_%s" % a.path: sum(1 for k in exploit_low if scores[k] < g),
                                           "lost": sorted(k for k in exploit_low if scores[k] >= g)},
        "E_class_region_ordering": {"median_original": {c: med_o([k for k in alive if out_rows[k]["class"] == c]) for c in classes},
                                    "median_%s" % a.path: {c: med([k for k in alive if out_rows[k]["class"] == c]) for c in classes}},
        "F_classifications_observer_dependent": {"n_changed": sum(1 for k in out_rows if out_rows[k]["class_changed"]),
                                                 "changed": {k: [out_rows[k]["class"], out_rows[k]["class_%s" % a.path]] for k in out_rows if out_rows[k]["class_changed"]},
                                                 "note": "only the OBSERVER_EXPLOIT branch of classify() reads d_clip; coh/d_pix/mass_cv are frame-based and observer-independent"},
    }
    out = {"schema": "techne.harm55.scores/2", "identity": ident, "boundaries": BOUNDARIES, "rows": out_rows, "discordance": disc,
           "questions": questions, "scores": scores}
    if a.path == "torch":
        diffs = [out_rows[k]["abs_diff"] for k in out_rows if out_rows[k]["abs_diff"] is not None]
        out["self_check_vs_manifest_score_torch"] = {"n": len(diffs), "max_abs_diff": max(diffs) if diffs else None, "mean_abs_diff": float(np.mean(diffs)) if diffs else None}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("scored", len(scores), "frames verified", verified, "| %.1fs" % ident["seconds"])
    if "self_check_vs_manifest_score_torch" in out:
        print("self-check vs manifest score_torch:", out["self_check_vs_manifest_score_torch"])
    for name, d in disc.items():
        print("band %-13s in_band %3d pairs %5d discordant %4d" % (name, d["n_in_band"], d["n_pairs"], d["n_discordant"]))
    print("F changed classes:", questions["F_classifications_observer_dependent"]["n_changed"])
    print("wrote", a.out)


if __name__ == "__main__":
    main()
