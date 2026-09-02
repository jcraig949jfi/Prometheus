"""Mechanical audits that make the D-10 information boundary checkable.

Nothing here interprets anything. Every function returns a boolean or a
number derived from bytes, source text, or recorded events.
"""
from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from foundry.core.hashing import object_hash

# Every experimenter-authored surface that can touch the organizer path.
SUPPLIED_SOURCES = [
    "d10/lib/organizer.py",
    "d10/lib/acquire.py",
    "d10/lib/progtasks.py",
    "d10/lib/tasks.py",
    "d10/lib/audit.py",
]

# Identifiers that must NEVER appear in the organizer input path.
FORBIDDEN_IN_ORGANIZER_PATH = [
    "task_id", "admin_metadata", "family_id", "provenance", "difficulty",
    "test_cases", "check_exact", "value_kinds", "n_mut", "reference",
]


def supplied_manifest(root: str = ".") -> dict:
    """Content hash of every supplied surface plus the frozen constants."""
    from d10.lib import organizer as org  # noqa: F401  (import for constants)
    files = {}
    for rel in SUPPLIED_SOURCES:
        p = Path(root) / rel
        files[rel] = "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()
    return {"files": files}


def organizer_source_audit(root: str = ".") -> list:
    """Fail-closed source audit of the organizer input path.

    `artifact_words` and `evidence_words` are the ONLY functions whose output
    reaches a key program. Their source must not mention any forbidden
    identifier. This is a structural check on the code that will run, not a
    promise in a docstring.
    """
    import d10.lib.organizer as org
    hits = []
    for fn in (org.artifact_words, org.evidence_words):
        src = inspect.getsource(fn)
        body = src.split('"""')[-1] if '"""' in src else src   # strip docstring
        for name in FORBIDDEN_IN_ORGANIZER_PATH:
            if name in body:
                hits.append({"function": fn.__name__, "identifier": name})
    return hits


def differential_key_test(genome: bytes, task_a, task_b) -> dict:
    """E3 differential test.

    task_a and task_b must have IDENTICAL train cases and DIFFERENT test
    cases. Their task_ids therefore differ (task_id hashes train AND test)
    while everything a query key is entitled to see is identical. A key
    function that can read task_id will produce different keys; one that
    cannot must produce byte-identical keys.
    """
    from d10.lib.organizer import query_key
    ka = query_key(genome, task_a.evidence())
    kb = query_key(genome, task_b.evidence())
    return {"task_id_differs": task_a.task_id != task_b.task_id,
            "keys_identical": ka == kb, "key_a": ka, "key_b": kb}


def lineage_audit(store, artifact_id: str) -> dict:
    """E1: complete lineage, terminating in create_random, with no import."""
    recs = store.lineage(artifact_id)
    ops = [r.creation_op for r in recs]
    roots = [r for r in recs if not r.parent_ids]
    return {"n_nodes": len(recs),
            "ops": sorted(set(ops)),
            "has_import": any(o == "import" for o in ops),
            "n_roots": len(roots),
            "all_roots_random": all(r.creation_op == "create_random"
                                    for r in roots),
            "all_seeds_recorded": all(r.creation_seed is not None
                                      for r in recs)}


def write_manifest(path: str, extra: dict, root: str = ".") -> str:
    m = {**supplied_manifest(root), "constants": extra}
    Path(path).write_text(json.dumps(m, indent=1, sort_keys=True),
                          encoding="utf-8")
    return object_hash(m)
