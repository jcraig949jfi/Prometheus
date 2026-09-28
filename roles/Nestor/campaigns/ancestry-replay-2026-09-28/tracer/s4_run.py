"""s4 tests on the production births (ANCESTRY_PREREG v4 s4 as amended through C10), COMMITTED BEFORE PRODUCTION.

Owner obligations (v4 s0): run the s4 tests on the production sample and export them. Q/verdict synthesis is Archaeon's.
Sample (v4 s4): all births, which is fewer than 200, so every birth is tested. Duplicated realisations (C7.4:
s9200006 C and s9200008 C duplicate their A arms) are ALSO run and marked duplicate_of. No case is dropped. Summaries are
given over the 9 distinct simulations, with the duplicates reported separately.

Per birth, with interventions.analyse_birth under the v3 freeze (all parameters fixed HERE, before any production data):
  - flip test: prefix rule (C7.2, gating), with the strict rule reported;
  - R1 dependence + Q8c (K_DEP = 8 draws per source group);
  - C4 existence dependence (performer included; K_DEP);
  - per-byte completeness (R5, gating: <= 5% leak per class) and precision (C1, reported), K_BYTE = 4, on a SEEDED 20%
    subset: sha256("PB|<SEED>|<run>|<child>") mod 5 == 0;
  - per-birth seed = int(sha256("S4|<SEED>|<run>|<child>")[:16], 16).
Class key (R1): the majority performer entity over written loci, relative to the writer (donor):
  self = the donor's material, other = the victim's, none = no ENTITY performer.

Instrument-gate tallies ONLY (no Q, no prediction, no verdict), per class, over distinct simulations:
  flip coverage = (CONFIRMED + FAILED) / rule-identified MOVE loci, floor 50%; FAILED <= 1% of covered;
  per-byte completeness leak share <= 5%; precision (reported).

    python s4_run.py      (after run_production.py; reads exports/, writes exports/S4_RESULTS.jsonl, S4_SUMMARY.json)
"""
import hashlib, json, pathlib, sys
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
EXPORTS = HERE.parent / "exports"
SEED = 20260928
K_DEP, K_BYTE = 8, 4


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def job(args):
    import interventions as I
    rec, dup = args
    key = "%s|%d" % (rec["run"], rec["child"])
    seed = int(h("S4|%d|%s" % (SEED, key))[:16], 16)
    per_byte = int(h("PB|%d|%s" % (SEED, key)), 16) % 5 == 0
    out = I.analyse_birth(rec, seed=seed, K_dep=K_DEP, K_byte=K_BYTE, per_byte=per_byte)
    written = [l for l in out["loci"] if l["written"]]
    donor = rec["donor_side"]
    perf = Counter(("self" if l["performer_ent"] == donor else "other") if l["performer_ent"] else "none" for l in written)
    out.update({"run": rec["run"], "child": rec["child"], "duplicate_of": dup, "per_byte_sampled": per_byte,
                "s4_seed": seed, "class": perf.most_common(1)[0][0] if perf else "none"})
    return out


def main():
    idx = json.loads((EXPORTS / "PRODUCTION_INDEX.json").read_text(encoding="utf-8"))
    tasks = []
    for p in sorted(EXPORTS.glob("*.births.jsonl")):
        if "__ep" in p.name:
            continue
        for line in open(p, encoding="utf-8"):
            rec = json.loads(line)
            tasks.append((rec, idx.get(rec["run"], {}).get("duplicate_of")))
    with Pool(8, maxtasksperchild=4) as pool:
        res = pool.map(job, tasks, chunksize=1)
    with open(EXPORTS / "S4_RESULTS.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in res:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    tal = defaultdict(Counter)
    for r in res:
        if r["duplicate_of"]:
            continue
        c = r["class"]
        for l in r["loci"]:
            if l.get("flip_prefix"):
                tal[c]["move_loci"] += 1
                tal[c]["prefix_" + l["flip_prefix"]] += 1
                tal[c]["strict_" + l["flip"]] += 1
                tal[c]["identified"] += bool(l.get("identified"))
        for pb in r.get("per_byte") or []:
            tal[c]["pb_unnamed_tested"] += pb["unnamed_tested"]
            tal[c]["pb_unnamed_leaks"] += pb["unnamed_leaks"]
            tal[c]["pb_named_tested"] += pb["named_tested"]
            tal[c]["pb_named_effective"] += pb["named_effective"]
    summ = {}
    for c, t in tal.items():
        cov = t["prefix_CONFIRMED"] + t["prefix_FAILED"]
        summ[c] = dict(t, flip_coverage=round(cov / t["move_loci"], 4) if t["move_loci"] else None,
                       flip_failed_share=round(t["prefix_FAILED"] / cov, 4) if cov else None,
                       completeness_leak_share=round(t["pb_unnamed_leaks"] / t["pb_unnamed_tested"], 4)
                       if t["pb_unnamed_tested"] else None,
                       precision_share=round(t["pb_named_effective"] / t["pb_named_tested"], 4)
                       if t["pb_named_tested"] else None)
    out = {"n_births_tested": len(res), "n_duplicates": sum(1 for r in res if r["duplicate_of"]),
           "per_class_distinct_sims": summ, "seed": SEED, "K_dep": K_DEP, "K_byte": K_BYTE,
           "results_sha256": hashlib.sha256((EXPORTS / "S4_RESULTS.jsonl").read_bytes()).hexdigest()}
    (EXPORTS / "S4_SUMMARY.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_class_distinct_sims"}))


if __name__ == "__main__":
    main()
