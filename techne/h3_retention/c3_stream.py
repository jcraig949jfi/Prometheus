"""Build the REAL H3 stream from Archaeon's cs-c3-2 corpus.

    python -m techne.h3_retention.c3_stream --out <candidates.json> --edges-out <edges.json>

Mapping: `roles/Techne/INBOX_ARCHAEON_C3_2_COMPLETE_2026-09-10.md`, implemented field for
field. Nothing here is inferred where the inbox states a rule.

    stream_id        campaign_c3.plan() `index` minus 1 (issue order)
    candidate_digest the row's spec_hash (sha256 over the sealed spec)
    birth_status     evaluated | failed, from the readout's outcome
    assay_ref        one string for the whole stream, given by the inbox
    score            mean of accuracy_stable over the four IC samples
    descriptors      (popcount of the 128-entry rule table,
                      count of output-1 entries among centre-1 neighbourhoods)
    byte_size        len(json.dumps(spec, sort_keys=True))
    replay_ref       sfe:<sfe_experiment_id>
    parent_ids       () -- C3 has no lineage

THE JOIN IS ON LABEL, not on position. `plan()` and the readout table carry the same 150
labels but NOT in the same order, so joining by index would silently pair each candidate's
spec with another candidate's score. That is the kind of error that produces a clean-looking
result about nothing, so the join key is the label and the builder asserts the label sets match
exactly before it pairs anything.

THE RULE-TABLE CONVENTION IS ARCHAEON'S, QUOTED: "bit k from the LEFT of the 32-hex string is
the output for neighbourhood index k, where k = sum cell[i+j] * 2^(3-j) over j = -3..3
(leftmost cell is the MSB of k). The centre cell is bit 3 of k (value 8)." The descriptors are
derived from that and from nothing else; a descriptor computed under a different bit order
would be a different descriptor wearing the same name.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

N_NEIGHBOURHOODS = 128
CENTRE_BIT = 3                       # Archaeon: the centre cell is bit 3 of the neighbourhood index
ASSAY_REF = "ca_density_v0@6d5d7406f:seed_root=930001:n_ic=100:steps=320:stable"


def rule_table(rule_hex: str) -> list[int]:
    """The 128 outputs, index k = neighbourhood index, per Archaeon's left-MSB convention."""
    if len(rule_hex) != 32:
        raise ValueError(f"expected 32 hex chars, got {len(rule_hex)}")
    n = int(rule_hex, 16)
    return [(n >> (N_NEIGHBOURHOODS - 1 - k)) & 1 for k in range(N_NEIGHBOURHOODS)]


def descriptors(rule_hex: str) -> tuple[float, float]:
    t = rule_table(rule_hex)
    popcount = sum(t)
    centre_one_ones = sum(t[k] for k in range(N_NEIGHBOURHOODS) if (k >> CENTRE_BIT) & 1)
    return float(popcount), float(centre_one_ones)


