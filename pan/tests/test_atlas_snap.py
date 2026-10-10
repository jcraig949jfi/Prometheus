"""PAN-27 atlas snapshot: the order-free row fingerprint and the SELECT list. No database."""
import datetime as dt

from pan import atlas_snap

T = dt.datetime(2026, 10, 10, 8, 30, tzinfo=dt.timezone(dt.timedelta(hours=-4)))
ROWS = [(1, "a", T, ["x", None], 0.1, True, None), (2, "b", None, [], 2.5, False, '{"k": 1}')]


def test_fingerprint_is_order_free_and_timezone_blind():
    utc = [(1, "a", T.astimezone(dt.timezone.utc), ["x", None], 0.1, True, None), ROWS[1]]
    assert atlas_snap.fingerprint(ROWS) == atlas_snap.fingerprint(reversed(utc))
    assert atlas_snap.fingerprint(ROWS)[0] == 2


def test_fingerprint_sees_one_changed_value_and_a_duplicate_row():
    base = atlas_snap.fingerprint(ROWS)
    assert atlas_snap.fingerprint([ROWS[0], ROWS[1][:1] + ("b ",) + ROWS[1][2:]]) != base
    assert atlas_snap.fingerprint(ROWS + [ROWS[0]]) != base
    assert atlas_snap.fingerprint([]) == (0, "0000000000000000")


def test_select_keeps_simple_types_and_casts_the_rest_to_text():
    sql, kinds = atlas_snap._select("fact", [("fact_id", "bigint"), ("payload", "jsonb"), ("tags", "text[]"),
                                             ("x", "numeric(10,2)")])
    assert sql == 'select "fact_id", "payload"::text, "tags", "x"::text from atlas."fact"'
    assert kinds == ["int64", "string", "list", "string"]
