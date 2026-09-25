"""Post-campaign adjudication. P-5: the INDEX alone is sufficient; there is no fallback.

THE DEFECT THIS REPAIRS (Z80A-D03). The predecessor's index whitelist carried
`replicated` and `replication_rate` but not `replication_events` or
`births_similar_no_write` - the two counters that separate a birth backed by evidence
that the organism placed the child's bytes from a resemblance that copying never caused.
The first adjudicator read them from the index, found them absent, and returned
INADMISSIBLE for all 36 spontaneity flags then in flight with the reason "no
evidence-backed replication event", which was false. The fix at the time was to make the
adjudicator open each per-run RESULT.json instead.

That fix worked and was the wrong shape. It left an adjudicator whose answers depended on
files the index does not describe, so the index silently stopped being a sufficient
record of the campaign and nobody could tell by reading it. Here the dependency runs the
other way: INDEX_WHITELIST declares everything adjudication needs, the scheduler is
required to write exactly that, and `adjudicate()` accepts index rows and nothing else.

THERE IS NO PER-RUN READ PATH IN THIS MODULE. A row missing a required field yields a
structured MISSING_FIELD verdict naming the field. It never opens a file to recover,
because a recovery path is how the index stopped being checkable in the first place.

VERDICTS
  ADMISSIBLE    the record supports the claim the flag names, on the flag's own declared
                basis, with a margin
  WEAK          the flag fired on a real event but the evidence does not separate it
                from its control, or the run is a seeded instrument
  INADMISSIBLE  the evidence contradicts the flag's name, or the run cannot bear on it
  MISSING_FIELD the index does not carry what this verdict needs (a defect in the
                writer, not a property of the run)
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

from constants import C, CONSTANTS_SHA256   # S3-2: one hash-covered source of thresholds

# Everything adjudication reads. The scheduler writes exactly these into each index row's
# "summary". Adding a verdict that needs a new field means adding the field HERE first,
# which is the check T-P5 enforces.
INDEX_WHITELIST = (
    # identity / outcome
    "pop_final", "extinct", "epochs_run", "ops",
    # P-3: the historical/final-state pair, never collapsed
    "crossed_ever", "crossed_at_final", "held_max_ever", "held_max_final", "n_cross_events",
    # replication evidence (the two Z80A-D03 omitted)
    "replicated", "replication_rate", "replication_events", "births_similar_no_write",
    "births_endogenous", "births_external",
    # P-2: causal replication depth
    "max_ancestry_depth", "n_lineages_depth_ge_2", "n_lineages_depth_ge_5",
    "max_causal_replication_depth", "n_causal_lineages_depth_ge_2",
    "n_causal_lineages_depth_ge_5", "propagating_replicators",
    # P-11: pair-tape causal-copy reassay, and the predecessor depth kept beside it
    "p11_events", "max_predecessor_replication_depth", "max_causal_replication_depth_literal",
    # P-1: certificate and completeness
    "lineage_complete", "migration_events", "has_reservoir_certificate",
    "ancestry_certificate",
    # descriptive
    "comp_max", "span_mean_final", "niche_occupancy", "first_replicator",
    "entropy_drop", "dom_share_final", "uniq_final", "len_mean_final", "fid_mean_final",
)

# Fields each flag's verdict requires present in the row summary.
REQUIRED = {
    "RESERVOIR_CROSSED_A_MOAT": (
        "has_reservoir_certificate", "ancestry_certificate", "lineage_complete",
        "held_max_ever", "held_max_final"),
    "REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION": (
        "crossed_ever", "crossed_at_final", "held_max_ever", "held_max_final"),
    "REACHED_ONLY_IN_INCREMENTAL_REPRESENTATION": (
        "crossed_ever", "held_max_ever", "held_max_final"),
    "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES": (
        "replication_events", "births_similar_no_write", "max_causal_replication_depth"),
    "REPRODUCTIVE_ARCHITECTURE_CHANGED_UNDER_TASK_DEMAND": (
        "replication_events", "span_mean_final"),
}

_MISSING = object()


def _need(summary, fields):
    """Fields absent from the row. Absent means the KEY is missing, not that it is None:
    a null is a measured value, a missing key is a defect in the writer."""
    return [f for f in fields if summary.get(f, _MISSING) is _MISSING]


def _verdict(v, why, numbers):
    return {"verdict": v, "why": why, "numbers": numbers}


# ------------------------------------------------------------------ per-flag rules
def _reservoir(s, d, ev):
    cert = s.get("ancestry_certificate")
    n = {"has_certificate": s.get("has_reservoir_certificate"),
         "lineage_complete": s.get("lineage_complete"),
         "held_ever": s.get("held_max_ever"), "held_final": s.get("held_max_final"),
         "crossing_niche": (cert or {}).get("crossing_niche"),
         "founder_niche": (cert or {}).get("founder_niche"),
         "seeded_instrument": d.get("seeded_instrument")}
    if d.get("seeded_instrument"):
        return _verdict("INADMISSIBLE", "seeded instrument population", n)
    if not d.get("endogenous"):
        return _verdict("INADMISSIBLE", "exogenous control, not a reservoir result", n)
    if not s.get("lineage_complete"):
        return _verdict("INADMISSIBLE",
                        "lineage incomplete: an absent migration record cannot support a "
                        "causal ancestry claim", n)
    if not (s.get("has_reservoir_certificate") and cert):
        return _verdict("INADMISSIBLE", "no complete easy-niche ancestry certificate", n)
    if cert.get("crossing_niche") == cert.get("founder_niche"):
        return _verdict("INADMISSIBLE", "crossing occurred in the easy niche itself", n)
    if (s.get("held_max_ever") or 0) < C["CROSS"]:
        return _verdict("WEAK", "certificate present but below the crossing threshold", n)
    return _verdict("ADMISSIBLE",
                    "complete certificate: founder in the easy niche, logged migration, "
                    "crossing in a hard niche", n)


def _endogenous(s, d, ev):
    endo = ev.get("endogenous_held_ever")
    ext = ev.get("external_held_ever")
    margin = (endo or 0) - (ext or 0)
    n = {"endogenous_held_ever": endo, "external_held_ever": ext,
         "margin_ever": round(margin, 4),
         "endogenous_held_final": s.get("held_max_final"),
         "endogenous_crossed_at_final": s.get("crossed_at_final"),
         "endogenous": d.get("endogenous")}
    if not d.get("endogenous"):
        return _verdict("INADMISSIBLE", "the flagged run is not an endogenous treatment", n)
    if margin < 0:
        return _verdict("INADMISSIBLE", "the exogenous control finished better", n)
    if (endo or 0) < C["CROSS"]:
        return _verdict("WEAK", "below the crossing threshold on its own declared basis", n)
    if margin < C["MARGIN"]:
        return _verdict("WEAK", "margin below %.2f: the control is not separated" % C["MARGIN"], n)
    if not s.get("crossed_at_final"):
        return _verdict("WEAK",
                        "crossed historically but not at final state; the claim is about "
                        "reaching, so this is preserved, not promoted", n)
    return _verdict("ADMISSIBLE",
                    "crossed on its declared basis, control below it, margin >= %.2f "
                    "and still at threshold at final state" % C["MARGIN"], n)


def _incremental(s, d, ev):
    inc, at = ev.get("incremental_held_ever"), ev.get("atomic_held_ever")
    margin = (inc or 0) - (at or 0)
    n = {"incremental_held_ever": inc, "atomic_held_ever": at, "margin": round(margin, 4)}
    if margin < C["MARGIN"]:
        return _verdict("WEAK", "margin below %.2f" % C["MARGIN"], n)
    if (inc or 0) < C["CROSS"]:
        return _verdict("WEAK", "below the crossing threshold", n)
    return _verdict("ADMISSIBLE", "incremental at threshold, atomic separated", n)


def _spontaneous(s, d, ev):
    depth = s.get("max_causal_replication_depth")
    n = {"seeded_instrument": d.get("seeded_instrument"),
         "spontaneity_test": d.get("spontaneity_test"),
         "replication_events": s.get("replication_events"),
         "births_similar_no_write": s.get("births_similar_no_write"),
         "max_causal_replication_depth": depth,
         "propagating_replicators": s.get("propagating_replicators"),
         "fidelity": ((ev.get("first_replicator") or {}).get("fidelity"))}
    if d.get("seeded_instrument") or not d.get("spontaneity_test"):
        return _verdict("INADMISSIBLE", "seeded population: cannot bear on spontaneous origin", n)
    if not s.get("replication_events"):
        return _verdict("INADMISSIBLE", "no evidence-backed replication event", n)
    if (n["fidelity"] or 0) < C["CROSS"]:
        return _verdict("WEAK", "first replicator fidelity below %.2f" % C["CROSS"], n)
    if (depth or 0) < C["CAUSAL_DEPTH"]:
        # The predecessor's headline result, stated at its true size.
        return _verdict("WEAK",
                        "evidence-backed replication events without propagation: causal "
                        "depth %s is below %d" % (depth, C["CAUSAL_DEPTH"]), n)
    return _verdict("ADMISSIBLE",
                    "random initial population, evidence-backed copy, and a causal "
                    "replication lineage of depth >= %d" % C["CAUSAL_DEPTH"], n)


def _architecture(s, d, ev):
    n = {"span_mean_final": ev.get("span_mean_final"), "pressure": ev.get("pressure"),
         "replication_events": s.get("replication_events")}
    if not s.get("replication_events"):
        return _verdict("INADMISSIBLE", "no evidence-backed replication in the run", n)
    return _verdict("WEAK",
                    "compression is measured against the representation length, not a "
                    "matched no-task control", n)


RULES = {
    "RESERVOIR_CROSSED_A_MOAT": _reservoir,
    "REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION": _endogenous,
    "REACHED_ONLY_IN_INCREMENTAL_REPRESENTATION": _incremental,
    "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES": _spontaneous,
    "REPRODUCTIVE_ARCHITECTURE_CHANGED_UNDER_TASK_DEMAND": _architecture,
}


# ------------------------------------------------------------------ entry point
def adjudicate(rows, source="INDEX"):
    """Adjudicate every special on every row. INDEX ROWS ONLY - no file is opened.

    `rows` is an iterable of index rows, each carrying at least run_id, derived, and a
    "summary" dict restricted to INDEX_WHITELIST, plus "specials" as full flag records
    (flag, reads, evidence). `source` is recorded in the result for provenance only and
    never changes what is read.
    """
    # S3-1. Materialise ONCE. The predecessor iterated `rows` and then evaluated
    # `len(list(rows))`, which on a generator counts an exhausted iterator and on any
    # non-list returned None - so an unattended run feeding rows lazily recorded a row
    # count that did not describe what was adjudicated.
    rows = list(rows)
    verdicts = []
    for row in rows:
        s = row.get("summary") or {}
        d = row.get("derived") or {}
        for sp in row.get("specials") or []:
            flag = sp["flag"] if isinstance(sp, dict) else sp
            ev = (sp.get("evidence") or {}) if isinstance(sp, dict) else {}
            missing = _need(s, REQUIRED.get(flag, ()))
            if missing:
                # The index does not carry what this verdict needs. That is a defect in
                # the writer; it is reported, never repaired by reading elsewhere.
                v = _verdict("MISSING_FIELD",
                             "index row lacks required field(s): %s" % ", ".join(sorted(missing)),
                             {"missing": sorted(missing)})
            else:
                rule = RULES.get(flag)
                v = (rule(s, d, ev) if rule else
                     _verdict("INADMISSIBLE", "no adjudication rule for this flag", {}))
            verdicts.append(dict(v, run_id=row.get("run_id"), family=row.get("family"),
                                 flag=flag, reads=(sp.get("reads") if isinstance(sp, dict) else None),
                                 cell=row.get("cell")))

    by = collections.Counter((x["flag"], x["verdict"]) for x in verdicts)
    summary = {}
    for flag in sorted({x["flag"] for x in verdicts}):
        summary[flag] = {v: by[(flag, v)] for v in
                         ("ADMISSIBLE", "WEAK", "INADMISSIBLE", "MISSING_FIELD")
                         if by[(flag, v)]}
    return {"source": source, "n_rows": len(rows),
            "n_verdicts": len(verdicts),
            "rules": dict(C), "constants_sha256": CONSTANTS_SHA256,
            "summary": summary, "verdicts": verdicts}


def load_index(path):
    out = []
    p = pathlib.Path(path)
    if not p.exists():
        return out
    for line in p.read_text(encoding="ascii").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def main(argv):
    root = pathlib.Path(argv[1] if len(argv) > 1 else "observatory")
    rows = load_index(root / "INDEX.jsonl")
    out = adjudicate(rows, source=str(root / "INDEX.jsonl"))
    (root / "ADJUDICATION.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=True, default=str), encoding="ascii")
    print(json.dumps({"n_verdicts": out["n_verdicts"], "summary": out["summary"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
