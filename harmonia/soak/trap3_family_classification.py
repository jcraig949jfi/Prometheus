"""Which root-cause family does mirror trap 3 belong to? (soak P41, rotation (b))

ATTACK_PATTERNS §2's ROOT CAUSE note (HARMA-P8, narrowed P16) sorts the traps into
ERASURE (1, 2, 5, value-side of 6 -- casts fix these), SOURCE-SERIALIZATION (7 --
casts do NOT), and IDENTIFIER-CASING (8). Trap 3 (arrays are Postgres literals)
is NOT classified by that note.

Decidable by one measurement: does a SERVER-SIDE cast recover the structure?

v1 of this script scanned 4000 columns with a query each and timed out at 2 min.
Narrowed to artin_reps, which carries trap 7's named specimen (GaloisConjugates)
and array-shaped columns alongside it. Read-only; no writes.
"""
import psycopg2

DSN = dict(host="192.168.1.202", port=5432, user="lmfdb", password="lmfdb", connect_timeout=15)
TBL = "artin_reps"
CANDIDATES = ["BadPrimes", "HardPrimes", "GalConjSigns", "GaloisConjugates"]


def calibrate(cur):
    cur.execute("select ('{1,2,3}'::int[])[2]")
    a = cur.fetchone()[0] == 2
    try:
        cur.execute("select '{a: 1}'::json"); cur.fetchone(); p = False
    except Exception:
        cur.connection.rollback(); p = True
    return a, p


def try_cast(cur, col, cast):
    try:
        cur.execute(f'select ("{col}"::{cast}) from "{TBL}" where "{col}" is not null limit 20')
        cur.fetchall(); return True, ""
    except Exception as e:
        cur.connection.rollback(); return False, type(e).__name__


with psycopg2.connect(dbname="lmfdb", **DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = 20000")
        a_ok, p_ok = calibrate(cur)
        print(f"CALIBRATION  array cast works: {a_ok} | pseudo-JSON rejected: {p_ok}")
        if not (a_ok and p_ok):
            raise SystemExit("calibration failed — result uninterpretable (trap 4)")

        print(f"\n{'column':20s} {'sample':30s} {'int[]':8s} {'numeric[]':11s} {'json':10s}")
        print("-" * 86)
        rows = {}
        for col in CANDIDATES:
            cur.execute(f'select "{col}" from "{TBL}" where "{col}" is not null limit 1')
            r = cur.fetchone()
            sample = (str(r[0])[:28] if r else "(none)")
            res = {}
            for cast in ("int[]", "numeric[]", "json"):
                ok, err = try_cast(cur, col, cast)
                res[cast] = "YES" if ok else f"no({err[:6]})"
            rows[col] = (sample, res)
            print(f"{col:20s} {sample:30s} {res['int[]']:8s} {res['numeric[]']:11s} {res['json']:10s}")
        print("-" * 86)

        arraycols = [c for c in CANDIDATES if c != "GaloisConjugates"]
        arr_ok = sum(rows[c][1]["int[]"] == "YES" or rows[c][1]["numeric[]"] == "YES"
                     for c in arraycols)
        gj = rows["GaloisConjugates"][1]
        print(f"array-shaped columns recovered by a server-side cast : {arr_ok}/{len(arraycols)}")
        print(f"GaloisConjugates (trap 7) recovered by ::json        : {gj['json']}")
        print()
        # client-side half of trap 3: what Python does with the same literal
        lit = rows[arraycols[0]][0]
        import ast
        try:
            parsed = ast.literal_eval(lit); kind = type(parsed).__name__
        except Exception as e:
            kind = f"raises {type(e).__name__}"
        print(f"CLIENT SIDE — ast.literal_eval({lit[:22]}...) -> {kind}")
        print("  (trap 3's actual danger: a Postgres array literal is valid PYTHON SET syntax)")
