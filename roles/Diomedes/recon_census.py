"""Diomedes recon census — the rows behind RECON_2026-08-24_navigational_information.md §C.

Read-only. Streams a stratified sample of theseus/corpus and reports, per
(generator_id, claim_kind) cell, what fraction of records carry:

  * a parent link          -> the domain x of a transition
  * a named action         -> the action a
  * both                   -> a reconstructable named edge (x, a, x')

Also characterises `step_trace`, which is the corpus's only trajectory-shaped
field, and h1's counterexample-hunt success/failure split.

Corpus-wide shares must be taken from ergon/probe/ledgers/corpus_scan/full_scan.json
(Ergon's 165/165-file scan). This sample over-represents edge-bearing cells --
its parent share is 50.0% against the full scan's authoritative 36.61% -- so only
the PER-CELL classifications here are exact. See §C.5 of the report.

    python roles/Diomedes/recon_census.py
"""
import collections
import glob
import gzip
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS = ROOT / "theseus/corpus"
OUT = pathlib.Path(__file__).resolve().parent / "recon_census.json"

# Payload keys that name a transformation applied to reach this record's state.
ACTION_KEYS = {
    "operator", "operator_f", "operator_g", "scale_factor", "original_relation",
    "hunter_varied_side", "n_applications", "polynomial_degree", "mutation",
    "varied_side",
}
N_FILES = 10          # stratified stride over the batch files
MAX_LINES = 40_000    # per file


def main():
    files = sorted(glob.glob(str(CORPUS / "batch-*.jsonl.gz")))
    if not files:
        raise SystemExit(f"no batch files under {CORPUS}")
    idx = [int(len(files) * k / N_FILES) for k in range(N_FILES)]

    tot = 0
    cells = collections.Counter()
    c_parent = collections.Counter()
    c_action = collections.Counter()
    c_both = collections.Counter()
    step_kind = collections.Counter()
    step_method = collections.Counter()
    step_input_varies = collections.Counter()
    h1_success = collections.Counter()
    h1_side = collections.Counter()

    for i in idx:
        f = files[min(i, len(files) - 1)]
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            for j, line in enumerate(fh):
                if j >= MAX_LINES:
                    break
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                tot += 1
                cell = f"{d.get('generator_id') or '?'}/{d.get('claim_kind') or '?'}"
                cells[cell] += 1
                payload = d.get("claim_payload") or {}

                has_action = bool(ACTION_KEYS & set(payload))
                has_parent = bool(d.get("parent_record_id")) or "parent_record_id" in payload
                if has_parent:
                    c_parent[cell] += 1
                if has_action:
                    c_action[cell] += 1
                if has_parent and has_action:
                    c_both[cell] += 1

                trace = d.get("step_trace")
                if trace:
                    keysets = []
                    for s in trace:
                        step_kind[s.get("step_kind")] += 1
                        step_method[s.get("step_method")] += 1
                        si = s.get("step_input") or {}
                        # everything except the RNG seed
                        keysets.append(tuple(sorted(
                            (k, str(v)) for k, v in si.items() if k != "child_seed"
                        )))
                    step_input_varies[
                        "identical_ignoring_seed" if len(set(keysets)) == 1 else "varies"
                    ] += 1

                if d.get("generator_id") == "h1":
                    h1_success[str(payload.get("hunter_success"))] += 1
                    h1_side[str(payload.get("hunter_varied_side"))] += 1

    report = {
        "scope": f"{N_FILES} stratified files of {len(files)}, <={MAX_LINES} lines each",
        "sampled_records": tot,
        "n_cells": len(cells),
        "share_parent": round(sum(c_parent.values()) / tot, 4),
        "share_named_action": round(sum(c_action.values()) / tot, 4),
        "share_full_named_edge": round(sum(c_both.values()) / tot, 4),
        "authoritative_full_scan_parent_share": 0.3661,
        "sample_is_edge_enriched": True,
        "per_cell": {
            c: {
                "n": n,
                "parent": round(c_parent[c] / n, 4),
                "action": round(c_action[c] / n, 4),
                "both": round(c_both[c] / n, 4),
            }
            for c, n in cells.most_common()
        },
        "step_trace": {
            "step_kind": dict(step_kind),
            "step_method": dict(step_method),
            "input_variation": dict(step_input_varies),
        },
        "h1_hunts": {"success": dict(h1_success), "varied_side": dict(h1_side)},
    }
    OUT.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"sampled {tot:,} records, {len(cells)} cells -> {OUT}")
    print(f"  parent {report['share_parent']:.1%}  "
          f"action {report['share_named_action']:.1%}  "
          f"full named edge {report['share_full_named_edge']:.1%}")
    print(f"  step_kind: {dict(step_kind)}")


if __name__ == "__main__":
    main()
