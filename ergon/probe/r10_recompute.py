"""R10 — independent re-computation of a probe headline from committed result objects.

FOR THE INDEPENDENT SEAT (Aporia; fallback Harmonia B). This script deliberately imports
NOTHING from ergon.probe — no analysis.py, no extract.py, no schema.py. Every statistic is
re-derived here from first principles against the raw ledger JSONL, so agreement with the
driver's reported numbers is a second measurement, not a second pointer to the first one
(meta-synthesis §1.6). If this file and the driver ever disagree, BOTH are suspect and the
discrepancy is the finding.

Usage:
    python ergon/probe/r10_recompute.py <ledger.jsonl> [--prom ARM] [--null ARM]

Recomputes: per-arm accuracy / parse-fail / transport census, the paired task-level
prom-null delta, a two-sided paired bootstrap (10,000 resamples, seed 0 — the preregistered
test), an exact McNemar on the discordants, and the admissibility guards (parse-fail spread,
transport rate). Prints a table and exits nonzero if the ledger is structurally unsound
(duplicate task-arm rows, missing arms, synthetic rows).
"""
import argparse
import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict


def normalize(r, gold):
    """Accept either ledger shape without importing the driver's code.

    The pilot ledgers carry flat `arm`/`uid`/`correct`; the campaign ledgers carry
    `key: [arm, uid]` and `extracted_int` with NO stored correctness flag. Deriving `correct`
    here from the manifest's gold — rather than trusting a boolean the driver wrote — is
    strictly better for R10's purpose: it removes one more thing this script has to take on
    the driver's word.
    """
    out = dict(r)
    if "arm" not in out and isinstance(out.get("key"), (list, tuple)) and len(out["key"]) == 2:
        out["arm"], out["uid"] = out["key"][0], out["key"][1]
    if "extracted" not in out and "extracted_int" in out:
        out["extracted"] = out["extracted_int"]
    if gold is not None:
        if out["uid"] not in gold:
            sys.exit(f"REFUSED: ledger uid {out['uid']!r} absent from the manifest")
        out["correct"] = (out.get("extracted") is not None
                          and out["extracted"] == gold[out["uid"]])
    elif "correct" not in out:
        sys.exit("REFUSED: ledger has no `correct` field and no --manifest was given, so "
                 "correctness cannot be independently derived. Pass --manifest.")
    return out


def load(path, manifest=None):
    rows = [json.loads(l) for l in pathlib.Path(path).read_text(encoding="utf-8").splitlines()
            if l.strip()]
    gold = None
    if manifest:
        gold = {m["uid"]: m["gold_int"] for m in
                (json.loads(l) for l in
                 pathlib.Path(manifest).read_text(encoding="utf-8").splitlines() if l.strip())}
    rows = [normalize(r, gold) for r in rows]
    bad = [r for r in rows if r.get("synthetic")]
    if bad:
        sys.exit(f"REFUSED: {len(bad)} synthetic rows in a results ledger")
    if any(isinstance(r.get("arm"), int) for r in rows):
        sys.exit("REFUSED: this looks like a PRE-PASS ledger (key = [rep, uid]), not an arms "
                 "ledger. R10 recomputes the arm contrast; point it at the arms ledger.")
    seen = Counter((r["arm"], r["uid"]) for r in rows)
    dupes = {k: v for k, v in seen.items() if v > 1}
    if dupes:
        sys.exit(f"REFUSED: duplicate task-arm rows: {list(dupes)[:5]}")
    return rows


def paired_bootstrap(deltas, n_boot=10_000, seed=0):
    """Plain-python re-derivation. Two-sided p: doubled smaller tail of the resampled mean."""
    rng = random.Random(seed)
    n = len(deltas)
    obs = sum(deltas) / n
    lo_ct = hi_ct = 0
    means = []
    for _ in range(n_boot):
        s = sum(deltas[rng.randrange(n)] for _ in range(n)) / n
        means.append(s)
    means.sort()
    ci_lo = means[int(0.025 * n_boot)]
    ci_hi = means[min(n_boot - 1, int(0.975 * n_boot))]
    le = sum(1 for m in means if m <= 0) / n_boot
    ge = sum(1 for m in means if m >= 0) / n_boot
    return obs, ci_lo, ci_hi, min(1.0, 2 * min(le, ge))


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--prom", default="F-prom-retrieved")
    ap.add_argument("--null", default="F-null")
    ap.add_argument("--manifest", default=None,
                    help="manifest JSONL; when given, `correct` is re-derived here from gold "
                         "instead of trusting the driver's stored flag (preferred)")
    args = ap.parse_args()

    rows = load(args.ledger, args.manifest)
    arms = sorted({r["arm"] for r in rows})
    by = {(r["arm"], r["uid"]): r for r in rows}
    uids = sorted({r["uid"] for r in rows})

    print(f"ledger: {args.ledger}")
    print(f"rows {len(rows)} · arms {arms} · tasks {len(uids)}\n")
    print(f"{'arm':20s} {'n':>4} {'acc':>7} {'pf':>6} {'transport-fail':>14}")
    stats = {}
    for a in arms:
        sub = [by[(a, u)] for u in uids if (a, u) in by]
        n = len(sub)
        acc = sum(1 for r in sub if r.get("correct")) / n
        pf = sum(1 for r in sub if r.get("extracted") is None) / n
        tf = sum(1 for r in sub if r.get("status") != "ok")
        stats[a] = (acc, pf, tf, n)
        print(f"{a:20s} {n:4d} {acc:7.4f} {pf:6.3f} {tf:14d}")

    # guards, re-derived
    comparable = [a for a in arms if a != "F-answer"]
    pf_spread = max(stats[a][1] for a in comparable) - min(stats[a][1] for a in comparable)
    tf_worst = max(stats[a][2] / stats[a][3] for a in arms)
    print(f"\nparse-fail spread (comparable arms): {pf_spread:.4f}  "
          f"({'OK' if pf_spread <= 0.10 else 'INADMISSIBLE-FORMAT-CONFOUNDED'})")
    print(f"worst transport-fail rate: {tf_worst:.4f}  "
          f"({'OK' if tf_worst <= 0.05 else 'TRANSPORT-COMPROMISED'})")

    # primary endpoint, re-derived
    paired = [(float(bool(by[(args.prom, u)]["correct"])), float(bool(by[(args.null, u)]["correct"])))
              for u in uids if (args.prom, u) in by and (args.null, u) in by]
    deltas = [p - q for p, q in paired]
    obs, lo, hi, p2 = paired_bootstrap(deltas)
    b = sum(1 for p_, q in paired if p_ == 1 and q == 0)
    c = sum(1 for p_, q in paired if p_ == 0 and q == 1)
    print(f"\nPRIMARY  {args.prom} - {args.null}   (n paired = {len(paired)})")
    print(f"  delta {obs:+.4f}   CI95 [{lo:+.4f}, {hi:+.4f}]   bootstrap p = {p2:.4f}")
    print(f"  McNemar exact p = {mcnemar_exact(b, c):.4f}   discordant {b} vs {c}")
    print("\nNOTE: this is a re-computation, not a verdict. Classification belongs to the")
    print("      kill authority against the preregistration (spec §4.1).")


if __name__ == "__main__":
    main()
