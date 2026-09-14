"""Q2: Did the Nous scores predict anything downstream?  Join Nous entries to the
Hephaestus forge ledger (agents/hephaestus/ledger.jsonl) via combo_key.

Separates Nous quality (does its rating rank forge survivors above chance?)
from forge instrument state (api_call_failed rows are not a verdict on Nous).
Also splits by Nous PROMPT REGIME: v1 = runs before 20260325_085453 (theorist
prompt), v2 = runs from 20260325_085453 onward (engineer prompt, commit da42cc7e0).
Output: nous_forge_join_result.json next to this file.  numpy only.
"""
import glob, json, os, sys, types, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *([".."] * 4)))
m = types.ModuleType("openai"); m.OpenAI = object; sys.modules["openai"] = m
sys.path.insert(0, os.path.join(ROOT, "agents", "hephaestus", "src"))
from hephaestus import load_ledger, combo_key, _composite   # noqa: E402
led = load_ledger()
rng = np.random.default_rng(7)

nous = []; run = []
for d in sorted(glob.glob(os.path.join(ROOT, "agents", "nous", "runs", "*", ""))):
    p = os.path.join(d, "responses.jsonl")
    if not os.path.exists(p):
        continue
    rid = os.path.basename(os.path.normpath(d))
    for line in open(p, encoding="utf-8"):
        if line.strip():
            nous.append(json.loads(line)); run.append(rid)
run = np.array(run)
keys = [combo_key(e) for e in nous]
att = np.array([k in led for k in keys])
forged = np.array([1 if (k in led and led[k].get("status") == "forged") else 0 for k in keys])
apifail = np.array([k in led and str(led[k].get("reason", "")).startswith("api_call_failed") for k in keys])
reason = [str(led[k].get("reason", "")) if k in led else None for k in keys]
comp = np.array([_composite(e) for e in nous])
hp = np.array([1 if (e.get("score") or {}).get("high_potential") else 0 for e in nous])
unprod = np.array([1 if (e.get("score") or {}).get("is_unproductive") else 0 for e in nous])
impl = np.array([((e.get("score") or {}).get("ratings") or {}).get("implementability") or 0 for e in nous], dtype=float)
regime = np.array(["v2" if r >= "20260325_085453" else "v1" for r in run])
forge_day = np.array([led[k]["timestamp"][:10] if k in led else "" for k in keys])


def auc(score, y):
    """Rank AUC (Mann-Whitney), ties averaged."""
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


def perm_null(score, y, n=200):
    vals = [auc(score, rng.permutation(y)) for _ in range(n)]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"mean": round(float(np.mean(vals)), 4), "p975": round(float(np.percentile(vals, 97.5)), 4),
            "p025": round(float(np.percentile(vals, 2.5)), 4)}


OUT = {"n_nous_entries": int(len(nous)), "n_ledger_keys": int(len(led)),
       "ledger_status_counts": dict(collections.Counter(v.get("status") for v in led.values())),
       "ledger_keys_not_in_any_nous_run": int(sum(1 for k in led if k not in set(keys)))}


def block(tag, mask):
    yv = forged[mask]; n = int(mask.sum())
    r = {"n": n, "n_forged": int(yv.sum()), "forge_rate": round(float(yv.mean()), 4) if n else None}
    if n and yv.sum() and yv.sum() < n:
        r["auc_composite"] = round(auc(comp[mask], yv), 4)
        r["auc_composite_null"] = perm_null(comp[mask], yv)
        r["auc_implementability"] = round(auc(impl[mask], yv), 4)
        r["n_high_potential"] = int((hp[mask] == 1).sum())
        r["forge_rate_high_potential"] = round(float(yv[hp[mask] == 1].mean()), 4) if (hp[mask] == 1).any() else None
        r["forge_rate_not_high_potential"] = round(float(yv[hp[mask] == 0].mean()), 4) if (hp[mask] == 0).any() else None
        r["forge_rate_composite_ge7"] = round(float(yv[comp[mask] >= 7].mean()), 4) if (comp[mask] >= 7).any() else None
        r["forge_rate_composite_lt7"] = round(float(yv[comp[mask] < 7].mean()), 4) if (comp[mask] < 7).any() else None
    OUT[tag] = r
    print(tag, json.dumps(r))


