"""R3 control battery, LIVE (BC-9). Four controls, real packets, paid lane, R3-namespaced.

  A  payload consumption   F-answer - F0 >= +25pp AND McNemar exact p < 0.01
  B  cheat control         content-zeroed, format-intact packet must NOT beat F0
                           (FAIL iff p < 0.05 AND delta >= +5pp)
  C  leakage, live         100 projected D0 packets, PROBLEM TEXT WITHHELD, solver must not
                           recover gold: exact binomial p > 0.05 vs chance 0.25 AND point <= 0.35
                           (rule adapted from the binary family's 0.50/0.60 — chance moved, the
                           +0.10 margin is preserved; adaptation recorded, forced by the family)
  D  headroom              measured ceiling (F-answer accuracy) - F0 >= 25pp — the ceiling is
                           what the instrument demonstrates, never an assumed 1.0

Every row carries run_id R3-LIVE so control data can never pool into a substantive comparison.
"""
import json, pathlib, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.solver import call
from ergon.probe.extract import extract_numeric
from ergon.probe.assemble import assemble_retrieved, load_prepass, select_residue
from ergon.probe.analysis import mcnemar_exact

SOLVER = "deepseek:deepseek-v4-flash"
N_PAIRED = 200      # A, B, D share this paired task set
N_C = 100
RATE_RPM, WORKERS, MAX_TOK, TIMEOUT = 40.0, 6, 8192, 420
RUN_ID = "R3-LIVE-2026-08-19"
OUT = ROOT / "ergon/probe/ledgers/r3_live_2026-08-19.json"

MAN = ROOT / "ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl"
LED = ROOT / "ergon/probe/ledgers/nearmiss_mix-M30_prepass.jsonl"

rows = [json.loads(l) for l in MAN.read_text(encoding="utf-8").splitlines()]
gold = {r["uid"]: r["gold_int"] for r in rows}
pool = load_prepass(LED)
tau = {"nearmiss_mix-M30_prepass": 10_000}
rng = random.Random(20260819)
paired = rng.sample(rows, N_PAIRED)
c_rows = rng.sample(rows, N_C)

def d0_packet(uid):
    recs = select_residue(pool, stratum="D0", target_uid=uid)
    return assemble_retrieved(task_uid=uid, stratum="D0", records=recs, tau=tau).body

_ALNUM = re.compile(r"[A-Za-z0-9]")
def zero_content(text):  # format intact, content gone (Harmonia B's redact_content shape)
    return _ALNUM.sub("x", text)

def batch(prompts):
    interval = 60.0 / RATE_RPM
    out = [None]*len(prompts); t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = []
        for i, p in enumerate(prompts):
            sl = (t0 + i*interval) - time.monotonic()
            if sl > 0: time.sleep(sl)
            futs.append((i, ex.submit(call, SOLVER, p, max_tokens=MAX_TOK, timeout=TIMEOUT)))
        for i, f in futs: out[i] = f.result()
    return out

def score(rs, uids):
    return [extract_numeric(r.text if r.status=="ok" else None).value == gold[u]
            for r, u in zip(rs, uids)]

uids = [r["uid"] for r in paired]
print(f"[R3] F0 arm x{N_PAIRED}"); f0 = score(batch([r["prompt"] for r in paired]), uids)
print(f"[R3] F-answer arm x{N_PAIRED}")
fa = score(batch([r["prompt"] + f"\n\nPrior context: the correct count is {gold[r['uid']]}."
                  for r in paired]), uids)
print(f"[R3] B cheat arm x{N_PAIRED}")
fb = score(batch([r["prompt"] + "\n\nPrior attempt record:\n" + zero_content(d0_packet(r["uid"]))
                  for r in paired]), uids)
print(f"[R3] C leakage x{N_C}")
c_prompts = [("A prior attempt's record is shown. The problem statement is withheld.\n\n"
              + d0_packet(r["uid"]) +
              "\n\nBased ONLY on the record above: how many of the five integers were prime?\n"
              "Give your final answer on the last line in the form: ANSWER: <count>")
             for r in c_rows]
c_res = batch(c_prompts)
c_hits = sum(extract_numeric(r.text if r.status=="ok" else None).value == gold[row["uid"]]
             for r, row in zip(c_res, c_rows))

import math
def binom_p(k, n, p0):
    return sum(math.comb(n,i)*p0**i*(1-p0)**(n-i) for i in range(k, n+1))

acc = lambda v: sum(v)/len(v)
b_a = sum(1 for x,y in zip(fa,f0) if x and not y); c_a = sum(1 for x,y in zip(fa,f0) if y and not x)
b_b = sum(1 for x,y in zip(fb,f0) if x and not y); c_b = sum(1 for x,y in zip(fb,f0) if y and not x)
A = {"f0": acc(f0), "f_answer": acc(fa), "delta": acc(fa)-acc(f0),
     "mcnemar_p": mcnemar_exact(b_a, c_a),
     "pass": (acc(fa)-acc(f0) >= 0.25) and mcnemar_exact(b_a, c_a) < 0.01}
B = {"f0": acc(f0), "cheat": acc(fb), "delta": acc(fb)-acc(f0),
     "mcnemar_p": mcnemar_exact(b_b, c_b),
     "fail": (mcnemar_exact(b_b, c_b) < 0.05) and (acc(fb)-acc(f0) >= 0.05)}
B["pass"] = not B["fail"]
C = {"recovery": c_hits/N_C, "n": N_C, "binom_p_vs_025": binom_p(c_hits, N_C, 0.25),
     "pass": binom_p(c_hits, N_C, 0.25) > 0.05 and c_hits/N_C <= 0.35,
     "rule_note": "adapted from binary 0.50/0.60 -> count-family 0.25/0.35 (margin preserved)"}
D = {"ceiling_measured": acc(fa), "f0": acc(f0), "headroom": acc(fa)-acc(f0),
     "pass": acc(fa)-acc(f0) >= 0.25}
res = {"run_id": RUN_ID, "solver": SOLVER, "n_paired": N_PAIRED,
       "A_payload_consumption": A, "B_cheat": B, "C_leakage_live": C, "D_headroom": D,
       "all_pass": all([A["pass"], B["pass"], C["pass"], D["pass"]]),
       "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
tmp = OUT.with_suffix(".json.tmp"); tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
import os; os.replace(tmp, OUT)
print(json.dumps(res, indent=2))
