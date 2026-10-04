"""Fail-closed defects in comms.identity.check (Aporia #1283, from Epimetheus #1246 /
NEW_DEFECTS.md "comms/identity.py"). No cluster needed: a fake connection
reports an arbitrary identity, so these run everywhere.

Before the repair, check() skipped every expected field whose value was None,
so a registry entry with null or missing identity fields MATCHED any
database; and a set expected_uuid was compared against a key that observe()
never produces. Both were written to FAIL on origin/main b92cdf196.
"""
from comms import identity as G


class _Cur:
    def __init__(self, row):
        self.row = row

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql):
        pass

    def fetchone(self):
        return self.row


class FakeConn:
    def __init__(self, sysid="1111", dbname="some_db"):
        self.row = (sysid, dbname)

    def cursor(self):
        return _Cur(self.row)

    def rollback(self):
        pass


FULL = {"db_system_id": "1111", "db_name": "some_db", "expected_uuid": None}


def test_positive_control_a_complete_matching_entry_is_accepted():
    v = G.check(FakeConn(), "env", registry={"env": dict(FULL)})
    assert v["ok"] is True and v["reason"] == "MATCH"


def test_negative_control_a_complete_mismatching_entry_is_refused():
    v = G.check(FakeConn(sysid="2222"), "env", registry={"env": dict(FULL)})
    assert v["ok"] is False and v["reason"] == "WRONG_ENVIRONMENT"


def test_null_identity_fields_do_not_match_any_database():
    v = G.check(FakeConn(), "env", registry={"env": {"db_system_id": None, "db_name": None}})
    assert v["ok"] is False and v["reason"] == "MALFORMED_EXPECTATION"


def test_an_entry_with_only_a_description_does_not_match():
    v = G.check(FakeConn(), "env", registry={"env": {"description": "a store"}})
    assert v["ok"] is False and v["reason"] == "MALFORMED_EXPECTATION"


def test_one_null_field_is_enough_to_refuse():
    v = G.check(FakeConn(), "env", registry={"env": {"db_system_id": "1111", "db_name": None}})
    assert v["ok"] is False and v["reason"] == "MALFORMED_EXPECTATION"


def test_a_set_expected_uuid_that_cannot_be_observed_is_refused_not_ignored():
    entry = dict(FULL, expected_uuid="0f0f0f0f-0000-0000-0000-000000000000")
    v = G.check(FakeConn(), "env", registry={"env": entry})
    assert v["ok"] is False and v["reason"] == "UNVERIFIABLE_EXPECTATION"


def test_the_committed_registry_has_no_malformed_entry():
    """Every live entry must stay admissible under the stricter rule."""
    for name, entry in G.load_registry().items():
        assert entry.get("db_system_id") and entry.get("db_name") and not entry.get("expected_uuid"), name
