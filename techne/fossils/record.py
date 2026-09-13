"""The package record every specimen carries (operator directive 2026-09-12, PACKAGE RECORD).

A record is context for Nyx, never decomposition: what humans built the system to do, what
pressure it answers, what success means in its native domain, where it came from, how to
run it, how we know it runs. It names no organ and no function of interest.
"""
from __future__ import annotations

import json
import pathlib
import time

from . import vault

SCHEMA = "techne.fossil.record/1"

RUN_CLASSES = ("RUNNABLE_NATIVE", "RUNNABLE_CONTAINER", "RUNNABLE_VM", "RUNNABLE_EMULATED",
               "RUNNABLE_HISTORICAL_TOOLCHAIN",   # added by the 2026-09-12 global-archaeology charter
               "BUILDS_BUT_NOT_RUN", "SOURCE_ONLY", "BINARY_ONLY", "BLOCKED_DEPENDENCY",
               "BLOCKED_PLATFORM", "BROKEN_UPSTREAM", "LEGAL_RESTRICTION", "NOT_ATTEMPTED")

#: Behavioral-observability dimensions (charter 2026-09-12), independent of run class. Each is
#: yes/no/unknown; they are acquisition facts for Nyx, not a decomposition. INTERVENTION and
#: PATCH_INTERVENTION say only whether behaviour CAN be varied, never which behaviour matters.
OBSERVABILITY_DIMS = ("EXECUTABLE", "OBSERVABLE", "ORACLE_BACKED", "INTERVENTION_READY",
                      "PATCH_INTERVENTION", "OPAQUE")

#: Provenance relations for the lineage graph (charter 2026-09-12). NOT behavioral-equivalence
#: claims -- that is a downstream question. Each edge: {relation, to (a fossil_id or an external
#: name), note}.
LINEAGE_RELATIONS = ("forked_from", "derived_from", "rewrote", "superseded", "inspired_by",
                     "port_of", "reimplementation_of", "historical_version_of", "algorithm_from",
                     "shares_ancestor_with")
TEST_CLASSES = ("UPSTREAM_TESTS_PASS", "UPSTREAM_TESTS_FAIL", "UPSTREAM_TESTS_NOT_RUN",
                "UPSTREAM_DRIVERS_RUN_NO_ORACLE",   # the shipped test programs ran to completion and produced their tables; no reference output exists in the vault to grade them
                "TECHNE_SMOKE_HARNESS_PASS", "TECHNE_SMOKE_HARNESS_FAIL", "NO_TESTS", "NOT_ATTEMPTED")
# Charter 2026-09-13 (batch 09, P7): the historical disposition is a FACTUAL field about what
# happened to this software, never an inference from age or looks. A non-ACTIVE/UNKNOWN state
# REQUIRES at least one citation in evidence[] -- validate() enforces that.
DISPOSITION_STATES = ("ACTIVE", "SUPERSEDED", "ABANDONED", "FAILED", "LOSING_RIVAL",
                      "OBSOLETED_BY_ENVIRONMENT", "LEGAL_OR_PATENT_DISPLACED",
                      "HISTORICAL_ONLY", "UNKNOWN")
FAILURE_REASONS = ("performance_collapse", "instability", "poor_scaling", "resource_explosion",
                   "brittleness", "incorrect_assumptions", "security_weakness", "ecosystem_loss",
                   "patent_or_legal_displacement", "architectural_dead_end", "superior_rival",
                   "maintainability_failure", "numerical_failure", "concurrency_failure")
EVIDENCE_KINDS = ("original_paper", "retrospective", "release_notes", "standards_history",
                  "benchmark_history", "project_documentation", "successor_documentation",
                  "archived_technical_discussion")

SOURCE_TYPES = ("ORIGINAL_AUTHORITATIVE_RELEASE", "HISTORICAL_ARCHIVE_MIRROR", "LATER_SAME_LINEAGE_RELEASE",
                "FAITHFUL_PORT", "PSEUDOCODE_PLUS_REFERENCE_IMPL", "BINARY_WITH_SYMBOLS",
                "RECOVERED_REPRESENTATION_NOT_ORIGINAL_SOURCE")

REQUIRED = ["specimen_id", "canonical_name", "aliases", "lineage", "domain", "era",
            "version", "source_origin", "source_type", "source_identity", "hashes", "license",
            "acquisition_date", "language", "build_system", "compiler_or_interpreter",
            "dependencies", "run_classification", "test_classification", "entry_points",
            "example", "environment", "patches", "recovered_status", "upstream_docs",
            "human_capability_summary"]



# ---------------------------------------------------------------- pin evidence (batch 10 P1)
# PREREG: techne/fossils/PREREG_PIN_EVIDENCE_2026-09-13.md
# source_origin.artifacts[] is the REQUEST; hashes.artifacts[] is the RECEIPT written by acquire().
# A pin is ESTABLISHED when either side carries a FIXED identifier -- a sha256, or a 40-hex commit.
# "HEAD" is not fixed. Once established, a pin must never be lost or downgraded to a moving
# reference: the batch scripts used to rebuild source_origin from a literal and destroy it.

def _artifact_key(a: dict):
    return (a.get("kind"), a.get("url") if a.get("kind") == "git" else a.get("filename"))


def established_pin(art: dict, hashes_artifacts=None) -> str:
    """The fixed identifier for this artifact, or "" if none is established."""
    if not art:
        return ""
    hashes_artifacts = hashes_artifacts or []
    key = art.get("url") if art.get("kind") == "git" else art.get("filename")
    h = {}
    for x in hashes_artifacts:
        if str(x.get("filename") or "") == str(key or ""):
            h = x
            break
    if art.get("kind") == "git":
        for c in (art.get("commit_resolved"), art.get("commit"), h.get("commit")):
            c = str(c or "")
            if len(c) == 40 and all(ch in "0123456789abcdef" for ch in c.lower()):
                return c
        return ""
    for sh in (art.get("sha256"), h.get("sha256")):
        if sh:
            return str(sh)
    return ""


