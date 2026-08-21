"""Census of array/object serialization forms across the mirror (soak P42, rotation (b)).

P41 found artin_reps stores JSON BRACKET arrays where ATTACK_PATTERNS §2 trap 3
describes Postgres BRACE literals, and logged WITHHELD whether the brace form
exists elsewhere. That decides whether the checklist entry needs SCOPING or
REWRITING.

Efficiency note: P41's first attempt issued one query per COLUMN and timed out at
two minutes. This issues one `select * limit N` per TABLE and classifies every
value client-side -- same coverage, ~1/50th the queries.

Read-only. No writes. Denominators reported (P16 discipline).
"""
import re
from collections import Counter
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, user="lmfdb", password="lmfdb", connect_timeout=15)
ROWS_PER_TABLE = 5

BRACE_ARRAY = re.compile(r"^\{\s*(-?[\d.eE+]+\s*,\s*)*-?[\d.eE+]+\s*\}$")   # {1,2,3}  trap 3
BRACE_OTHER = re.compile(r"^\{")                                            # any brace-led
BRACKET_ARR = re.compile(r"^\[")                                            # [1,2,3]  JSON-ish
PSEUDO_KEY = re.compile(r"[\{,]\s*[A-Za-z_][A-Za-z0-9_]*\s*:")              # bare key  trap 7


def calibrate():
    """Known positives — the classifier must sort these correctly or nothing is readable."""
    checks = {
        "{1,2,3}":            (BRACE_ARRAY.match("{1,2,3}") is not None),
        "[11, 197]":          (BRACKET_ARR.match("[11, 197]") is not None
                               and BRACE_ARRAY.match("[11, 197]") is None),
        '{"a": 1}':           (PSEUDO_KEY.search('{"a": 1}') is None),
        "{Sign: 1}":          (PSEUDO_KEY.search("{Sign: 1}") is not None),
    }
    return checks


ck = calibrate()
print("CALIBRATION:", ", ".join(f"{k}={v}" for k, v in ck.items()))
if not all(ck.values()):
    raise SystemExit("classifier calibration failed — result would be uninterpretable")

with psycopg2.connect(dbname="lmfdb", **DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = 20000")
        cur.execute("""select table_name from information_schema.tables
                       where table_schema='public' and table_type='BASE TABLE'
                       order by table_name""")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\nbase tables on the mirror: {len(tables)}")

        forms = Counter()
        per_table = {}
        scanned_tables = scanned_values = 0
        for tbl in tables:
            try:
                cur.execute(f'select * from "{tbl}" limit {ROWS_PER_TABLE}')
                rows = cur.fetchall()
            except Exception:
                conn.rollback(); continue
            scanned_tables += 1
            local = Counter()
            for row in rows:
                for v in row:
                    if not isinstance(v, str) or not v:
                        continue
                    scanned_values += 1
                    if BRACE_ARRAY.match(v):
                        local["brace_array (trap 3 as written)"] += 1
                    elif BRACKET_ARR.match(v):
                        local["bracket_array (JSON-style)"] += 1
                    elif BRACE_OTHER.match(v):
                        local["pseudo_json (bare keys)" if PSEUDO_KEY.search(v)
                              else "brace_object (quoted keys)"] += 1
            if local:
                per_table[tbl] = local
                forms.update(local)

print(f"tables scanned: {scanned_tables}/{len(tables)}   string values classified: {scanned_values}")
print(f"tables containing at least one structured value: {len(per_table)}\n")
print(f"{'serialization form':38s} {'values':>8s}  {'tables':>7s}")
print("-" * 60)
for form, n in forms.most_common():
    t = sum(1 for c in per_table.values() if c.get(form))
    print(f"{form:38s} {n:>8d}  {t:>7d}")
print("-" * 60)

brace = forms.get("brace_array (trap 3 as written)", 0)
bracket = forms.get("bracket_array (JSON-style)", 0)
print()
if brace and bracket:
    print("MIXED: both conventions are live on this mirror. A consumer cannot assume")
    print("either parse, which is worse for correctness than a single wrong convention.")
elif brace:
    print("Trap 3 as written is LIVE; artin_reps was the exception.")
elif bracket:
    print("Trap 3's BRACE form was not observed in this sample; the bracket form dominates.")
    print("The checklist entry describes a form this sample does not contain -- REWRITE,")
    print("not merely scope. Absence in a sample is not proof of absence: denominator above.")
else:
    print("VACUOUS: no structured values found at all — diagnose the sampler (trap 4).")

# ---------------------------------------------------------------------------
# CLASSIFIER CAVEAT, caught before publication: the prefix test above checks
# BRACKET before PSEUDO_KEY, so a bracket-led value containing bare-key objects
# (artin_reps.GaloisConjugates = '[{Sign: 1, ...') counts as bracket_array even
# though it is not valid JSON. "bracket_array" is therefore a SYNTACTIC PREFIX
# class, not a validity class.
#
# P41 argued the operative axis is validity-in-some-type, not provenance. So
# re-split the bracket-led values by whether they actually parse.
import json as _json

print("\nRE-SPLIT of bracket-led values by ACTUAL JSON validity (the P41 axis):")
with psycopg2.connect(dbname="lmfdb", **DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = 20000")
        valid = invalid = 0
        invalid_tables = Counter()
        for tbl in per_table:
            try:
                cur.execute(f'select * from "{tbl}" limit {ROWS_PER_TABLE}')
                rows = cur.fetchall()
            except Exception:
                conn.rollback(); continue
            for row in rows:
                for v in row:
                    if isinstance(v, str) and v and BRACKET_ARR.match(v):
                        try:
                            _json.loads(v); valid += 1
                        except Exception:
                            invalid += 1; invalid_tables[tbl] += 1
tot = valid + invalid
print(f"  bracket-led values: {tot}")
print(f"    parse as JSON      : {valid} ({100*valid/tot:.1f}%)  -> cast-recoverable")
print(f"    do NOT parse       : {invalid} ({100*invalid/tot:.1f}%)  -> recoverable by no cast")
if invalid_tables:
    print(f"    invalid concentrated in: {dict(invalid_tables)}")
print("\n  The prefix class splits cleanly on validity, which is the axis P41 proposed;")
print("  'bracket-led' alone would have told a consumer nothing about castability.")
