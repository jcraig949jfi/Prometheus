"""Assemble the residual catalogue from drafted sources, admitting only what
validate() admits at a pinned ref. Deterministic; rerunnable.

Usage: python -m tyche.residuals.build <ref> <out_dir> <in.jsonl> [<in.jsonl> ...]
Writes CATALOGUE_v0.jsonl (admitted), REJECTED_v0.jsonl (with reasons),
SUMMARY_v0.json (counts; the ref; input files).
"""

from __future__ import annotations

import collections
import json
import os
import sys

from .catalogue import validate


def main(ref, out_dir, *inputs):
    os.makedirs(out_dir, exist_ok=True)
    ok, bad, seen = [], [], set()
    for path in inputs:
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            e = json.loads(line)
            why = validate(e, ref)
            if e["rid"] in seen:
                why.append("duplicate rid")
            seen.add(e["rid"])
            if why:
                bad.append({**e, "rejected_because": why})
            else:
                ok.append(e)

    def dump(rows, name):
        with open(os.path.join(out_dir, name), "w", encoding="ascii", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True, ensure_ascii=True) + "\n")

    dump(ok, "CATALOGUE_v0.jsonl")
    dump(bad, "REJECTED_v0.jsonl")
    summ = {
        "ref": ref, "inputs": list(inputs), "admitted": len(ok), "rejected": len(bad),
        "by_kind": dict(collections.Counter(e["residual_kind"] for e in ok)),
        "by_seat": dict(collections.Counter(e["seat"] for e in ok)),
        "by_origin": dict(collections.Counter(e["drafted_by"] for e in ok)),
        "with_raw_rows": sum(bool(e.get("raw_rows")) for e in ok),
        "with_behaviour_tags": sum(bool(e.get("behaviour_tags")) for e in ok),
    }
    with open(os.path.join(out_dir, "SUMMARY_v0.json"), "w", encoding="ascii", newline="\n") as f:
        json.dump(summ, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps(summ, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:])