def merge_artifact_pins(new_rec: dict, old_rec: dict) -> int:
    """Carry established pins from old_rec onto new_rec's artifacts. Adding or removing artifacts
    stays legal; LOSING an established pin does not. Returns how many pins were restored."""
    if not old_rec:
        return 0
    old_arts = (old_rec.get("source_origin") or {}).get("artifacts") or []
    old_hashes = (old_rec.get("hashes") or {}).get("artifacts") or []
    idx = {_artifact_key(a): a for a in old_arts}
    restored = 0
    for a in (new_rec.get("source_origin") or {}).get("artifacts") or []:
        if established_pin(a):           # this record already carries its own fixed pin
            continue
        o = idx.get(_artifact_key(a))
        pin = established_pin(o, old_hashes) if o else established_pin(a, old_hashes)
        if not pin:
            continue
        if a.get("kind") == "git":
            a["commit"] = pin
            a["commit_resolved"] = pin
            if o and o.get("commit_date") and not a.get("commit_date"):
                a["commit_date"] = o["commit_date"]
        else:
            a["sha256"] = pin
        restored += 1
    return restored

def skeleton(specimen_id: str, **fields) -> dict:
    rec = {
        "schema": SCHEMA,
        "specimen_id": specimen_id,
        "canonical_name": "", "aliases": [], "lineage": "", "domain": [], "era": "",
        "version": "", "source_origin": {}, "source_type": "", "source_identity": {},
        "hashes": {}, "license": {"spdx": "", "status": "", "evidence": ""},
        "acquisition_date": time.strftime("%Y-%m-%d", time.gmtime()),
        "language": [], "build_system": "", "compiler_or_interpreter": "", "dependencies": [],
        "run_classification": "NOT_ATTEMPTED", "test_classification": "NOT_ATTEMPTED",
        "entry_points": [], "example": {"command": "", "input": "", "output": ""},
        "environment": {}, "patches": [], "recovered_status": "NOT_RECOVERED_SOURCE_IS_ORIGINAL",
        "upstream_docs": [],
        "human_capability_summary": {"built_to": "", "pressure": "", "success_means": ""},
        "known_human_problem_solved": "",
        "hardware_assumptions": "",
        # batch 04 (machinery under pressure): context only, never a Nyx decomposition.
        "human_environmental_pressure": "",   # the external condition that made this necessary
        "human_failure_condition": "",        # what happens if it fails at its human purpose
        "behavioral_entry_point": "",         # one reproducible way to stimulate/perturb it
        # charter 2026-09-12: observability is a set of independent yes/no/unknown flags, and
        # lineage is a list of provenance edges. Both default empty; the harvest fills them.
        "observability": {d: "unknown" for d in OBSERVABILITY_DIMS},
        "lineage_relations": [],
        "acquisition_tags": [],
        # P7: factual disposition + the citations that establish it (evidence REQUIRED
        # for any state other than ACTIVE/UNKNOWN).
        "historical_disposition": {"state": "UNKNOWN", "failure_reasons": [],
                                   "superseded_by": "", "rival_of": "", "evidence": []},
        "versions_preserved": [],
        "receipts": [],
        "nyx_handoff": {"here_is_the_machine": "", "where_it_came_from": "", "how_to_run_it": "",
                        "how_we_know_it_runs": "", "what_humans_used_it_for": ""},
        "seat": "Techne",
    }
    rec.update(fields)
    return rec


def validate(rec: dict) -> list[str]:
    problems = [k for k in REQUIRED if k not in rec]
    if rec.get("run_classification") not in RUN_CLASSES:
        problems.append("run_classification %r not in RUN_CLASSES" % rec.get("run_classification"))
    if rec.get("test_classification") not in TEST_CLASSES:
        problems.append("test_classification %r not in TEST_CLASSES" % rec.get("test_classification"))
    if rec.get("source_type") not in SOURCE_TYPES:
        problems.append("source_type %r not in SOURCE_TYPES" % rec.get("source_type"))
    hd = rec.get("historical_disposition")
    if hd is not None:
        st = hd.get("state")
        if st not in DISPOSITION_STATES:
            problems.append("historical_disposition.state %r not in DISPOSITION_STATES" % st)
        for fr in hd.get("failure_reasons") or []:
            if fr not in FAILURE_REASONS:
                problems.append("failure_reason %r not in FAILURE_REASONS" % fr)
        if st not in (None, "ACTIVE", "UNKNOWN") and not (hd.get("evidence") or []):
            problems.append("historical_disposition.state %s requires at least one evidence entry" % st)
        for ev in hd.get("evidence") or []:
            if ev.get("kind") not in EVIDENCE_KINDS:
                problems.append("evidence.kind %r not in EVIDENCE_KINDS" % ev.get("kind"))
            if not ev.get("says"):
                problems.append("evidence entry missing 'says' (what the source actually states)")
    hs = rec.get("human_capability_summary") or {}
    for k in ("built_to", "pressure", "success_means"):
        if not hs.get(k):
            problems.append("human_capability_summary.%s empty" % k)
    return problems


def path(specimen_id: str) -> pathlib.Path:
    return vault.specimen_dir(specimen_id) / "record.json"


def load(specimen_id: str) -> dict:
    return json.loads(path(specimen_id).read_text(encoding="utf-8"))


def save(rec: dict) -> pathlib.Path:
    p = path(rec["specimen_id"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8", newline="\n")
    return p
