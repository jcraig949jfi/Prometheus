"""The pre-pass wire contract: two producers, one loader.

Filed by Techne (cycle 049) against HITL #78 / #192 / #209, under James's 2026-08-23
ruling lifting the read-only constraint on other roles' code.

TWO wire formats reach `load_prepass`, and until this file neither was written down:

  FLAT  (5 ledgers, 1,852 rows)  {"uid": ..., "rep": 1, "domain": ..., "attempt_text": ...}
  KEY   (2 ledgers, 1,604 rows)  {"key": [rep, uid], "attempt_text": ..., ...}

`campaign.py::best()` reads the KEY form correctly; `load_prepass` read only the FLAT
form, so every KEY-form row was silently dropped (1,248 rows -> 0 accepted).

These tests pin BOTH forms so the next producer cannot drift without going red.
"""
import json

import pytest

from ergon.probe import assemble as A
from ergon.probe.assemble import FirewallViolation


def _write(p, *rows):
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return p


# --------------------------------------------------------------- KEY form (the defect)

def test_key_tuple_rep1_row_is_accepted(tmp_path):
    """The campaign producer writes rep inside `key`; it must not be read as absent."""
    p = _write(tmp_path / "p1_prepass.jsonl",
               {"key": [1, "camp-M20-00000"], "attempt_text": "a", "derives_from_gold": False})
    recs = A.load_prepass(p)
    assert len(recs) == 1, "KEY-form rep-1 row was dropped — this is HITL #78"
    assert recs[0].rep == 1


def test_key_tuple_rep2_row_is_still_dropped(tmp_path):
    """Reading the right field must not weaken the rep-2 exclusion (prereg §4.2)."""
    p = _write(tmp_path / "p1_prepass.jsonl",
               {"key": [2, "camp-M20-00000"], "attempt_text": "b"})
    assert A.load_prepass(p) == []


def test_uid_is_lifted_from_key_not_silently_defaulted_to_seq(tmp_path):
    """`best()` keys on (rep, uid); the loader must agree or the two indexes diverge."""
    p = _write(tmp_path / "p1_prepass.jsonl",
               {"key": [1, "camp-M20-00007"], "attempt_text": "a"})
    rec = A.load_prepass(p)[0]
    assert rec.uid == "camp-M20-00007"
    assert rec.record_id == "camp-M20-00007", "record_id fell back to seq — uid was not lifted"


def test_firewall_still_fires_on_key_form_rows(tmp_path):
    """The gold screen must not be reachable-around by using the other wire format."""
    p = _write(tmp_path / "p1_prepass.jsonl",
               {"key": [1, "u1"], "gold_bool": True})
    with pytest.raises(FirewallViolation, match="gold"):
        A.load_prepass(p)


# ------------------------------------------------------- FLAT form (regression guard)

def test_flat_form_behaviour_is_bit_for_bit_unchanged(tmp_path):
    """5 live ledgers use the FLAT form. Fixing KEY must not perturb them."""
    p = _write(tmp_path / "probe_prepass.jsonl",
               {"uid": "t1", "rep": 1, "domain": "ood_coprime", "attempt_text": "a"},
               {"uid": "t1", "rep": 2, "domain": "ood_coprime", "attempt_text": "b"})
    recs = A.load_prepass(p)
    assert len(recs) == 1 and recs[0].rep == 1 and recs[0].uid == "t1"
    assert recs[0].body == "a"


# --------------------------------------------- the leakage the 100%-drop was hiding

def test_prose_can_be_withheld_explicitly_by_the_caller(tmp_path):
    """The count-family prose channel is a measured answer oracle (45% vs 25% chance).

    Routing it was decided by a FILENAME PREFIX (`ledger_id.startswith("nearmiss")`) — a
    proxy. The campaign ledger carries no `ledger_id` at all, so it fell to the default
    `probe_prepass` and would have shipped RAW COUNT-FAMILY PROSE the moment the rep bug
    was fixed. The caller that knows the family must be able to say so.
    """
    p = _write(tmp_path / "p1_prepass.jsonl",
               {"key": [1, "u1"], "attempt_text": "I counted 7 primes, so the answer is 7."})
    rec = A.load_prepass(p, withhold_prose=True)[0]
    assert "7" not in rec.body, "raw count-family prose reached the packet body"
    assert "method projection" in rec.body or "no recognizable method" in rec.body


def test_withhold_prose_default_preserves_the_legacy_inference(tmp_path):
    """Default must not silently re-redact the 5 live FLAT ledgers other roles are running."""
    p = _write(tmp_path / "probe_prepass.jsonl",
               {"uid": "t1", "rep": 1, "attempt_text": "plain trace"})
    assert A.load_prepass(p)[0].body == "plain trace"


def test_nearmiss_prefix_still_projects_when_no_policy_is_given(tmp_path):
    p = _write(tmp_path / "nearmiss_mix.jsonl",
               {"uid": "t1", "rep": 1, "ledger_id": "nearmiss_mix-M30",
                "attempt_text": "I used Miller-Rabin and got 7."})
    body = A.load_prepass(p)[0].body
    assert "7" not in body and "method projection" in body
