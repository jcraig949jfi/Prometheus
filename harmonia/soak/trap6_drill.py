"""Mirror encoding-trap drill 6 (Harmonia-A soak P5).

ATTACK_PATTERNS section 2 trap 6: cross-table keys differ in SPELLING -- Artin
conductors are float-strings ('12435.0') while newform levels are integer strings
('1000'), so a raw join intersects nothing (attack 0130).

The lesson carried from P4 is structural here: a raw-join zero has TWO possible
causes -- a spelling artifact, or key domains that genuinely do not meet -- and
they demand opposite responses. So the discriminator (compare numeric ranges) is
designed into this script rather than reached for after a suspicious result.

Read-only. No writes to any database.
"""
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, dbname="lmfdb",
           user="lmfdb", password="lmfdb", connect_timeout=20)


def drill():
    c = psycopg2.connect(**DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='45s'")

    # TRIAGE FIRST: a zero is uninterpretable without the probed cardinalities.
    cur.execute('select count(distinct "Conductor") from public.artin_reps '
                'where "Conductor" is not null')
    n_a = cur.fetchone()[0]
    cur.execute("select count(distinct level) from public.mf_newforms where level is not null")
    n_b = cur.fetchone()[0]
    print(f"TRIAGE distinct keys: artin={n_a:,}  newforms={n_b:,}")

    cur.execute("""select count(*) from
      (select distinct "Conductor" k from public.artin_reps where "Conductor" is not null) a
      join (select distinct level k from public.mf_newforms where level is not null) b using (k)""")
    raw = cur.fetchone()[0]

    cur.execute("""select count(*) from
      (select distinct "Conductor"::numeric k from public.artin_reps
         where "Conductor" ~ '^[0-9.]+$') a
      join (select distinct level::numeric k from public.mf_newforms
              where level ~ '^[0-9]+$') b using (k)""")
    norm = cur.fetchone()[0]
    print(f"RAW string join       : {raw:,}")
    print(f"NORMALIZED ::numeric  : {norm:,}  ({norm/n_b:.1%} of newform levels)")

    # DISCRIMINATOR: spelling artifact vs genuinely disjoint domains.
    cur.execute("""select min("Conductor"::numeric), max("Conductor"::numeric)
                   from public.artin_reps where "Conductor" ~ '^[0-9.]+$'""")
    a_lo, a_hi = cur.fetchone()
    cur.execute("select min(level::numeric), max(level::numeric) from public.mf_newforms "
                "where level ~ '^[0-9]+$'")
    b_lo, b_hi = cur.fetchone()
    overlap = max(a_lo, b_lo) <= min(a_hi, b_hi)
    print(f"ranges: artin [{a_lo}, {a_hi}]  newforms [{b_lo}, {b_hi}]  overlap={overlap}")
    print(f"VERDICT: spelling artifact (not disjoint domains) = {raw == 0 and norm > 0 and overlap}")
    c.close()


if __name__ == "__main__":
    drill()
