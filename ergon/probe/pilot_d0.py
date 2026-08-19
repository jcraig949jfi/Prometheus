"""THE PILOT — D0 scope (prereg, as amended; every gate passed 2026-08-19).

Gates cleared before this ran: leveled manifest (M30, LEVELED, point 0.500, CI wholly in band,
movable 0.415) - R7-D0 on this family (classifier 0.317 vs 0.55) - R3 live A/B/C/D all PASS.

Arms (5, per the prereg pilot): F0, F-null, F-prom-retrieved(D0), F-oracle, F-answer.
Tasks: the POST-SCREEN set (146 of 200 — contaminated-or-trivial excluded per R13).
Permitted verdicts: PIPELINE_ADMISSIBLE / PIPELINE_NOT_ADMISSIBLE plus a directional estimate.
At this N the MDE is ~11-13pp, so a flat result is INCONCLUSIVE-UNDERPOWERED BY CONSTRUCTION
and can never route a diagnostic-matrix row. D1-D3 do not run: F-null is
INADMISSIBLE-NO-FAIR-NULL there (Charon), and distance description is a separate measurement.

Recorded deviation (BC-7 makes it a number): projected packets are ~15-60 tokens, so the ±5%
per-task token-matching rule is unmeetable at this scale without neutral-filler padding, which
is itself the topic-priming hazard. Per-arm token counts are logged instead.
"""
import json
import os
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.solver import call
from ergon.probe.extract import extract_numeric
from ergon.probe.assemble import assemble_retrieved, count_tokens, load_prepass, select_residue
from ergon.probe.f_null import build_f_null
from ergon.probe.analysis import mcnemar_exact, paired_bootstrap
import numpy as np

SOLVER = "deepseek:deepseek-v4-flash"
RATE_RPM, WORKERS, MAX_TOK, TIMEOUT = 40.0, 6, 8192, 420
RUN_ID = "PILOT-D0-2026-08-19"
OUT = ROOT / "ergon/probe/ledgers/pilot_d0_2026-08-19.json"

MAN = ROOT / "ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl"
LED = ROOT / "ergon/probe/ledgers/nearmiss_mix-M30_prepass.jsonl"
SCREEN = ROOT / "ergon/probe/ledgers/nearmiss_mix-M30_prepass_screen.json"

rows = [json.loads(l) for l in MAN.read_text(encoding="utf-8").splitlines()]
gold = {r["uid"]: r["gold_int"] for r in rows}
screen = json.loads(SCREEN.read_text(encoding="utf-8"))
excluded = set(screen["contaminated_or_trivial_lenient"])
tasks = [r for r in rows if r["uid"] not in excluded]
pool = load_prepass(LED)
tau = {"nearmiss_mix-M30_prepass": 10_000}

# rep-1 correctness per task (GOLD-DERIVED — legal for the F-oracle ceiling arm ONLY)
led_rows = [json.loads(l) for l in LED.read_text(encoding="utf-8").splitlines()]
rep1_verdict = {r["uid"]: r.get("extracted_int") for r in led_rows if r["rep"] == 1}
rep1_correct = {u: (v == gold[u]) for u, v in rep1_verdict.items() if u in gold}


def prom_packet(uid):
    recs = select_residue(pool, stratum="D0", target_uid=uid)
    return assemble_retrieved(task_uid=uid, stratum="D0", records=recs, tau=tau)


def null_packet(uid, prom_text):
    fn = build_f_null(task_uid=uid, stratum="D0",
                      prom_records=select_residue(pool, stratum="D0", target_uid=uid),
                      prom_packet_text=prom_text, pool=pool, tau=tau, seed=20260819)
    return fn.packet.text if hasattr(fn, "packet") else fn.text


def oracle_text(uid):
    if rep1_correct.get(uid):
        return ("Ground-truth diagnosis of the prior attempt: its method was sound and its "
                "conclusion was correct. The same care suffices.")
    return ("Ground-truth diagnosis of the prior attempt: it misjudged at least one element "
            "by relying on an insufficient primality test (a single small-base Fermat-style "
            "check). For integers of this size, a deterministic Miller-Rabin test over the "
            "first twelve prime bases is decisive. The number of misjudged elements is withheld.")


ARMS = ("F0", "F-null", "F-prom-retrieved", "F-oracle", "F-answer")


