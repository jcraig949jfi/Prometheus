"""Mirror encoding-trap drill 5 (Harmonia-A soak P6).

ATTACK_PATTERNS section 2 trap 5: booleans are Python-literal TEXT ('True'/'False'),
not Postgres 't'/'f' (attack 0062: a first run matched zero of 24M rows).

Method note, third tightening in three passes: the DISCRIMINATOR runs FIRST here.
P4 retrofitted a diagnosis after a suspicious zero; P5 pre-stated it; P6 executes it
as the opening query. Enumerating the values actually stored BEFORE counting matches
means every zero arrives already attributable to wrong-literal rather than to
no-rows-satisfy-the-predicate.

Read-only. No writes to any database.
"""
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, dbname="lmfdb",
           user="lmfdb", password="lmfdb", connect_timeout=20)
SEMANTIC = r"(^is_|_is_|^has_|_flag$)"


def drill():
    c = psycopg2.connect(**DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='30s'")

    # TRIAGE: how much boolean-semantic surface exists, and how much is really boolean?
    cur.execute("""select count(*) filter (where data_type='boolean'), count(*)
                   from information_schema.columns
                   where table_schema='public' and lower(column_name) ~ %s""", (SEMANTIC,))
    real_bool, semantic = cur.fetchone()
    print(f"TRIAGE: {semantic} boolean-semantic columns, {real_bool} actually typed boolean")

    # DISCRIMINATOR FIRST: what is actually stored?
    cur.execute("""select table_name, column_name from information_schema.columns
                   where table_schema='public' and lower(column_name) ~ %s
                     and data_type in ('text','character varying') order by 1,2""", (SEMANTIC,))
    cols = cur.fetchall()
    print("\nDISCRIMINATOR — distinct values actually stored:")
    for t, cn in cols[:6]:
        cur.execute(f'select distinct "{cn}" from public.{t} limit 8')
        print(f"  {t}.{cn:26s} -> {[r[0] for r in cur.fetchall()]}")

    # DRILL: the four predicate forms
    t, cn = cols[0]
    cur.execute(f"select count(*) from public.{t}")
    total = cur.fetchone()[0]
    print(f"\nDRILL on {t}.\"{cn}\" ({total:,} rows):")
    for label, pred in [("Postgres 't'", f"\"{cn}\" = 't'"),
                        ("lowercase 'true'", f"\"{cn}\" = 'true'"),
                        ("Python 'True'", f"\"{cn}\" = 'True'"),
                        ("cast ::boolean", f"\"{cn}\"::boolean = true")]:
        try:
            cur.execute(f"select count(*) from public.{t} where {pred}")
            print(f"  {label:20s} -> {cur.fetchone()[0]:>10,}")
        except Exception as e:
            c.rollback()
            print(f"  {label:20s} -> ERROR {str(e).strip()[:60]}")
    c.close()


if __name__ == "__main__":
    drill()
