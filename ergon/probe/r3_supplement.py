"""R3 supplement — HB exit-review C-2 and C-3.

C-2: control C re-run WITH the diagnostics the first run omitted. The recorded 0/100 was
     uninterpretable: under the control's own chance rate (0.25), P(X=0 | n=100) = 3.2e-13 —
     a pass and a non-execution produced the same number. This run logs parse-failure rate,
     the extracted-value distribution, and refusal count, so 'clean' and 'broken' are
     distinguishable in the record.
C-3: control B at N >= 400 as the operating characteristics require (the n=200 run had 60%
     power at the +10pp effect it polices).
"""
import json
import os
import pathlib
import random
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.solver import call
from ergon.probe.extract import extract_numeric
from ergon.probe.assemble import assemble_retrieved, load_prepass, select_residue
from ergon.probe.analysis import mcnemar_exact

SOLVER = "deepseek:deepseek-v4-flash"
RATE_RPM, WORKERS, MAX_TOK, TIMEOUT = 40.0, 6, 8192, 420
OUT = ROOT / "ergon/probe/ledgers/r3_supplement_2026-08-19.json"

MAN = ROOT / "ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl"
LED = ROOT / "ergon/probe/ledgers/nearmiss_mix-M30_prepass.jsonl"

rows = [json.loads(l) for l in MAN.read_text(encoding="utf-8").splitlines()]
gold = {r["uid"]: r["gold_int"] for r in rows}
pool = load_prepass(LED)
tau = {"nearmiss_mix-M30_prepass": 10_000}
rng = random.Random(20260820)

_ALNUM = re.compile(r"[A-Za-z0-9]")


def d0_body(uid):
    recs = select_residue(pool, stratum="D0", target_uid=uid)
    return assemble_retrieved(task_uid=uid, stratum="D0", records=recs, tau=tau).body


def batch(prompts):
    interval = 60.0 / RATE_RPM
    out = [None] * len(prompts)
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = []
        for i, p in enumerate(prompts):
            sl = (t0 + i * interval) - time.monotonic()
            if sl > 0:
                time.sleep(sl)
            futs.append((i, ex.submit(call, SOLVER, p, max_tokens=MAX_TOK, timeout=TIMEOUT)))
        for i, f in futs:
            out[i] = f.result()
    return out


# ---------------- C-3: control B at N=400, paired ------------------------------------------
b_tasks = rng.sample(rows, 200) + rng.sample(rows, 200)  # 400 with replacement across halves
b_tasks = (rows * 2)[:400] if len(rows) < 400 else rng.sample(rows, 400)
b_tasks = (rows + rows)[:400]  # deterministic: every task twice (manifest has 200)
print("[C-3] control B at N=400 (each task twice, paired vs F0)")
f0_res = batch([r["prompt"] for r in b_tasks])
ch_res = batch([r["prompt"] + "\n\nPrior attempt record:\n" + _ALNUM.sub("x", d0_body(r["uid"]))
                for r in b_tasks])
f0_ok = [extract_numeric(x.text if x.status == "ok" else None).value == gold[r["uid"]]
         for x, r in zip(f0_res, b_tasks)]
ch_ok = [extract_numeric(x.text if x.status == "ok" else None).value == gold[r["uid"]]
         for x, r in zip(ch_res, b_tasks)]
b = sum(1 for x, y in zip(ch_ok, f0_ok) if x and not y)
c = sum(1 for x, y in zip(ch_ok, f0_ok) if y and not x)
acc = lambda v: sum(v) / len(v)
B = {"n": 400, "f0": acc(f0_ok), "cheat": acc(ch_ok), "delta": acc(ch_ok) - acc(f0_ok),
     "mcnemar_p": mcnemar_exact(b, c),
     "fail": (mcnemar_exact(b, c) < 0.05) and (acc(ch_ok) - acc(f0_ok) >= 0.05)}
B["pass"] = not B["fail"]

# ---------------- C-2: control C with full diagnostics -------------------------------------
print("[C-2] control C x100 with diagnostics")
c_tasks = rng.sample(rows, 100)
c_prompts = [("A prior attempt's record is shown. The problem statement is withheld.\n\n"
              + d0_body(r["uid"]) +
              "\n\nBased ONLY on the record above: how many of the five integers were prime?\n"
              "If the record does not contain enough information, give your best guess anyway.\n"
              "Give your final answer on the last line in the form: ANSWER: <count>")
             for r in c_tasks]
c_res = batch(c_prompts)
extracted, flags = [], Counter()
for x in c_res:
    ex = extract_numeric(x.text if x.status == "ok" else None)
    extracted.append(ex.value)
    for f in ex.flags:
        flags[f] += 1
hits = sum(1 for v, r in zip(extracted, c_tasks) if v == gold[r["uid"]])
in_range = sum(1 for v in extracted if v in (1, 2, 3, 4))
import math
pv_hi = sum(math.comb(100, i) * 0.25**i * 0.75**(100 - i) for i in range(hits, 101))
pv_lo = sum(math.comb(100, i) * 0.25**i * 0.75**(100 - i) for i in range(0, hits + 1))
C = {"n": 100, "recovery": hits / 100,
     "parse_fail_rate": sum(1 for v in extracted if v is None) / 100,
     "in_answer_range_rate": in_range / 100,
     "extracted_distribution": dict(Counter(str(v) for v in extracted)),
     "extract_flags": dict(flags),
     "refusals": flags.get("refusal", 0),
     "binom_p_vs_025_upper": pv_hi, "binom_p_vs_025_lower": pv_lo,
     "interpretable": (in_range / 100) >= 0.80,
     "pass": (pv_hi > 0.05) and (hits / 100 <= 0.35) and (in_range / 100) >= 0.80,
     "note": ("v2: solver instructed to guess when uninformed, so answers land in the gold "
              "space and a pass is distinguishable from a broken scorer (HB C-2). "
              "Two-sided honesty: below-chance recovery is reported, not credited.")}

res = {"run_id": "R3-SUPPLEMENT-2026-08-19", "solver": SOLVER,
       "B_cheat_n400": B, "C_leakage_diagnosed": C,
       "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
       "host": "SKULLPORT", "executor": "ergon"}
tmp = OUT.with_suffix(".json.tmp")
tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
os.replace(tmp, OUT)
print(json.dumps(res, indent=2))
