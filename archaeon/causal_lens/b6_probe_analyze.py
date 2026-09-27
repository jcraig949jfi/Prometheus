"""B6 analysis over a code-provenance replay: do 'foreign-LOCATION' writes come from foreign MATERIAL or from self-copied code?"""
import collections, gzip, json, sys
from archaeon.causal_lens import adapters_v02 as A2

def main(rid):
    d = json.load(open(r"C:\Prometheus-data\evidence\contract_v02_2026-09-27\bee_codeprov_%s.json" % rid))
    pres = [json.loads(l) for l in gzip.open(r"C:\Users\James\z80atlas_forensics_2026-09-23_local\births\%s.jsonl.gz" % rid, "rt") if l.strip()]
    same = sum(1 for a, b in zip(pres, d["births_rows"]) if list(a) == list(b))
    cfg = json.load(open(r"C:\Users\James\z80atlas_campaign_2026-09-19\runs\%s\config.json" % rid)); L = 32 if "32" in str(cfg["config"].get("representation")) else 64
    agg = collections.Counter(); c = collections.Counter(); sr = collections.Counter()
    for r, cp in zip(d["births_rows"], d["codeprov"]):
        e = A2.bee_row(list(r), L); own_mat = cp["own_region"] + cp["self_copied"]
        by_mat = "YES" if own_mat > r[7] / 2 else ("NO" if cp["foreign"] > r[7] / 2 else "NI")
        c[("W_by_location=" + e["autonomy_write"], "W_by_material=" + by_mat)] += 1
        if e["autonomy_write"] == "NO":
            for k, v in cp.items(): agg[k] += v
        if r[11]: sr[("native_SR", "self_copied_writes>0" if cp["self_copied"] else "none")] += 1
    rep = {"rid": rid, "rows_identical_to_preserved_log": "%d/%d" % (same, len(pres)), "location_vs_material": {" | ".join(k): v for k, v in c.most_common()},
           "code_material_of_writes_in_W=NO_births": dict(agg), "native_SR_births": {" | ".join(k): v for k, v in sr.items()}}
    json.dump(rep, open(r"D:\Prometheus-worktrees\archaeon-contract-v02-2026-09-27\archaeon\causal_lens\out_v02\B6_PROBE_%s.json" % rid, "w"), indent=1)
    print(json.dumps(rep, indent=1))

if __name__ == "__main__":
    main(sys.argv[1])
