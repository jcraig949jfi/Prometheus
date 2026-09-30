"""Behaviour clusters of the residual catalogue (operator v1 directive,
item 2): group residuals by the SHAPE of the phenomenon, not by the engine
that produced it. Deterministic over behaviour_tags.

The tags are model-assigned descriptors, not evidence; a cluster is a
candidate ecological niche for later lens evolution, never a finding that
its members share a cause. Tags that describe missing work rather than an
observed phenomenon (untested_precondition, control_never_run) are listed
separately and never form a niche.

Usage: python -m tyche.residuals.cluster <CATALOGUE.jsonl> <out.json>
"""

from __future__ import annotations

import collections
import itertools
import json
import sys

WORK_TAGS = {"untested_precondition", "control_never_run"}


def main(cat, out):
    rows = [json.loads(x) for x in open(cat, encoding="ascii") if x.strip()]
    by_tag = collections.defaultdict(list)
    for r in rows:
        for t in r.get("behaviour_tags", []):
            by_tag[t].append(r)

    def desc(rs):
        return {"n": len(rs), "seats": sorted({r["seat"] for r in rs}),
                "engines": sorted({r.get("engine") or r["seat"] for r in rs}),
                "with_raw_rows": sum(bool(r.get("raw_rows")) for r in rs),
                "with_framing_note": sum("framing_note" in r for r in rs),
                "rids": sorted(r["rid"] for r in rs)}

    tags = {t: desc(rs) for t, rs in sorted(by_tag.items())}
    niches = sorted(((t, d) for t, d in tags.items() if t not in WORK_TAGS and len(d["engines"]) >= 3),
                    key=lambda x: (-len(x[1]["engines"]), -x[1]["with_raw_rows"], x[0]))
    co = collections.Counter()
    for r in rows:
        ts = sorted(set(r.get("behaviour_tags", [])) - WORK_TAGS)
        for a, b in itertools.combinations(ts, 2):
            co[(a, b)] += 1
    res = {
        "catalogue": cat, "n_entries": len(rows),
        "cross_engine_niches": [{"tag": t, **d} for t, d in niches],
        "work_tags": {t: tags[t] for t in WORK_TAGS if t in tags},
        "all_tags": tags,
        "tag_pairs": [{"pair": list(k), "n": v} for k, v in co.most_common() if v >= 2],
        "note": "tags are model-assigned descriptors; a niche is a candidate habitat, not a shared cause",
    }
    json.dump(res, open(out, "w", encoding="ascii"), indent=1, sort_keys=True)
    for n in res["cross_engine_niches"]:
        print(f"{n['tag']:42s} n={n['n']:3d} engines={len(n['engines']):2d} raw={n['with_raw_rows']:2d} "
              f"flagged={n['with_framing_note']}")


if __name__ == "__main__":
    main(*sys.argv[1:])
