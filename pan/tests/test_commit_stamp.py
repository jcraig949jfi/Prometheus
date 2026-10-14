"""Controls for the artifact commit stamp (pan.commits.stamp), run against session-only
TEMP tables on the Pan database (nothing in schema pan is touched). Skips when the
database is unreachable.

POSITIVE  first/last commit time and the tip sha are stamped onto a git artifact
NEGATIVE  a second run writes 0 rows; a non-git artifact with the same path is never stamped
CHEAT     a same-second tie between a commit and its child picks the child, even when plain
          "sha desc" would pick the parent; a tie with no parent relation is decided by sha,
          and repeated runs agree (the 2026-10-14 defect: the tip flipped between runs)
"""
import pytest

from pan.commits import stamp

P = "a" * 40      # parent: sorts AFTER the child under "sha desc"
K = "0" * 40      # child of P, same second
X, Y = "1" * 40, "2" * 40


@pytest.fixture()
def cur():
    from pan import db
    try:
        conn = db.connect()
    except Exception as e:  # pragma: no cover - environment dependent
        pytest.skip("database unreachable: {}".format(e))
    c = conn.cursor()
    c.execute("create temp table commit (sha text primary key, committed_at timestamptz, parents text[])")
    c.execute("create temp table commit_file (sha text, path text)")
    c.execute("""create temp table artifact (source text, host text, path text, first_commit_at timestamptz,
                 last_commit_at timestamptz, last_commit_sha text)""")
    c.execute("""insert into pg_temp.commit values
        ('c1', '2026-10-01 10:00+00', '{}'), ('c2', '2026-10-01 11:00+00', '{c1}'),
        (%s, '2026-10-01 12:00+00', '{c2}'), (%s, '2026-10-01 12:00+00', %s),
        (%s, '2026-10-01 13:00+00', '{}'), (%s, '2026-10-01 13:00+00', '{}')""", (P, K, [P], X, Y))
    c.execute("""insert into pg_temp.commit_file values ('c1','a.txt'), ('c2','a.txt'),
        ('c1','b.txt'), (%s,'b.txt'), (%s,'b.txt'), (%s,'c.txt'), (%s,'c.txt')""", (P, K, X, Y))
    c.execute("""insert into pg_temp.artifact (source, host, path) values
        ('git','repo','a.txt'), ('git','repo','b.txt'), ('git','repo','c.txt'), ('lake','SPECTREX5','a.txt')""")
    yield c
    conn.rollback()
    conn.close()


def rows(c):
    c.execute("""select source, path, to_char(first_commit_at at time zone 'UTC','HH24:MI'),
                 to_char(last_commit_at at time zone 'UTC','HH24:MI'), last_commit_sha
                 from pg_temp.artifact order by source, path""")
    return {(r[0], r[1]): r[2:] for r in c.fetchall()}


def test_positive_stamped(cur):
    assert stamp(cur, schema="pg_temp") == 3
    got = rows(cur)
    assert got[("git", "a.txt")] == ("10:00", "11:00", "c2")
    assert got[("git", "b.txt")][:2] == ("10:00", "12:00")


def test_negative_second_run_writes_nothing(cur):
    stamp(cur, schema="pg_temp")
    assert stamp(cur, schema="pg_temp") == 0
    assert rows(cur)[("lake", "a.txt")] == (None, None, None)


def test_cheat_ties(cur):
    stamp(cur, schema="pg_temp")
    got = rows(cur)
    assert got[("git", "b.txt")][2] == K           # the child, not the parent "sha desc" would pick
    assert got[("git", "c.txt")][2] == Y           # no parent relation: highest sha
    for _ in range(3):
        assert stamp(cur, schema="pg_temp") == 0   # stable across runs
        assert rows(cur) == got
