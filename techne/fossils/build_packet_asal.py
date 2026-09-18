"""Build the FIRST executable fossil packet (operator directive 4 s5): asal-sakana-2024 on world
m3-native-python. Every Techne field is read from the record, the hash list, the world record and the
TECHNE-107 receipt -- nothing typed twice. Run: python -m techne.fossils.build_packet_asal [--write]"""
from __future__ import annotations

import argparse
import hashlib
import json
import time

from techne.fossils import packet, record, vault

SID = "asal-sakana-2024"


def lf_sha256(path) -> str:
    return hashlib.sha256(open(path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()


def _executor_acceptance() -> dict:
    """Exact accepted/refused counts of the numpy Lenia port over the pinned catalogue (rule A4)."""
    p = vault.REPO / "techne" / "acquisition" / "poet_alife" / "PORT_ACCEPTANCE_2026-09-18.json"
    if not p.exists():
        return {"status": "NOT_MEASURED"}
    d = json.loads(p.read_text(encoding="utf-8"))
    return {"executor": "techne/scripts/techne107_asal_observer.py Lenia2D (numpy port; NOT the body's substrates/lenia.py)",
            "catalogue": d["catalogue"], "accepted": d["accepted"], "refused": d["refused"], "refusal_reasons": d["refusal_reasons"],
            "supports": d["port"]["supports"], "receipt": "techne/acquisition/poet_alife/PORT_ACCEPTANCE_2026-09-18.json",
            "receipt_sha256_lf": lf_sha256(p)}


def build() -> dict:
    rec = record.load(SID)
    sd = vault.specimen_dir(SID)
    hashes = rec["hashes"]
    world = json.loads((vault.REPO / "techne" / "fossils" / "worlds" / "m3-native-python.json").read_text(encoding="utf-8"))
    reg = packet.worlds_registry()["worlds"]["m3-native-python"]
    receipt_rel = "techne/acquisition/poet_alife/TECHNE107_RECEIPT_2026-09-17.json"
    rcpt = json.loads((vault.REPO / receipt_rel).read_text(encoding="utf-8"))
    arts = rec["source_origin"]["artifacts"]
    lenia_animals = vault.body_dir("lenia-chan-2019") / "upstream" / "tree" / "Python" / "animals.json"
    lenia_animals_sha = hashlib.sha256(lenia_animals.read_bytes()).hexdigest() if lenia_animals.exists() else "BODY_MISSING_ON_THIS_HOST"
    git = next(a for a in arts if a["kind"] == "git")
    npz = [a for a in arts if a["kind"] == "url"]
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return {
        "schema": packet.SCHEMA, "specimen_id": SID, "pipeline_id": "MECHANISM_ARCHAEOLOGY", "written_utc": now,
        "written_by": "Techne[gandalf-a04f7c25] (M3)", "amendment": "Founding Charter + Amendments 1-3; operator directive 4 s5 (executable fossil packet)",
        "FOSSIL_RAW_ID": {"tree_sha256": hashes["tree_sha256"], "n_files": hashes["n_files"],
                          "git": {"url": git["url"], "commit": git["commit_resolved"], "commit_date": git.get("commit_date")},
                          "hash_list": "techne/fossils/specimens/%s/UPSTREAM_HASHES.txt" % SID,
                          "host_stability": "M3 body acquired and verified 2026-09-18 (harvest acquire + verify); no second host yet"},
        "PAYLOAD_MANIFEST_ID": lf_sha256(sd / "UPSTREAM_HASHES.txt"),
        "PAYLOAD_MANIFEST_ID_basis": "sha256 over the LF-normalised bytes of UPSTREAM_HASHES.txt (equals the git blob; R36 encoding rule applied to the manifest, not to the body)",
        "PROVENANCE_GRADE": [
            {"artifact": "github.com/SakanaAI/asal @ %s" % git["commit_resolved"][:12], "grade": "ORIGINAL_ARTIFACT",
             "basis": "the authors' own repository at a pinned commit; the code as the authors published it", "edges": ["PACKAGES ASAL as released 2024-12 .. 2025-10"]}]
            + [{"artifact": a["filename"], "grade": "ORIGINAL_ARTIFACT", "basis": "served by the authors' host pub.sakana.ai; sha256 %s, %s bytes" % (a["sha256"], a["bytes"]),
                "edges": ["DATA the simulations the paper's illumination/sweep figures were drawn from (per README)"]} for a in npz],
        "FOSSIL_WORLD_ID": world["FOSSIL_WORLD_ID"],
        "FOSSIL_WORLD": {"name": "m3-native-python", "class": "native_python", "manifest": "techne/fossils/worlds/m3-native-python.manifest.json",
                         "interpreter": world["manifest"]["interpreter"], "n_packages": len(world["manifest"]["packages"]),
                         "note": "R36 identity: sha256 of the canonical manifest; NOT the JAX world the body's own path needs (jaxlib requires AVX, absent on M3)"},
        "RUNTIME_WITNESS": world["runtime_witnesses"][0],
        "HOST_CAPS_ID": {"host": "GANDALF (M3)", "cpus": 8, "ram_gb": 24, "container_runtime": "none (no virtualization in firmware)", "cpu_flags": "no AVX", "kernel": "Windows 10 Home 19045"},
        "CAPABILITY_MATRIX": reg["capabilities"],
        "SCAFFOLDING_LEDGER": {"applied": [], "measured_and_rejected": [],
                               "note": "the body is untouched; the demonstration below runs a PORT beside it (a derived artifact, not a scaffold on the body)"},
        "INSTRUMENT_CONTROLS": [
            {"control_id": "TECHNE107-P1", "kind": "positive", "construction": "STATIC arm: one frame repeated 8x must score exactly (T-1)/T = 0.8750", "result": rcpt["predictions"]["P1_static_equals_0.8750"]},
            {"control_id": "TECHNE107-CHEAT", "kind": "cheat", "construction": "8 identical images passed as 8 distinct frames through the full pipeline must score 0.8750", "result": rcpt["controls"]["cheat_8_identical_images"]}],
        "TECHNE_STATE": "BODY_RECOVERED_WORLD_NAMED",
        "TECHNE_STATE_BASIS": "body pinned and hash-verified on M3; its own JAX execution path cannot run here (no AVX); the world in which it would run (JAX + CLIP) is NAMED by requirements.txt, not reconstructed. What WAS executed on m3-native-python is a numpy/torch port of asal_metrics.py:53 + CLIP (techne/scripts/techne107_asal_observer.py), recorded in the receipt below and declared as runs_the_body=false.",
        "BEHAVIOR_EVIDENCE": None,
        "REQUIRED_STATE_FOR_HANDOFF": "BODY_RECOVERED_WORLD_NAMED",
        "REQUIRED_STATE_BASIS": "Nyx's ASAL cut (#379 3d, operator directive 4 s2) is function-level reading of asal_metrics.py plus a numpy prediction packet; that needs the body and a named world, not an executing JAX path. Harmonia's calibration fixture is the receipt's seven-arm CLIP values.",
        "TECHNE_RUN_RECEIPTS": [receipt_rel],
        "PRESERVATION": {"copies": [{"object": "body tree %s + 3 npz" % hashes["tree_sha256"][:12], "location_class": "host-local vault (C:/Prometheus/vault/fossils, GANDALF)", "failure_domain": "M3",
                                     "verification_time": now, "verification_result": "VERIFIED", "artifact": "harvest verify 2026-09-18 (journal)"}],
                         "note": "one host; re-fetchable from origin by commit + npz sha256; the Google Drive mirror is TECHNE-100 (operator)"},
        "PRESERVATION_STATUS": "PRESERVATION_GATE_OPEN",
        "HANDOFF": {
            "runtime": rec["runtime"],
            # rule A4 (Harmonia STANDING_RULES, operator review 2026-09-18): the EXECUTOR's accepted subdomain, exact counts
            "executor": _executor_acceptance(),
            "entry_point": {"path": "asal_metrics.py", "symbol": "calc_open_endedness_score(z)", "also": ["rollout.py rollout_simulation", "foundation_models/clip.py CLIP.embed_img", "substrates/lenia.py"]},
            "demonstration": {"command": "<isolated-env python> techne/scripts/techne107_asal_observer.py --out receipt.json --frames frames/   (pattern file resolved from the vault specimen lenia-chan-2019, never from a temp path; Harmonia #429)",
                              "observable": "seven per-arm scores of the open-endedness metric through CLIP ViT-B/32 (lower = more open-ended) + two controls; 56 s on M3",
                              "runs_the_body": False,
                              "what_it_runs_instead": "a numpy port of asal_metrics.py:53 and a torch CLIP with the same weights (sha256 40d36571..950af); Lenia from Chakazul/Lenia@adfc5429, not substrates/lenia.py",
                              "claims": "none",
                              "reference_values": {k: v for k, v in rcpt["arms"].items() if "seed" not in k}},
            "license_constraints": {"spdx": "Apache-2.0", "constraints": ["NOTICE/attribution on redistribution", "datasets carry no separate licence statement (recorded, not assumed)"]},
            "preservation_cost": {"class": "CHEAP", "basis": "46 MB body incl. datasets; re-fetchable by commit and sha256 while github.com and pub.sakana.ai serve; illumination_lenia.npz already 404 (2026-09-17), which is the reason to mirror now"},
            "fixtures": [{"name": a["filename"], "path_or_url": a["url"], "sha256": a["sha256"], "bytes": a["bytes"]} for a in npz]
                        + [{"name": "TECHNE-107 seven-arm CLIP values (Harmonia calibration/cheat fixture)", "path_or_url": receipt_rel, "sha256": lf_sha256(vault.REPO / receipt_rel)},
                           {"name": "Lenia lifeform catalogue animals.json (Orbium O2u)", "path_or_url": "vault specimen lenia-chan-2019 (Chakazul/Lenia@adfc5429) upstream/tree/Python/animals.json",
                            "sha256": lenia_animals_sha, "specimen": "lenia-chan-2019"}]},
        "CUT_ID": None, "NYX_PREDICTION_PACKET": None, "ORACLE_SOURCES": None, "ORACLE_PROVENANCE_GRADES": None,
        "HARMONIA_SURROGATE_ID": None, "EQUIVALENCE_RESULT": None, "DIVERGENCE_LEDGER": None, "TEST_WORLD_ID": None,
        "PRESSURE_ID": None, "INTERVENTION_ID": None, "TENSOR_ADMISSION_RESULT": None, "PAYLOAD_READING_NULL": None, "FINAL_DISPOSITION": None,
        "downstream_owners": packet.DOWNSTREAM, "HANDOFF_REQUESTED": True,
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); a = ap.parse_args()
    p = build()
    why = packet.validate(p)
    print("validate:", "VALID" if not why else "; ".join(why))
    if a.write and not why:
        out = packet.packet_path(SID)
        out.write_text(json.dumps(p, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("wrote", out)


if __name__ == "__main__":
    main()
