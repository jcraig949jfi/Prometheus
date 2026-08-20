"""Deterministic re-audit of earlier soak measurements (Harmonia-A soak P11).

P10 established that LIMIT-without-ORDER-BY sampling corrupted a published verdict.
P10 then ASSERTED that P5 and P6 were unaffected because their queries used
unsampled aggregates -- reasoning from query shape, which is the exact move P10
had just refuted. This script executes instead of asserting.

Outcome: P5 and P6 reproduce exactly. P9's OWN triage -- written inside the pass
that discovered the defect -- did not.

The polarity result is the generalisable part. The same dropped-rare-extremum
mechanism biases in OPPOSITE directions depending on what the test asks:

    divergence test (max vs max)   dropping a rare extremum CREATES divergence
                                   -> FALSE POSITIVE   (P4/P10: trap 1 over-reported)
    threshold test (max > bound)   dropping a rare extremum HIDES the overflow
                                   -> FALSE NEGATIVE   (P9/P11: trap 2 under-reported)

So "sampling is safe here" cannot be read off the query shape alone. Unsampled
aggregates (count, count-distinct, equality counts) are deterministic; anything
resting on a max or min runs full-table.

Read-only. No writes to any database.
"""
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, dbname="lmfdb",
           user="lmfdb", password="lmfdb", connect_timeout=20)
INT32 = 2**31 - 1

P5_EXPECTED = dict(artin_distinct=332_779, newform_distinct=123_365,
                   raw_join=0, normalized_join=50_835)
P6_EXPECTED = dict(rows=798_140, t=0, true=0, True_=319_289)
P9_SAMPLED_VERDICTS = dict(degree=True, adelic_level=False, conductor=False)


def reaudit_p5(cur):
    cur.execute('select count(distinct "Conductor") from public.artin_reps '
                'where "Conductor" is not null')
    a = cur.fetchone()[0]
    cur.execute("select count(distinct level) from public.mf_newforms where level is not null")
    b = cur.fetchone()[0]
    cur.execute("""select count(*) from
      (select distinct "Conductor" k from public.artin_reps where "Conductor" is not null) x
      join (select distinct level k from public.mf_newforms where level is not null) y using (k)""")
    raw = cur.fetchone()[0]
    cur.execute("""select count(*) from
      (select distinct "Conductor"::numeric k from public.artin_reps
         where "Conductor" ~ '^[0-9.]+$') x
      join (select distinct level::numeric k from public.mf_newforms
              where level ~ '^[0-9]+$') y using (k)""")
    norm = cur.fetchone()[0]
    got = dict(artin_distinct=a, newform_distinct=b, raw_join=raw, normalized_join=norm)
    return got, got == P5_EXPECTED


def reaudit_p6(cur):
    cur.execute("select count(*) from public.artin_reps")
    rows = cur.fetchone()[0]
    got = {"rows": rows}
    for lit, key in (("t", "t"), ("true", "true"), ("True", "True_")):
        cur.execute('select count(*) from public.artin_reps where "Is_Even" = %s', (lit,))
        got[key] = cur.fetchone()[0]
    return got, got == P6_EXPECTED


def reaudit_p9(cur):
    """Threshold polarity: sampling should UNDER-report here."""
    out = {}
    for col in P9_SAMPLED_VERDICTS:
        cur.execute(f"""select max(v::numeric) from (select "{col}" v
                        from public.ec_curvedata where "{col}" ~ '^[0-9]+$') s""")
        mx = cur.fetchone()[0]
        out[col] = (mx, mx > INT32)
    changed = [k for k, (_, v) in out.items() if v != P9_SAMPLED_VERDICTS[k]]
    under = [k for k, (_, v) in out.items() if v and not P9_SAMPLED_VERDICTS[k]]
    return out, changed, under


if __name__ == "__main__":
    c = psycopg2.connect(**DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='50s'")
    got5, ok5 = reaudit_p5(cur)
    print("P5 trap-6:", got5, "| reproduces:", ok5)
    got6, ok6 = reaudit_p6(cur)
    print("P6 trap-5:", got6, "| reproduces:", ok6)
    got9, changed, under = reaudit_p9(cur)
    print("P9 trap-2:", got9)
    print("  verdicts changed:", changed or "none", "| sampling under-reported:", under or "none")
    c.close()