def _spec_hash(spec: dict) -> str:
    """Archaeon's canonical form. Their spec_hash delegates to Vivarium's when importable and
    falls back to a byte-identical local form; the fallback is reproduced here so this builder
    does not need the engine importable."""
    blob = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build(repo_root: pathlib.Path) -> tuple[list[dict], list[list[float]], dict]:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from archaeon.producer import campaign_c3 as C
    try:
        from archaeon.producer.specbuild import spec_hash as arch_spec_hash
    except Exception:
        arch_spec_hash = None

    readout = json.loads((repo_root / "archaeon" / "docs" / "h0h5" /
                          "C3_2_READOUT.json").read_text(encoding="utf-8"))
    if not readout.get("complete"):
        raise RuntimeError("the readout is not marked complete; refusing to build a stream from "
                           "a partial corpus")
    table = {r["label"]: r for r in readout["table"]}
    plan = C.plan()

    plan_labels = {r["label"] for r in plan}
    read_labels = set(table)
    if plan_labels != read_labels:
        raise RuntimeError(
            f"label sets differ: {len(plan_labels - read_labels)} only in plan, "
            f"{len(read_labels - plan_labels)} only in readout. The join is on LABEL, so a "
            f"mismatch would pair a spec with another candidate's score.")

    recs = []
    hash_source = "archaeon.producer.specbuild.spec_hash" if arch_spec_hash else "local canonical fallback"
    for p in sorted(plan, key=lambda r: r["index"]):
        row = table[p["label"]]
        spec = p["spec"]
        try:
            digest = arch_spec_hash(spec) if arch_spec_hash else _spec_hash(spec)
        except Exception:
            digest = _spec_hash(spec)
            hash_source = "local canonical fallback (Archaeon's raised)"
        failed = row["outcome"] not in ("FALSIFIED", "SURVIVED")
        recs.append({
            "stream_id": int(p["index"]) - 1,
            "candidate_digest": "sha256:" + digest if not digest.startswith("sha256:") else digest,
            "birth_status": "failed" if failed else "evaluated",
            "assay_ref": ASSAY_REF,
            "score": None if failed else float(row["mean"]),
            "descriptors": list(descriptors(p["rule_hex"])),
            "byte_size": len(json.dumps(spec, sort_keys=True)),
            "replay_ref": f"sfe:{row['sfe_experiment_id']}",
            "parent_ids": [],
            # carried for the report, not part of Archaeon's record shape
            "_label": p["label"], "_arm": p["arm_id"], "_rule_hex": p["rule_hex"],
            "_outcome": row["outcome"],
        })

    # Edges: declared here, once, and never learned. Quartiles of the OBSERVED descriptor range
    # would be learned from the data; instead the edges are fixed at the structurally meaningful
    # points of each axis -- popcount over 128 entries and output-1 count over the 64 centre-1
    # neighbourhoods -- so the same edges apply to any rule table of this shape.
    edges = [[32.0, 64.0, 96.0], [16.0, 32.0, 48.0]]

    scored = [r["score"] for r in recs if r["score"] is not None]
    from collections import Counter
    hist = Counter(scored)
    by_arm: dict[str, dict] = {}
    for r in recs:
        a = by_arm.setdefault(r["_arm"], {"n": 0, "zeros": 0, "failed": 0})
        a["n"] += 1
        if r["score"] == 0.0:
            a["zeros"] += 1
        if r["score"] is None:
            a["failed"] += 1
    meta = {
        "source": "archaeon/docs/h0h5/C3_2_READOUT.json + archaeon.producer.campaign_c3.plan()",
        "mapping": "roles/Techne/INBOX_ARCHAEON_C3_2_COMPLETE_2026-09-10.md",
        "join_key": "label (plan and readout share 150 labels in DIFFERENT order)",
        "spec_hash_source": hash_source,
        "rule_table_convention": ("bit k from the LEFT of the 32-hex string is the output for "
                                  "neighbourhood index k; the centre cell is bit 3 of k "
                                  "(Archaeon, campaign_c3 module docstring, re-earned by test)"),
        "declared_edges": edges,
        "edges_rationale": ("fixed at structurally meaningful points of each axis (128-entry "
                            "table, 64 centre-1 neighbourhoods), NOT at observed quantiles -- "
                            "quantile edges would be learned from the stream the archive is "
                            "about to retain from"),
        "n": len(recs),
        "n_failed": sum(1 for r in recs if r["score"] is None),
        "per_arm": by_arm,
        "n_exact_zero": sum(1 for s in scored if s == 0.0),
        "distinct_nonzero_scores": sorted({s for s in scored if s != 0.0}),
        "descriptor_ranges_observed": [
            [min(r["descriptors"][j] for r in recs), max(r["descriptors"][j] for r in recs)]
            for j in (0, 1)],
    }
    return recs, edges, meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=str(pathlib.Path(__file__).resolve().parents[2]))
    ap.add_argument("--out", required=True)
    ap.add_argument("--edges-out", required=True)
    ap.add_argument("--meta-out", default=None)
    a = ap.parse_args(argv)

    recs, edges, meta = build(pathlib.Path(a.repo_root))
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(recs, indent=1), encoding="utf-8")
    pathlib.Path(a.edges_out).write_text(json.dumps(edges), encoding="utf-8")
    if a.meta_out:
        pathlib.Path(a.meta_out).write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"built {meta['n']} candidates ({meta['n_failed']} failed) -> {a.out}")
    print(f"spec_hash via    {meta['spec_hash_source']}")
    print(f"exact zeros      {meta['n_exact_zero']} of {meta['n'] - meta['n_failed']} scored")
    print(f"distinct nonzero {meta['distinct_nonzero_scores']}")
    print(f"per arm          {meta['per_arm']}")
    print(f"descriptor range {meta['descriptor_ranges_observed']}  edges {edges}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
