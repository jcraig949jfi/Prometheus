"""Full-corpus scan of the native failure residue — the 165-batch version of the 6-batch
sample in CORPUS_CHARACTERIZATION_FOR_R2-6_2026-08-22.md.

The sample produced a claim large enough that it should not rest on 6 of 165 files: that
`kill_pattern` never crosses a (generator_id, claim_kind) cell, which if true corpus-wide says
there is little cross-generator transfer for D2/D3 to measure at all.

Streams line by line — the corpus is 346 GB and must never be loaded. Writes partial results
after every file, so a kill loses at most one file's work and the run is resumable. Read-only:
opens nothing outside theseus/corpus/ and writes only its own output.

    python ergon/probe/corpus_scan_full.py
"""
import collections
import json
import math
import os
import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS = ROOT / "theseus/corpus"
OUT = ROOT / "ergon/probe/ledgers/corpus_scan"
GEN_PREFIX = re.compile(r"^[a-z]\d+_")
TOKEN_SPLIT = re.compile(r"[_=<>\-\s]+")


def tokens(kp):
    return {t for t in TOKEN_SPLIT.split(GEN_PREFIX.sub("", kp)) if t and not t.isdigit()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    state_path = OUT / "scan_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    done = set(state.get("files_done", []))

    kp_counts = collections.Counter(state.get("kp_counts", {}))
    cell_counts = collections.Counter({tuple(k.split("\x1f")): v
                                       for k, v in state.get("cell_counts", {}).items()})
    # kill_pattern -> set of cells it appears in (the claim under test)
    # JOINT counts (cell -> pattern -> n). The previous version kept only marginals and
    # then built each cell's conditional distribution from patterns EXCLUSIVE to that cell —
    # dropping every crossing pattern, i.e. exactly the evidence that would refute "the cell
    # determines the failure mode". ATK-014 (Techne): on a synthetic corpus where 66.7% of
    # records carry a crossing pattern, ground truth H(kp|cell)=0.9183 and the estimator
    # reported 0.0000. It was correct only while crossing was 0 — and crossing is 0 only
    # because raw kill_pattern embeds generator_id, which my own §3c called a tautology.
    joint = collections.defaultdict(collections.Counter)
    for k, v in state.get("joint", {}).items():
        joint[tuple(k.split(""))] = collections.Counter(v)
    joint_proj = collections.defaultdict(collections.Counter)
    for k, v in state.get("joint_proj", {}).items():
        joint_proj[tuple(k.split(""))] = collections.Counter(v)
    kp_cells = collections.defaultdict(set)
    for k, v in state.get("kp_cells", {}).items():
        kp_cells[k] = {tuple(c.split("\x1f")) for c in v}
    cell_vocab = collections.defaultdict(set)
    for k, v in state.get("cell_vocab", {}).items():
        cell_vocab[tuple(k.split("\x1f"))] = set(v)
    totals = collections.Counter(state.get("totals", {}))

    files = sorted(CORPUS.glob("batch-*.jsonl"))
    todo = [f for f in files if f.name not in done]
    print(f"{len(files)} batch files, {len(todo)} remaining", flush=True)

    t0 = time.time()
    for n, f in enumerate(todo, 1):
        try:
            with f.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"REJECTED"' not in line:      # cheap prefilter before json.loads
                        totals["skipped_fast"] += 1
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        totals["unparseable"] += 1
                        continue
                    totals["records"] += 1
                    if d.get("verdict") != "REJECTED":
                        continue
                    totals["rejected"] += 1
                    kp = str(d.get("kill_pattern"))[:120]
                    cell = (str(d.get("generator_id")), str(d.get("claim_kind")))
                    kp_counts[kp] += 1
                    cell_counts[cell] += 1
                    kp_cells[kp].add(cell)
                    joint[cell][kp] += 1
                    joint_proj[cell][GEN_PREFIX.sub("", kp)] += 1
                    cell_vocab[cell] |= tokens(kp)
                    if d.get("step_trace"):
                        totals["with_step_trace"] += 1
                    if d.get("parent_record_id"):
                        totals["with_parent"] += 1
        except Exception as e:                        # a bad file must not kill the scan
            totals["file_errors"] += 1
            print(f"  !! {f.name}: {type(e).__name__}", flush=True)
        done.add(f.name)

        state = {
            "files_done": sorted(done),
            "kp_counts": dict(kp_counts),
            "cell_counts": {"\x1f".join(k): v for k, v in cell_counts.items()},
            "kp_cells": {k: ["\x1f".join(c) for c in v] for k, v in kp_cells.items()},
            "cell_vocab": {"\x1f".join(k): sorted(v) for k, v in cell_vocab.items()},
            "joint": {chr(31).join(c): dict(v) for c, v in joint.items()},
            "joint_proj": {chr(31).join(c): dict(v) for c, v in joint_proj.items()},
            "totals": dict(totals),
        }
        tmp = state_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        os.replace(tmp, state_path)
        if n % 5 == 0 or n == len(todo):
            el = time.time() - t0
            print(f"  [{n}/{len(todo)}] {f.name[:34]} · rejected={totals['rejected']:,} · "
                  f"cells={len(cell_counts)} · patterns={len(kp_counts)} · {el/60:.1f}m",
                  flush=True)

    # ---- the claim under test, corpus-wide
    crossing = {k: v for k, v in kp_cells.items() if len(v) > 1}
    n_rej = max(1, totals["rejected"])
    H = -sum((c / n_rej) * math.log2(c / n_rej) for c in kp_counts.values() if c)
    def _cond(jnt):
        """H(X|Y) = sum_y P(y) H(X|Y=y), over the ACTUAL within-cell distribution. No filter
        may mention the quantity under test (ATK-014 generalization)."""
        acc = 0.0
        for cell, sub in jnt.items():
            tot = sum(sub.values())
            if tot:
                acc += (tot / n_rej) * (
                    -sum((c / tot) * math.log2(c / tot) for c in sub.values()))
        return acc

    cond = _cond(joint)
    cond_proj = _cond(joint_proj)
    proj_marg = collections.Counter()
    for sub in joint_proj.values():
        proj_marg.update(sub)
    n_proj = max(1, sum(proj_marg.values()))
    H_proj = -sum((c / n_proj) * math.log2(c / n_proj) for c in proj_marg.values() if c)
    cells = sorted(cell_vocab)
    pairs = [(len(cell_vocab[a] & cell_vocab[b]) / max(1, len(cell_vocab[a] | cell_vocab[b])),
              a, b) for i, a in enumerate(cells) for b in cells[i + 1:]]
    zero = sum(1 for j, _, _ in pairs if j == 0)

    result = {
        "scope": f"FULL CORPUS — {len(done)} of {len(files)} batch files",
        "rejected_records": totals["rejected"],
        "distinct_kill_patterns": len(kp_counts),
        "distinct_cells": len(cell_counts),
        "kill_patterns_crossing_a_cell": len(crossing),
        "kill_patterns_crossing_examples": {k: ["/".join(c) for c in sorted(v)]
                                            for k, v in list(crossing.items())[:10]},
        "records_under_crossing_patterns": sum(kp_counts[k] for k in crossing),
        "H_kill_pattern_bits": round(H, 6),
        "H_kill_pattern_given_cell_bits": round(cond, 6),
        "H_projected_bits": round(H_proj, 6),
        "H_projected_given_cell_bits": round(cond_proj, 6),
        "estimator_note": "conditional entropies computed from the JOINT (cell x pattern); "
                          "the prior version filtered to patterns exclusive to a cell and so "
                          "could not report evidence against its own hypothesis (ATK-014).",
        "per_cell": {"".join(c).replace("", "/"): {
            "n": sum(v.values()), "distinct_patterns": len(v),
            "distinct_projected": len(joint_proj.get(c, {})),
        } for c, v in joint.items()},
        "top5_pattern_share": round(sum(c for _, c in kp_counts.most_common(5)) / n_rej, 4),
        "mean_pairwise_jaccard": round(sum(j for j, _, _ in pairs) / max(1, len(pairs)), 4),
        "cell_pairs_zero_overlap": f"{zero}/{len(pairs)}",
        "with_step_trace_share": round(totals["with_step_trace"] / n_rej, 4),
        "with_parent_share": round(totals["with_parent"] / n_rej, 4),
        "top_jaccard_pairs": [{"j": round(j, 3), "a": "/".join(a), "b": "/".join(b)}
                              for j, a, b in sorted(pairs, reverse=True)[:8]],
        "totals": dict(totals),
    }
    (OUT / "full_scan.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "scope", "rejected_records", "distinct_kill_patterns", "distinct_cells",
        "kill_patterns_crossing_a_cell", "records_under_crossing_patterns",
        "mean_pairwise_jaccard", "cell_pairs_zero_overlap")}, indent=2), flush=True)


if __name__ == "__main__":
    sys.exit(main())
