"""Cleric attack script for the NOUS grave (Rhadamanthus native trial, 2026-09-11).

Two attacks on the Necromancer's nous_forge_join.py, offline, numpy only,
no import of agents/hephaestus (that import writes log files as a side effect).

A. Weak point 1 (strata mix prompt regimes): the Necromancer's stratified null
   iterates set(strata) (hash-randomised order) so its null is not reproducible,
   and its strata are forge days only, which mix the v1 (theorist) and v2
   (engineer) prompt regimes.  Here: strata = regime x forge_day, strata iterated
   in sorted order, 2000 permutations, seed 7, and the same test restricted to
   each regime alone.  Also the day-only stratification re-run deterministically.

B. Weak point 2 (orphan ledger keys attributed to Nous by shape only): census of
   the ledger keys that match no committed Nous responses.jsonl -- timestamps,
   frames, statuses, concept count per key and whether every concept name is in
   the Nous built-in dictionary (agents/nous/src/concepts.py).

Output: cleric_strata_and_orphans_result.json next to this file, written from
Python with a flush after every item.
"""
import glob, json, os, sys, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *([".."] * 4)))
OUT_PATH = os.path.join(HERE, "cleric_strata_and_orphans_result.json")
OUT = {}


def emit(k, v):
    OUT[k] = v
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(OUT, f, indent=1)
        f.flush()
    print(k, json.dumps(v)[:300])


def combo_key(entry):
    return " + ".join(sorted(entry.get("concept_names", [])))


def composite(entry):
    return (entry.get("score") or {}).get("composite_score") or 0.0


