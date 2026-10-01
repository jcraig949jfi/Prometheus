"""Re-attack H7(a): does the recorded-vs-actual dest_mode alias change WHICH dials wave B
transected? Recompute campaign.dial_effects on the A0/A rows with levels.dest_mode replaced
by physics.dest_mode, and compare the selected dial lists with the recorded ones."""
from common import *
import gzip, json, copy, pathlib
from prometheus.ananke import campaign
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
cfg = campaign.CampaignConfig()
A0 = [r for r in R if r["wave"] == "A0"]; A = [r for r in R if r["wave"] == "A"]
def fix(rows):
    out = []
    for r in rows:
        r2 = copy.deepcopy(r); r2["levels"]["dest_mode"] = r["physics"]["dest_mode"]; out.append(r2)
    return out
def sel(A0, A):
    res = {}
    for fam in cfg.families:
        dials = []
        for metric in ("plant", "sens"):
            k = 0
            for _, d, _ in campaign.dial_effects(A0, fam, metric):
                if d not in dials:
                    dials.append(d); k += 1
                    if k >= cfg.b_dials // 2: break
        res[(fam, "phys")] = dials
        r1 = [r for r in A if r["env"]["family"] == fam]
        if any(campaign.classify(r, cfg)["SIGNAL"] for r in r1):
            res[(fam, "evo")] = [d for _, d, _ in campaign.dial_effects(A, fam, "acc")[:3]]
    return res
rec = sel(A0, A); cor = sel(fix(A0), fix(A))
# what B actually ran
ran = {}
for r in R:
    e = r.get("extra") or {}
    if r["wave"] == "B": ran.setdefault((r["env"]["family"], e["track"]), set()).add(e["transect"])
for k in sorted(rec):
    flag = "" if rec[k] == cor[k] else "   <-- DIFFERS"
    print(k, "recorded-levels:", rec[k], "| actual-physics:", cor[k], "| ran:", sorted(ran.get(k, [])), flag)
# dest_mode effect sizes recorded vs corrected
for fam in cfg.families:
    for metric in ("plant", "sens"):
        a = {d: (round(s, 2), m) for s, d, m in campaign.dial_effects(A0, fam, metric) if d == "dest_mode"}
        b = {d: (round(s, 2), m) for s, d, m in campaign.dial_effects(fix(A0), fam, metric) if d == "dest_mode"}
        print(fam, metric, "dest_mode effect recorded", a.get("dest_mode"), " corrected", b.get("dest_mode"))