# 1. coverage of Nous by the forge
OUT["attempted"] = {"n_attempted": int(att.sum()), "frac_attempted": round(float(att.mean()), 4),
                    "n_api_call_failed": int(apifail.sum()),
                    "n_unproductive_never_attempted": int((unprod & ~att).sum()),
                    "n_unproductive_attempted": int((unprod & att).sum())}
OUT["attempted_by_run"] = {r: {"n": int((run == r).sum()), "attempted": int(att[run == r].sum()),
                               "api_failed": int(apifail[run == r].sum()), "forged": int(forged[run == r].sum()),
                               "hp": int(hp[run == r].sum())} for r in sorted(set(run))}
print(json.dumps(OUT["attempted"])); print(json.dumps(OUT["attempted_by_run"], indent=0))
# 2. blocks
block("ALL_attempted", att)
block("ALL_attempted_excl_apifail", att & ~apifail)
block("v1_attempted_excl_apifail", att & ~apifail & (regime == "v1"))
block("v2_attempted_excl_apifail", att & ~apifail & (regime == "v2"))
# 3. within forge day (controls for forge instrument drift)
days = sorted(set(forge_day[att & ~apifail]))
OUT["by_forge_day"] = {}
for dday in days:
    mk = att & ~apifail & (forge_day == dday)
    yv = forged[mk]
    row = {"n": int(mk.sum()), "forged": int(yv.sum()), "rate": round(float(yv.mean()), 4) if mk.sum() else None,
           "n_v1": int((regime[mk] == "v1").sum()), "n_v2": int((regime[mk] == "v2").sum())}
    if yv.sum() and yv.sum() < mk.sum():
        row["auc_composite"] = round(auc(comp[mk], yv), 4); row["auc_impl"] = round(auc(impl[mk], yv), 4)
        row["rate_hp"] = round(float(yv[hp[mk] == 1].mean()), 4) if (hp[mk] == 1).any() else None
        row["rate_not_hp"] = round(float(yv[hp[mk] == 0].mean()), 4) if (hp[mk] == 0).any() else None
    OUT["by_forge_day"][dday] = row
print(json.dumps(OUT["by_forge_day"], indent=0))
# 4. stratified permutation: shuffle forged within forge-day strata, pooled composite AUC
mk = att & ~apifail


def strat_auc(score, y, strata):
    num = 0.0; den = 0.0
    for s in set(strata):
        m2 = strata == s; a = auc(score[m2], y[m2])
        if a is None:
            continue
        w = y[m2].sum() * (len(y[m2]) - y[m2].sum()); num += a * w; den += w
    return num / den if den else None


obs = strat_auc(comp[mk], forged[mk], forge_day[mk])
nulls = []
for _ in range(200):
    yp = forged[mk].copy()
    for s in set(forge_day[mk]):
        m2 = forge_day[mk] == s; yp[m2] = rng.permutation(yp[m2])
    nulls.append(strat_auc(comp[mk], yp, forge_day[mk]))
OUT["stratified_by_forge_day"] = {"auc_composite_obs": round(obs, 4), "null_mean": round(float(np.mean(nulls)), 4),
                                  "null_p025": round(float(np.percentile(nulls, 2.5)), 4),
                                  "null_p975": round(float(np.percentile(nulls, 97.5)), 4),
                                  "frac_null_ge_obs": round(float(np.mean([v >= obs for v in nulls])), 3),
                                  "auc_implementability_obs": round(strat_auc(impl[mk], forged[mk], forge_day[mk]), 4)}
print("stratified:", json.dumps(OUT["stratified_by_forge_day"]))
# 5. reason breakdown of attempted rows by regime
for rg in ("v1", "v2"):
    c = collections.Counter((reason[i].split(":")[0].split("(")[0].strip() or "forged") if reason[i] is not None else None
                            for i in np.where(att & (regime == rg))[0])
    OUT["reason_by_regime_" + rg] = dict(c.most_common())
print(json.dumps({k: v for k, v in OUT.items() if k.startswith("reason_by")}, indent=0))
# 6. README claim "20-30% warrant forging" vs measured high_potential by regime
OUT["high_potential_by_regime"] = {rg: {"n": int((regime == rg).sum()), "hp": int(hp[regime == rg].sum()),
                                        "frac": round(float(hp[regime == rg].mean()), 4)} for rg in ("v1", "v2")}
print("hp by regime:", json.dumps(OUT["high_potential_by_regime"]))
json.dump(OUT, open(os.path.join(HERE, "nous_forge_join_result.json"), "w"), indent=1)
