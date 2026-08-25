"""Charon plan step 1 — generator census over the UNION of both corpus file populations.

The generator list is DERIVED FROM THE DATA, not carried from a prior pass. That is the whole
point: a "corpus closed" verdict is live and rests on an eight-generator census that missed c1,
which is the entire basis of the current decisive experiment.

Kill rule (PLAN_2026-08-25_post_reset.md step 1): if c1 is the ONLY generator carrying an action
field that is populated on FAILURE as well as success, the reviewer's "the corpus is spent"
verdict is EARNED and gets recorded as such.

    python charon/generator_census.py
"""
import collections, glob, gzip, json, pathlib, sys

ACT = ("mutation_side", "hunter_varied_side", "original_relation", "operator_f", "step_kind")
MAXLINES = 200_000
OUT = pathlib.Path(__file__).resolve().parent / "generator_census_2026-08-25.json"

files = [(p, True) for p in sorted(glob.glob("theseus/corpus/batch-*.jsonl.gz"))] + \
        [(p, False) for p in sorted(glob.glob("theseus/corpus/batch-*.jsonl"))]

rows = collections.Counter(); par = collections.Counter()
actf = collections.defaultdict(collections.Counter)
onfail = collections.defaultdict(collections.Counter)
multi = collections.defaultdict(lambda: collections.defaultdict(set))

for i, (p, gz) in enumerate(files):
    try:
        fh = gzip.open(p, "rt", encoding="utf-8") if gz else open(p, encoding="utf-8")
        with fh:
            for ln, l in enumerate(fh):
                if ln > MAXLINES: break
                try: d = json.loads(l)
                except Exception: continue
                g = str(d.get("generator_id")); rows[g] += 1
                pl = d.get("claim_payload")
                if not isinstance(pl, dict): pl = {}
                pid = d.get("parent_record_id") or pl.get("parent_record_id")
                if pid: par[g] += 1
                a = None
                for f in ACT:
                    v = d.get(f) if d.get(f) is not None else pl.get(f)
                    if v is not None:
                        a = str(v); actf[g][f] += 1; break
                if a and pid:
                    ok = pl.get("holds")
                    if ok is None: ok = str(d.get("verdict", "")).upper() == "ACCEPTED"
                    onfail[g][bool(ok)] += 1
                    multi[g][pid].add(a)
    except Exception as e:
        print("skip", p, e, file=sys.stderr)
    if i % 25 == 0:
        print(f"  ...{i}/{len(files)} files", flush=True)

out = []
for g in sorted(rows, key=lambda x: -rows[x]):
    if rows[g] < 500: continue
    af = actf[g].most_common(1)
    out.append({"generator": g, "rows": rows[g],
                "parent_pct": round(100 * par[g] / rows[g], 1),
                "action_field": af[0][0] if af else None,
                "actions_on_FAIL": onfail[g][False], "actions_on_OK": onfail[g][True],
                "multi_action_parents": sum(1 for v in multi[g].values() if len(v) > 1)})
qual = [o["generator"] for o in out
        if o["action_field"] and o["actions_on_FAIL"] > 0 and o["multi_action_parents"] > 0]

print(f"\n{'gen':<5}{'rows':>11}{'parent%':>9}  {'action field':<22}{'act@FAIL':>10}{'act@OK':>10}{'multi-par':>11}")
for o in out:
    print(f"{o['generator']:<5}{o['rows']:>11}{o['parent_pct']:>8}%  {str(o['action_field']):<22}"
          f"{o['actions_on_FAIL']:>10}{o['actions_on_OK']:>10}{o['multi_action_parents']:>11}")
print("\nQUALIFIERS (action field + recorded on FAILURE + >=1 parent with 2 distinct actions):")
print("  ", qual)
print("\nKILL RULE: c1 alone => 'the corpus is spent' is EARNED.")
print("VERDICT:", "EARNED — c1 is the only qualifier" if qual == ["c1"]
      else f"NOT EARNED — {len(qual)} qualifiers: {qual}")
OUT.write_text(json.dumps({
    "scope": "UNION of batch-*.jsonl.gz (100 files) and batch-*.jsonl (165 files), "
             f"<= {MAXLINES} lines per file; generator list derived from data",
    "generators": out, "qualifiers": qual,
    "kill_rule": "c1 as sole qualifier => the corpus-is-spent verdict is earned",
    "verdict": "EARNED" if qual == ["c1"] else "NOT-EARNED"}, indent=2), encoding="utf-8")
print("\nwrote", OUT)
