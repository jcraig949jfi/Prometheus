"""Independent re-derivation of the W-G (T-RET-2) retention claims from raw per-specimen JSON.

Run from the worktree root:  python roles/Ananke/research/harvest/wave2/W2-G/sub_arc3/rederive_groupG.py
Does NOT import workers/W-G/summarize.py; own Holm step-down. Reads only workers/W-G/out/0x5e?/*.json.
Optionally imports prometheus.ananke.c1b_run (project code) to count distinct physics points.
"""
import csv, glob, json, os, sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("OMP_NUM_THREADS", "2")
ROOT = os.getcwd()
WG = os.path.join(ROOT, "roles/Ananke/research/workers/W-G/out")
HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = 0.01
PROBES = ["BLANK", "PING", "CLEAR_S0", "CLEAR_FAST", "RELOC"]


def holm(pv):
    items = sorted(pv.items(), key=lambda kv: kv[1])
    m = len(items)
    out, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[k] = run
    return out


def load(ns):
    spec, ctrl = {}, {}
    for f in sorted(glob.glob(os.path.join(WG, ns, "*.json"))):
        d = json.load(open(f))
        (ctrl if d["cell"] == "plant" else spec)[d["name"]] = d
    return spec, ctrl


res = {}
for ns in ("0x5eb", "0x5ec"):
    spec, ctrl = load(ns)
    a3 = holm({n: r["L3"]["p"] for n, r in spec.items()})
    a4 = holm({(n, p): r["probes"][p]["p"] for n, r in spec.items() for p in PROBES})
    a2 = holm({(n, d): r["decoders"][d]["p"] for n, r in spec.items() for d in ("D1", "D2")})
    raw_low = [(n, p, r["probes"][p]["p"], r["probes"][p]["T"]) for n, r in spec.items() for p in PROBES
               if r["probes"][p]["p"] < 0.1]
    raw_low_L3 = [(n, r["L3"]["p"]) for n, r in spec.items() if r["L3"]["p"] < 0.1]
    L2 = sorted({n for (n, d), q in a2.items() if q < ALPHA})
    # controls (unadjusted alpha .01)
    c = ctrl
    sig = lambda r, key: (r["L3"]["p"] if key == "L3" else r["probes"][key]["p"]) < ALPHA
    cv = {
        "C-NEG": all(not sig(c["C-NEG"], k) for k in ["L3"] + PROBES) and all(c["C-NEG"]["decoders"][d]["p"] >= ALPHA for d in ("D1", "D2", "PAIR")),
        "C-INT": (min(c["C-INT"]["decoders"]["D1"]["p"], c["C-INT"]["decoders"]["D2"]["p"]) < ALPHA and not sig(c["C-INT"], "L3")
                  and not any(sig(c["C-INT"], k) for k in PROBES[:4]) and sig(c["C-INT"], "RELOC")),
        "C-EFF": sig(c["C-EFF"], "L3") and sig(c["C-EFF"], "BLANK"),
        "C-AVL": (not sig(c["C-AVL"], "L3")) and sig(c["C-AVL"], "CLEAR_S0") and sig(c["C-AVL"], "CLEAR_FAST"),
        "C-CHAOS": all(not sig(c["C-CHAOS"], k) for k in ["L3"] + PROBES) and all(c["C-CHAOS"]["decoders"][d]["p"] >= ALPHA for d in ("D1", "D2", "PAIR")),
    }
    fam = {}
    for n, r in spec.items():
        fam.setdefault(r["family"], []).append(n)
    res[ns] = dict(n_spec=len(spec), n_ctrl=len(ctrl), max_adj_L3=max(a3.values()), min_adj_L3=min(a3.values()),
                   min_adj_L4=min(a4.values()), n_L4_tests=len(a4), L3_hits=[k for k, v in a3.items() if v < ALPHA],
                   L4dyn_hits=[k for k, v in a4.items() if v < ALPHA and k[1] != "RELOC"], raw_probe_lt_0p1=raw_low,
                   raw_L3_lt_0p1=raw_low_L3, L2_after_holm=L2, controls_valid=cv,
                   families={k: sorted(v) for k, v in fam.items()})

