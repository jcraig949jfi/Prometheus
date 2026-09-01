"""Classification fossils: every superseded classification, kept and readable.

THE REQUIREMENT. Mistaken classifications must be preserved as fossils rather than silently
rewritten. The append-only stores already keep every write, so nothing was ever destroyed --
but `store.current()` returns last-write-wins, so the earlier classifications were INVISIBLE.
Preserved and unreadable is not preserved for any practical purpose.

WHAT THIS EXPOSES. For every genome that was ever retagged or remediated, the full sequence of
(bottleneck, descriptors, mechanisms, domain_status) it has held, with the reason recorded at
each step. That makes two things checkable by a reviewer who does not trust us:

  1. how often a classification CHANGED, which bounds how much the current corpus depends on
     instrument revisions rather than on evidence;
  2. whether any revision moved a paper in a direction that flattered a result.

The second is the one that matters. Every retag in this campaign was applied corpus-wide by
rule, never per-paper, and this view is what lets someone verify that rather than take it on
trust.
"""
from __future__ import annotations

import json
from typing import Optional

from . import store


def history(genome_id: Optional[str] = None) -> dict:
    """genome_id -> ordered list of classification states, oldest first."""
    out = {}
    for rec in store.read("genomes"):
        gid = rec.get("research_genome_id")
        if not gid or (genome_id and gid != genome_id):
            continue
        state = {
            "written_at": rec.get("_written_at"),
            "cycle": rec.get("discovered_in_cycle"),
            "bottleneck": rec.get("bottleneck"),
            "descriptors": rec.get("descriptors") or {},
            "mechanisms": sorted(rec.get("claimed_mechanism") or []),
            "domain_status": rec.get("domain_status"),
            "reason": (rec.get("_retagged") or rec.get("_remediated")
                       or rec.get("duplicate_reason") or rec.get("recovery_note")),
            "digest": rec.get("_digest"),
        }
        seq = out.setdefault(gid, [])
        # Only record a fossil when the CLASSIFICATION actually moved.
        if seq:
            prev = seq[-1]
            same = (prev["bottleneck"] == state["bottleneck"]
                    and prev["descriptors"] == state["descriptors"]
                    and prev["mechanisms"] == state["mechanisms"]
                    and prev["domain_status"] == state["domain_status"])
            if same:
                continue
        seq.append(state)
    return out


def summary() -> dict:
    h = history()
    changed = {g: s for g, s in h.items() if len(s) > 1}
    # Which transitions occurred, and did any move a paper INTO a placed state?
    def placed(st):
        d = st["descriptors"] or {}
        return (st["bottleneck"] not in (None, "B_UNASSIGNED")
                and all(d.get(k, "unknown") != "unknown"
                        for k in ("representation_family", "selection_family",
                                  "evaluation_regime")))
    gained = sum(1 for s in changed.values() if not placed(s[0]) and placed(s[-1]))
    lost = sum(1 for s in changed.values() if placed(s[0]) and not placed(s[-1]))
    reasons = {}
    for s in changed.values():
        for st in s[1:]:
            r = str(st.get("reason") or "unrecorded")[:60]
            reasons[r] = reasons.get(r, 0) + 1
    return {
        "genomes_total": len(h),
        "genomes_reclassified_at_least_once": len(changed),
        "reclassification_rate": (len(changed) / len(h)) if h else 0.0,
        "max_states_for_one_genome": max([len(s) for s in h.values()], default=0),
        "moved_INTO_placed": gained,
        "moved_OUT_of_placed": lost,
        "revision_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
        "note": ("every revision in this campaign was applied corpus-wide by rule, never "
                 "per-paper. moved_INTO_placed and moved_OUT_of_placed are reported together "
                 "so a reviewer can see whether revisions ran in only one direction."),
    }


def export(path: str = "techne/cartography/store/classification_fossils.json") -> str:
    import pathlib
    h = history()
    out = {"summary": summary(),
           "histories": {g: s for g, s in h.items() if len(s) > 1}}
    p = pathlib.Path(path)
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    return str(p)


def main() -> int:
    s = summary()
    for k, v in s.items():
        if k == "revision_reasons":
            print("revision_reasons:")
            for r, n in v.items():
                print("    %4d  %s" % (n, r))
        else:
            print("%-38s %s" % (k, str(v)[:100]))
    print("\nexported ->", export())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
