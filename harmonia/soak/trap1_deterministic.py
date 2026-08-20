"""Deterministic re-run of the trap-1 sweep (Harmonia-A soak P10).

P4 ran this sweep on a 200,000-row LIMIT sample and reported 14 divergent columns.
P9 found the sampling non-deterministic but ARGUED the verdicts survived, because
each comparison is two aggregates over one identical subquery. This script tests
that argument instead of trusting it.

Result: the argument is wrong. Full-table gives 13, not 14. adelic_genus has
lexicographic max == numeric max == '97' -- no divergence exists -- and it appeared
divergent only because the 96 rows holding '97' (of 3,816,674) were never drawn.

The generalisable part: sampled extremum comparisons are biased toward FALSE
POSITIVES in a predictable direction, because a divergence is resolved by rare
extreme values and sampling is exactly the operation that drops rare rows. A
bigger sample shrinks the bias asymptotically while still over-reporting. The fix
is to stop sampling -- which costs nothing here: 1.1s per column over 3.8M rows.

Read-only. No writes to any database.
"""
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, dbname="lmfdb",
           user="lmfdb", password="lmfdb", connect_timeout=20)
NUMERIC_STR = r"^-?[0-9]+$"

# What P4 reported from the sampled sweep, kept for comparison.
P4_SAMPLED = {
    "adelic_genus", "adelic_index", "adelic_level", "class_deg", "conductor",
    "degree", "faltings_ratio", "id", "iso_nlabel", "min_quad_twist_disc",
    "nonmax_rad", "num_int_pts", "sha", "torsion",
}


def sweep(schema="public", table="ec_curvedata"):
    c = psycopg2.connect(**DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='45s'")
    cur.execute("""select column_name from information_schema.columns
                   where table_schema=%s and table_name=%s
                     and data_type in ('text','character varying') order by 1""",
                (schema, table))
    cols = [r[0] for r in cur.fetchall()]
    probed = empty = err = 0
    hits = set()
    for col in cols:
        try:
            # NO LIMIT: deterministic by construction.
            cur.execute(f"""select max(v), max(v::numeric)::text, count(*)
                            from (select "{col}" v from {schema}.{table}
                                  where "{col}" ~ %s) s""", (NUMERIC_STR,))
            lex, num, n = cur.fetchone()
        except Exception:
            c.rollback(); err += 1; continue
        if not n:
            empty += 1; continue
        probed += 1
        if lex != num:
            hits.add(col)
    c.close()
    return cols, probed, empty, err, hits


if __name__ == "__main__":
    cols, probed, empty, err, hits = sweep()
    print(f"{len(cols)} text cols | TRIAGE empty={empty} errors={err} PROBED={probed}")
    print(f"trap 1 fires on {len(hits)} columns (deterministic, full-table)")
    print(f"P4 sampled reported {len(P4_SAMPLED)}")
    print(f"  false positives introduced by sampling: {sorted(P4_SAMPLED - hits) or 'none'}")
    print(f"  missed by sampling:                     {sorted(hits - P4_SAMPLED) or 'none'}")
    print(f"  verdict sets identical: {hits == P4_SAMPLED}")