for ns, r in res.items():
    print("==", ns)
    for k, v in r.items():
        print("  ", k, v)

# distinct physics points (project code, not worker code)
nphys = None
try:
    sys.path.insert(0, ROOT)
    from prometheus.ananke import c1b_run
    rows = c1b_run.d_wave_cells()
    phys = {json.dumps(x["physics"], sort_keys=True) for x in rows}
    fams = {}
    for x in rows:
        fams.setdefault(x["env"]["family"], set()).add(json.dumps(x["physics"], sort_keys=True))
    nphys = len(phys)
    print("D-wave cells:", len(rows), "distinct physics:", nphys, {k: len(v) for k, v in fams.items()},
          "(+1 M2 physics for the 4 M2 champions)")
except Exception as e:  # noqa
    print("physics count unavailable:", e)

ec = res["0x5ec"]
nspec = ec["n_spec"]
fam_s = "; ".join(f"{k} {len(v)}" for k, v in sorted(ec["families"].items()))
none_hit = not ec["L3_hits"] and not ec["L4dyn_hits"] and not res["0x5eb"]["L3_hits"] and not res["0x5eb"]["L4dyn_hits"]
allone = ec["min_adj_L3"] == 1.0 and res["0x5eb"]["min_adj_L3"] == 1.0 and ec["min_adj_L4"] == 1.0 and res["0x5eb"]["min_adj_L4"] == 1.0
ctrl_ok = all(ec["controls_valid"].values()) and all(res["0x5eb"]["controls_valid"].values())
phys_s = (f"{nphys + 1} physics points ({nphys} distinct among the 12 D-wave cells -- all 4 RELAY cells share one -- + 1 M2 physics shared by the 4 M2 champions)" if nphys else "physics count unavailable")
raw = "roles/Ananke/research/workers/W-G/out/0x5eb/*.json; out/0x5ec/*.json"
e79 = [x for x in ec["raw_probe_lt_0p1"] if x[0] == "D_e79e72df"]

rows = []
H = ["claim_id", "doc", "location", "claim_text", "source_report", "report_value", "raw_path", "rederived_value",
     "status", "denominator", "denominator_ok", "wording_exceeds", "notes"]
den = f"{nspec} champions ({fam_s}; 12 C1 D-wave cells + 4 M2 HOLD champions), {phys_s}; 32 twin pairs/specimen; 2 namespaces"
rows.append(["1a", "SYNTHESIS_2026-09-28_ARC3.md", "s3 RETENTION l.44-46",
             "There is no nontrivial retention regime in the evolved champions (preregistered, replicated in two namespaces; 5 controls valid ...; W-G)",
             "workers/W-G/REPORT.md", "NO among these 16 champions; every adj p = 1.0 (L3, P1-P5) both namespaces; 5 controls behaved",
             raw, f"L3/L4 hits 0x5eb={res['0x5eb']['L3_hits']+res['0x5eb']['L4dyn_hits']} 0x5ec={ec['L3_hits']+ec['L4dyn_hits']}; min adj L3/L4 both ns = 1.0: {allone}; controls valid both ns: {ctrl_ok}",
             "MATCH" if (none_hit and allone and ctrl_ok) else "MISMATCH", den, "yes (stated in REPORT, not in synthesis)", "minor",
             "Synthesis says 'the evolved champions' without the count; REPORT scopes to 'these 16 champions'. Suggested: 'no nontrivial retention regime in the 16 champions tested (12 C1 D-wave cells + 4 M2 HOLD champions), none selected for cross-trial memory'."])
