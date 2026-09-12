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
SOURCE_TYPES = ("ORIGINAL_AUTHORITATIVE_RELEASE", "HISTORICAL_ARCHIVE_MIRROR", "LATER_SAME_LINEAGE_RELEASE",
                "FAITHFUL_PORT", "PSEUDOCODE_PLUS_REFERENCE_IMPL", "BINARY_WITH_SYMBOLS",
                "RECOVERED_REPRESENTATION_NOT_ORIGINAL_SOURCE")

REQUIRED = ["specimen_id", "canonical_name", "aliases", "lineage", "domain", "era",
            "version", "source_origin", "source_type", "source_identity", "hashes", "license",
            "acquisition_date", "language", "build_system", "compiler_or_interpreter",
            "dependencies", "run_classification", "test_classification", "entry_points",
            "example", "environment", "patches", "recovered_status", "upstream_docs",
            "human_capability_summary"]


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
        # charter 2026-09-12: observability is a set of independent yes/no/unknown flags, and
        # lineage is a list of provenance edges. Both default empty; the harvest fills them.
        "observability": {d: "unknown" for d in OBSERVABILITY_DIMS},
        "lineage_relations": [],
        "acquisition_tags": [],
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
