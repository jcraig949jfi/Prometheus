"""PAN-47 content REFUSE rule, without a database: the pattern exactly as migration 015 stores it, applied as the
chunker applies it (Python re, case-insensitive). Live checks (purge, parity with PostgreSQL) are in
`python -m pan access controls`."""
import re
from pathlib import Path

from pan import access

ROOT = Path(__file__).resolve().parents[1]


def _pattern():
    sql = (ROOT / "migrations" / "015_content_refuse.sql").read_text(encoding="utf-8")
    m = re.search(r"\('R-credential-content',\s*'((?:[^']|'')*)'", sql)
    return m.group(1).replace("''", "'")


def test_shapes_refused_and_placeholders_kept():
    rx = re.compile(_pattern(), re.I)
    pos, neg = access.synthetic_credentials()
    assert all(rx.search(s) for s in pos), [s[:12] for s in pos if not rx.search(s)]
    assert not any(rx.search(s) for s in neg), [s for s in neg if rx.search(s)]


def test_the_rule_does_not_refuse_its_own_source():
    """The files that define and test the rule must stay searchable: none may carry a credential-shaped literal."""
    rx = re.compile(_pattern(), re.I)
    for f in ("migrations/015_content_refuse.sql", "access.py", "chunker.py", "tests/test_content_rule.py"):
        assert not rx.search((ROOT / f).read_text(encoding="utf-8")), f