rows.append(["1b", "SYNTHESIS_2026-09-28_ARC3.md", "s14 PTE'S VALUE l.180",
             "What PTE does NOT give: persistent memory in evolved champions",
             "workers/W-G/REPORT.md; workers/W-L/REPORT.md", "W-G: NO for 16 champions under tasks never rewarding cross-trial memory; W-L: retention reachable when rewarded (integration)",
             raw, "same as 1a; W-G REPORT DISAGREEMENT 2 says the NO is about what evolved under non-rewarding tasks, not PTE",
             "PARTIAL", den, "no (no count given)", "YES",
             "Generalises a 16-specimen null (task never rewards retention) to PTE's capability, and is in tension with ARC3 s3 / W-L (retention IS reachable when rewarded, as integration) and W-G's plants (substrate retains). Suggested: 'PTE's current champions (16 tested, selected on tasks without cross-trial reward) show no trial-specific memory; rewarded searches evolve integration, not selective storage'."])
rows.append(["1c", "PTE_ENGINE_CARD.md", "KNOWN FAILURE MODES l.99-101",
             "No champion expresses trial-specific retention (preregistered, replicated).",
             "workers/W-G/REPORT.md", "NO among 16 champions", raw, "same as 1a", "PARTIAL", den, "no", "YES",
             "'No champion' reads as universal; only 16 were tested. Also the card was later aware of W-L (T-RET-EVO): W-L champions evolved under 1-back reward DO retain (integration) -- 'no champion' is then false for W-L's rewarded champions unless 'trial-specific' is read as 'selective'. Suggested: 'None of the 16 C1/M2 champions tested expresses trial-specific retention (preregistered, replicated); W-L's rewarded champions retain only as integration.' The card's own next sentence ('evolution was never rewarded for it') is outdated after W-L."])
rows.append(["1d", "BACKLOG_V2.md", "T-RET-2 row l.16",
             "ANSWERED (W-G): NO retention regime (L3/L4 all adj p = 1.0 in both namespaces; 5 controls valid, incl. a latent Kp store the L4 probes detect)",
             "workers/W-G/REPORT.md", "all adj p = 1.0; controls valid", raw,
             f"min adj L3 = {ec['min_adj_L3']} (0x5ec), {res['0x5eb']['min_adj_L3']} (0x5eb); min adj L4 = {ec['min_adj_L4']} / {res['0x5eb']['min_adj_L4']}; C-AVL CLEAR_S0/CLEAR_FAST fire (p 1.5e-4) while L3 null: {ec['controls_valid']['C-AVL']}",
             "MATCH" if (allone and ctrl_ok) else "MISMATCH", den, "no", "minor",
             "Numbers re-derive exactly with independent Holm. Row does say 'SI01 CLOSED for current champions' and 'the NO is about what evolved' -- adequately scoped in the follow-on text; headline 'NO retention regime' lacks the n=16."])
rows.append(["1e", "workers/W-G/REPORT.md", "VERDICT PER SPECIMEN",
             "Of the raw probe statistics, only e79e72df BLANK (raw p 0.022, 0x5EB) was below 0.1, and it did not replicate.",
             "workers/W-G/REPORT.md", "raw p .022 in 0x5EB only; not replicated", raw,
             f"0x5eb raw<0.1: {res['0x5eb']['raw_probe_lt_0p1']}; 0x5ec raw<0.1: {ec['raw_probe_lt_0p1']}",
             "MISMATCH" if e79 else "MATCH", "16 specimens x 5 probes = 80 tests per namespace", "yes", "no",
             "e79e72df BLANK has raw p ~.0225 (T=7) in 0x5EC as well; the report's 'did not replicate' is wrong at the raw level. Non-consequential for the verdict (Holm adj = 1.0 in both; 80-test family), but the replication sentence should read 'raw p .022 in both namespaces, adj p 1.0'."])
rows.append(["1f", "SYNTHESIS_2026-09-28_ARC2.md / ARC3", "ARC2 s9; ARC3 s3 'SI01 is CLOSED for the current champions'",
             "SI01 CLOSED for the current champions",
             "workers/W-G/REPORT.md", "Close SI01 for these champions only", raw, f"{nspec} champions tested", "MATCH", den, "n/a", "no",
             "Correctly scoped ('current champions'), though 'current' = the 16 W-G specimens, not all 166 C1 cells."])

with open(os.path.join(HERE, "rows_groupG.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(H)
    w.writerows(rows)
print("wrote rows_groupG.csv", len(rows))