def build_prompt(arm, r):
    base = r["prompt"]
    if arm == "F0":
        return base
    if arm == "F-prom-retrieved":
        return "A prior attempt record:\n" + prom_packet(r["uid"]).body + "\n\n" + base
    if arm == "F-null":
        return ("A prior attempt record:\n"
                + null_packet(r["uid"], prom_packet(r["uid"]).body) + "\n\n" + base)
    if arm == "F-oracle":
        return oracle_text(r["uid"]) + "\n\n" + base
    return "Prior context: the correct count is %d.\n\n" % gold[r["uid"]] + base


jobs = [(arm, r) for arm in ARMS for r in tasks]
print("[pilot] %d tasks x %d arms = %d calls" % (len(tasks), len(ARMS), len(jobs)))
interval = 60.0 / RATE_RPM
t0 = time.monotonic()
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = []
    for i, (arm, r) in enumerate(jobs):
        sl = (t0 + i * interval) - time.monotonic()
        if sl > 0:
            time.sleep(sl)
        prompt = build_prompt(arm, r)
        futs.append((arm, r["uid"], count_tokens(prompt),
                     ex.submit(call, SOLVER, prompt, max_tokens=MAX_TOK, timeout=TIMEOUT)))
    ledger = []
    for arm, uid, ptoks, f in futs:
        res = f.result()
        v = extract_numeric(res.text if res.status == "ok" else None).value
        ledger.append({"run_id": RUN_ID, "arm": arm, "uid": uid, "status": res.status,
                       "packet_tokens": ptoks, "prompt_tokens": res.prompt_tokens,
                       "extracted": v, "correct": (v == gold[uid]),
                       "latency_s": res.latency_s, "error_type": res.error_type,
                       "ts_utc": res.ts_utc})

led_path = ROOT / "ergon/probe/ledgers/pilot_d0_ledger.jsonl"
with led_path.open("w", encoding="utf-8") as fh:
    for row in ledger:
        fh.write(json.dumps(row) + "\n")

by = {}
for row in ledger:
    by[(row["arm"], row["uid"])] = row
acc = {a: sum(by[(a, t["uid"])]["correct"] for t in tasks) / len(tasks) for a in ARMS}
transport = {a: sum(1 for t in tasks if by[(a, t["uid"])]["status"] != "ok") for a in ARMS}
pf = {a: sum(1 for t in tasks if by[(a, t["uid"])]["extracted"] is None) / len(tasks)
      for a in ARMS}
tok = {a: sum(by[(a, t["uid"])]["packet_tokens"] for t in tasks) / len(tasks) for a in ARMS}

prom = np.array([float(by[("F-prom-retrieved", t["uid"])]["correct"]) for t in tasks])
null = np.array([float(by[("F-null", t["uid"])]["correct"]) for t in tasks])
delta, lo, hi, p = paired_bootstrap(prom - null)
b = int(np.sum((prom == 1) & (null == 0)))
c = int(np.sum((prom == 0) & (null == 1)))

comparable = [a for a in ARMS if a != "F-answer"]
pf_spread = max(pf[a] for a in comparable) - min(pf[a] for a in comparable)
admissible = (pf_spread <= 0.10) and all(transport[a] / len(tasks) <= 0.05 for a in ARMS)

res = {
    "run_id": RUN_ID, "solver": SOLVER, "n_tasks": len(tasks),
    "scope": "D0 ONLY (Delta_carry interpretable at D0 alone; D1-D3 not run)",
    "accuracy_by_arm": {k: round(v, 4) for k, v in acc.items()},
    "parse_fail_by_arm": {k: round(v, 4) for k, v in pf.items()},
    "transport_fail_by_arm": transport,
    "mean_packet_tokens_by_arm": {k: round(v, 1) for k, v in tok.items()},
    "pf_spread_comparable_arms": round(pf_spread, 4),
    "directional_estimate": {
        "label": "F-prom-retrieved(D0) - F-null, paired bootstrap 10k seed 0",
        "delta": round(delta, 4), "ci95": [round(lo, 4), round(hi, 4)],
        "p": round(p, 4), "mcnemar_p": round(mcnemar_exact(b, c), 4),
        "discordant": {"prom_only": b, "null_only": c},
    },
    "verdict": "PIPELINE_ADMISSIBLE" if admissible else "PIPELINE_NOT_ADMISSIBLE",
    "verdict_constraints": [
        "directional estimate ONLY - MDE at this N is ~11-13pp",
        "a flat result is INCONCLUSIVE-UNDERPOWERED BY CONSTRUCTION",
        "this run can NEVER route a diagnostic-matrix row",
        "F-answer participates in no substantive comparison",
    ],
    "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "host": "SKULLPORT", "executor": "ergon",
}
tmp = OUT.with_suffix(".json.tmp")
tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
os.replace(tmp, OUT)
print(json.dumps(res, indent=2))
