"""PORTABLE SPECIMEN CAPSULE (operator directive 6, 2026-09-19, s3): the unit Techne preserves from now on.

A capsule is one JSON file, CAPSULE.json, beside a specimen's record.json. It contains or refers IMMUTABLY
(by sha256, commit, or committed path) to everything Nyx needs to cut the specimen open months later
without today's filesystem or today's experiment in mind. For an ASAL rollout:

  specimen_id, source_bodies + lineage, params, initial_condition, seed, frame hashes, replay,
  original_observer {score, identity}, native_observer {score, identity} or an explicit PENDING,
  alive, classification, preservation_reason, provenance (packets, runs, blobs), relatives,
  evidence (raw pointers), observer_internals (per-frame scores, embedding hashes) where cheap.

Rules the validator enforces (controls in techne/tests/test_fossil_capsule.py):
  - every directive field present; nulls only where the directive allows a pending value;
  - a native score may not appear WITHOUT the native observer's identity (a number with no scorer is
    the cheat the directive warns about);
  - the frame hash in the capsule equals the record's pinned artifact sha256;
  - replay names the instrument (path + sha) that regenerates the frames, never a host path only.
CLI:  python -m techne.fossils.capsule build --rollouts [--flax FILE] [--internals] [--write]
      python -m techne.fossils.capsule validate --all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time

import numpy as np

from techne.fossils import record, vault

SCHEMA = "techne.fossil.capsule/1"
RULER = vault.REPO / "roles" / "Harmonia" / "science" / "asal_ruler"
RUN = RULER / "out" / "run_2026-09-18"
HARM55_TORCH = vault.REPO / "techne" / "acquisition" / "poet_alife" / "HARM55_TORCH_ORIGINAL_2026-09-19.json"
RUNBOOK = "techne/acquisition/poet_alife/HARM55_RUNBOOK_AVX_HOST.md"

REQUIRED = ["schema", "specimen_id", "source_bodies", "lineage", "params", "initial_condition", "seed", "frames",
            "replay", "original_observer", "native_observer", "alive", "classification", "preservation_reason",
            "provenance", "relatives", "evidence", "observer_internals", "written_utc", "written_by"]
_HEX64 = lambda s: isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)


def lf_sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def capsule_path(specimen_id: str) -> pathlib.Path:
    return vault.specimen_dir(specimen_id) / "CAPSULE.json"


# --------------------------------------------------------------------------- validation
def validate(c: dict) -> list[str]:
    why = []
    if c.get("schema") != SCHEMA:
        return ["schema is %r, expected %r" % (c.get("schema"), SCHEMA)]
    for k in REQUIRED:
        if k not in c:
            why.append("missing field: %s" % k)
    if why:
        return why
    fr = c["frames"]
    for k in ("file", "sha256", "shape", "dtype", "sampling"):
        if k not in fr:
            why.append("frames lacks %s" % k)
    if not _HEX64(fr.get("sha256", "")):
        why.append("frames.sha256 is not sha256")
    rp = c["replay"]
    for k in ("instrument", "instrument_sha256_lf", "how"):
        if not rp.get(k):
            why.append("replay lacks %s (a host path alone is not a replay)" % k)
    for name in ("original_observer", "native_observer"):
        o = c[name]
        if o.get("status") == "PENDING":
            if name == "original_observer":
                why.append("original_observer may not be PENDING")
            if not o.get("how_to_obtain"):
                why.append("%s PENDING needs how_to_obtain" % name)
            continue
        if o.get("score") is None:
            why.append("%s has neither a score nor status PENDING" % name)
        ident = o.get("identity") or {}
        if o.get("score") is not None and not (ident.get("scorer") and (ident.get("weights_sha256") or ident.get("weights_files_sha256"))):
            why.append("%s carries a score without a scorer identity + weights hash (refused: a number with no scorer)" % name)
    if not isinstance(c["alive"], bool):
        why.append("alive must be bool")
    if not c["classification"].get("class") or not c["classification"].get("procedure"):
        why.append("classification needs class + procedure (which classifier, which thresholds)")
    if not c["preservation_reason"]:
        why.append("preservation_reason empty")
    pv = c["provenance"]
    for k in ("experiment", "rows_sha256_lf", "manifest_sha256_lf"):
        if not pv.get(k):
            why.append("provenance lacks %s" % k)
    if not isinstance(c["relatives"], list):
        why.append("relatives must be a list (empty is a statement)")
    for e in c["evidence"]:
        if "path" not in e or "sha256" not in e:
            why.append("evidence pointer lacks path or sha256")
    oi = c["observer_internals"]
    if oi.get("status") not in ("PRESENT", "NOT_CAPTURED"):
        why.append("observer_internals.status must be PRESENT or NOT_CAPTURED")
    if oi.get("status") == "PRESENT":
        for k in ("per_frame_max_similarity_to_earlier", "embedding_sha256_per_frame", "embeddings_file"):
            if k not in oi:
                why.append("observer_internals PRESENT lacks %s" % k)
    return why


def validate_against_record(c: dict) -> list[str]:
    """Cross-checks that need the record: the frame hash must equal the pinned artifact."""
    why = validate(c)
    try:
        rec = record.load(c["specimen_id"])
    except Exception as e:                       # noqa: BLE001
        return why + ["record.json unreadable: %s" % e]
    arts = rec.get("source_origin", {}).get("artifacts", [])
    pins = {a.get("sha256") for a in arts}
    if c["frames"]["sha256"] not in pins:
        why.append("frames.sha256 %s is not a pinned artifact of the record (%s)" % (c["frames"]["sha256"][:12], [p[:12] for p in pins if p]))
    return why


# --------------------------------------------------------------------------- observer internals (cheap; the fossil untouched)
def per_frame_internals(z: np.ndarray) -> dict:
    """asal_metrics.py:53 decomposed per frame: max cosine similarity to any EARLIER frame (row 0 = 0 by construction)."""
    k = np.tril(z @ z.T, k=-1)
    return {"per_frame_max_similarity_to_earlier": [float(x) for x in k.max(axis=-1)],
            "embedding_sha256_per_frame": [hashlib.sha256(np.ascontiguousarray(z[i].astype(np.float32)).tobytes()).hexdigest() for i in range(len(z))],
            "aggregation": "score = mean of the per-frame values (frame 0 contributes 0)"}


def compute_internals_original(specimen_id: str) -> dict:
    """Embed the specimen's own frames with the ORIGINAL observer (torch CLIP of techne107) and store the
    embeddings beside the record as evidence. Needs the isolated env (torch + clip)."""
    import sys
    sys.path.insert(0, str(vault.REPO / "techne" / "scripts"))
    import techne107_asal_observer as port
    import harm55_flax_score as h55
    rec = record.load(specimen_id)
    body = vault.body_dir(specimen_id) / "upstream" / rec["source_origin"]["artifacts"][0]["filename"]
    frames = np.load(body)
    obs = port.Observer()
    z = obs.embed(h55.frames_to_rgb224(frames))
    d = per_frame_internals(z)
    out = vault.specimen_dir(specimen_id) / "observer_internals"
    out.mkdir(exist_ok=True)
    f = out / "original_observer_embeddings.npz"
    np.savez_compressed(f, z=z.astype(np.float32))
    d.update({"status": "PRESENT", "observer": "original", "embeddings_file": str(f.relative_to(vault.REPO)).replace("\\", "/"),
              "embeddings_file_sha256": hashlib.sha256(f.read_bytes()).hexdigest(), "score_from_internals": float(np.mean(d["per_frame_max_similarity_to_earlier"]))})
    return d


# --------------------------------------------------------------------------- builder
def build_rollout_capsule(specimen_id: str, torch_json: dict, flax_json: dict | None, internals: dict | None, reason: str | None = None) -> dict:
    rec = record.load(specimen_id)
    ro = rec["rollout"]
    key = "%s_%s" % (ro["stage"], ro["idx"])
    art = rec["source_origin"]["artifacts"][0]
    trow = torch_json["rows"].get(key, {})
    tid = torch_json["identity"]
    original = {"score": trow.get("score_torch", ro.get("score_original")), "score_from_manifest": ro.get("score_original"),
                "identity": {"scorer": tid.get("scorer"), "torch": tid.get("torch"), "weights_sha256": tid.get("weights_sha256"),
                             "port_sha256_lf": tid.get("port_sha256_lf"), "preprocessing": tid["frames"]["contract"]},
                "crossings": trow.get("crossings_original"), "boundaries": torch_json.get("boundaries"), "d_clip": trow.get("d_clip_original")}
    if flax_json and key in flax_json.get("scores", {}):
        frow = flax_json["rows"].get(key, {})
        fid = flax_json["identity"]
        native = {"score": flax_json["scores"][key], "identity": {k: fid.get(k) for k in ("scorer", "jax", "jaxlib", "flax", "transformers", "model", "weights_files_sha256", "body_commit", "body_tree_sha256") if k in fid},
                  "crossings": frow.get("crossings_flax"), "d_clip": frow.get("d_clip_flax"), "class_rederived": frow.get("class_flax"),
                  "signed_diff_vs_original": frow.get("signed_diff"), "source_file": flax_json.get("_source_path")}
    else:
        native = {"status": "PENDING", "how_to_obtain": "%s (harm55_flax_score.py --path flax on an AVX host; HARM-55)" % RUNBOOK, "score": None, "identity": None}
    reg = RULER / "regen_frames128.py"
    port_path = vault.REPO / "techne" / "scripts" / "techne107_asal_observer.py"
    manifest = json.loads((RUN / "frames128_manifest.json").read_text(encoding="utf-8"))
    return {
        "schema": SCHEMA, "specimen_id": specimen_id, "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "written_by": "Techne[gandalf-a04f7c25] techne/fossils/capsule.py",
        "source_bodies": [{"specimen": "lenia-chan-2019", "role": "substrate reference + catalogue (animals.json)", "commit": "adfc542939266de7f4bb7ebb552e8499701ee107"},
                          {"specimen": "asal-sakana-2024", "role": "the objective (asal_metrics.py:53) the search optimised", "commit": "677ba0ea4d3b3ca78273c9906c6e84d2b1481ce7"}],
        "lineage": {"stage": ro["stage"], "meaning": {"S0": "catalogue lifeform with its own params", "S1": "random envelope draw", "S2": "local step from a stage-1/2 parent"}[ro["stage"]],
                    "relations": rec.get("lineage_relations", [])},
        "params": ro["params"], "initial_condition": {"ic": ro["ic"], "resolution": "IC-CAT:<code> = FIRST catalogue entry with that code (regen_frames128.py rule); IC-ORB = Orbium; IC-BLOB = the ruler's blob initialiser (asal_ruler.py)"},
        "seed": ro["seed"],
        "frames": {"file": art["filename"], "sha256": art["sha256"], "bytes": art.get("bytes"), "shape": manifest["shape"], "dtype": manifest["dtype"],
                   "sampling": "steps 0,32,...,224 of 256 (rollout.py time_sampling=(8, False)); uint8(clip(x,0,1)*255) of the 128x128 greyscale world",
                   "vault_location_on_this_host": str(vault.body_dir(specimen_id) / "upstream" / art["filename"]), "tree_sha256": rec["hashes"]["tree_sha256"]},
        "replay": {"instrument": "roles/Harmonia/science/asal_ruler/regen_frames128.py -> asal_ruler.py rollout on techne/scripts/techne107_asal_observer.py Lenia2D",
                   "instrument_sha256_lf": lf_sha256(reg) if reg.exists() else None, "port_sha256_lf": lf_sha256(port_path), "port_sha256_at_search": manifest.get("port_sha256"),
                   "how": "instantiate params + initial_condition on Lenia2D (128 world), step 256 with the recorded seed, sample 8 frames, uint8; the result must hash to frames.sha256 (Harmonia's controls C-TOP20 / C-TRAJ64 established determinism)"},
        "original_observer": original, "native_observer": native,
        "alive": bool(ro["alive"]),
        "classification": {"class": ro["class_original"], "procedure": "asal_ruler.py classify() on (coh, d_pix, mass_cv, d_clip) with thresholds.json (Orbium/HUECYCLE-derived), original observer",
                           "observables": {k: ro.get(k) for k in ("coh", "d_pix", "mass_cv", "disp", "d_clip_original")}, "class_under_native_observer": (native.get("class_rederived") if native.get("score") is not None else "PENDING")},
        "preservation_reason": reason or rec.get("preservation_reason"),
        "provenance": {"experiment": "Harmonia PREREG_ASAL_LEGIT_SEARCH_2026-09-18 (+ AMENDMENT_A), run_2026-09-18/search", "rows_sha256_lf": lf_sha256(RUN / "search" / "rows.jsonl"),
                       "manifest_sha256_lf": lf_sha256(RUN / "frames128_manifest.json"), "harm55_original_column": {"path": str(HARM55_TORCH.relative_to(vault.REPO)).replace("\\", "/"), "sha256_lf": lf_sha256(HARM55_TORCH)},
                       "packets": ["techne/fossils/specimens/asal-sakana-2024/FOSSIL_PACKET.json"], "directives": ["roles/Techne/prompts/2026-09-19_asal_direction/"]},
        "relatives": [{"specimen": "asal-rollout-%s" % k, "relation": rel} for k, rel in _relatives(key, torch_json)],
        "evidence": [{"what": "frames", "path": "vault body (gitignored); hash list techne/fossils/specimens/%s/UPSTREAM_HASHES.txt" % specimen_id, "sha256": art["sha256"]},
                     {"what": "search row", "path": "roles/Harmonia/science/asal_ruler/out/run_2026-09-18/search/rows.jsonl", "sha256": lf_sha256(RUN / "search" / "rows.jsonl")},
                     {"what": "frames manifest", "path": "roles/Harmonia/science/asal_ruler/out/run_2026-09-18/frames128_manifest.json", "sha256": lf_sha256(RUN / "frames128_manifest.json")}],
        "observer_internals": internals or {"status": "NOT_CAPTURED"},
    }


def _relatives(key: str, torch_json: dict) -> list[tuple[str, str]]:
    """Nearest preserved specimens by original score (the metric neighbourhood) and by observables (the
    behavioural neighbourhood) among rollouts that have capsules or records -- restricted to the preserved
    set so every relative is addressable."""
    rows = torch_json["rows"]
    preserved = [k for k in rows if (vault.specimen_dir("asal-rollout-%s" % k) / "record.json").exists() and k != key]
    if key not in rows or not preserved:
        return []
    me = rows[key]
    out = []
    by_score = sorted(preserved, key=lambda k: abs((rows[k]["score_original"] or 9) - (me["score_original"] or 9)))[:2]
    for k in by_score:
        out.append((k, "nearest preserved by original score (|d|=%.4f)" % abs(rows[k]["score_original"] - me["score_original"])))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--rollouts", action="store_true"); b.add_argument("--flax", default=None); b.add_argument("--internals", action="store_true"); b.add_argument("--write", action="store_true"); b.add_argument("--only", nargs="*", default=None)
    v = sub.add_parser("validate"); v.add_argument("--all", action="store_true"); v.add_argument("specimen_id", nargs="?")
    a = ap.parse_args(argv)
    if a.cmd == "validate":
        ids = [a.specimen_id] if a.specimen_id else sorted(p.parent.name for p in vault.SPECIMENS.glob("*/CAPSULE.json"))
        bad = 0
        for sid in ids:
            why = validate_against_record(json.loads(capsule_path(sid).read_text(encoding="utf-8")))
            print(sid, "VALID" if not why else "INVALID: " + "; ".join(why)); bad += bool(why)
        return 1 if bad else 0
    torch_json = json.loads(HARM55_TORCH.read_text(encoding="utf-8"))
    flax_json = None
    if a.flax:
        flax_json = json.loads(pathlib.Path(a.flax).read_text(encoding="utf-8")); flax_json["_source_path"] = a.flax
    ids = a.only or sorted(p.parent.name for p in vault.SPECIMENS.glob("asal-rollout-*/record.json"))
    for sid in ids:
        internals = compute_internals_original(sid) if a.internals else None
        c = build_rollout_capsule(sid, torch_json, flax_json, internals)
        why = validate_against_record(c)
        print("%-24s %s" % (sid, "VALID" if not why else "; ".join(why)))
        if a.write and not why:
            capsule_path(sid).write_text(json.dumps(c, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
