"""Type-erasure census across the Prometheus databases (Harmonia-A soak P8).

Written after a FAILED trap-3 drill. No array-literal columns were found on the
lmfdb mirror, and the reassuring reading is "trap 3 is handled here". The
discriminator says otherwise: psycopg2 returns zero lists, and every column in
the mirror is declared text. Arrays are not safe -- nothing is typed.

That single property explains two traps already drilled separately:
  trap 1 (P4) numeric columns compared lexicographically  -> numbers are text
  trap 5 (P6) boolean predicates matching zero rows       -> flags are text

The cross-database control is what makes it a finding rather than an observation:
if every database were ~100% text this would be house style, not an import
artifact. Run it before attributing type erasure to any one mirror.

Read-only. No writes to any database.
"""
import collections
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, user="lmfdb", password="lmfdb",
           connect_timeout=20)
DATABASES = ("lmfdb", "prometheus_fire", "prometheus_sci")


def census(db: str):
    c = psycopg2.connect(dbname=db, **DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='20s'")
    cur.execute("""select data_type, count(*) from information_schema.columns
                   where table_schema not in ('pg_catalog','information_schema')
                   group by 1 order by 2 desc""")
    rows = cur.fetchall()
    c.close()
    total = sum(n for _, n in rows)
    text = dict(rows).get("text", 0)
    return total, text, rows


def returned_types(db: str, table: str, limit: int = 50):
    """What Python types does the driver actually hand back? A column that is a
    real ARRAY comes back as list; text comes back as str. This is the check
    that separates 'properly typed' from 'not typed at all'."""
    c = psycopg2.connect(dbname=db, **DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='20s'")
    cur.execute(f"select * from public.{table} limit {limit}")
    rows = cur.fetchall()
    tc = collections.Counter()
    for r in rows:
        for v in r:
            tc[type(v).__name__] += 1
    c.close()
    return dict(tc)


if __name__ == "__main__":
    for db in DATABASES:
        try:
            total, text, rows = census(db)
            print(f"{db:16s} {total:>5} cols  text={text:<5} ({text/total:.0%})  {rows[:5]}")
        except Exception as e:
            print(f"{db:16s} ERROR {str(e).strip()[:60]}")
    print("\ndriver-returned types (separates 'typed' from 'text'):")
    print("  lmfdb.ec_curvedata ->", returned_types("lmfdb", "ec_curvedata"))
