"""Preserve ASAL-search rollouts as first-class fossils (operator directive 2026-09-19 s6).

A rollout fossil = one specimen `asal-rollout-<stage>_<idx>` whose body is the DELIVERED 128x128 uint8
frame file (artifact kind 'file', pinned by Harmonia's manifest sha256, copied never moved), and whose
record carries the rollout's identity (params, initial condition, seed, stage, index), Harmonia's alive /
class / original score, the run it came from (rows.jsonl + manifest blob identities), and the REASON it
was preserved (which of the directive's categories). Nothing is re-simulated; nothing is re-scored.

Usage:
  python -m techne.fossils.preserve_rollouts --keys S2_135 S2_103 --reason "genuine organism with very low score" [--write] [--acquire]
  python -m techne.fossils.preserve_rollouts --from-json selection.json [--write] [--acquire]
     (selection.json = {"<key>": "<reason>", ...})
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess

from techne.fossils import harvest, record, vault

RULER = vault.REPO / "roles" / "Harmonia" / "science" / "asal_ruler" / "out" / "run_2026-09-18"
MANIFEST = RULER / "frames128_manifest.json"
ROWS = RULER / "search" / "rows.jsonl"

REASONS = ("strongest cross-observer disagreement", "genuine organism with very low score",
           "exploit case with ordinary native-ASAL score", "catalogue member crossing one threshold but not another",
           "nearest behavioural pair with sharply different metric values", "nearest metric-score pair with sharply different behaviours",
           "deepest search witness", "other (state it)")


def _blob_sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def build_record(key: str, reason: str, man: dict, rows: dict) -> dict:
    m = man["rollouts"][key]
    r = rows.get(key, {})
    stage, idx = key.split("_", 1)
    params = r.get("params")
    sid = "asal-rollout-%s" % key
    rec = record.skeleton(sid,
        canonical_name="ASAL legitimate-search rollout %s (Harmonia run_2026-09-18, stage %s index %s)" % (key, stage, idx),
        aliases=[key, "IC %s" % r.get("ic")],
        lineage="a Lenia rollout executed by Harmonia's asal_ruler on Techne's numpy Lenia port (techne107_asal_observer.py) during the preregistered legitimate-search experiment (PREREG_ASAL_LEGIT_SEARCH_2026-09-18 + AMENDMENT_A); frames preserved as delivered for HARM-55",
        domain=["artificial-life", "lenia", "asal", "rollout-fossil", "observer-comparison"], era="2026-09-18",
        version="run_2026-09-18/search key %s; frames128 manifest %s" % (key, m["sha256"][:12]),
        source_origin={"artifacts": [{"kind": "file", "source_path": str(pathlib.Path(man["dest"]) / (key + ".npy")), "filename": key + ".npy", "sha256": m["sha256"]}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
        source_identity={"run": "roles/Harmonia/science/asal_ruler/out/run_2026-09-18/search", "rows_jsonl_sha256_lf": _blob_sha(ROWS), "frames128_manifest_sha256_lf": _blob_sha(MANIFEST),
                         "regenerated_by": "roles/Harmonia/science/asal_ruler/regen_frames128.py (controls C-TOP20, C-TRAJ64 pass)", "port_sha256": man.get("port_sha256")},
        license={"spdx": "Prometheus-internal (Techne port MIT-compatible; Lenia catalogue MIT)", "status": "internal data", "evidence": "produced by this programme's instruments"},
        language=["numpy uint8 array"], build_system="none", compiler_or_interpreter="n/a",
        dependencies=[], entry_points=["<key>.npy: (8,128,128) uint8 greyscale frames at steps 0,32,...,224"],
        example={"command": "python -c \"import numpy as np; a=np.load('%s.npy'); print(a.shape, a.dtype)\"" % key, "input": "the frame file", "output": "(8, 128, 128) uint8"},
        environment={"runner": "native"},
        runtime={"python_major": 3, "native_deps": ["numpy"], "host_class": "any"},
        upstream_docs=["roles/Harmonia/science/asal_ruler/PREREG_ASAL_LEGIT_SEARCH_2026-09-18.md", "techne/acquisition/poet_alife/TECHNE107_RESULTS_2026-09-17.md"],
        human_capability_summary={"built_to": "n/a (a preserved rollout)", "pressure": "n/a", "success_means": "n/a"},
        known_human_problem_solved="n/a",
        rollout={"stage": stage, "idx": idx, "ic": r.get("ic"), "seed": r.get("seed"), "params": params, "alive": m["alive"], "class_original": m["class"],
                 "score_original": m.get("score_torch"), "coh": r.get("coh"), "d_pix": r.get("d_pix"), "d_clip_original": r.get("d_clip"), "mass_cv": r.get("mass_cv"),
                 "disp": r.get("disp"), "mass": r.get("mass")},
        preservation_reason=reason,
        lineage_relations=[{"relation": "derived_from", "target": "lenia-chan-2019", "note": "pattern and parameters from the catalogue (S0) or a mutated descendant of one (S1/S2)"},
                           {"relation": "derived_from", "target": "asal-sakana-2024", "note": "the objective the search optimised (asal_metrics.py:53) through the observer of TECHNE-107"}],
        acquisition_tags=["operator-directive-2026-09-19", "poet_alife", "HARM-55", "rollout-fossil"])
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", nargs="*", default=[]); ap.add_argument("--reason", default=None)
    ap.add_argument("--from-json", default=None); ap.add_argument("--write", action="store_true"); ap.add_argument("--acquire", action="store_true")
    a = ap.parse_args()
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = {"%s_%s" % (r["stage"], r["idx"]): r for r in (json.loads(l) for l in open(ROWS, encoding="utf-8")) if "error" not in r}
    sel = json.loads(pathlib.Path(a.from_json).read_text(encoding="utf-8")) if a.from_json else {k: a.reason for k in a.keys}
    if not sel or any(v is None for v in sel.values()):
        raise SystemExit("every key needs a reason (one of: %s)" % "; ".join(REASONS))
    for key, reason in sel.items():
        if key not in man["rollouts"]:
            print(key, "NOT IN MANIFEST -- skipped"); continue
        rec = build_record(key, reason, man, rows)
        probs = record.validate(rec)
        exists = (vault.specimen_dir(rec["specimen_id"]) / "record.json").exists()
        print("%-24s %s%s" % (rec["specimen_id"], "OK" if not probs else "; ".join(probs), "  [EXISTS: not rewritten]" if exists else ""))
        if a.write and not probs and not exists:
            record.save(rec)
            if a.acquire:
                out = harvest.acquire(rec["specimen_id"])
                print("   acquired tree", out.get("tree_sha256", "?")[:16], "n_files", out.get("n_files"))


if __name__ == "__main__":
    main()