# ---- load ledger (last row per key, as hephaestus.load_ledger does) ----
led = {}
rows = []
with open(os.path.join(ROOT, "agents", "hephaestus", "ledger.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            led[e["key"]] = e
            rows.append(e)
        except (json.JSONDecodeError, KeyError):
            pass

# ---- load committed Nous runs ----
nous, run = [], []
for d in sorted(glob.glob(os.path.join(ROOT, "agents", "nous", "runs", "*", ""))):
    p = os.path.join(d, "responses.jsonl")
    if not os.path.exists(p):
        continue
    rid = os.path.basename(os.path.normpath(d))
    for line in open(p, encoding="utf-8"):
        if line.strip():
            nous.append(json.loads(line))
            run.append(rid)
run = np.array(run)
keys = [combo_key(e) for e in nous]
keyset = set(keys)
att = np.array([k in led for k in keys])
forged = np.array([1 if (k in led and led[k].get("status") == "forged") else 0 for k in keys])
apifail = np.array([k in led and str(led[k].get("reason", "")).startswith("api_call_failed") for k in keys])
comp = np.array([composite(e) for e in nous])
regime = np.array(["v2" if r >= "20260325_085453" else "v1" for r in run])
forge_day = np.array([led[k]["timestamp"][:10] if k in led else "" for k in keys])
emit("inputs", {"n_nous_entries": int(len(nous)), "n_ledger_rows": int(len(rows)),
                "n_ledger_keys": int(len(led)), "n_attempted": int(att.sum()),
                "n_attempted_excl_apifail": int((att & ~apifail).sum())})


def auc(score, y):
    y = np.asarray(y); score = np.asarray(score, dtype=float)
    npos, nneg = y.sum(), len(y) - y.sum()
    if npos == 0 or nneg == 0:
        return None
    order = score.argsort(); ranks = np.empty(len(score))
    s = score[order]; i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return float((ranks[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))


def strat_auc(score, y, strata):
    num = 0.0; den = 0.0
    for s in sorted(set(strata)):
        m2 = strata == s; a = auc(score[m2], y[m2])
        if a is None:
            continue
        w = y[m2].sum() * (len(y[m2]) - y[m2].sum()); num += a * w; den += w
    return num / den if den else None


def strat_test(tag, mask, strata_all, n_perm=2000, seed=7):
    rng = np.random.default_rng(seed)
    sc = comp[mask]; y = forged[mask]; st = strata_all[mask]
    obs = strat_auc(sc, y, st)
    if obs is None:
        emit(tag, {"n": int(mask.sum()), "note": "no informative stratum"}); return
    nulls = []
    for _ in range(n_perm):
        yp = y.copy()
        for s in sorted(set(st)):
            m2 = st == s; yp[m2] = rng.permutation(yp[m2])
        nulls.append(strat_auc(sc, yp, st))
    nulls = np.array(nulls, dtype=float)
    per = {}
    for s in sorted(set(st)):
        m2 = st == s; a = auc(sc[m2], y[m2])
        row = {"n": int(m2.sum()), "forged": int(y[m2].sum())}
        if a is not None:
            row["auc"] = round(a, 4)
            hi = sc[m2] >= 7; lo = ~hi
            row["rate_composite_ge7"] = round(float(y[m2][hi].mean()), 4) if hi.any() else None
            row["rate_composite_lt7"] = round(float(y[m2][lo].mean()), 4) if lo.any() else None
            row["n_ge7"] = int(hi.sum())
        per[s] = row
    emit(tag, {"n": int(mask.sum()), "n_forged": int(y.sum()), "n_strata": len(per),
               "auc_composite_obs": round(obs, 4), "null_mean": round(float(nulls.mean()), 4),
               "null_p025": round(float(np.percentile(nulls, 2.5)), 4),
               "null_p975": round(float(np.percentile(nulls, 97.5)), 4),
               "frac_null_ge_obs": round(float((nulls >= obs).mean()), 4),
               "n_perm": n_perm, "seed": seed, "per_stratum": per})


mk = att & ~apifail
day_strata = forge_day
rd_strata = np.array([r + "|" + d for r, d in zip(regime, forge_day)])
# A1: Necromancer's day-only stratification, deterministic order
strat_test("A1_day_strata_pooled_regimes", mk, day_strata)
# A2: regime x day strata (finest honest stratification)
strat_test("A2_regime_x_day_strata", mk, rd_strata)
# A3/A4: within one regime, day strata
strat_test("A3_v1_only_day_strata", mk & (regime == "v1"), day_strata)
strat_test("A4_v2_only_day_strata", mk & (regime == "v2"), day_strata)
# A5: unstratified per regime (the Necromancer's v1/v2 blocks, deterministic, 2000 perms)
for rg in ("v1", "v2"):
    m = mk & (regime == rg)
    rng = np.random.default_rng(7)
    obs = auc(comp[m], forged[m])
    nulls = np.array([auc(comp[m], rng.permutation(forged[m])) for _ in range(2000)], dtype=float)
    emit("A5_" + rg + "_unstratified", {"n": int(m.sum()), "n_forged": int(forged[m].sum()),
                                        "auc_composite_obs": round(obs, 4),
                                        "null_p975": round(float(np.percentile(nulls, 97.5)), 4),
                                        "frac_null_ge_obs": round(float((nulls >= obs).mean()), 4)})
# A6: composite drift within regime across forge days (why day strata matter)
drift = {}
for rg in ("v1", "v2"):
    for d in sorted(set(forge_day[mk & (regime == rg)])):
        m = mk & (regime == rg) & (forge_day == d)
        drift[rg + "|" + d] = {"n": int(m.sum()), "mean_composite": round(float(comp[m].mean()), 3),
                               "forge_rate": round(float(forged[m].mean()), 4)}
emit("A6_composite_and_forge_rate_by_regime_day", drift)

# ---- B: orphan census ----
sys.path.insert(0, os.path.join(ROOT, "agents", "nous", "src"))
from concepts import CONCEPTS  # noqa: E402
dict_names = set(c["name"] for c in CONCEPTS)
orphan_keys = [k for k in led if k not in keyset]
orphan_rows = [r for r in rows if r["key"] not in keyset]
ts = sorted(r.get("timestamp", "") for r in orphan_rows if r.get("timestamp"))
ncon = collections.Counter(len(led[k].get("concept_names", [])) for k in orphan_keys)
all_in_dict = sum(1 for k in orphan_keys if led[k].get("concept_names") and
                  all(n in dict_names for n in led[k]["concept_names"]))
emit("B1_orphans", {"n_orphan_keys": len(orphan_keys), "n_orphan_rows": len(orphan_rows),
                    "n_dictionary_concepts": len(dict_names),
                    "ts_min": ts[0] if ts else None, "ts_max": ts[-1] if ts else None,
                    "rows_by_day": dict(collections.Counter(t[:10] for t in ts)),
                    "concepts_per_key": {str(k): v for k, v in sorted(ncon.items())},
                    "keys_all_concepts_in_nous_dictionary": all_in_dict,
                    "status_by_key": dict(collections.Counter(led[k].get("status") for k in orphan_keys)),
                    "frame_by_row": dict(collections.Counter(str(r.get("frame")) for r in orphan_rows)),
                    "reason_head_by_row": dict(collections.Counter(
                        str(r.get("reason", "")).split(":")[0].split("(")[0].strip()[:40] or "forged"
                        for r in orphan_rows).most_common(8))})
# B2: rows in the ledger overall by day, and the last committed Nous timestamp
last_nous_ts = max((e.get("timestamp") or "") for e in nous)
emit("B2_ledger_rows_by_day", {"rows_by_day": dict(sorted(collections.Counter(
    (r.get("timestamp") or "")[:10] for r in rows).items())),
    "last_committed_nous_entry_timestamp": last_nous_ts,
    "first_orphan_row_timestamp": ts[0] if ts else None})
# B3: do any ledger rows whose key matches committed Nous fall inside the orphan window?
win = [r for r in rows if r["key"] in keyset and ts and ts[0] <= (r.get("timestamp") or "") <= ts[-1]]
emit("B3_matched_rows_inside_orphan_window", {"n": len(win),
     "by_day": dict(sorted(collections.Counter((r.get("timestamp") or "")[:10] for r in win).items()))})
print("done ->", os.path.relpath(OUT_PATH, ROOT))
