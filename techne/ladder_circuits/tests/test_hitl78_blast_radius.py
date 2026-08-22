"""HITL #78 blast radius — the finding, pinned reproducibly. (Cycle 042.)

**Read-only throughout. Ergon is not patched.**

The live measurement is in `techne/loop/cycle_042.md` and its pre-registration in
`rung_notes/HITL78_BLAST_RADIUS_PREREG.md`. This file pins the MECHANISM against a synthetic row
built in the live writer's schema, so the evidence survives the campaign continuing to write to
the real ledger and does not depend on a file that changes under it.

These tests SHOULD FAIL once ergon repairs the seam. That is the intended signal, not a fragility:
when they go red, the finding has been fixed and the file should be deleted.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from ergon.probe.assemble import load_prepass  # noqa: E402


# The live writer's row shape, taken verbatim from ergon/probe/ledgers/campaign/p1_prepass.jsonl
# (962 rows, every one of this shape). Note what is present and what is NOT.
LIVE_ROW_SCHEMA = {
    "key": [1, "camp-M20-00000"],          # <- rep and uid live HERE, as a 2-element list
    "status": "ok",
    "error_type": None,
    "latency_s": 3.2,
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "extracted_int": 42,
    "attempt_text": "a worked attempt with reasoning in it",
    "solver": "some-model",
    "derives_from_gold": False,
    "ts_utc": "2026-08-22T01:00:00+00:00",
    "host": "h",
    "executor": "e",
}


def _write(tmp_path: pathlib.Path, rows) -> pathlib.Path:
    p = tmp_path / "p1_prepass.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return p


def test_THE_SEAM_two_readers_of_one_file_disagree_about_its_schema():
    """**The root cause, on the live row shape.**

    `campaign.py:best()` reads `tuple(r["key"])` and works. `assemble.load_prepass()` reads the
    flat fields `d["rep"]` and `d["uid"]`, which DO NOT EXIST in these rows. Same file, same
    package, two readers, and only one of them is right about the schema.
    """
    assert "key" in LIVE_ROW_SCHEMA
    assert "rep" not in LIVE_ROW_SCHEMA          # the field load_prepass filters on
    assert "uid" not in LIVE_ROW_SCHEMA          # the field it keys records by
    # best()'s view: the data is present and correct
    rep, uid = tuple(LIVE_ROW_SCHEMA["key"])
    assert rep == 1 and uid == "camp-M20-00000"


def test_LOAD_PREPASS_DROPS_EVERY_ROW_OF_THE_LIVE_SCHEMA(tmp_path):
    """`int(d.get("rep", -1)) != 1` — absent field defaults to -1, so every row is skipped.

    Not a corrupt-data problem and not a partial filter: the rejection is total and silent.
    """
    rows = [dict(LIVE_ROW_SCHEMA, key=[1, f"camp-M20-{i:05d}"]) for i in range(10)]
    path = _write(tmp_path, rows)
    assert load_prepass(path) == []              # ten valid rep-1 records in, zero out


def test_the_same_rows_load_when_rep_and_uid_are_flat(tmp_path):
    """**The data is loadable — it is the seam that is wrong, not the substrate.**

    Identical rows, with `rep`/`uid` lifted out of `key` into flat fields, load fine. This is the
    control that distinguishes "the ledger is bad" from "the reader disagrees with the writer".
    """
    rows = []
    for i in range(10):
        r = dict(LIVE_ROW_SCHEMA, key=[1, f"camp-M20-{i:05d}"])
        r["rep"], r["uid"] = r["key"][0], r["key"][1]
        rows.append(r)
    path = _write(tmp_path, rows)
    loaded = load_prepass(path)
    assert len(loaded) == 10
    assert all(r.rep == 1 for r in loaded)


def test_rep2_rows_are_correctly_excluded_once_the_schema_matches(tmp_path):
    """The rep-1-only rule is legitimate and still enforced — the defect is that it never gets to
    apply. With flat fields present, rep-2 rows are dropped and rep-1 rows survive, which is the
    intended behaviour and confirms the filter itself is not what is broken."""
    rows = []
    for i in range(6):
        rep = 1 if i % 2 == 0 else 2
        r = dict(LIVE_ROW_SCHEMA, key=[rep, f"camp-M20-{i:05d}"])
        r["rep"], r["uid"] = rep, r["key"][1]
        rows.append(r)
    path = _write(tmp_path, rows)
    assert len(load_prepass(path)) == 3


def test_THE_CONSEQUENCE_an_empty_pool_reports_the_bug_as_a_SUBSTRATE_FACT(tmp_path):
    """**The part that makes this worth fifteen cycles of escalation.**

    With an empty pool the assembled packet does not fail, warn, or return nothing. It emits a
    confident statement about the world:

        (no residue recorded at this distance)
        SPARSITY (what the substrate did not record — shipped as measured):
          no residue exists at this distance for this task.
          D[COUNT-REDACTED]: NOT-RUN-FOR-LACK-OF-RESIDUE (no eligible records)

    "no residue EXISTS" and "the loader rejected every row" are conflated into one message, and
    the sparsity report — whose entire purpose is honest accounting of what the substrate did not
    record — is the component asserting it. This is the answering-outside-your-domain class at
    pipeline scale, in production rather than in my own modules.
    """
    from ergon.probe.assemble import assemble_retrieved, select_residue

    rows = [dict(LIVE_ROW_SCHEMA, key=[1, f"camp-M20-{i:05d}"]) for i in range(10)]
    path = _write(tmp_path, rows)
    pool = load_prepass(path)
    assert pool == []

    body = assemble_retrieved(task_uid="camp-M20-00000", stratum="D0",
                              records=select_residue(pool, stratum="D0",
                                                     target_uid="camp-M20-00000"),
                              tau={"p1_prepass": 10 ** 9}).body
    assert "no residue" in body.lower()
    # It asserts non-existence, not non-retrieval. That is the conflation.
    assert "exists" in body.lower() or "NOT-RUN-FOR-LACK-OF-RESIDUE" in body


@pytest.mark.parametrize("field", ["rep", "uid"])
def test_the_missing_fields_are_named_so_the_fix_is_unambiguous(field):
    """Ergon is not mine to patch, so the finding has to be actionable without a diff: the two
    fields `load_prepass` needs, and which reader already gets them right."""
    assert field not in LIVE_ROW_SCHEMA
    assert field in ("rep", "uid")
