"""Leave-one-source-out ablation corpus generator.

Reads the FULL greedy train corpus and emits one train file per condition:
  - full            : all sources (baseline, == train_v1 modulo path)
  - minus_<family>  : the full corpus with one source family removed

The gold eval set is held FIXED (gold_eval_v1.jsonl) across all conditions, so
the only thing that changes between runs is which source's training signal is
present. Accuracy drop on the fixed gold set = that source's contribution.

This step is pure data plumbing (no GPU). Training + eval are driven by
run_ablation.* over the files this writes.

Usage:
    python -m ergon.learner.greedy.ablate_sources \
        --train ergon/learner/greedy/corpus/train_v1.jsonl \
        --out-dir ergon/learner/greedy/corpus/ablation
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import List

FAMILIES = ["theseus", "hephaestus", "erebos", "pollux", "charon_md", "harmonia"]


def family(src: str) -> str:
    if src.startswith("charon_md"):
        return "charon_md"
    if src.startswith("harmonia"):
        return "harmonia"
    return src


def read_jsonl(path: str) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="F:/Prometheus/ergon/learner/greedy/corpus/train_v1.jsonl")
    ap.add_argument("--out-dir", default="F:/Prometheus/ergon/learner/greedy/corpus/ablation")
    args = ap.parse_args()

    rows = read_jsonl(args.train)
    fam_counts = Counter(family(r["source"]) for r in rows)
    print(f"[ablate] full corpus: {len(rows)} rows")
    print(f"[ablate] by family: {dict(fam_counts)}")

    out = Path(args.out_dir)
    conditions = {}

    # full baseline
    write_jsonl(out / "train_full.jsonl", rows)
    conditions["full"] = len(rows)

    # leave-one-out per family present in the corpus
    present = [f for f in FAMILIES if fam_counts.get(f, 0) > 0]
    for fam in present:
        kept = [r for r in rows if family(r["source"]) != fam]
        write_jsonl(out / f"train_minus_{fam}.jsonl", kept)
        conditions[f"minus_{fam}"] = len(kept)
        print(f"[ablate] minus_{fam}: kept {len(kept)} (dropped {len(rows) - len(kept)})")

    manifest = {
        "source_train": args.train,
        "full_rows": len(rows),
        "by_family": dict(fam_counts),
        "conditions": conditions,
        "families_present": present,
    }
    (out / "ablation_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[ablate] wrote {len(conditions)} condition files + manifest to {out}")


if __name__ == "__main__":
    main()
