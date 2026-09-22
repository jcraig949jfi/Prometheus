"""June-2026 dossier's proposed settle test for Argos, run as an instrument with an apparatus control (LAW N14).
Proposal (pivot/COMPONENT_DOSSIERS_2026-06-24.md ### Argos): run the Stage-1 claim-miner on the 20 Argos DR reports;
'zero dispatchable claims => exhaust'. Control: the same miner on a hand-requested batch dir (deep_research_batch6, 21 reports)
of the same era; if the control also yields ~0 the test is inert and says nothing about Argos.
Also: a matched NON-Argos sample of 20 Pythia reports from the same deep_research_reports/ date dirs (same instrument, same era)
so the Argos yield is read against its reference class rather than an absolute zero. Run from repo root."""
import os, sys, json, glob, shutil, subprocess, random, re
sp = os.environ.get("SP", os.path.dirname(os.path.abspath(__file__)))
tmp = os.environ.get("ARGOS_TMP", os.path.join(sp, "_settle_tmp")); shutil.rmtree(tmp, ignore_errors=True)
M = "prometheus_math/substrate_generation/claim_mining/extract_deep_research_claims_v0_1.py"
def run(batch, out):
    os.makedirs(out, exist_ok=True)
    r = subprocess.run([sys.executable, M, "--batch-dir", batch, "--out-dir", out], capture_output=True, text=True, encoding="utf-8", errors="replace")
    summ = os.path.join(out, "_summary.json")
    s = json.load(open(summ)) if os.path.exists(summ) else {"_no_summary": True, "stdout": r.stdout[-800:], "stderr": r.stderr[-800:]}
    counts = {}
    for f in glob.glob(os.path.join(out, "*.jsonl")):
        counts[os.path.basename(f)] = sum(1 for l in open(f, encoding="utf-8", errors="replace") if l.strip())
    return {"rc": r.returncode, "summary": s, "claims_per_file": counts, "total_claims": sum(counts.values())}
OUT = {}
argos = sorted(glob.glob("aporia/docs/deep_research_reports/*/*argos_lens_fingerprint*.md"))
A = set(argos)
# control 1: hand batch of the same era
OUT["control_batch6"] = run("aporia/docs/deep_research_batch6", os.path.join(tmp, "out_control"))
OUT["control_batch6"]["n_reports"] = len(glob.glob("aporia/docs/deep_research_batch6/*.md"))
# control 2: matched non-Argos Pythia reports from the same date dirs
dirs = sorted({os.path.dirname(p) for p in argos})
pool = [p for d in dirs for p in glob.glob(os.path.join(d, "*.md")) if p not in A]
random.seed(20260910); sample = random.sample(pool, min(20, len(pool)))
d2 = os.path.join(tmp, "in_matched"); os.makedirs(d2)
for p in sample: shutil.copy(p, d2)
OUT["matched_nonargos"] = run(d2, os.path.join(tmp, "out_matched")); OUT["matched_nonargos"]["n_reports"] = len(sample); OUT["matched_nonargos"]["pool_n"] = len(pool)
# treatment: the 20 Argos reports
d3 = os.path.join(tmp, "in_argos"); os.makedirs(d3)
for p in argos: shutil.copy(p, d3)
OUT["argos"] = run(d3, os.path.join(tmp, "out_argos")); OUT["argos"]["n_reports"] = len(argos)
for k in ("control_batch6", "matched_nonargos", "argos"):
    OUT[k]["claims_per_report"] = round(OUT[k]["total_claims"] / max(1, OUT[k]["n_reports"]), 3)
OUT["reading"] = "claims/report: control(batch6)=%s matched_nonargos=%s argos=%s" % tuple(OUT[k]["claims_per_report"] for k in ("control_batch6", "matched_nonargos", "argos"))
json.dump(OUT, open(os.path.join(sp, "argos_settle_test_result.json"), "w"), indent=1)
for k in ("control_batch6", "matched_nonargos", "argos"): print(k, json.dumps({x: OUT[k][x] for x in ("rc", "n_reports", "total_claims", "claims_per_report", "claims_per_file")}))
print(OUT["reading"])
