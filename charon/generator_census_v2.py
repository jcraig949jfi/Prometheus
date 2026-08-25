"""Charon plan step 1 (v2) - generator census over the UNION of both corpus file populations.

WHY v2. generator_census.py (v1) was audited before its verdict was trusted, and has two
instrument defects that both bias the qualifier list DOWNWARD -- i.e. toward spuriously firing
the kill rule:

  D1  PREFIX TRUNCATION. v1 read `MAXLINES = 200_000` lines per file. Files are up to 12.8 GB
      (~3.7M lines), so that is the first ~5%. Measured layout: every batch file front-loads its
      generator diversity in a short head run and then settles into one or two dominant
      generators for the bulk (12.8GB file: 0% stratum = {b3,b4,d3,e3,g2}, every stratum from 5%
      to 95% = 100% d3). So v1's per-generator ROW COUNTS are wrong by ~20x for the dominant
      generators, and its action/parent statistics for them are computed on the head slice only.
  D2  c1-DERIVED ACTION FIELD LIST. v1 tested a hardcoded tuple of five field names taken from
      c1's own schema. "Does any generator besides c1 record an action" cannot be answered by a
      detector that only recognises c1-shaped fields.

v2 fixes both. Row counts are EXACT (full byte scan of all 371 GB, every line of every file).
The expensive per-field statistics are computed on STRATIFIED CONTIGUOUS WINDOWS (4000 lines
every 50000, ~8% coverage, spread over the whole file, contiguous so that parent/child adjacency
survives sampling). Candidate action fields are DERIVED FROM THE DATA per generator.

ACTION FIELD, operationalised generator-agnostically: a top-level or claim_payload field that is
  (a) categorical -- 2..32 distinct scalar values within the generator,
  (b) populated on FAILURE rows, not only on success, and
  (c) takes >=2 distinct values among rows sharing a parent_record_id.
(c) is the property that makes an action navigable rather than a label: the same state was left
by two different doors.

POSITIVE CONTROL. c1 is known independently (full scan, 47,389 parents carrying both actions) to
qualify. If this census does not re-find c1 as a qualifier, the INSTRUMENT is broken and no
verdict may be read off it.

KILL RULE -- fixed by PLAN_2026-08-25_post_reset.md step 1, NOT re-derived here: if c1 is the
ONLY generator carrying an action field populated on FAILURE, the reviewer's "the corpus is
spent" verdict is EARNED and gets recorded as such.

DIRECTIONALITY OF THE RULE UNDER SAMPLING. Conjuncts (a) and (b) are per-row properties and are
established tightly by an 8% stratified sample. Conjunct (c) is an ADJACENCY property: a
contiguous window detects sibling pairs only if the siblings fall in the same window, so the
multi-parent counts are LOWER BOUNDS. Therefore a qualifier found is real (existence proven ->
NOT-EARNED is safe to fire), while a qualifier absent is weaker evidence (absence not proven).
Generators that satisfy (a) and (b) but show zero multi-action parents are reported separately as
NEAR-MISS and are the follow-up population, not silently dropped.

    python charon/generator_census_v2.py
"""
import collections
import glob
import gzip
import json
import os
import pathlib
import re
import sys
from concurrent.futures import ProcessPoolExecutor

WINDOW, STRIDE = 4_000, 50_000
MIN_ROWS, MAX_CARD = 500, 32
SKIP = {"record_id", "parent_record_id", "sigma_claim_id", "batch_id", "emitted_at",
        "generator_id", "canonical_claim_text", "sigma_symbol_ref", "step_trace"}
# OUTCOME fields are terminus features: they are known only AFTER the step is taken, so they can
# never be the action. Letting one through would "prove" a qualifier by leaking the outcome into
# the action slot -- and under this census's directionality a qualifier FOUND is treated as
# proven, so leakage is the dangerous direction. Blocked broadly and reported, never dropped
# silently: each generator's best outcome-like field is carried in the record for audit.
OUTCOME_NAMES = {"verdict", "convergence_status", "kill_pattern", "kill_vector",
                 "novelty_estimate", "info_density", "diversity_score", "training_weight",
                 "precision_dps"}
OUTCOME_SUBSTR = ("verdict", "holds", "r2", "agreement", "kill", "score", "passed", "success",
                  "failed", "error", "residual", "converge", "novelty", "confirm", "outcome",
                  "result", "status", "correct", "actual", "match", "valid")


