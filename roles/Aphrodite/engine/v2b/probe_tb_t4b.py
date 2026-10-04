"""DEV-1 probe TB-T4b: does T4 v1a change admission of any A23 (E-011) family? Read-only re-score with
direct_score, which conformance C3 shows agrees with the artifact path. Correction-only: no A23 label changes."""
import json
import paths
import a17, a18
import tribunal_t4 as T4
import tribunal_t4_v1a as T4a
a18.worker_init()
rows = [json.loads(x) for x in open(paths.ENG / "A23_C3R2C" / "A20_FOUNDRY_ROWS_2026-09-28.jsonl", encoding="utf-8")]
roles = json.load(open(paths.ENG / "A23_C3R2C" / "A18_ROLES_2026-09-28.json", encoding="utf-8"))
role_of = {f["name"]: f["role"] + ":" + f["tclass"] for v in roles.values() for f in v["families"]}
out = {"rows": 0, "witness_admission_flips": [], "profile_admissible_flips": [], "by_role": {}}
for r in rows:
    if not r.get("Q2_size"):
        continue
    prov = a17.Prov({r["name"]: (r["body"], r["final"], r["init"])})
    T4.use_provider(prov)
    w = prov.witness(r["name"])
    a = T4a.direct_score(w, r["name"], w, "v1")["qualified"]
    b = T4a.direct_score(w, r["name"], w, "v1a")["qualified"]
    pa, pb = T4.family_profile(w)["admissible"], T4a.family_profile(w)["admissible"]
    out["rows"] += 1
    role = role_of.get(r["name"], "UNUSED")
    e = out["by_role"].setdefault(role.split(":")[0], {"n": 0, "flips": 0})
    e["n"] += 1
    if a != b:
        out["witness_admission_flips"].append([r["name"], role, a, b])
        e["flips"] += 1
    if pa != pb:
        out["profile_admissible_flips"].append([r["name"], role, pa, pb])
    if r.get("T4_qualified") is not None and r["T4_qualified"] != a:
        out.setdefault("v1_reproduction_mismatch", []).append(r["name"])
out["A23_used_family_flips"] = [x for x in out["witness_admission_flips"] if x[1] != "UNUSED"]
json.dump(out, open(paths.V2B / "receipts" / "PROBE_TB_T4B_A23.json", "w"), indent=1)
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in out.items()}, default=str))
