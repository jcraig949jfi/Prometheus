"""Controls for the lexeme_df rebuild (pan.refresh.rebuild_lexeme_df), run against session-only
TEMP tables on the Pan database (nothing in schema pan is touched). Skips when the database is
unreachable.

POSITIVE  the rebuilt table holds ts_stat's document frequencies of the chunk corpus
NEGATIVE  a second rebuild gives the same rows and leaves no lexeme_df_new / lexeme_df_old behind;
          the primary key and the table comment survive the swap
CHEAT     a rebuild that fails while building leaves the old table and its rows untouched; a swap
          that hits lock_timeout keeps the old table, cleans up, and reports None (not a count)
"""
import pytest
from psycopg2.errors import LockNotAvailable

from pan.refresh import rebuild_lexeme_df

S = "pg_temp"


@pytest.fixture()
def conn():
    from pan import db
    try:
        c = db.connect()
    except Exception as e:  # pragma: no cover - environment dependent
        pytest.skip("database unreachable: {}".format(e))
    cur = c.cursor()
    cur.execute("create temp table chunk (tsv tsvector)")
    cur.execute("""insert into pg_temp.chunk values (to_tsvector('english', 'falsify the latch')),
                   (to_tsvector('english', 'latch and gate')), (to_tsvector('english', 'gate gate gate'))""")
    cur.execute("create temp table lexeme_df (lexeme text primary key, ndoc integer not null, nentry integer not null)")
    cur.execute("insert into pg_temp.lexeme_df values ('stale', 9, 9)")
    cur.execute("comment on table pg_temp.lexeme_df is 'df of every lexeme'")
    c.commit()
    yield c
    c.rollback()
    c.close()


def table(c):
    cur = c.cursor()
    cur.execute("select lexeme, ndoc, nentry from pg_temp.lexeme_df order by lexeme")
    return cur.fetchall()


def leftovers(c):
    cur = c.cursor()
    cur.execute("""select relname from pg_class where relnamespace = pg_my_temp_schema()
                   and relname in ('lexeme_df_new', 'lexeme_df_old')""")
    return [r[0] for r in cur.fetchall()]


def test_positive_frequencies(conn):
    assert rebuild_lexeme_df(conn, schema=S) == 3
    assert table(conn) == [("falsifi", 1, 1), ("gate", 2, 4), ("latch", 2, 2)]


def test_negative_repeatable_and_tidy(conn):
    first = (rebuild_lexeme_df(conn, schema=S), table(conn))
    assert (rebuild_lexeme_df(conn, schema=S), table(conn)) == first
    assert leftovers(conn) == []
    cur = conn.cursor()
    cur.execute("select obj_description('pg_temp.lexeme_df'::regclass)")
    assert cur.fetchone()[0] == "df of every lexeme"
    cur.execute("""select indexrelid::regclass::text from pg_index
                   where indrelid = 'pg_temp.lexeme_df'::regclass and indisprimary""")
    assert cur.fetchone()[0].endswith("lexeme_df_pkey")


def test_cheat_failed_build_keeps_old(conn):
    cur = conn.cursor()
    cur.execute("alter table pg_temp.chunk rename column tsv to body")   # the build query now fails
    conn.commit()
    with pytest.raises(Exception):
        rebuild_lexeme_df(conn, schema=S)
    assert table(conn) == [("stale", 9, 9)]
    assert leftovers(conn) == []


class _LockedCursor:
    """Wraps a real cursor; the first rename of the live table raises lock_timeout."""
    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, *a):
        if "rename to lexeme_df_old" in sql:
            raise LockNotAvailable("canceling statement due to lock timeout")
        return self._cur.execute(sql, *a)

    def __getattr__(self, name):
        return getattr(self._cur, name)


class _LockedConn:
    def __init__(self, c):
        self._c = c

    def cursor(self):
        return _LockedCursor(self._c.cursor())

    def __getattr__(self, name):
        return getattr(self._c, name)


def test_cheat_swap_timeout_keeps_old(conn):
    assert rebuild_lexeme_df(_LockedConn(conn), schema=S) is None
    assert table(conn) == [("stale", 9, 9)]
    assert leftovers(conn) == []
