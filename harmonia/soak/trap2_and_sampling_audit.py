"""Trap 2 drill + an audit of my own sampling probe (Harmonia-A soak P9).

Two things happen here, and the second matters more.

1. TRAP 2 (ATTACK_PATTERNS section 2): big values overflow ::int -- always
   ::numeric. This is run as a TEST OF P8'S PREDICTION, not as a fresh drill:
   P8 claimed type erasure is the root of the type-shaped traps, which predicts
   trap 2 must fire here. A refutation would have cost P8's synthesis.

2. SAMPLING AUDIT. The three casts reported mutually inconsistent maxima, and the
   available story was "the casts disagree" -- a striking and completely false
   finding about Postgres. The truth is that LIMIT without ORDER BY draws a
   DIFFERENT arbitrary subset per execution, so every "sample max" figure in this
   soak (including P4's) is run-dependent.

   What the defect kills: every printed maximum.
   What it spares: the DIVERGENCE verdicts, because those compare two aggregates
   computed over one identical subquery within a single query.
   The fix is determinism (ORDER BY / full-table aggregate), NOT a bigger sample.

Read-only. No writes to any database.
"""
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, dbname="lmfdb",
           user="lmfdb", password="lmfdb", connect_timeout=20)
INT32 = 2**31 - 1
SAMPLE = 200_000


def trap2(cur, table: str, col: str):
    print(f"--- trap 2 on {table}.{col} (int32 max {INT32:,}) ---")
    for label, expr in [("::int  (documented failure)", f'max("{col}"::int)'),
                        ("::bigint", f'max("{col}"::bigint)'),
                        ("::numeric (documented safe)", f'max("{col}"::numeric)')]:
        try:
            cur.execute(f"""select {expr} from (select "{col}" from public.{table}
                            where "{col}" ~ '^[0-9]+$' limit {SAMPLE}) s""")
            print(f"  {label:30s} -> {cur.fetchone()[0]}")
        except Exception as e:
            cur.connection.rollback()
            print(f"  {label:30s} -> RAISES: {str(e).strip()[:70]}")


def sampling_audit(cur, table: str, col: str, runs: int = 4):
    """Is my own probe deterministic? Suspect the instrument before the target."""
    print(f"\n--- sampling audit: {runs} identical runs ---")
    vals = []
    for i in range(runs):
        cur.execute(f"""select max(v::numeric) from (select "{col}" v from public.{table}
                        where "{col}" ~ '^[0-9]+$' limit {SAMPLE}) s""")
        v = cur.fetchone()[0]
        vals.append(v)
        print(f"  run {i+1}: {v}")
    print(f"  deterministic: {len(set(vals)) == 1}")

    # The divergence verdict is computed WITHIN one query, so it survives.
    cur.execute(f"""select max(v), max(v::numeric)::text from (select "{col}" v
                    from public.{table} where "{col}" ~ '^[0-9]+$' limit {SAMPLE}) s""")
    lex, num = cur.fetchone()
    print(f"  within-query divergence still holds: lex={lex!r} numeric={num!r} "
          f"differ={lex != num}")


if __name__ == "__main__":
    c = psycopg2.connect(**DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='25s'")
    trap2(cur, "ec_curvedata", "degree")
    sampling_audit(cur, "ec_curvedata", "degree")
    c.close()
