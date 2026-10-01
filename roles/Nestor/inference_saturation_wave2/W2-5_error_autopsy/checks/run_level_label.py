"""Run-level-label check: does the label hold for the unit it names?

Incidents: dossier D U1 -- 8 of 23 runs labelled ESTABLISHED had first-donor (D0)
lineage_births = 0, yet "about half of established donors also self-poison" was read as a
property of the donors (directive Block C premise). Dossier A W7 -- the X-RUNAWAY
"causal descendant share" comment named the implant's descendants, but the code only asked
whether an organism had any causal parent. Also "57 replicators" (run flag read as genome).

Input: records (one per run) with a run-level label and a field that evidences the named unit
directly, e.g. label "ESTABLISHED" and unit evidence ``lineage_births`` of D0.

Verdicts
    LABEL_NOT_UNIT   at least `max_violations`+1 labelled runs lack the unit evidence
    OK               every labelled run carries the unit evidence
    NOT_VERIFIED     no labelled run, or the unit-evidence field is missing on any labelled run
                     (missing evidence is never read as support)
"""
from typing import Callable, Iterable, Mapping, Optional

from . import CheckResult, OK, NOT_VERIFIED

NAME = "run_level_label"


def check_label_holds_for_unit(records: Iterable[Mapping], label_key: str, label_value,
                               unit_evidence_key: str,
                               unit_ok: Optional[Callable[[object], bool]] = None,
                               max_violations: int = 0, id_key: str = "run") -> CheckResult:
    unit_ok = unit_ok or (lambda v: v is not None and v >= 1)
    labelled = [r for r in records if r.get(label_key) == label_value]
    if not labelled:
        return CheckResult(NAME, NOT_VERIFIED, "no record carries %s=%r" % (label_key, label_value))
    missing = [r.get(id_key) for r in labelled if unit_evidence_key not in r]
    if missing:
        return CheckResult(NAME, NOT_VERIFIED,
                           "%d labelled record(s) lack %r: the label cannot be checked against its unit"
                           % (len(missing), unit_evidence_key), {"missing": missing})
    bad = [{"id": r.get(id_key), unit_evidence_key: r[unit_evidence_key]}
           for r in labelled if not unit_ok(r[unit_evidence_key])]
    details = {"labelled": len(labelled), "violations": len(bad),
               "holds_fraction": 1 - len(bad) / len(labelled)}
    if len(bad) > max_violations:
        return CheckResult(NAME, "LABEL_NOT_UNIT",
                           "%d of %d runs labelled %r show no evidence for the named unit (%s): "
                           "the label is a run property" % (len(bad), len(labelled), label_value,
                                                            unit_evidence_key), details, bad)
    return CheckResult(NAME, OK, "label holds for its unit in every labelled run", details)
