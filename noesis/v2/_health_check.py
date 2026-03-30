import duckdb, json, sys, numpy as np
from collections import Counter

con = duckdb.connect('noesis_v2.duckdb', read_only=True)
R = {}

# 1. Table row counts
tnames = [r[0] for r in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main' ORDER BY table_name").fetchall()]
tinfo = {}
for tn in tnames:
    cnt = con.execute(f'SELECT COUNT(*) FROM {tn}').fetchone()[0]
    ccnt = con.execute(f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{tn}'").fetchone()[0]
    tinfo[tn] = {"rows": cnt, "columns": ccnt}
R["table_row_counts"] = tinfo
print("1. Table row counts done")

# Canonical 9
ops = con.execute("SELECT operator_id, name FROM damage_operators ORDER BY operator_id").fetchall()
canonical_ids = [o[0] for o in ops]
canonical_names = [o[1] for o in ops]
R["canonical_operators"] = [{"id": o[0], "name": o[1]} for o in ops]

# 2. Fill rate
fill = con.execute("SELECT source_hub, damage_operator, COUNT(*) FROM cross_domain_links WHERE damage_operator IS NOT NULL GROUP BY source_hub, damage_operator").fetchall()
hubs_l = sorted(set(r[0] for r in fill))
ops_l = sorted(set(r[1] for r in fill if r[1]))
tc = len(hubs_l) * len(ops_l) if ops_l else 0
fc = len(fill)
R["fill_rate_links"] = {"hubs": len(hubs_l), "operators": len(ops_l), "total_cells": tc, "filled": fc, "pct": round(fc/tc*100,2) if tc else 0}

mat = np.load("damage_hub_matrix.npy")
R["numpy_matrix"] = {"shape": list(mat.shape), "total": int(mat.size), "filled": int(np.count_nonzero(mat)), "pct": round(int(np.count_nonzero(mat))/mat.size*100,2)}
print("2. Fill rate done")

# 3. Operator coverage
oc = con.execute("SELECT damage_operator, COUNT(DISTINCT source_hub) FROM cross_domain_links WHERE damage_operator IS NOT NULL GROUP BY damage_operator ORDER BY COUNT(DISTINCT source_hub) DESC").fetchall()
R["operator_coverage"] = {r[0]: r[1] for r in oc}

eod = con.execute("SELECT shared_damage_operator, COUNT(*), COUNT(DISTINCT source_resolution_id), COUNT(DISTINCT target_resolution_id) FROM cross_domain_edges WHERE shared_damage_operator IS NOT NULL GROUP BY shared_damage_operator ORDER BY COUNT(*) DESC").fetchall()
R["edge_op_dist"] = [{"op": r[0], "edges": r[1], "src": r[2], "tgt": r[3]} for r in eod]
print("3. Operator coverage done")

# 4. Hub completion
hc = con.execute("SELECT hub_id, COUNT(DISTINCT damage_operator) FROM discoveries WHERE hub_id IS NOT NULL AND damage_operator IS NOT NULL GROUP BY hub_id").fetchall()
hist = Counter(r[1] for r in hc)
R["hub_completion"] = {"histogram": {f"{k}/9": hist.get(k,0) for k in range(10)}, "detail": [{"hub": r[0], "ops": r[1]} for r in sorted(hc, key=lambda x: -x[1])]}
print("4. Hub completion done")

# 5. Source distributions
prov = con.execute("SELECT provenance, COUNT(*) FROM cross_domain_edges GROUP BY provenance ORDER BY COUNT(*) DESC").fetchall()
R["edge_provenance"] = {str(r[0]): r[1] for r in prov}
csrc = con.execute("SELECT source, COUNT(*) FROM chains GROUP BY source ORDER BY COUNT(*) DESC").fetchall()
R["chain_sources"] = {str(r[0]): r[1] for r in csrc}
dm = con.execute("SELECT discovery_method, COUNT(*) FROM discoveries GROUP BY discovery_method ORDER BY COUNT(*) DESC").fetchall()
R["discovery_methods"] = {str(r[0]): r[1] for r in dm}
print("5. Sources done")

# 6. Cross-domain edges
te = con.execute("SELECT COUNT(*) FROM cross_domain_edges").fetchone()[0]
tl = con.execute("SELECT COUNT(*) FROM cross_domain_links").fetchone()[0]
et = con.execute("SELECT edge_type, COUNT(*) FROM cross_domain_edges GROUP BY edge_type ORDER BY COUNT(*) DESC").fetchall()
lt = con.execute("SELECT link_type, COUNT(*) FROM cross_domain_links GROUP BY link_type ORDER BY COUNT(*) DESC").fetchall()
nodes = con.execute("SELECT COUNT(*) FROM (SELECT DISTINCT source_resolution_id as n FROM cross_domain_edges UNION SELECT DISTINCT target_resolution_id FROM cross_domain_edges)").fetchone()[0]
maxe = nodes*(nodes-1)/2 if nodes>1 else 1
R["cross_domain"] = {"edges": te, "links": tl, "nodes": nodes, "density": round(te/maxe,6), "edge_types": {str(r[0]):r[1] for r in et}, "link_types": {str(r[0]):r[1] for r in lt}}
print("6. Cross-domain done")

# 7. Discoveries
discs = con.execute("SELECT discovery_id, hub_id, damage_operator, resolution_name, verification_status, verified_as, tensor_score, discovery_method FROM discoveries ORDER BY discovery_id").fetchall()
dl = [{"id":d[0],"hub":d[1],"op":d[2],"res":d[3],"status":d[4],"verified_as":d[5],"score":d[6],"method":d[7]} for d in discs]
sc = Counter(d["status"] for d in dl)
R["discoveries"] = {"total": len(dl), "by_status": dict(sc), "entries": dl}
print("7. Discoveries done")

# 8. Ethnomathematics
et_tot = con.execute("SELECT COUNT(*) FROM ethnomathematics").fetchone()[0]
et_enr = con.execute("SELECT COUNT(*) FROM ethnomathematics WHERE enriched_primitive_vector IS NOT NULL").fetchone()[0]
et_cls = con.execute("SELECT COUNT(*) FROM ethnomathematics WHERE classification_agreement IS NOT NULL").fetchone()[0]
et_comp = con.execute("SELECT COUNT(DISTINCT e.system_id) FROM ethnomathematics e JOIN composition_instances ci ON e.system_id = ci.system_id").fetchone()[0]
trad = con.execute("SELECT tradition, COUNT(*) FROM ethnomathematics GROUP BY tradition ORDER BY COUNT(*) DESC").fetchall()
R["ethnomathematics"] = {"total": et_tot, "traditions": len(trad), "with_compositions": et_comp, "enriched": et_enr, "classified": et_cls, "orphaned": et_tot - et_comp, "by_tradition": {str(r[0]):r[1] for r in trad}}
print("8. Ethno done")

# 9. Chains
cc = con.execute("SELECT COUNT(*) FROM chains").fetchone()[0]
cv = con.execute("SELECT COUNT(*) FROM chains WHERE verified = true").fetchone()[0]
cs = con.execute("SELECT COUNT(*) FROM chain_steps").fetchone()[0]
av = con.execute("SELECT AVG(c) FROM (SELECT COUNT(*) as c FROM chain_steps GROUP BY chain_id)").fetchone()[0]
tc2 = con.execute("SELECT COUNT(*) FROM transformations").fetchone()[0]
inv = con.execute("SELECT COUNT(*) FROM transformations WHERE invertible = true").fetchone()[0]
pd2 = con.execute("SELECT primitive_type, COUNT(*) FROM transformations GROUP BY primitive_type ORDER BY COUNT(*) DESC").fetchall()
R["chains"] = {"total": cc, "verified": cv, "steps": cs, "avg_steps": round(av,2) if av else 0, "transforms": tc2, "invertible": inv, "non_invertible": tc2-inv, "primitives": {r[0]:r[1] for r in pd2}}
print("9. Chains done")

# 10. Quality
qual = {}
for tn in tnames:
    pk = con.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{tn}' AND is_nullable='NO' AND ordinal_position=1").fetchall()
    if pk:
        n = con.execute(f"SELECT COUNT(*) FROM {tn} WHERE {pk[0][0]} IS NULL").fetchone()[0]
        if n>0: qual[f"null_pk_{tn}"] = n

dupi = con.execute("SELECT instance_id, COUNT(*) FROM composition_instances GROUP BY instance_id HAVING COUNT(*)>1").fetchall()
orph_c = con.execute("SELECT COUNT(*) FROM composition_instances ci LEFT JOIN abstract_compositions ac ON ci.comp_id=ac.comp_id WHERE ac.comp_id IS NULL").fetchone()[0]
orph_s = con.execute("SELECT COUNT(*) FROM chain_steps cs LEFT JOIN chains c ON cs.chain_id=c.chain_id WHERE c.chain_id IS NULL").fetchone()[0]
nc_d = con.execute("SELECT DISTINCT damage_operator FROM discoveries WHERE damage_operator IS NOT NULL AND damage_operator NOT IN (SELECT name FROM damage_operators) AND damage_operator NOT IN (SELECT operator_id FROM damage_operators)").fetchall()
nc_e = con.execute("SELECT DISTINCT shared_damage_operator FROM cross_domain_edges WHERE shared_damage_operator IS NOT NULL AND shared_damage_operator NOT IN (SELECT name FROM damage_operators) AND shared_damage_operator NOT IN (SELECT operator_id FROM damage_operators)").fetchall()

R["data_quality"] = {
    "null_pks": qual if qual else "CLEAN",
    "duplicate_instance_ids": len(dupi),
    "duplicate_details": [(d[0],d[1]) for d in dupi[:10]],
    "orphan_composition_instances": orph_c,
    "orphan_chain_steps": orph_s,
    "non_canonical_in_discoveries": [r[0] for r in nc_d],
    "non_canonical_in_edges": [r[0] for r in nc_e]
}
print("10. Quality done")

# 11. Prediction stability
ps = []
with open("prediction_stability.jsonl","r") as f:
    for line in f:
        if line.strip(): ps.append(json.loads(line.strip()))
R["prediction_stability"] = {"entries": len(ps), "data": ps}
print("11. Prediction stability done")

# 12. Archaeological
with open("archaeological_predictions.json","r") as f:
    ap = json.load(f)
if isinstance(ap, dict):
    R["archaeological_predictions"] = {"keys": list(ap.keys()), "summary": {k: len(v) if isinstance(v,list) else type(v).__name__ for k,v in ap.items()}}
elif isinstance(ap, list):
    R["archaeological_predictions"] = {"total": len(ap)}
print("12. Arch done")

try:
    with open("novel_predictions.json","r") as f:
        nv = json.load(f)
    if isinstance(nv, dict):
        R["novel_predictions"] = {"keys": list(nv.keys()), "summary": {k: len(v) if isinstance(v,list) else type(v).__name__ for k,v in nv.items()}}
    elif isinstance(nv, list):
        R["novel_predictions"] = {"total": len(nv)}
except: pass

# Extra stats
of = con.execute("SELECT field, COUNT(*) FROM operations GROUP BY field ORDER BY COUNT(*) DESC").fetchall()
R["operations_by_field"] = {r[0]:r[1] for r in of}
R["total_op_fields"] = len(of)

cs2 = con.execute("SELECT COUNT(DISTINCT comp_id), COUNT(DISTINCT system_id), COUNT(DISTINCT tradition), COUNT(DISTINCT domain) FROM composition_instances").fetchone()
R["composition_overview"] = {"compositions": cs2[0], "systems": cs2[1], "traditions": cs2[2], "domains": cs2[3]}

pl = con.execute("SELECT category, name FROM prime_landscape ORDER BY entry_id").fetchall()
R["prime_landscape"] = [{"category": r[0], "name": r[1]} for r in pl]

vp = con.execute("SELECT pair_id, domain_a_system, domain_b_system FROM validation_pairs").fetchall()
R["validation_pairs"] = [{"id": r[0], "a": r[1], "b": r[2]} for r in vp]

con.close()

with open("database_health.json", "w") as f:
    json.dump(R, f, indent=2, default=str)
print("\nJSON saved to database_health.json")
print("ALL_DONE")
