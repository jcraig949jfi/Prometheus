"""PAN-16 controls for the JSON Lines consolidation (pure functions; no database).

POSITIVE  a strict JSON line parses, with its top-level keys
PREFIXED  a log-prefixed line ("TAG k=v {...}") parses in 'prefixed' mode
NEGATIVE  a line with no JSON object is kept but parse_ok is False
CHEAT     a line that LOOKS like JSON but is not ("{not json") is not accepted,
          and a JSON array is accepted with no keys (the parser does not
          invent structure)
ORACLE    the line counter used as the oracle agrees with the iterator the
          writer uses, on input with blank lines, CRLF and no trailing newline
"""
from pan.consolidate import _count_nonempty, _lines, parse_line


def test_positive_strict():
    ok, mode, keys = parse_line('{"a": 1, "b": {"c": 2}}')
    assert ok and mode == "strict" and keys == ["a", "b"]


def test_prefixed():
    ok, mode, keys = parse_line('AETH01_FL {"kind": "run_start", "worlds": 6}')
    assert ok and mode == "prefixed" and keys == ["kind", "worlds"]


def test_negative_no_json():
    assert parse_line("AETH01_FL_SERVER_UP pid=118") == (False, "none", [])


def test_cheat_lookalike_and_array():
    assert parse_line("{not json") == (False, "none", [])
    assert parse_line("TAG {still not json") == (False, "none", [])
    assert parse_line("[1, 2, 3]") == (True, "strict", [])


def test_oracle_counter_agrees_with_iterator():
    data = b'{"a":1}\r\n\r\n{"a":2}\n   \nTAG {"b":3}\n{"c":4}'
    assert _count_nonempty(data) == sum(1 for _ in _lines(data)) == 4
