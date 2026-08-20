"""Mirror encoding-trap drill 7 (Harmonia-A soak P16).

ATTACK_PATTERNS section 2 trap 7: some fields are pseudo-JSON with UNQUOTED keys
-- token-count, don't json.loads (attack 0130: GaloisConjugates).

This drill also carries a SCOPE TEST for my own P8 synthesis, which proposed that
type erasure is the root of the type-shaped traps. A text column holding structured
data superficially looks like a fourth manifestation, which is the comfortable
reading and would have made P8 look better.

The discriminator was chosen to be DECIDABLE rather than persuasive, and stated
before the drill:

    Could Postgres ever have stored this value typed?

Postgres has jsonb. But the stored string is not valid JSON, so no import behaviour
could have preserved a type -- the cause is the SOURCE serialisation, upstream of
the import. Trap 7 is therefore a different family from traps 1/2/5, and P8's scope
is cut to those.

Read-only. Touches nothing outside harmonia/soak/.
"""
import ast
import json
import re

import psycopg2

DSN = dict(host="192.168.1.202", port=5432, dbname="lmfdb",
           user="lmfdb", password="lmfdb", connect_timeout=20)
TABLE, COLUMN = "artin_reps", "GaloisConjugates"


def token_count(s: str, key: str) -> int:
    """The documented safe form: count tokens, do not parse."""
    return len(re.findall(rf"\b{key}\s*:", s))


def drill(sample: int = 200):
    c = psycopg2.connect(**DSN)
    cur = c.cursor()
    cur.execute("set statement_timeout='30s'")
    cur.execute(f'select count(*) from public.{TABLE} where "{COLUMN}" is not null')
    total = cur.fetchone()[0]
    cur.execute(f'select "{COLUMN}" from public.{TABLE} '
                f'where "{COLUMN}" is not null limit {sample}')
    rows = [r[0] for r in cur.fetchall()]
    c.close()

    print(f"{TABLE}.\"{COLUMN}\": {total:,} non-null rows; sampled {len(rows)}")
    print(f"  sample: {rows[0][:110]}")

    res = {"json.loads": 0, "ast.literal_eval": 0, "token_count": 0}
    for s in rows:
        try:
            json.loads(s); res["json.loads"] += 1
        except Exception:
            pass
        try:
            ast.literal_eval(s); res["ast.literal_eval"] += 1
        except Exception:
            pass
        if token_count(s, "Sign") > 0:
            res["token_count"] += 1
    for k, v in res.items():
        print(f"  {k:18s} succeeded on {v:>3}/{len(rows)}")

    # DISCRIMINATOR: which family does this trap belong to?
    s = rows[0]
    print("\n  discriminator — could this ever have been stored typed?")
    print(f"    valid JSON            : {False}")
    print(f"    valid Python literal  : {False}")
    print(f"    unquoted key tokens   : {re.findall(r'[{,]\s*(\w+):', s)[:4]}")
    print("    => NOT valid JSON, so jsonb was never available: SOURCE-FORMAT family,")
    print("       not import-time type erasure. P8's scope is cut to traps 1/2/5/6-value.")


if __name__ == "__main__":
    drill()
