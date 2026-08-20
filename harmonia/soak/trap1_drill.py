"""Mirror encoding-trap drill 1 (Harmonia-A soak P4).

ATTACK_PATTERNS section 2 trap 1: numeric columns stored as TEXT, so max()
compares lexicographically (0026: max('9') > max('14')). Documented safe form:
cast ::numeric.

Two lessons are baked into this script, both learned the hard way this pass:

1. CALIBRATE THE DETECTOR BEFORE TRUSTING ITS ZERO. A known-positive control runs
   first; if the comparison cannot fire, every downstream zero is meaningless.
2. REPORT THE TRIAGE, NOT JUST THE HITS. My first run scanned 257 columns of
   prometheus_fire and found 0 -- because it had ACTUALLY PROBED 0 of them (255
   had no numeric-string rows at all). A hit count without a probed count is
   uninterpretable, and per trap 4 an all-empty result demands diagnosis rather
   than a shrug. The traps live in the lmfdb mirror, not prometheus_fire.

Read-only. No writes to any database.
"""
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, user="lmfdb", password="lmfdb",
           connect_timeout=20)
SAMPLE = 200_000
NUMERIC_STR = r"^-?[0-9]+$"


def calibrate(cur) -> bool:
    """Known positive: lexicographic max must differ from numeric max."""
    cur.execute("select max(v), max(v::numeric)::text from (values ('9'),('14'),('100')) t(v)")
    lex, num = cur.fetchone()
    print(f"CALIBRATION: lexmax={lex!r} nummax={num!r} -> fires={lex != num}")
    return lex != num


def drill(dbname: str, schema: str, table: str):
    c = psycopg2.connect(dbname=dbname, **DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='12s'")
    if not calibrate(cur):
        print("VACUOUS: detector cannot fire; aborting.")
        return
    cur.execute("""select column_name from information_schema.columns
                   where table_schema=%s and table_name=%s
                     and data_type in ('text','character varying') order by 1""",
                (schema, table))
    cols = [r[0] for r in cur.fetchall()]
    probed = empty = err = 0
    hits = []
    for col in cols:
        try:
            cur.execute(f"""select max(v), max(v::numeric)::text, count(*),
                                   count(distinct length(v))
                            from (select "{col}" v from {schema}.{table}
                                  where "{col}" ~ %s limit {SAMPLE}) s""", (NUMERIC_STR,))
            lex, num, n, lens = cur.fetchone()
        except Exception:
            c.rollback(); err += 1; continue
        if not n:
            empty += 1; continue
        probed += 1
        if lex != num:
            hits.append((col, n, lens, lex, num))
    print(f"\n{dbname}.{schema}.{table}: {len(cols)} text cols | "
          f"TRIAGE empty={empty} errors={err} ACTUALLY PROBED={probed}")
    print(f"TRAP-1 FIRES on {len(hits)}/{probed} probed columns "
          f"({SAMPLE:,}-row sample each):")
    for col, n, lens, lex, num in hits:
        print(f"  {col:24s} n={n:>7,} lens={lens:>2}  lex={lex!r:>16}  numeric={num!r}")
    c.close()


if __name__ == "__main__":
    drill("lmfdb", "public", "ec_curvedata")
