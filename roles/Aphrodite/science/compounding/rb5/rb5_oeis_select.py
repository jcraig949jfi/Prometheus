"""RB-5 part (b): OEIS selection (forensic, not a disposition). Criteria fixed
BEFORE any witness search; none of them refers to the fold DSL.

Sources (cached under rb5/cache/, fetched 2026-09-27):
  oeis_keyword_core_*.json  OEIS search 'keyword:core' (anonymous access returns
                            the first ~110 results in OEIS's own ranking)
  stripped.gz, names.gz     the OEIS bulk files (all sequences' leading terms)
SMALL-TERMS filter (all strata): >= 14 known terms; |a(i)| <= 10^30 for the first
  14 (below the DSL ceiling 10^40); >= 3 distinct values among them.
Strata (lowest A-numbers first = OEIS's historical order, deterministic):
  CORE     keyword:core sequences passing SMALL-TERMS.
  CLASSIC  the first 250 sequences from A000001 passing SMALL-TERMS (no
           recurrence filter: a representative slice of the 'classic' OEIS).
  LINREC   the first 150 sequences (not in CORE/CLASSIC) whose first
           min(20, len) terms satisfy a(n) = c1 a(n-1) + ... + cd a(n-d) + c0,
           d <= 3, integer |ci| <= 9 (Gauthier-Urban-style 'simple recurrence').
  NONLIN   the first 100 sequences (not above) satisfying, on the same terms, one of
           a(n) = (p n + q) a(n-1) + r            (P-recursive order 1, p != 0)
           a(n) = a(n-1)^2 + p a(n-1) + q
           a(n) = a(n-1) a(n-2) + q
           with integer |p|, |q|, |r| <= 9 and n the 0-based position in the data.
"""
import glob
import gzip
import json
import re
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
NMIN, BOUND, NREC = 14, 10 ** 30, 20
QUOTA = {"CLASSIC": 250, "LINREC": 150, "NONLIN": 100}


def small(t):
    return (len(t) >= NMIN and all(abs(x) <= BOUND for x in t[:NMIN])
            and len(set(t[:NMIN])) >= 3)


def solve(rows, rhs):
    """Exact solution of the square-or-overdetermined system (first nonsingular
    square subset by Gaussian elimination on all rows), then verified on all rows."""
    n = len(rows[0])
    A = [[Fraction(x) for x in r] + [Fraction(y)] for r, y in zip(rows, rhs)]
    piv_rows, col = [], 0
    M = [r[:] for r in A]
    r = 0
    for col in range(n):
        p = next((i for i in range(r, len(M)) if M[i][col] != 0), None)
        if p is None:
            return None
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][col] != 0:
                f = M[i][col] / M[r][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    sol = [M[i][n] / M[i][i] for i in range(n)]
    for row in A:
        if sum(a * s for a, s in zip(row[:n], sol)) != row[n]:
            return None
    return sol


def fits(sol, bound=9):
    return sol is not None and all(s.denominator == 1 and abs(s) <= bound for s in sol)


def linrec(t):
    t = t[:NREC]
    for d in (1, 2, 3):
        if len(t) - d < d + 4:
            continue
        rows = [[t[n - i] for i in range(1, d + 1)] + [1] for n in range(d, len(t))]
        sol = solve(rows, t[d:])
        if fits(sol):
            return {"kind": "linrec", "d": d, "coef": [int(s) for s in sol]}
    return None


def nonlin(t):
    t = t[:NREC]
    forms = [
        ("prec1", lambda n: [n * t[n - 1], t[n - 1], 1], 1),
        ("square", lambda n: [t[n - 1] ** 2, t[n - 1], 1], 1),
        ("product2", lambda n: [t[n - 1] * t[n - 2], 1], 2),
    ]
    for name, row, s in forms:
        rows = [row(n) for n in range(s, len(t))]
        sol = solve(rows, t[s:])
        if fits(sol) and (name != "prec1" or sol[0] != 0) and (name != "square" or sol[0] == 1):
            return {"kind": name, "coef": [int(x) for x in sol]}
    return None


def load_names():
    out = {}
    with gzip.open(CACHE / "names.gz", "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("A"):
                a, _, nm = line.partition(" ")
                out[a] = nm.strip()
    return out


def main():
    core = {}
    for fn in sorted(glob.glob(str(CACHE / "oeis_keyword_core_*.json"))):
        for x in json.loads(Path(fn).read_text(encoding="utf-8")):
            core["A%06d" % x["number"]] = x
    names = load_names()
    counts = {"stripped_scanned": 0, "small_terms": 0}
    sel = {}
    fill = {k: 0 for k in QUOTA}
    with gzip.open(CACHE / "stripped.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("A"):
                continue
            a, _, data = line.partition(" ")
            terms = [int(x) for x in data.strip().strip(",").split(",") if re.fullmatch(r"-?\d+", x)]
            counts["stripped_scanned"] += 1
            if not small(terms):
                continue
            counts["small_terms"] += 1
            strata = []
            if a in core:
                strata.append("CORE")
            if fill["CLASSIC"] < QUOTA["CLASSIC"]:
                strata.append("CLASSIC")
            need = fill["LINREC"] < QUOTA["LINREC"] or fill["NONLIN"] < QUOTA["NONLIN"]
            lr = linrec(terms) if (need or strata) else None
            nl = None if lr or not (need or strata) else nonlin(terms)
            if lr and not strata and fill["LINREC"] < QUOTA["LINREC"]:
                strata.append("LINREC")
            if nl and not strata and fill["NONLIN"] < QUOTA["NONLIN"]:
                strata.append("NONLIN")
            for s in strata:
                if s in fill:
                    fill[s] += 1
            if strata:
                sel[a] = {"A": a, "name": names.get(a, ""), "terms": terms[:NREC],
                          "strata": strata, "recurrence": lr or nl}
            if all(fill[k] >= QUOTA[k] for k in QUOTA) and int(a[1:]) > max(
                    int(k[1:]) for k in core):
                break
    counts["core_listed"] = len(core)
    counts["core_small"] = sum(1 for v in sel.values() if "CORE" in v["strata"])
    counts.update({"stratum_" + k: sum(1 for v in sel.values() if k in v["strata"])
                   for k in ("CORE", "CLASSIC", "LINREC", "NONLIN")})
    counts["selected_unique"] = len(sel)
    counts["last_A_scanned"] = a
    (CACHE / "oeis_selection_rb5.json").write_text(
        json.dumps({"criteria": __doc__, "counts": counts,
                    "sequences": sorted(sel.values(), key=lambda x: x["A"])}, indent=0),
        encoding="utf-8")
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
