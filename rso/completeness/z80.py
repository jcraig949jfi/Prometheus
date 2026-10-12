"""C-018-T011 Z80 wrapper: verify the six confirmatory shards, THEN run the frozen C-017 analyzer (rso/z80/analysis.py, untouched).

    python -m rso.completeness.z80 rso/z80/runs/CONFIRM.*-6.jsonl.gz     verify, then print {completeness, analysis} JSON
    python -m rso.completeness.z80 build-manifest [--write]            re-derive the manifest from PREREGISTRATION s6 + the shards

exit 0 COMPLETE, 3 INCOMPLETE, 4 REFUSED (no analysis is computed unless the verdict is licensed).
The manifest is DERIVED, not read off the rows: seeds / per-shard row counts come from the preregistered design
(subjects.seeds = PREREGISTRATION s6, assay.run's shard rule `(arm index + k) % shards`, assay.CONFIRM_N, assay.N_FORGE,
assay.FORGERIES); only the artifact digests come from the committed shards. A test asserts build_manifest() == the committed file.
This module is a NEW analyzer version ("z80-complete 1.0.0"); rso/z80/ is not edited (C-017's frozen result does not change).
"""
import glob
import gzip
import json
import os
import sys

from rso.completeness import manifest as M, verify as V
from rso.registry.registry import ROOT, file_sha
from rso.slice001.receipt import sha256_hex as native_digest

ANALYZER = "rso.completeness.z80 1.0.0 (wraps rso.z80.analysis, frozen v1.1.0, unmodified)"
RUNS = os.path.join(ROOT, "rso", "z80", "runs")
MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifests", "z80_confirm.manifest.json")
PINNED_MANIFEST_SHA256 = "8d0f9caa1c08c0401cc3cc41636ea6ec20d1fb792ab3daff46b3d541d0175355"   # sha of manifests/z80_confirm.manifest.json (build-manifest)
K = 6                                                                 # PREREGISTRATION s9: shards i/6, i = 0..5


def shard_paths(runs=RUNS):
    return sorted(glob.glob(os.path.join(runs, "CONFIRM.*-%d.jsonl.gz" % K)))


def _load_one(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    with open(path[:-len(".jsonl.gz")] + ".meta.json", encoding="utf-8") as f:
        meta = json.load(f)
    return {"id": "%s.%d-%d" % (meta["mode"].upper(), meta["shard"][0], meta["shard"][1]), "rows": rows, "meta": meta}


def load_shards(paths):
    return [_load_one(p) for p in paths]


def expected_design():
    """{shard id: (seeds, {key: n})} from the preregistered design, with no look at any row."""
    from rso.z80 import assay, subjects as S
    out = {i: (set(), {}) for i in range(K)}
    for idx, arm in enumerate(S.ARMS):
        for k, sd in enumerate(S.seeds(arm["name"], "confirm", assay.CONFIRM_N.get(arm["name"], 24))):
            i = (idx + k) % K
            out[i][0].add(sd)
            keys = [arm["name"] + "|"]
            keys += ["%s|%s" % (arm["name"], kind) for kind, src in assay.FORGERIES.items()
                     if arm["name"] in (src if isinstance(src, tuple) else (src,)) and k < assay.N_FORGE]
            for key in keys:
                out[i][1][key] = out[i][1].get(key, 0) + 1
    return {"CONFIRM.%d-%d" % (i, K): v for i, v in out.items()}


def build_manifest(runs=RUNS):
    from rso.z80 import subjects as S
    design = expected_design()
    specs = []
    for sh in load_shards(shard_paths(runs)):
        seeds, counts = design[sh["id"]]
        specs.append({"id": sh["id"], "seeds": sorted(seeds), "arm_counts": counts, "rows": sum(counts.values()),
                      "rows_sha256": M.digest(sh["rows"]), "meta_sha256": M.digest(sh["meta"])})
    with open(os.path.join(ROOT, "rso", "z80", "FROZEN.json"), encoding="utf-8") as f:
        frozen = json.load(f)
    sources = dict(frozen["files"])
    sources["rso/z80/FROZEN.json"] = file_sha("rso/z80/FROZEN.json", ROOT)
    return M.build("C-017 Z80 attribution confirmatory (PREREGISTRATION v1.1.0 s6, s9)", arms=S.NAMES, shards=specs, sources=sources,
                   row_key_fields=["arm", "forgery"])


def committed_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def current_sources(manifest):
    return {p: file_sha(p, ROOT) for p in manifest["sources"] if os.path.exists(os.path.join(ROOT, p))}


def verify_set(manifest, shards, sources):
    return V.verify(manifest, shards, sources=sources, native_digest=native_digest, pinned_manifest_sha256=PINNED_MANIFEST_SHA256)


def analyse(paths):
    manifest = committed_manifest()
    shards = load_shards(paths)
    res = verify_set(manifest, shards, current_sources(manifest))
    out = {"analyzer": ANALYZER, "completeness": res.to_dict()}
    if res.licenses_verdict:
        from rso.z80 import analysis
        rows = [r for sh in sorted(shards, key=lambda s: s["id"]) for r in sh["rows"]]
        out["analysis"] = analysis.verdict(rows)
    return out


def main(argv):
    if argv and argv[0] == "build-manifest":
        m = build_manifest()
        if "--write" in argv:
            os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
            with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(m, indent=1, sort_keys=True) + "\n")
        print(m["manifest_sha256"])
        return 0
    out = analyse(argv or shard_paths())
    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    return {V.COMPLETE: 0, V.COMPLETE_EARLY_STOP: 0, V.INCOMPLETE: 3}.get(out["completeness"]["status"], 4)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
