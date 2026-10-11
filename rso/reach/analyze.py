"""Preregistered analysis of a D1 ledger (PREREGISTRATION.md s6; C-013-T012 runs it, C-013-T010 froze it).

    python -m rso.reach.analyze --run-dir rso/reach/runs/D1

Unit: one lineage. Success: a CERTIFIED DISCOVERY (training-perfect hit found by search from a knock-out start,
certified by certify.py on selection + sealed lives with the oracle agreeing). Seeded controls are never counted.
Family: the five declared contrasts below, each an exact conditional test stratified by d (stats.stratified_exact),
two-sided, Holm-adjusted over the five; a contrast SEPARATES iff its Holm-adjusted p <= ALPHA. Fewer than MIN_ROUNDS
completed rounds: no contrast is read (UNDERPOWERED). Every zero is reported with its one-sided 95% upper bound.
"""
import argparse
import json
import pathlib
import statistics

from rso.reach import stats

ARMS = ("chain_strict", "chain_neutral", "X1", "X2", "X3", "X3G")
DISTANCES = (1, 3, 8)
CONTRASTS = (
    ("C1_neutral_acceptance", "chain_neutral", "chain_strict"),
    ("C2_retention", "X1", "chain_neutral"),
    ("C3_rarely_visited_selection", "X2", "X1"),
    ("C4_new_cell_admission_of_worse", "X3", "X2"),
    ("C5_behaviour_cells_vs_genotype_hash", "X3", "X3G"),
)
ALPHA = 0.05
MIN_ROUNDS = 12
CHECKPOINTS = (2_000, 20_000, 200_000)


def load(run_dir):
    run_dir = pathlib.Path(run_dir)
    rows = [json.loads(x) for x in (run_dir / "LEDGER.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    meta = json.loads((run_dir / "RUN.json").read_text(encoding="utf-8")) if (run_dir / "RUN.json").exists() else {}
    return rows, meta


def complete_rounds(rows):
    by_round = {}
    for r in rows:
        by_round.setdefault(r["round"], set()).add((r["arm"], r["d"]))
    need = {(a, d) for a in ARMS for d in DISTANCES}
    n = 0
    while n in by_round and by_round[n] == need:
        n += 1
    return n


def analyze(rows, meta=None):
    meta = meta or {}
    n = complete_rounds(rows)
    rows = [r for r in rows if r["round"] < n]
    out = dict(rounds_completed=n, run_status=meta.get("status"), alpha=ALPHA, min_rounds=MIN_ROUNDS)
    if any(r.get("certificate") and r["certificate"]["status"] == "VOID" for r in rows) \
            or meta.get("status") in ("VOID_INSTRUMENT", "VOID_CONTROLS"):
        out["status"] = "VOID"
        return out
    cells = {}
    for a in ARMS:
        for d in DISTANCES:
            rs = [r for r in rows if r["arm"] == a and r["d"] == d]
            k = sum(r["discovery"] for r in rs)
            when = sorted(r["evals"] for r in rs if r["discovery"])
            cells["%s d=%d" % (a, d)] = dict(
                arm=a, d=d, n=len(rs), discoveries=k, rate=k / len(rs) if rs else None,
                upper_95=stats.upper_bound_95(k, len(rs)) if rs else None,
                training_perfect_not_certified=sum(1 for r in rs if r["hit"] and not r["discovery"]),
                by_budget={str(b): sum(1 for w in when if w <= b) for b in CHECKPOINTS},
                median_evals_to_discovery=statistics.median(when) if when else None,
                hit_times=when,
                median_cells=statistics.median(r["cells"] for r in rs) if rs else None,
                median_distinct_genomes=statistics.median(r["distinct_genomes"] for r in rs) if rs else None,
                lineages_retaining_a_stone_at_end=sum(1 for r in rs if r["stones_retained_end"] > 0),
                lineages_evaluating_a_stone=sum(1 for r in rs if r["stones_evaluated"] > 0),
                max_stone_restored=max((r["max_stone_restored"] for r in rs), default=0))
    out["cells"] = cells
    pooled = {a: (sum(cells["%s d=%d" % (a, d)]["discoveries"] for d in DISTANCES), n * len(DISTANCES)) for a in ARMS}
    out["pooled"] = {a: dict(discoveries=k, n=m, upper_95=stats.upper_bound_95(k, m) if m else None)
                     for a, (k, m) in pooled.items()}
    if n < MIN_ROUNDS:
        out["status"] = "UNDERPOWERED"
        return out
    raw = {}
    for name, a, b in CONTRASTS:
        strata = [(cells["%s d=%d" % (a, d)]["discoveries"], n, cells["%s d=%d" % (b, d)]["discoveries"], n)
                  for d in DISTANCES]
        raw[name] = stats.stratified_exact(strata)
    adj = stats.holm(raw)
    con = {}
    for name, a, b in CONTRASTS:
        ka, kb = pooled[a][0], pooled[b][0]
        sep = adj[name] <= ALPHA
        direction = ("%s > %s" % (a, b)) if ka > kb else (("%s < %s" % (a, b)) if ka < kb else "equal")
        con[name] = dict(arm=a, versus=b, pooled=[ka, kb, n * len(DISTANCES)], p=raw[name], p_holm=adj[name],
                         verdict=("SEPARATES: " + direction) if sep else "NOT SEPARATED at this budget and n")
    out["contrasts"] = con
    out["status"] = "ANALYZED"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    rows, meta = load(a.run_dir)
    res = analyze(rows, meta)
    p = pathlib.Path(a.run_dir) / "RESULT.json"
    p.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: res.get(k) for k in ("status", "rounds_completed", "contrasts")}, indent=1))


if __name__ == "__main__":
    main()