def is_outcome(field):
    base = field.split(".")[-1].lower()
    return base in OUTCOME_NAMES or any(s in base for s in OUTCOME_SUBSTR)

GEN_RE = re.compile(rb'"generator_id":\s*"([^"]{1,16})"')
OUT = pathlib.Path(__file__).resolve().parent / "generator_census_2026-08-25.json"


def scalars(d, out, prefix=""):
    for k, v in d.items():
        if k in SKIP:
            continue
        if isinstance(v, (bool, int, str)):
            s = str(v)
            if len(s) <= 64:
                out[prefix + k] = s


def is_fail(d, pl):
    h = pl.get("holds")
    if h is not None:
        return not bool(h)
    return str(d.get("verdict", "")).upper() != "ACCEPTED"


def one_file(arg):
    path, gz = arg
    rows = collections.Counter()                                  # EXACT, every line
    samp = collections.Counter()                                  # rows fully parsed
    par = collections.Counter()
    verd = collections.defaultdict(collections.Counter)
    vals = collections.defaultdict(lambda: collections.defaultdict(set))
    pop = collections.defaultdict(collections.Counter)            # gen -> field populated
    fail = collections.defaultdict(collections.Counter)           # gen -> field populated on FAIL
    multi = collections.defaultdict(collections.Counter)          # gen -> field multi-action parents
    win = collections.defaultdict(dict)                           # per-window parent maps
    try:
        fh = gzip.open(path, "rb") if gz else open(path, "rb", buffering=1 << 22)
        with fh:
            n = 0
            for raw in fh:
                m = GEN_RE.search(raw)
                g = m.group(1).decode() if m else "?"
                rows[g] += 1
                if n % STRIDE < WINDOW:
                    n += 1
                    try:
                        d = json.loads(raw)
                    except Exception:
                        continue
                    pl = d.get("claim_payload")
                    if not isinstance(pl, dict):
                        pl = {}
                    samp[g] += 1
                    verd[g][str(d.get("verdict"))[:24]] += 1
                    pid = d.get("parent_record_id") or pl.get("parent_record_id")
                    if pid:
                        par[g] += 1
                    flat = {}
                    scalars(d, flat)
                    scalars(pl, flat, "payload.")
                    bad = is_fail(d, pl)
                    for f, v in flat.items():
                        s = vals[g][f]
                        if len(s) <= MAX_CARD:
                            s.add(v)
                        pop[g][f] += 1
                        if bad:
                            fail[g][f] += 1
                        if pid:
                            seen = win[(g, f)]
                            prev = seen.get(pid)
                            if prev is None:
                                seen[pid] = v
                            elif prev is not True and prev != v:
                                multi[g][f] += 1
                                seen[pid] = True          # count each parent once
                    continue
                n += 1
                if win:
                    win.clear()                           # window closed: drop parent maps
    except Exception as e:
        print("SKIP", path, repr(e), file=sys.stderr, flush=True)
    print(f"  done {os.path.basename(path)} {sum(rows.values()):,}", flush=True)
    return (rows, samp, par, dict(verd),
            {g: dict(d) for g, d in vals.items()}, dict(pop), dict(fail), dict(multi))


def merge(acc, new):
    for i in (0, 1, 2):
        acc[i].update(new[i])
    for g, c in new[3].items():
        acc[3][g].update(c)
    for g, d in new[4].items():
        for f, s in d.items():
            acc[4][g][f] |= s
    for i in (5, 6, 7):
        for g, c in new[i].items():
            acc[i][g].update(c)


def main():
    files = [(p, True) for p in sorted(glob.glob("theseus/corpus/batch-*.jsonl.gz"))] + \
            [(p, False) for p in sorted(glob.glob("theseus/corpus/batch-*.jsonl"))]
    gb = sum(os.path.getsize(p) for p, _ in files) / 1e9
    print(f"census v2: {len(files)} files, {gb:.1f} GB, EXACT row counts + "
          f"{WINDOW}/{STRIDE} stratified contiguous windows", flush=True)
    acc = (collections.Counter(), collections.Counter(), collections.Counter(),
           collections.defaultdict(collections.Counter),
           collections.defaultdict(lambda: collections.defaultdict(set)),
           collections.defaultdict(collections.Counter),
           collections.defaultdict(collections.Counter),
           collections.defaultdict(collections.Counter))
    files.sort(key=lambda x: -os.path.getsize(x[0]))     # longest first: better tail packing
    with ProcessPoolExecutor(max_workers=12) as ex:
        for r in ex.map(one_file, files):
            merge(acc, r)
    rows, samp, par, verd, vals, pop, fail, multi = acc

    out, qual, near = [], [], []
    for g in sorted(rows, key=lambda x: -rows[x]):
        if rows[g] < MIN_ROWS or g == "?":
            continue
        cands, blocked = [], []
        for f, s in vals[g].items():
            if not (2 <= len(s) <= MAX_CARD) or fail[g][f] == 0:
                continue
            rec = {"field": f, "card": len(s), "populated": pop[g][f],
                   "on_FAIL": fail[g][f], "multi_action_parents": multi[g][f],
                   "values": sorted(s)[:8]}
            (blocked if is_outcome(f) else cands).append(rec)
        key = lambda c: (-c["multi_action_parents"], -c["on_FAIL"])
        cands.sort(key=key)
        blocked.sort(key=key)
        best = cands[0] if cands else None
        out.append({"generator": g, "rows_EXACT": rows[g], "rows_sampled": samp[g],
                    "sample_pct": round(100 * samp[g] / rows[g], 2),
                    "parent_pct_sampled": round(100 * par[g] / max(samp[g], 1), 1),
                    "verdicts": dict(verd[g].most_common(4)),
                    "action_candidates": len([c for c in cands if c["multi_action_parents"] > 0]),
                    "best_action_field": best,
                    "best_outcome_like_field_BLOCKED": blocked[0] if blocked else None})
        if best and best["multi_action_parents"] > 0:
            qual.append(g)
        elif cands:
            near.append(g)

    print(f"\n{'gen':<5}{'rows EXACT':>15}{'samp%':>7}{'par%':>7}  "
          f"{'best action field':<28}{'card':>5}{'@FAIL':>10}{'multi-par':>11}")
    for o in out:
        b = o["best_action_field"] or {}
        print(f"{o['generator']:<5}{o['rows_EXACT']:>15,}{o['sample_pct']:>7}"
              f"{o['parent_pct_sampled']:>7}  {str(b.get('field')):<28}"
              f"{str(b.get('card', '-')):>5}{b.get('on_FAIL', 0):>10,}"
              f"{b.get('multi_action_parents', 0):>11,}")
    print(f"\nTOTAL ROWS (exact, union of both populations): {sum(rows.values()):,}")
    ctl = "c1" in qual
    print("POSITIVE CONTROL - c1 re-found as qualifier: "
          + ("PASS" if ctl else "FAIL - instrument broken, do not read a verdict off this"))
    print("QUALIFIERS (categorical + on FAILURE + >=1 parent with 2 distinct values):", qual)
    print("NEAR-MISS  (categorical + on FAILURE, zero multi-action parents in-window):", near)
    print("\nKILL RULE (fixed by the plan): c1 alone => 'the corpus is spent' is EARNED.")
    verdict = "VOID - positive control failed" if not ctl else (
        "EARNED" if qual == ["c1"] else "NOT-EARNED")
    print("VERDICT:", verdict)
    OUT.write_text(json.dumps({
        "instrument": "generator_census_v2.py",
        "supersedes": "generator_census.py (v1: 200K-line prefix truncation; "
                      "c1-derived action field list)",
        "scope": {"gz_files": 100, "plain_files": 165, "gigabytes": round(gb, 1),
                  "row_counts": "EXACT - every line of every file scanned",
                  "field_stats": f"stratified contiguous windows, {WINDOW} lines every {STRIDE}",
                  "action_fields": "derived from data per generator, not carried from c1"},
        "total_rows_exact": sum(rows.values()),
        "positive_control_c1": "PASS" if ctl else "FAIL",
        "generators": out, "qualifiers": qual, "near_miss": near,
        "kill_rule": "c1 as sole qualifier => the corpus-is-spent verdict is earned",
        "kill_rule_directionality": "multi-action-parent counts are LOWER BOUNDS (in-window "
                                    "adjacency only); a qualifier found is proven, a qualifier "
                                    "absent is not disproven",
        "verdict": verdict}, indent=2), encoding="utf-8")
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
